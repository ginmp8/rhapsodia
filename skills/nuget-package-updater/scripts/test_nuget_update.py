#!/usr/bin/env python3
"""Offline smoke tests for nuget_update.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("nuget_update.py")


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="nuget-updater-test-") as tmp:
        root = Path(tmp)
        props = root / "Directory.Packages.props"
        versions = root / "versions.json"

        props.write_text(
            """<Project>
  <ItemGroup>
    <PackageVersion Include="Newtonsoft.Json" Version="13.0.1" />
    <PackageVersion Include="Pinned.Package" Version="1.0.0" Locked="true" />
    <!-- nuget-updater: lock -->
    <PackageVersion Include="Comment.Locked" Version="2.0.0" />
    <PackageVersion Include="Property.Package" Version="$(PropertyPackageVersion)" />
  </ItemGroup>
</Project>
""",
            encoding="utf-8",
        )

        versions.write_text(
            json.dumps(
                {
                    "Newtonsoft.Json": ["13.0.1", "13.0.4", "14.0.0-beta.1"],
                    "Pinned.Package": ["1.0.0", "1.1.0"],
                    "Comment.Locked": ["2.0.0", "2.1.0"],
                    "Property.Package": ["3.0.0", "3.1.0"],
                }
            ),
            encoding="utf-8",
        )

        scan = run_command(["scan", "--file", str(props), "--report-format", "json"], root)
        assert_true(scan.returncode == 0, scan.stdout)
        scan_payload = json.loads(scan.stdout)
        assert_true(scan_payload["lockedCount"] == 2, scan.stdout)

        update = run_command(
            [
                "update",
                "--file",
                str(props),
                "--versions-file",
                str(versions),
                "--allow-untrusted-versions-file",
                "--disable-restore-validation",
                "--write",
                "--report-format",
                "json",
                "--write-decision-doc",
                "--decision-doc-name",
                "nuget-package-update-decisions-test.md",
            ],
            root,
        )
        assert_true(update.returncode == 0, update.stdout)
        payload = json.loads(update.stdout)
        assert_true(payload["updatedCount"] == 1, update.stdout)
        assert_true(payload["lockedCount"] == 2, update.stdout)
        decision_doc = root / "docs" / "pkgs-versions" / "nuget-package-update-decisions-test.md"
        assert_true(decision_doc.exists(), update.stdout)
        decision_text = decision_doc.read_text(encoding="utf-8")
        assert_true("# NuGet package version decisions" in decision_text, decision_text)
        assert_true("Do not use MCP" in decision_text, decision_text)

        updated = props.read_text(encoding="utf-8")
        assert_true('Include="Newtonsoft.Json" Version="13.0.4"' in updated, updated)
        assert_true('Include="Pinned.Package" Version="1.0.0" Locked="true"' in updated, updated)
        assert_true('Include="Comment.Locked" Version="2.0.0"' in updated, updated)
        assert_true('Include="Property.Package" Version="$(PropertyPackageVersion)"' in updated, updated)

        unsafe = run_command(
            [
                "check",
                "--file",
                str(props),
                "--versions-file",
                str(versions),
                "--disable-restore-validation",
                "--report-format",
                "json",
            ],
            root,
        )
        assert_true(unsafe.returncode == 0, unsafe.stdout)
        unsafe_payload = json.loads(unsafe.stdout)
        skipped = [p for p in unsafe_payload["packages"] if p["package_id"] == "Newtonsoft.Json"]
        assert_true(skipped and skipped[0]["action"] in {"skipped", "unchanged"}, unsafe.stdout)

    print("offline smoke tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
