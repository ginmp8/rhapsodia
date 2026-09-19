#!/usr/bin/env python3
"""Deterministic regression tests for reproducibility controls."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("nuget_update.py")
spec = importlib.util.spec_from_file_location("nuget_update", SCRIPT)
assert spec and spec.loader
nuget = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = nuget
spec.loader.exec_module(nuget)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def args_for(tmp: Path, *extra: str):
    props = tmp / "Directory.Packages.props"
    argv = ["check", "--file", str(props), "--disable-restore-validation", *extra]
    args = nuget.build_parser().parse_args(argv)
    if not args.source:
        args.source = [nuget.DEFAULT_SOURCE]
    return args


def candidate(version: str, *, listed=True, deprecated=False, vulnerabilities=None, trusted=True, source="feed-a"):
    parsed = nuget.parse_nuget_version(version)
    assert parsed is not None
    metadata = nuget.PackageMetadata(
        version=version,
        listed=listed,
        deprecated=deprecated,
        vulnerabilities=vulnerabilities or [],
        source=source,
        trusted=trusted,
    )
    return nuget.Candidate(parsed, metadata, source)


def test_candidate_safety(tmp: Path) -> None:
    args = args_for(tmp)
    prerelease = nuget.parse_nuget_version("1.2.0-beta.1")
    stable = nuget.parse_nuget_version("1.2.0")
    current = nuget.parse_nuget_version("1.0.0")
    assert prerelease and stable and current
    assert_true(not nuget.is_allowed_by_version_policy(current, prerelease, False, True, True, False), "prerelease must be rejected")
    assert_true(nuget.is_allowed_by_version_policy(current, stable, False, True, True, False), "stable candidate should be allowed")

    vuln = nuget.Vulnerability("high", 2, "https://advisory", "[1.0.0,2.0.0)", "vuln-feed")
    cases = [
        (candidate("1.2.0", vulnerabilities=[vuln]), "candidate-vulnerable"),
        (candidate("1.2.0", deprecated=True), "candidate-deprecated"),
        (candidate("1.2.0", listed=False), "candidate-unlisted"),
        (candidate("1.2.0", trusted=False), "candidate-metadata-untrusted"),
    ]
    for item, code in cases:
        rejection = nuget.safety_rejection_reason(item, args)
        assert_true(rejection is not None and rejection.code == code, f"expected {code}, got {rejection}")


def test_lock_pin_identity(tmp: Path) -> None:
    text = """<Project><ItemGroup>
