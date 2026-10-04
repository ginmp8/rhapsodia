#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
from pathlib import Path

SCRIPT = Path(os.environ.get("NUGET_UPDATE_SCRIPT", str(Path(__file__).with_name("nuget_update.py"))))
spec = importlib.util.spec_from_file_location("nuget_update_research_eval", SCRIPT)
assert spec and spec.loader
nuget = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = nuget
spec.loader.exec_module(nuget)


def assert_true(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def make_props(root: Path, body: str = '<Project><ItemGroup><PackageVersion Include="Pkg" Version="1.0.0" /></ItemGroup></Project>\n') -> Path:
    path = root / "Directory.Packages.props"
    path.write_text(body, encoding="utf-8")
    return path


def test_semver_prerelease_total_order(root: Path) -> None:
    alpha1 = nuget.parse_nuget_version("1.0.0-alpha.1")
    alphabeta = nuget.parse_nuget_version("1.0.0-alpha.beta")
    alpha2 = nuget.parse_nuget_version("1.0.0-alpha.2")
    alpha10 = nuget.parse_nuget_version("1.0.0-alpha.10")
    stable = nuget.parse_nuget_version("1.0.0")
    assert all([alpha1, alphabeta, alpha2, alpha10, stable])
    assert_true(alpha1 < alphabeta, "numeric prerelease identifier must sort before alphanumeric")
    assert_true(alpha2 < alpha10, "numeric prerelease identifiers must compare numerically")
    assert_true(alpha10 < stable, "stable release must sort after prerelease")


def test_same_version_multi_source_is_ambiguous(root: Path) -> None:
    original_auto = nuget.fetch_autocomplete_versions
    original_reg = nuget.fetch_registration_metadata
    original_vuln = nuget.fetch_vulnerability_info_for_package
    try:
        nuget.fetch_autocomplete_versions = lambda package, source, timeout: ["1.2.0"]
        nuget.fetch_registration_metadata = lambda package, source, timeout: {
            "1.2.0": nuget.PackageMetadata("1.2.0", True, False, [], source, True)
        }
        nuget.fetch_vulnerability_info_for_package = lambda package, source, timeout: []
        items, _ = nuget.fetch_candidates(
            "Pkg",
            ["https://first.example/v3/index.json", "https://second.example/v3/index.json"],
            1,
            None,
            False,
        )
        assert_true(len(items) == 1, f"expected one version candidate, got {len(items)}")
        assert_true(len(items[0].source_candidates) == 2, f"source ambiguity not preserved: {items[0].source_candidates}")
        args = nuget.build_parser().parse_args(["check", "--file", str(make_props(root)), "--disable-restore-validation"])
        nuget.configure_nuget_inputs(args)
        rejection = nuget.safety_rejection_reason(items[0], args)
        assert_true(rejection is not None and rejection.code == "candidate-source-ambiguous", str(rejection))
    finally:
        nuget.fetch_autocomplete_versions = original_auto
        nuget.fetch_registration_metadata = original_reg
        nuget.fetch_vulnerability_info_for_package = original_vuln


def test_package_source_mapping_and_config_identity(root: Path) -> None:
    props = make_props(root)
    config = root / "NuGet.Config"
    config.write_text(
        """<configuration>
  <packageSources>
    <clear />
    <add key="public" value="https://api.nuget.org/v3/index.json" />
    <add key="internal" value="https://packages.example/v3/index.json" />
  </packageSources>
  <packageSourceMapping>
    <packageSource key="public"><package pattern="*" /></packageSource>
    <packageSource key="internal"><package pattern="Contoso.*" /><package pattern="Contoso.Core" /></packageSource>
  </packageSourceMapping>
</configuration>\n""",
        encoding="utf-8",
    )
    args = nuget.build_parser().parse_args([
        "check", "--file", str(props), "--nuget-config", str(config), "--disable-restore-validation"
    ])
    nuget.configure_nuget_inputs(args)
    assert_true(nuget.sources_for_package("Contoso.Core", args) == ["https://packages.example/v3/index.json"], "exact mapping should select internal source")
    assert_true(nuget.sources_for_package("Contoso.Widget", args) == ["https://packages.example/v3/index.json"], "prefix mapping should beat wildcard")
    assert_true(nuget.sources_for_package("Newtonsoft.Json", args) == ["https://api.nuget.org/v3/index.json"], "wildcard mapping should select public source")
    model = args._nuget_config_model
    assert_true(model.sha256 == nuget.sha256_file(config), "config identity must bind exact config bytes")
    assert_true(bool(model.mapping_identity), "source mapping identity must be recorded")


def test_config_aware_compatibility_restore_isolates_caches(root: Path) -> None:
    config = root / "NuGet.Config"
    config.write_text('<configuration><packageSources><add key="x" value="https://feed.example/v3/index.json" /></packageSources></configuration>', encoding="utf-8")
    original_has = nuget.has_dotnet
    original_run = nuget.subprocess.run
    captured: dict[str, object] = {}
    try:
        nuget.has_dotnet = lambda: True
        def fake_run(command, **kwargs):
            captured["command"] = list(command)
            captured["env"] = dict(kwargs.get("env") or {})
            return subprocess.CompletedProcess(command, 0, stdout="ok")
        nuget.subprocess.run = fake_run
        result = nuget.validate_package_compatibility(
            "Pkg", "1.2.0", "net10.0", ["https://ignored.example/v3/index.json"], 5, nuget_config=config
        )
        assert_true(result.compatible, str(result))
        command = captured["command"]
        assert_true("--configfile" in command and str(config.resolve()) in command, str(command))
        assert_true("--source" not in command, str(command))
        env = captured["env"]
        assert_true("NUGET_PACKAGES" in env and "NUGET_HTTP_CACHE_PATH" in env, str(env))
        assert_true(str(env["NUGET_PACKAGES"]).startswith(tempfile.gettempdir()), str(env["NUGET_PACKAGES"]))
    finally:
        nuget.has_dotnet = original_has
        nuget.subprocess.run = original_run


def test_cpm_guards_condition_and_duplicate(root: Path) -> None:
    props = make_props(root, '<Project><ItemGroup>\n<PackageVersion Include="Pkg" Version="1.0.0" Condition="\'$(TargetFramework)\' == \'net10.0\'" />\n</ItemGroup></Project>\n')
    args = nuget.build_parser().parse_args(["scan", "--file", str(props)])
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            nuget.run(args)
        raise AssertionError("conditional PackageVersion should fail closed")
    except nuget.UpdaterError as exc:
        assert_true(exc.code == "conditional-package-version-unsupported", str(exc))

    props.write_text('<Project><ItemGroup>\n<PackageVersion Include="Pkg" Version="1.0.0" />\n<PackageVersion Update="Pkg" Version="1.1.0" />\n</ItemGroup></Project>\n', encoding="utf-8")
    args2 = nuget.build_parser().parse_args(["scan", "--file", str(props)])
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            nuget.run(args2)
        raise AssertionError("duplicate selected PackageVersion should fail closed")
    except nuget.UpdaterError as exc:
        assert_true(exc.code == "duplicate-package-version-declarations", str(exc))


def test_version_override_is_not_silently_overwritten(root: Path) -> None:
    props = make_props(root)
    (root / "App.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><ItemGroup><PackageReference Include="Pkg" VersionOverride="1.0.5" /></ItemGroup></Project>', encoding="utf-8")
    versions = root / "versions.json"
    versions.write_text(json.dumps({"Pkg": ["1.0.0", "1.1.0"]}), encoding="utf-8")
    args = nuget.build_parser().parse_args([
        "check", "--file", str(props), "--versions-file", str(versions), "--allow-untrusted-versions-file",
        "--disable-restore-validation", "--repository-root", str(root)
    ])
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        code = nuget.run(args)
    report = json.loads(stream.getvalue())
    assert_true(code == 0, f"unexpected code {code}")
    assert_true(report["packages"][0]["reason_code"] == "version-override-active", str(report["packages"][0]))


def test_restore_audit_and_pruning_evidence(root: Path) -> None:
    output = "NU1903: Package 'Foo' 1.0.0 has a known high severity vulnerability\nNU1510: PackageReference Bar will not be pruned\n"
    result = nuget.analyze_restore_audit_output(output, "high")
    assert_true(result["status"] == "fail", str(result))
    assert_true(result["vulnerabilityWarningCount"] == 1, str(result))
    assert_true(result["pruneWarningCount"] == 1, str(result))
    missing = nuget.analyze_restore_audit_output("NU1905: Audit source did not provide vulnerability data", "low")
    assert_true(missing["status"] == "fail" and missing["auditSourceUnavailable"], str(missing))


def test_lockfile_rollback_and_exact_lkg_bytes(root: Path) -> None:
    props = make_props(root)
    original_props = b'\xef\xbb\xbf<Project><ItemGroup><PackageVersion Include="Pkg" Version="1.0.0" /></ItemGroup></Project>\r\n'
    props.write_bytes(original_props)
    lock = root / "packages.lock.json"
    original_lock = b'{"version":1,"dependencies":{"net10.0":{"Pkg":{"type":"Direct","requested":"[1.0.0, )","resolved":"1.0.0","contentHash":"abc"}}}}\n'
    lock.write_bytes(original_lock)
    versions = root / "versions.json"
    versions.write_text(json.dumps({"Pkg": ["1.0.0", "1.1.0"]}), encoding="utf-8")
    helper = root / "fail_validation.py"
    helper.write_text(
        "from pathlib import Path\np=Path('packages.lock.json'); p.write_bytes(b'changed')\nPath('nested').mkdir(exist_ok=True)\nPath('nested/packages.lock.json').write_text('{}')\nraise SystemExit(1)\n",
        encoding="utf-8",
    )
    args = nuget.build_parser().parse_args([
        "update", "--file", str(props), "--versions-file", str(versions), "--allow-untrusted-versions-file",
        "--disable-restore-validation", "--write", "--repository-root", str(root),
        "--validation-command", f"test::{sys.executable} {helper}"
    ])
    with contextlib.redirect_stdout(io.StringIO()):
        code = nuget.run(args)
    assert_true(code == nuget.EXIT_POLICY_FAILURE, str(code))
    assert_true(props.read_bytes() == original_props, "rollback must restore exact Directory.Packages.props bytes including BOM/newlines")
    assert_true(lock.read_bytes() == original_lock, "rollback must restore exact lock file bytes")
    assert_true(not (root / "nested" / "packages.lock.json").exists(), "validation-created lock file must be removed on rollback")


def test_authenticated_source_has_stable_diagnostic(root: Path) -> None:
    original = nuget.urllib.request.urlopen
    try:
        def denied(*args, **kwargs):
            raise urllib.error.HTTPError("https://feed.example/v3/index.json", 401, "Unauthorized", {}, None)
        nuget.urllib.request.urlopen = denied
        try:
            nuget.get_json("https://feed.example/v3/index.json", 1)
            raise AssertionError("401 should not be collapsed into a generic metadata failure")
        except nuget.UpdaterError as exc:
            assert_true(exc.code == "authenticated-source-credentials-required", str(exc))
    finally:
        nuget.urllib.request.urlopen = original


def test_report_output_cannot_alias_input(root: Path) -> None:
    props = make_props(root)
    args = nuget.build_parser().parse_args(["scan", "--file", str(props), "--report", str(props)])
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            nuget.run(args)
        raise AssertionError("report path aliasing input must fail before write")
    except nuget.UpdaterError as exc:
        assert_true(exc.code == "output-aliases-input", str(exc))
    assert_true("PackageVersion" in props.read_text(encoding="utf-8"), "input must remain intact")


def main() -> int:
    tests = [
        test_semver_prerelease_total_order,
        test_same_version_multi_source_is_ambiguous,
        test_package_source_mapping_and_config_identity,
        test_config_aware_compatibility_restore_isolates_caches,
        test_cpm_guards_condition_and_duplicate,
        test_version_override_is_not_silently_overwritten,
        test_restore_audit_and_pruning_evidence,
        test_lockfile_rollback_and_exact_lkg_bytes,
        test_authenticated_source_has_stable_diagnostic,
        test_report_output_cannot_alias_input,
    ]
    with tempfile.TemporaryDirectory(prefix="nuget-research-eval-") as raw:
        root = Path(raw)
        failures = []
        for index, test in enumerate(tests):
            case = root / f"case-{index}"
            case.mkdir()
            try:
                nuget.reset_runtime_state()
                test(case)
            except BaseException as exc:
                failures.append(f"{test.__name__}: {type(exc).__name__}: {exc}")
        if failures:
            print("research improvement evaluator failures:")
            for failure in failures:
                print(f"- {failure}")
            return 1
    print("research improvement evaluator passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