<PackageVersion Include="Pinned.Package" Version="1.0.0" Pin="true" />
<PackageVersion Include="Locked.Package" Version="2.0.0" Locked="true" />
</ItemGroup></Project>"""
    entries = nuget.parse_package_entries(text)
    assert_true(len(entries) == 2 and all(item.locked for item in entries), "pin/lock must be detected")
    identity1, records1 = nuget.lock_pin_identity(entries)
    identity2, records2 = nuget.lock_pin_identity(entries)
    assert_true(identity1 == identity2 and records1 == records2, "lock identity must be stable")


def test_multiple_feed_precedence(tmp: Path) -> None:
    original_auto = nuget.fetch_autocomplete_versions
    original_reg = nuget.fetch_registration_metadata
    original_vuln = nuget.fetch_vulnerability_info_for_package
    try:
        nuget.fetch_autocomplete_versions = lambda package, source, timeout: ["1.2.0"]
        nuget.fetch_registration_metadata = lambda package, source, timeout: {
            "1.2.0": nuget.PackageMetadata("1.2.0", True, False, [], source, True)
        }
        nuget.fetch_vulnerability_info_for_package = lambda package, source, timeout: []
        items, _ = nuget.fetch_candidates("Pkg", ["https://first.example/v3/index.json", "https://second.example/v3/index.json"], 1, None, False)
        assert_true(items[0].source == "https://first.example/v3/index.json", "first configured feed must win exact-version tie")
    finally:
        nuget.fetch_autocomplete_versions = original_auto
        nuget.fetch_registration_metadata = original_reg
        nuget.fetch_vulnerability_info_for_package = original_vuln


def test_metadata_snapshot_replay_and_miss(tmp: Path) -> None:
    body = json.dumps({"resources": []}, separators=(",", ":"))
    snapshot = {
        "schemaVersion": nuget.EVIDENCE_SCHEMA_VERSION,
        "records": [{"url": "https://feed.example/index.json", "body": body, "rawSha256": nuget.sha256_text(body)}],
    }
    path = tmp / "snapshot.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    nuget.reset_runtime_state()
    nuget.configure_metadata_replay(path)
    payload = nuget.get_json("https://feed.example/index.json", 1)
    assert_true(payload == {"resources": []}, "snapshot replay must return captured payload")
    try:
        nuget.get_json("https://feed.example/missing.json", 1)
        raise AssertionError("missing replay URL should fail closed")
    except nuget.UpdaterError as exc:
        assert_true(exc.code == "metadata-snapshot-miss", str(exc))


def test_expected_receipt_detects_metadata_change(tmp: Path) -> None:
    prior = {"decisionIdentity": "a", "metadataSnapshotSha256": "m1"}
    current = {"decisionIdentity": "b", "metadataSnapshotSha256": "m2"}
    path = tmp / "receipt.json"
    path.write_text(json.dumps(prior), encoding="utf-8")
    try:
        nuget.verify_expected_decision_receipt(path, current)
        raise AssertionError("receipt mismatch should fail")
    except nuget.UpdaterError as exc:
        assert_true(exc.code == "decision-receipt-mismatch", str(exc))


def test_framework_restore_failure_is_stable(tmp: Path) -> None:
    props = tmp / "Directory.Packages.props"
    props.write_text('<Project><ItemGroup><PackageVersion Include="Pkg" Version="1.0.0" /></ItemGroup></Project>', encoding="utf-8")
    entry = nuget.parse_package_entries(props.read_text())[0]
    args = args_for(tmp)
    args.disable_restore_validation = False
    args.source = ["https://feed.example/v3/index.json"]

    original_current = nuget.get_current_metadata
    original_fetch = nuget.fetch_candidates
    original_compat = nuget.validate_package_compatibility
    try:
        nuget.get_current_metadata = lambda *a, **k: nuget.PackageMetadata("1.0.0", True, False, [], args.source[0], True)
        safe = candidate("1.2.0", source=args.source[0])
        nuget.fetch_candidates = lambda *a, **k: ([safe], args.source[0])
        nuget.validate_package_compatibility = lambda *a, **k: nuget.CompatibilityResult(False, "restore-failed", "failure", ["dotnet", "restore"], 1, nuget.sha256_text("failure"))
        decision = nuget.decide_package_update(entry, args, None)
        assert_true(decision.reason_code == "no-compatible-candidate", decision.reason_code or "")
        assert_true(decision.compatibility_evidence[0]["kind"] == "restore-failed", str(decision.compatibility_evidence))
    finally:
        nuget.get_current_metadata = original_current
        nuget.fetch_candidates = original_fetch
        nuget.validate_package_compatibility = original_compat


def test_unsafe_latest_falls_back_with_stable_rejection(tmp: Path) -> None:
    props = tmp / "Directory.Packages.props"
    props.write_text('<Project><ItemGroup><PackageVersion Include="Pkg" Version="1.0.0" /></ItemGroup></Project>', encoding="utf-8")
    entry = nuget.parse_package_entries(props.read_text())[0]
    args = args_for(tmp)
    args.source = ["https://feed.example/v3/index.json"]
    vuln = nuget.Vulnerability("high", 2, "https://advisory", "[1.3.0]", "vuln-feed")
    unsafe = candidate("1.3.0", vulnerabilities=[vuln], source=args.source[0])
    safe = candidate("1.2.0", source=args.source[0])
    original_current = nuget.get_current_metadata
    original_fetch = nuget.fetch_candidates
    try:
        nuget.get_current_metadata = lambda *a, **k: nuget.PackageMetadata("1.0.0", True, False, [], args.source[0], True)
        nuget.fetch_candidates = lambda *a, **k: ([unsafe, safe], args.source[0])
        decision = nuget.decide_package_update(entry, args, None)
        assert_true(decision.selected_version == "1.2.0", str(decision))
        assert_true(decision.candidate_rejections and decision.candidate_rejections[0]["code"] == "candidate-vulnerable", str(decision.candidate_rejections))
    finally:
        nuget.get_current_metadata = original_current
        nuget.fetch_candidates = original_fetch


def test_metadata_unavailable_is_not_guessed(tmp: Path) -> None:
    props = tmp / "Directory.Packages.props"
    props.write_text('<Project><ItemGroup><PackageVersion Include="Pkg" Version="1.0.0" /></ItemGroup></Project>', encoding="utf-8")
    entry = nuget.parse_package_entries(props.read_text())[0]
    args = args_for(tmp)
    original_current = nuget.get_current_metadata
    original_fetch = nuget.fetch_candidates
    try:
        nuget.get_current_metadata = lambda *a, **k: None
        nuget.fetch_candidates = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("feed unavailable"))
        decision = nuget.decide_package_update(entry, args, None)
        assert_true(decision.action == "error" and decision.reason_code == "metadata-unavailable", str(decision))
        assert_true(decision.selected_version is None, str(decision))
    finally:
        nuget.get_current_metadata = original_current
        nuget.fetch_candidates = original_fetch


def test_atomic_write_interruption_preserves_input(tmp: Path) -> None:
    props = tmp / "Directory.Packages.props"
    original = '<Project><ItemGroup><PackageVersion Include="Pkg" Version="1.0.0" /></ItemGroup></Project>\n'
    updated = original.replace("1.0.0", "1.1.0")
    props.write_text(original, encoding="utf-8")
    baseline = nuget.sha256_file(props)
    args = args_for(tmp)
    original_atomic = nuget.atomic_write_text

    def fail_only_target(path: Path, content: str) -> None:
        if path.resolve() == props.resolve():
            raise OSError("simulated interruption")
        original_atomic(path, content)

    nuget.atomic_write_text = fail_only_target
    try:
        try:
            nuget.commit_package_update(props, updated, baseline, nuget.sha256_text(updated), args)
            raise AssertionError("interrupted write should fail")
        except nuget.UpdaterError as exc:
            assert_true(exc.code == "atomic-write-failed", str(exc))
        assert_true(nuget.sha256_file(props) == baseline, "input must survive interrupted atomic write")
    finally:
        nuget.atomic_write_text = original_atomic


def test_validation_failure_rolls_back_and_rerun_is_no_change(tmp: Path) -> None:
    props = tmp / "Directory.Packages.props"
    versions = tmp / "versions.json"
    original = '<Project><ItemGroup><PackageVersion Include="Pkg" Version="1.0.0" /></ItemGroup></Project>\n'
    props.write_text(original, encoding="utf-8")
    versions.write_text(json.dumps({"Pkg": ["1.0.0", "1.1.0", "1.2.0-beta.1"]}), encoding="utf-8")

    parser = nuget.build_parser()
    args = parser.parse_args([
        "update", "--file", str(props), "--versions-file", str(versions), "--allow-untrusted-versions-file",
        "--disable-restore-validation", "--write", "--validation-command", "test::python3 -c 'import sys;sys.exit(1)'"
    ])
    if not args.source:
        args.source = [nuget.DEFAULT_SOURCE]
    with contextlib.redirect_stdout(io.StringIO()):
        code = nuget.run(args)
    assert_true(code == nuget.EXIT_POLICY_FAILURE, f"expected policy failure, got {code}")
    assert_true(props.read_text(encoding="utf-8") == original, "validation failure must rollback")

    args2 = parser.parse_args([
        "update", "--file", str(props), "--versions-file", str(versions), "--allow-untrusted-versions-file",
        "--disable-restore-validation", "--write"
    ])
    if not args2.source:
        args2.source = [nuget.DEFAULT_SOURCE]
    with contextlib.redirect_stdout(io.StringIO()):
        code2 = nuget.run(args2)
    assert_true(code2 == 0, "successful update should pass")
    after_first = props.read_text(encoding="utf-8")
    assert_true("1.1.0" in after_first, after_first)
    with contextlib.redirect_stdout(io.StringIO()):
        code3 = nuget.run(args2)
    assert_true(code3 == 0, "rerun should pass without changes")
    assert_true(props.read_text(encoding="utf-8") == after_first, "rerun must be idempotent")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="nuget-repro-tests-") as raw:
        root = Path(raw)
        for index, test in enumerate([
            test_candidate_safety,
            test_lock_pin_identity,
            test_multiple_feed_precedence,
            test_metadata_snapshot_replay_and_miss,
            test_expected_receipt_detects_metadata_change,
            test_framework_restore_failure_is_stable,
            test_unsafe_latest_falls_back_with_stable_rejection,
            test_metadata_unavailable_is_not_guessed,
            test_atomic_write_interruption_preserves_input,
            test_validation_failure_rolls_back_and_rerun_is_no_change,
        ]):
            case = root / f"case-{index}"
            case.mkdir()
            nuget.reset_runtime_state()
            test(case)
    print("reproducibility regression tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
