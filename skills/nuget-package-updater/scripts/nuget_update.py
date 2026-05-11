#!/usr/bin/env python3
"""
Safely update NuGet package versions declared in Directory.Packages.props.

Local-first design for Copilot/ChatGPT-assisted repository work:
- reads PackageVersion entries from Directory.Packages.props
- detects locked/pinned packages directly from the props file
- finds stable listed versions from NuGet V3 autocomplete resources
- verifies candidate metadata through NuGet V3 registration resources
- cross-checks vulnerabilities through NuGet V3 VulnerabilityInfo resources when available
- rejects deprecated, unlisted, vulnerable, prerelease, and untrusted candidates
- applies conservative major/minor/patch policy
- optionally validates compatibility by running dotnet restore against a temp project
- updates only selected Version attributes
- prints deterministic JSON or Markdown reports
- optionally writes Markdown decision documents under docs/pkgs-versions
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import gzip
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

DEFAULT_SOURCE = "https://api.nuget.org/v3/index.json"
DEFAULT_TARGET_FRAMEWORK = "net10.0"

EXIT_OK = 0
EXIT_TECHNICAL_ERROR = 1
EXIT_POLICY_FAILURE = 2

PACKAGE_VERSION_TAG_RE = re.compile(
    r"<PackageVersion\b(?P<attrs>[^>]*)>",
    re.IGNORECASE | re.DOTALL,
)
ATTRIBUTE_RE = re.compile(
    r"\b(?P<name>[A-Za-z_][A-Za-z0-9_.:-]*)\s*=\s*([\"'])(?P<value>.*?)\2",
    re.IGNORECASE | re.DOTALL,
)
PACKAGE_ID_ATTR_RE = re.compile(
    r"\b(?:Include|Update)\s*=\s*([\"'])(.*?)\1",
    re.IGNORECASE | re.DOTALL,
)
VERSION_ATTR_RE = re.compile(
    r"\bVersion\s*=\s*([\"'])(.*?)\1",
    re.IGNORECASE | re.DOTALL,
)
XML_COMMENT_RE = re.compile(r"<!--(?P<comment>.*?)-->", re.DOTALL)

LOCK_ATTRIBUTE_NAMES = {
    "lock",
    "locked",
    "pin",
    "pinned",
    "noupdate",
    "no-update",
    "nugetupdaterlocked",
    "versionlocked",
    "manualupdate",
}
LOCK_ATTRIBUTE_VALUES = {"true", "1", "yes", "y", "locked", "pinned", "manual", "none", "no-update"}
LOCK_POLICY_VALUES = {"locked", "pinned", "manual", "none", "no-update", "ignore", "ignored"}
LOCK_COMMENT_MARKERS = {
    "nuget-updater: lock",
    "nuget-updater: ignore",
    "nuget-updater: pinned",
    "nuget-updater: no-update",
    "package-lock",
    "package lock",
    "version-lock",
    "version lock",
    "locked",
    "pinned",
    "travado",
    "fixado",
    "nao atualizar",
    "não atualizar",
    "no-update",
}

SEVERITY_ORDER = {
    "low": 0,
    "moderate": 1,
    "medium": 1,
    "high": 2,
    "critical": 3,
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
}
SEVERITY_LABELS = {
    0: "low",
    1: "moderate",
    2: "high",
    3: "critical",
}

_SERVICE_INDEX_CACHE: dict[tuple[str, int], dict[str, Any]] = {}
_REGISTRATION_CACHE: dict[tuple[str, str, int], dict[str, "PackageMetadata"]] = {}
_VULNERABILITY_INFO_CACHE: dict[tuple[str, int], dict[str, list["Vulnerability"]]] = {}


@dataclasses.dataclass(frozen=True, order=True)
class NuGetVersion:
    sort_key: tuple[int, int, int, int, tuple[int | str, ...]]
    original: str = dataclasses.field(compare=False)
    major: int = dataclasses.field(compare=False)
    minor: int = dataclasses.field(compare=False)
    patch: int = dataclasses.field(compare=False)
    revision: int = dataclasses.field(compare=False)
    prerelease: str | None = dataclasses.field(compare=False)

    @property
    def stable(self) -> bool:
        return self.prerelease is None


@dataclasses.dataclass
class PackageEntry:
    package_id: str
    current_version: str
    version_start: int
    version_end: int
    line: int
    locked: bool
    lock_reason: str | None


@dataclasses.dataclass
class Vulnerability:
    severity: str
    severity_rank: int
    advisory_url: str | None
    version_range: str | None = None
    source: str | None = None


@dataclasses.dataclass
class PackageMetadata:
    version: str
    listed: bool | None
    deprecated: bool
    vulnerabilities: list[Vulnerability]
    source: str
    trusted: bool
    deprecation_message: str | None = None


@dataclasses.dataclass
class Candidate:
    version: NuGetVersion
    metadata: PackageMetadata | None
    source: str | None


@dataclasses.dataclass
class CompatibilityResult:
    compatible: bool
    kind: str
    output: str


@dataclasses.dataclass
class PackageDecision:
    package_id: str
    current_version: str
    latest_stable_version: str | None
    selected_version: str | None
    target_framework: str
    compatible: bool | None
    action: str
    reason: str | None
    line: int
    locked: bool
    lock_reason: str | None
    candidate_count: int
    safe_candidate_count: int
    validated_candidates: int
    source: str | None
    current_version_deprecated: bool | None
    current_version_vulnerable: bool | None
    selected_version_deprecated: bool | None
    selected_version_vulnerable: bool | None
    selected_version_listed: bool | None
    vulnerabilities: list[dict[str, Any]]


def parse_nuget_version(value: str) -> NuGetVersion | None:
    raw = value.strip()
    if not raw or "$" in raw or "*" in raw or "," in raw:
        return None

    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1].strip()

    raw = raw.split("+", 1)[0]
    core, sep, prerelease = raw.partition("-")
    parts = core.split(".")
    if not 1 <= len(parts) <= 4:
        return None

    numbers: list[int] = []
    for part in parts:
        if not part.isdigit():
            return None
        numbers.append(int(part))

    while len(numbers) < 4:
        numbers.append(0)

    if sep:
        prerelease_key = tuple(_parse_prerelease_piece(p) for p in prerelease.split("."))
    else:
        prerelease = None
        prerelease_key = (sys.maxsize,)

    return NuGetVersion(
        sort_key=(numbers[0], numbers[1], numbers[2], numbers[3], prerelease_key),
        original=value.strip(),
        major=numbers[0],
        minor=numbers[1],
        patch=numbers[2],
        revision=numbers[3],
        prerelease=prerelease,
    )


def _parse_prerelease_piece(value: str) -> int | str:
    if value.isdigit():
        return int(value)
    return value.lower()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def find_directory_packages_file(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent

    while True:
        candidate = current / "Directory.Packages.props"
        if candidate.exists():
            return candidate
        if current.parent == current:
            return None
        current = current.parent


def parse_attributes(attrs: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in ATTRIBUTE_RE.finditer(attrs):
        result[match.group("name").lower()] = match.group("value").strip()
    return result


def comment_has_lock_marker(comment: str) -> bool:
    normalized = " ".join(comment.lower().split())
    return any(marker in normalized for marker in LOCK_COMMENT_MARKERS)


def lock_reason_from_attrs(attrs: dict[str, str]) -> str | None:
    for name, value in attrs.items():
        normalized_name = name.lower().replace("_", "").replace(".", "")
        normalized_value = value.lower().strip()
        if normalized_name in LOCK_ATTRIBUTE_NAMES and normalized_value in LOCK_ATTRIBUTE_VALUES:
            return f"locked by attribute {name}={value}"
        if normalized_name in {"updatepolicy", "versionpolicy", "nugetupdatepolicy"} and normalized_value in LOCK_POLICY_VALUES:
            return f"locked by policy {name}={value}"
    return None


def lock_reason_from_comments(content: str, tag_start: int) -> str | None:
    line_start = content.rfind("\n", 0, tag_start) + 1
    same_line = content[line_start:tag_start]
    for match in XML_COMMENT_RE.finditer(same_line):
        if comment_has_lock_marker(match.group("comment")):
            return "locked by same-line XML comment"

    prefix = content[:tag_start]
    previous_lines = prefix.splitlines()[-4:]
    for distance, line in enumerate(reversed(previous_lines), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            comment_text = stripped[4:-3]
            if comment_has_lock_marker(comment_text):
                return f"locked by preceding XML comment within {distance} line(s)"
            continue
        break
    return None


def parse_package_entries(content: str) -> list[PackageEntry]:
    entries: list[PackageEntry] = []

    for tag in PACKAGE_VERSION_TAG_RE.finditer(content):
        attrs_text = tag.group("attrs")
        attrs_offset = tag.start("attrs")

        id_match = PACKAGE_ID_ATTR_RE.search(attrs_text)
        version_match = VERSION_ATTR_RE.search(attrs_text)
        if not id_match or not version_match:
            continue

        package_id = id_match.group(2).strip()
        current_version = version_match.group(2).strip()
        version_start = attrs_offset + version_match.start(2)
        version_end = attrs_offset + version_match.end(2)
        line = content.count("\n", 0, tag.start()) + 1

        attrs = parse_attributes(attrs_text)
        lock_reason = lock_reason_from_attrs(attrs) or lock_reason_from_comments(content, tag.start())

        entries.append(
            PackageEntry(
                package_id=package_id,
                current_version=current_version,
                version_start=version_start,
                version_end=version_end,
                line=line,
                locked=lock_reason is not None,
                lock_reason=lock_reason,
            )
        )

    return entries


def normalize_source(source: str) -> str:
    source = source.strip()
    if source.endswith("/index.json"):
        return source
    if source.endswith("/"):
        return source + "index.json"
    return source + "/index.json"


def get_json(url: str, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nuget-package-updater-skill/2.0",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, identity",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
        encoding = response.headers.get("Content-Encoding", "").lower()
        if "gzip" in encoding:
            raw = gzip.decompress(raw)
        return json.loads(raw.decode("utf-8"))


def get_service_index(source: str, timeout: int) -> dict[str, Any]:
    service_index_url = normalize_source(source)
    cache_key = (service_index_url, timeout)
    cached = _SERVICE_INDEX_CACHE.get(cache_key)
    if cached is not None:
        return cached
    payload = get_json(service_index_url, timeout)
    _SERVICE_INDEX_CACHE[cache_key] = payload
    return payload


def get_resource_url(source: str, resource_prefix: str, timeout: int) -> str:
    service_index_url = normalize_source(source)
    service_index = get_service_index(source, timeout)
    resources = service_index.get("resources", [])

    # Prefer exact SemVer-aware registration resources when available.
    preferred_types = []
    if resource_prefix == "RegistrationsBaseUrl":
        preferred_types = ["RegistrationsBaseUrl/3.6.0", "RegistrationsBaseUrl/3.4.0", "RegistrationsBaseUrl"]
    elif resource_prefix == "SearchAutocompleteService":
        preferred_types = ["SearchAutocompleteService/3.5.0", "SearchAutocompleteService"]
    elif resource_prefix == "VulnerabilityInfo":
        preferred_types = ["VulnerabilityInfo/6.7.0", "VulnerabilityInfo"]

    for preferred_type in preferred_types:
        for resource in resources:
            resource_type = resource.get("@type", "")
            if resource_type == preferred_type:
                resource_id = resource.get("@id")
                if isinstance(resource_id, str):
                    return resource_id

    for resource in resources:
        resource_type = resource.get("@type", "")
        if isinstance(resource_type, str) and resource_type.startswith(resource_prefix):
            resource_id = resource.get("@id")
            if isinstance(resource_id, str):
                return resource_id

    raise RuntimeError(f"Resource {resource_prefix} not found in {service_index_url}")


def fetch_autocomplete_versions(package_id: str, source: str, timeout: int) -> list[str]:
    autocomplete_url = get_resource_url(source, "SearchAutocompleteService", timeout)
    query = urllib.parse.urlencode(
        {
            "id": package_id,
            "prerelease": "false",
            "semVerLevel": "2.0.0",
        }
    )
    payload = get_json(f"{autocomplete_url}?{query}", timeout)
    versions = payload.get("data", [])
    return [version for version in versions if isinstance(version, str)]


def fetch_registration_metadata(package_id: str, source: str, timeout: int) -> dict[str, PackageMetadata]:
    cache_key = (normalize_source(source), package_id.lower(), timeout)
    cached = _REGISTRATION_CACHE.get(cache_key)
    if cached is not None:
        return cached

    registration_url = get_resource_url(source, "RegistrationsBaseUrl", timeout)
    if not registration_url.endswith("/"):
        registration_url += "/"

    index_url = f"{registration_url}{urllib.parse.quote(package_id.lower())}/index.json"
    index_payload = get_json(index_url, timeout)
    result: dict[str, PackageMetadata] = {}

    for page in index_payload.get("items", []):
        page_items = page.get("items")
        if page_items is None:
            page_url = page.get("@id")
            if not isinstance(page_url, str):
                continue
            page_payload = get_json(page_url, timeout)
            page_items = page_payload.get("items", [])

        if not isinstance(page_items, list):
            continue

        for item in page_items:
            metadata = metadata_from_registration_item(item, source)
            if metadata is not None:
                result[metadata.version.lower()] = metadata

    _REGISTRATION_CACHE[cache_key] = result
    return result


def metadata_from_registration_item(item: Any, source: str) -> PackageMetadata | None:
    if not isinstance(item, dict):
        return None
    catalog_entry = item.get("catalogEntry")
    if isinstance(catalog_entry, str):
        return None
    if not isinstance(catalog_entry, dict):
        return None

    version = catalog_entry.get("version") or item.get("version")
    if not isinstance(version, str):
        return None

    listed = catalog_entry.get("listed")
    if listed is not None and not isinstance(listed, bool):
        listed = None

    deprecation = catalog_entry.get("deprecation")
    deprecated = deprecation is not None
    deprecation_message = None
    if isinstance(deprecation, dict):
        message = deprecation.get("message")
        if isinstance(message, str):
            deprecation_message = message
        reasons = deprecation.get("reasons")
        if isinstance(reasons, list) and reasons:
            deprecation_message = deprecation_message or ", ".join(str(r) for r in reasons)

    vulnerabilities = parse_vulnerabilities(catalog_entry)

    return PackageMetadata(
        version=version,
        listed=listed,
        deprecated=deprecated,
        vulnerabilities=vulnerabilities,
        source=source,
        trusted=True,
        deprecation_message=deprecation_message,
    )


def parse_vulnerabilities(catalog_entry: dict[str, Any]) -> list[Vulnerability]:
    raw = catalog_entry.get("vulnerabilities")
    if raw is None:
        raw = catalog_entry.get("vulnerability")
    if not isinstance(raw, list):
        return []

    result: list[Vulnerability] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        severity_value = str(item.get("severity", "0")).lower().strip()
        severity_rank = SEVERITY_ORDER.get(severity_value, 0)
        severity_label = SEVERITY_LABELS.get(severity_rank, severity_value or "low")
        advisory_url = item.get("advisoryUrl")
        if advisory_url is not None and not isinstance(advisory_url, str):
            advisory_url = None
        version_range = item.get("versions")
        if version_range is not None and not isinstance(version_range, str):
            version_range = None
        result.append(
            Vulnerability(
                severity=severity_label,
                severity_rank=severity_rank,
                advisory_url=advisory_url,
                version_range=version_range,
                source="registration",
            )
        )
    return result


def fetch_vulnerability_info_for_package(package_id: str, source: str, timeout: int) -> list[Vulnerability]:
    """Read NuGet VulnerabilityInfo pages and return advisories for one package.

    The Registration API is still consulted for exact package metadata, but
    VulnerabilityInfo is the bulk authoritative lookup optimized by NuGet for
    vulnerability checks across many packages. If the source does not expose
    VulnerabilityInfo, return an empty list and rely on registration metadata.
    """
    cache_key = (normalize_source(source), timeout)
    cached = _VULNERABILITY_INFO_CACHE.get(cache_key)
    if cached is None:
        cached = {}
        index_url = get_optional_resource_url(source, "VulnerabilityInfo", timeout)
        if index_url is not None:
            index_payload = get_json(index_url, timeout)
            if isinstance(index_payload, list):
                for page in index_payload:
                    if not isinstance(page, dict):
                        continue
                    page_url = page.get("@id")
                    if not isinstance(page_url, str):
                        continue
                    page_payload = get_json(page_url, timeout)
                    if page_payload == []:
                        continue
                    if not isinstance(page_payload, dict):
                        continue
                    for package_key, advisory_items in page_payload.items():
                        if not isinstance(package_key, str) or not isinstance(advisory_items, list):
                            continue
                        target_key = package_key.lower()
                        bucket = cached.setdefault(target_key, [])
                        for advisory in advisory_items:
                            vulnerability = vulnerability_from_info_item(advisory)
                            if vulnerability is not None:
                                bucket.append(vulnerability)
        _VULNERABILITY_INFO_CACHE[cache_key] = cached

    return list(cached.get(package_id.lower(), []))


def vulnerability_from_info_item(item: Any) -> Vulnerability | None:
    if not isinstance(item, dict):
        return None
    severity_value = str(item.get("severity", "0")).lower().strip()
    severity_rank = SEVERITY_ORDER.get(severity_value, 0)
    severity_label = SEVERITY_LABELS.get(severity_rank, severity_value or "low")
    advisory_url = item.get("url") or item.get("advisoryUrl")
    if advisory_url is not None and not isinstance(advisory_url, str):
        advisory_url = None
    version_range = item.get("versions")
    if not isinstance(version_range, str) or not version_range.strip():
        return None
    return Vulnerability(
        severity=severity_label,
        severity_rank=severity_rank,
        advisory_url=advisory_url,
        version_range=version_range.strip(),
        source="vulnerability-info",
    )


def vulnerabilities_for_version(version: NuGetVersion, advisories: list[Vulnerability]) -> list[Vulnerability]:
    return [item for item in advisories if item.version_range and nuget_range_contains(version, item.version_range)]


def merge_vulnerabilities(left: list[Vulnerability], right: list[Vulnerability]) -> list[Vulnerability]:
    merged: list[Vulnerability] = []
    seen: set[tuple[str, int, str | None, str | None]] = set()
    for item in [*left, *right]:
        key = (item.severity, item.severity_rank, item.advisory_url, item.version_range)
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
    return merged


def enrich_metadata_with_vulnerability_info(
    metadata: PackageMetadata,
    version: NuGetVersion,
    package_advisories: list[Vulnerability],
) -> PackageMetadata:
    matched = vulnerabilities_for_version(version, package_advisories)
    if not matched:
        return metadata
    metadata.vulnerabilities = merge_vulnerabilities(metadata.vulnerabilities, matched)
    return metadata


def nuget_range_contains(version: NuGetVersion, range_expression: str) -> bool:
    text = range_expression.strip()
    if not text:
        return False

    if text[0] in "[(" and text[-1:] in ")]":
        lower_inclusive = text[0] == "["
        upper_inclusive = text[-1] == "]"
        inner = text[1:-1].strip()
        if "," not in inner:
            exact = parse_nuget_version(inner)
            return exact is not None and version == exact

        lower_text, upper_text = (part.strip() for part in inner.split(",", 1))
        if lower_text:
            lower = parse_nuget_version(lower_text)
            if lower is None:
                return False
            if lower_inclusive:
                if version < lower:
                    return False
            else:
                if version <= lower:
                    return False
        if upper_text:
            upper = parse_nuget_version(upper_text)
            if upper is None:
                return False
            if upper_inclusive:
                if version > upper:
                    return False
            else:
                if version >= upper:
                    return False
        return True

    exact = parse_nuget_version(text)
    return exact is not None and version == exact


def load_versions_file(path: Path) -> dict[str, list[str]]:
    payload = json.loads(read_text(path))
    if not isinstance(payload, dict):
        raise RuntimeError("versions file must be a JSON object mapping package IDs to arrays")

    result: dict[str, list[str]] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or not isinstance(value, list):
            raise RuntimeError("versions file must map string package IDs to arrays")
        result[key.lower()] = [str(item) for item in value]
    return result


def fetch_candidates(
    package_id: str,
    sources: list[str],
    timeout: int,
    versions_by_package: dict[str, list[str]] | None,
    allow_untrusted_versions_file: bool,
) -> tuple[list[Candidate], str | None]:
    if versions_by_package is not None:
        versions = versions_by_package.get(package_id.lower(), [])
        candidates = []
        for value in versions:
            parsed = parse_nuget_version(value)
            if parsed is None:
                continue
            metadata = PackageMetadata(
                version=parsed.original,
                listed=None,
                deprecated=False,
                vulnerabilities=[],
                source="versions-file",
                trusted=allow_untrusted_versions_file,
            )
            candidates.append(Candidate(parsed, metadata, "versions-file"))
        candidates.sort(key=lambda c: c.version, reverse=True)
        return candidates, "versions-file"

    errors: list[str] = []
    candidate_by_version: dict[str, Candidate] = {}
    first_source: str | None = None

    for source in sources:
        try:
            versions = fetch_autocomplete_versions(package_id, source, timeout)
            metadata_by_version = fetch_registration_metadata(package_id, source, timeout)
            package_advisories = fetch_vulnerability_info_for_package(package_id, source, timeout)
            if versions and first_source is None:
                first_source = source

            for value in versions:
                parsed = parse_nuget_version(value)
                if parsed is None:
                    continue
                metadata = metadata_by_version.get(parsed.original.lower())
                if metadata is None:
                    metadata = PackageMetadata(
                        version=parsed.original,
                        listed=None,
                        deprecated=False,
                        vulnerabilities=[],
                        source=source,
                        trusted=False,
                    )
                metadata = enrich_metadata_with_vulnerability_info(metadata, parsed, package_advisories)
                key = parsed.original.lower()
                candidate_by_version[key] = Candidate(parsed, metadata, source)
        except Exception as exc:  # noqa: BLE001 - report source-specific failures.
            errors.append(f"{source}: {exc}")

    if not candidate_by_version and errors:
        raise RuntimeError("No versions could be read. " + " | ".join(errors))

    candidates = list(candidate_by_version.values())
    candidates.sort(key=lambda c: c.version, reverse=True)
    return candidates, first_source


def get_current_metadata(
    package_id: str,
    current_version: str,
    sources: list[str],
    timeout: int,
    versions_by_package: dict[str, list[str]] | None,
    allow_untrusted_versions_file: bool,
) -> PackageMetadata | None:
    parsed = parse_nuget_version(current_version)
    if parsed is None:
        return None

    if versions_by_package is not None:
        return PackageMetadata(
            version=current_version,
            listed=None,
            deprecated=False,
            vulnerabilities=[],
            source="versions-file",
            trusted=allow_untrusted_versions_file,
        )

    for source in sources:
        try:
            metadata_by_version = fetch_registration_metadata(package_id, source, timeout)
            found = metadata_by_version.get(parsed.original.lower())
            package_advisories = fetch_vulnerability_info_for_package(package_id, source, timeout)
            if found is not None:
                return enrich_metadata_with_vulnerability_info(found, parsed, package_advisories)
            matched = vulnerabilities_for_version(parsed, package_advisories)
            if matched:
                return PackageMetadata(
                    version=current_version,
                    listed=None,
                    deprecated=False,
                    vulnerabilities=matched,
                    source=source,
                    trusted=False,
                )
        except Exception:
            continue
    return None


def vulnerability_threshold_rank(value: str) -> int:
    normalized = value.lower().strip()
    if normalized not in SEVERITY_ORDER:
        raise RuntimeError(f"invalid vulnerability severity threshold: {value}")
    return SEVERITY_ORDER[normalized]


def is_allowed_by_version_policy(
    current: NuGetVersion,
    candidate: NuGetVersion,
    allow_major: bool,
    allow_minor: bool,
    allow_patch: bool,
    allow_downgrade: bool,
) -> bool:
    if not candidate.stable:
        return False

    if not allow_downgrade and candidate <= current:
        return False

    if not allow_major and candidate.major != current.major:
        return False

    if not allow_minor and candidate.minor != current.minor:
        return False

    if not allow_patch and candidate.patch != current.patch:
        return False

    return True


def safety_rejection_reason(candidate: Candidate, args: argparse.Namespace) -> str | None:
    if args.disable_safety_validation:
        return None

    metadata = candidate.metadata
    if metadata is None:
        return "missing trusted NuGet metadata"

    if args.require_trusted_metadata and not metadata.trusted:
        return "metadata is not trusted"

    if args.reject_unlisted and metadata.listed is False:
        return "candidate version is unlisted"

    if args.reject_deprecated and metadata.deprecated:
        detail = f": {metadata.deprecation_message}" if metadata.deprecation_message else ""
        return f"candidate version is deprecated{detail}"

    if args.reject_vulnerable:
        threshold = vulnerability_threshold_rank(args.vulnerability_severity_threshold)
        matching = [v for v in metadata.vulnerabilities if v.severity_rank >= threshold]
        if matching:
            severities = ", ".join(sorted({v.severity for v in matching}))
            return f"candidate version has known vulnerabilities at or above {args.vulnerability_severity_threshold}: {severities}"

    return None


def has_dotnet() -> bool:
    return shutil.which("dotnet") is not None


def validate_package_compatibility(
    package_id: str,
    version: str,
    target_framework: str,
    sources: list[str],
    timeout: int,
) -> CompatibilityResult:
    if not has_dotnet():
        return CompatibilityResult(
            compatible=False,
            kind="dotnet-not-found",
            output="dotnet CLI was not found in PATH",
        )

    escaped_package_id = html.escape(package_id, quote=True)
    escaped_version = html.escape(version, quote=True)
    escaped_target = html.escape(target_framework, quote=True)

    with tempfile.TemporaryDirectory(prefix="nuget-compat-") as tmp:
        project_path = Path(tmp) / "compat-check.csproj"
        project_path.write_text(
            f"""<Project Sdk=\"Microsoft.NET.Sdk\">
  <PropertyGroup>
    <TargetFramework>{escaped_target}</TargetFramework>
    <RestoreNoCache>true</RestoreNoCache>
    <NuGetAudit>false</NuGetAudit>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include=\"{escaped_package_id}\" Version=\"[{escaped_version}]\" />
  </ItemGroup>
</Project>
""",
            encoding="utf-8",
        )

        command = [
            "dotnet",
            "restore",
            str(project_path),
            "--nologo",
            "--verbosity",
            "minimal",
        ]
        for source in sources:
            command.extend(["--source", source])

        env = os.environ.copy()
        env.setdefault("DOTNET_CLI_TELEMETRY_OPTOUT", "1")
        env.setdefault("DOTNET_NOLOGO", "1")

        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            env=env,
            check=False,
        )

    output = completed.stdout.strip()
    if completed.returncode == 0:
        return CompatibilityResult(True, "compatible", output)

    lowered = output.lower()
    if "nu1202" in lowered:
        kind = "incompatible"
    elif "netsdk1045" in lowered or "targeting .net" in lowered:
        kind = "sdk-does-not-support-target-framework"
    else:
        kind = "restore-failed"

    return CompatibilityResult(False, kind, output)


def vulnerability_dicts(metadata: PackageMetadata | None) -> list[dict[str, Any]]:
    if metadata is None:
        return []
    return [dataclasses.asdict(v) for v in metadata.vulnerabilities]


def make_decision(
    entry: PackageEntry,
    current_metadata: PackageMetadata | None,
    latest_stable: str | None,
    selected_version: str | None,
    target_framework: str,
    compatible: bool | None,
    action: str,
    reason: str | None,
    candidate_count: int,
    safe_candidate_count: int,
    validated_candidates: int,
    source: str | None,
    selected_metadata: PackageMetadata | None = None,
) -> PackageDecision:
    return PackageDecision(
        package_id=entry.package_id,
        current_version=entry.current_version,
        latest_stable_version=latest_stable,
        selected_version=selected_version,
        target_framework=target_framework,
        compatible=compatible,
        action=action,
        reason=reason,
        line=entry.line,
        locked=entry.locked,
        lock_reason=entry.lock_reason,
        candidate_count=candidate_count,
        safe_candidate_count=safe_candidate_count,
        validated_candidates=validated_candidates,
        source=source,
        current_version_deprecated=None if current_metadata is None else current_metadata.deprecated,
        current_version_vulnerable=None if current_metadata is None else bool(current_metadata.vulnerabilities),
        selected_version_deprecated=None if selected_metadata is None else selected_metadata.deprecated,
        selected_version_vulnerable=None if selected_metadata is None else bool(selected_metadata.vulnerabilities),
        selected_version_listed=None if selected_metadata is None else selected_metadata.listed,
        vulnerabilities=vulnerability_dicts(selected_metadata),
    )


def decide_package_update(
    entry: PackageEntry,
    args: argparse.Namespace,
    versions_by_package: dict[str, list[str]] | None,
) -> PackageDecision:
    current = parse_nuget_version(entry.current_version)
    if current is None:
        return make_decision(
            entry=entry,
            current_metadata=None,
            latest_stable=None,
            selected_version=None,
            target_framework=args.target_framework,
            compatible=None,
            action="skipped",
            reason="current version is not a literal NuGet version",
            candidate_count=0,
            safe_candidate_count=0,
            validated_candidates=0,
            source=None,
        )

    current_metadata = get_current_metadata(
        entry.package_id,
        entry.current_version,
        args.source,
        args.http_timeout,
        versions_by_package,
        args.allow_untrusted_versions_file,
    )

    if entry.locked:
        return make_decision(
            entry=entry,
            current_metadata=current_metadata,
            latest_stable=None,
            selected_version=None,
            target_framework=args.target_framework,
            compatible=None,
            action="locked",
            reason=entry.lock_reason or "locked by directory.packages.props",
            candidate_count=0,
            safe_candidate_count=0,
            validated_candidates=0,
            source=None,
        )

    try:
        candidates, source = fetch_candidates(
            entry.package_id,
            args.source,
            args.http_timeout,
            versions_by_package,
            args.allow_untrusted_versions_file,
        )
    except Exception as exc:  # noqa: BLE001 - return per-package error.
        return make_decision(
            entry=entry,
            current_metadata=current_metadata,
            latest_stable=None,
            selected_version=None,
            target_framework=args.target_framework,
            compatible=None,
            action="error",
            reason=str(exc),
            candidate_count=0,
            safe_candidate_count=0,
            validated_candidates=0,
            source=None,
        )

    stable_candidates = [candidate for candidate in candidates if candidate.version.stable]
    latest_stable = stable_candidates[0].version.original if stable_candidates else None

    allowed_by_version_policy = [
        candidate
        for candidate in stable_candidates
        if is_allowed_by_version_policy(
            current=current,
            candidate=candidate.version,
            allow_major=args.allow_major,
            allow_minor=args.allow_minor,
            allow_patch=args.allow_patch,
            allow_downgrade=args.allow_downgrade,
        )
    ]

    safe_candidates: list[Candidate] = []
    first_safety_rejection: str | None = None
    for candidate in allowed_by_version_policy:
        rejection = safety_rejection_reason(candidate, args)
        if rejection is None:
            safe_candidates.append(candidate)
        elif first_safety_rejection is None:
            first_safety_rejection = rejection

    if args.max_candidates > 0:
        safe_candidates = safe_candidates[: args.max_candidates]

    if not allowed_by_version_policy:
        return make_decision(
            entry=entry,
            current_metadata=current_metadata,
            latest_stable=latest_stable,
            selected_version=None,
            target_framework=args.target_framework,
            compatible=None,
            action="unchanged",
            reason="no newer stable version allowed by major/minor/patch policy",
            candidate_count=len(stable_candidates),
            safe_candidate_count=0,
            validated_candidates=0,
            source=source,
        )

    if not safe_candidates:
        return make_decision(
            entry=entry,
            current_metadata=current_metadata,
            latest_stable=latest_stable,
            selected_version=None,
            target_framework=args.target_framework,
            compatible=False,
            action="skipped",
            reason=first_safety_rejection or "no safe candidate after metadata policy",
            candidate_count=len(stable_candidates),
            safe_candidate_count=0,
            validated_candidates=0,
            source=source,
        )

    validated = 0
    first_failure: CompatibilityResult | None = None

    for candidate in safe_candidates:
        if args.disable_restore_validation:
            selected = candidate.version.original
            action = "unchanged" if selected == entry.current_version else "update"
            return make_decision(
                entry=entry,
                current_metadata=current_metadata,
                latest_stable=latest_stable,
                selected_version=selected,
                target_framework=args.target_framework,
                compatible=None,
                action=action,
                reason=None if action == "update" else "already selected",
                candidate_count=len(stable_candidates),
                safe_candidate_count=len(safe_candidates),
                validated_candidates=validated,
                source=source,
                selected_metadata=candidate.metadata,
            )

        validated += 1
        compatibility = validate_package_compatibility(
            entry.package_id,
            candidate.version.original,
            args.target_framework,
            args.source,
            args.restore_timeout,
        )
        if compatibility.compatible:
            action = "unchanged" if candidate.version.original == entry.current_version else "update"
            return make_decision(
                entry=entry,
                current_metadata=current_metadata,
                latest_stable=latest_stable,
                selected_version=candidate.version.original,
                target_framework=args.target_framework,
                compatible=True,
                action=action,
                reason=None if action == "update" else "already selected",
                candidate_count=len(stable_candidates),
                safe_candidate_count=len(safe_candidates),
                validated_candidates=validated,
                source=source,
                selected_metadata=candidate.metadata,
            )

        if first_failure is None:
            first_failure = compatibility
        if compatibility.kind in {"dotnet-not-found", "sdk-does-not-support-target-framework"}:
            break

    reason = "no safe allowed candidate is compatible"
    if first_failure is not None:
        reason = f"{reason}; first failure: {first_failure.kind}"

    return make_decision(
        entry=entry,
        current_metadata=current_metadata,
        latest_stable=latest_stable,
        selected_version=None,
        target_framework=args.target_framework,
        compatible=False,
        action="skipped",
        reason=reason,
        candidate_count=len(stable_candidates),
        safe_candidate_count=len(safe_candidates),
        validated_candidates=validated,
        source=source,
    )


def apply_updates(content: str, entries: list[PackageEntry], decisions: list[PackageDecision]) -> str:
    decision_by_id = {
        decision.package_id.lower(): decision
        for decision in decisions
        if decision.action == "update" and decision.selected_version and not decision.locked
    }

    replacements: list[tuple[int, int, str]] = []
    for entry in entries:
        decision = decision_by_id.get(entry.package_id.lower())
        if decision and decision.selected_version and not entry.locked:
            replacements.append((entry.version_start, entry.version_end, decision.selected_version))

    updated = content
    for start, end, value in sorted(replacements, reverse=True):
        updated = updated[:start] + value + updated[end:]
    return updated


def decisions_to_dicts(decisions: Iterable[PackageDecision]) -> list[dict[str, Any]]:
    return [dataclasses.asdict(decision) for decision in decisions]


def build_report(
    file_path: Path,
    args: argparse.Namespace,
    entries: list[PackageEntry],
    decisions: list[PackageDecision],
    wrote_file: bool,
) -> dict[str, Any]:
    return {
        "file": str(file_path),
        "targetFramework": args.target_framework,
        "write": wrote_file,
        "restoreValidation": not args.disable_restore_validation,
        "safetyValidation": not args.disable_safety_validation,
        "policy": {
            "allowMajor": args.allow_major,
            "allowMinor": args.allow_minor,
            "allowPatch": args.allow_patch,
            "allowDowngrade": args.allow_downgrade,
            "rejectDeprecated": args.reject_deprecated,
            "rejectVulnerable": args.reject_vulnerable,
            "rejectUnlisted": args.reject_unlisted,
            "requireTrustedMetadata": args.require_trusted_metadata,
            "vulnerabilitySeverityThreshold": args.vulnerability_severity_threshold,
        },
        "packageCount": len(entries),
        "updatedCount": sum(1 for d in decisions if d.action == "update"),
        "unchangedCount": sum(1 for d in decisions if d.action == "unchanged"),
        "lockedCount": sum(1 for d in decisions if d.action == "locked"),
        "skippedCount": sum(1 for d in decisions if d.action == "skipped"),
        "errorCount": sum(1 for d in decisions if d.action == "error"),
        "packages": decisions_to_dicts(decisions),
    }


def format_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NuGet package update report",
        "",
        f"- File: `{report['file']}`",
        f"- Target framework: `{report['targetFramework']}`",
        f"- Restore validation: `{report['restoreValidation']}`",
        f"- Safety validation: `{report['safetyValidation']}`",
        f"- Wrote file: `{report['write']}`",
        f"- Decision document: `{report.get('decisionDocument', '')}`",
        f"- Updated: `{report['updatedCount']}`",
        f"- Unchanged: `{report['unchangedCount']}`",
        f"- Locked: `{report['lockedCount']}`",
        f"- Skipped: `{report['skippedCount']}`",
        f"- Errors: `{report['errorCount']}`",
        "",
        "| Package | Current | Selected | Latest stable | Action | Safe candidates | Locked | Reason |",
        "|---|---:|---:|---:|---|---:|---|---|",
    ]

    for package in report["packages"]:
        reason = package.get("reason") or ""
        locked = package.get("lock_reason") or ""
        lines.append(
            "| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} |".format(
                _md_cell(package.get("package_id")),
                _md_cell(package.get("current_version")),
                _md_cell(package.get("selected_version")),
                _md_cell(package.get("latest_stable_version")),
                _md_cell(package.get("action")),
                _md_cell(package.get("safe_candidate_count")),
                _md_cell(locked),
                _md_cell(reason),
            )
        )

    return "\n".join(lines) + "\n"


def _md_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def select_entries(entries: list[PackageEntry], args: argparse.Namespace) -> list[PackageEntry]:
    include = {p.lower() for p in args.package} if args.package else None
    ignore = {p.lower() for p in args.ignore_package}

    selected = []
    for entry in entries:
        package_key = entry.package_id.lower()
        if include is not None and package_key not in include:
            continue
        if package_key in ignore:
            continue
        selected.append(entry)
    return selected


def resolve_file_path(args: argparse.Namespace) -> Path:
    if args.file:
        return Path(args.file).resolve()

    discovered = find_directory_packages_file(Path.cwd())
    if discovered is None:
        raise RuntimeError("Directory.Packages.props was not found from the current directory upward")
    return discovered


def run(args: argparse.Namespace) -> int:
    file_path = resolve_file_path(args)
    if not file_path.exists():
        raise RuntimeError(f"file not found: {file_path}")

    content = read_text(file_path)
    entries = parse_package_entries(content)
    selected_entries = select_entries(entries, args)

    versions_by_package = load_versions_file(Path(args.versions_file)) if args.versions_file else None

    if args.command == "scan":
        decisions = [
            make_decision(
                entry=e,
                current_metadata=None,
                latest_stable=None,
                selected_version=None,
                target_framework=args.target_framework,
                compatible=None,
                action="locked" if e.locked else "found",
                reason=e.lock_reason if e.locked else None,
                candidate_count=0,
                safe_candidate_count=0,
                validated_candidates=0,
                source=None,
            )
            for e in selected_entries
        ]
        report = build_report(file_path, args, selected_entries, decisions, wrote_file=False)
        emit_report(report, args)
        return EXIT_OK

    decisions = [decide_package_update(entry, args, versions_by_package) for entry in selected_entries]

    wrote_file = False
    if args.command == "update" and args.write:
        updated_content = apply_updates(content, selected_entries, decisions)
        if updated_content != content:
            write_text(file_path, updated_content)
            wrote_file = True

    report = build_report(file_path, args, selected_entries, decisions, wrote_file=wrote_file)
    if args.write_decision_doc:
        decision_doc_path = write_decision_document(file_path, args, report)
        report["decisionDocument"] = str(decision_doc_path)
    emit_report(report, args)

    if report["errorCount"] > 0:
        return EXIT_TECHNICAL_ERROR
    if args.fail_on_incompatible and any(d.compatible is False for d in decisions):
        return EXIT_POLICY_FAILURE
    if args.fail_on_outdated and any(d.action == "update" for d in decisions):
        return EXIT_POLICY_FAILURE
    return EXIT_OK


def write_decision_document(file_path: Path, args: argparse.Namespace, report: dict[str, Any]) -> Path:
    output_dir = Path(args.decision_doc_dir)
    if not output_dir.is_absolute():
        output_dir = file_path.parent / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.decision_doc_name:
        file_name = args.decision_doc_name
    else:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%SZ")
        file_name = f"nuget-package-update-decisions-{stamp}.md"

    target = output_dir / file_name
    target.write_text(format_decision_document(report), encoding="utf-8")
    return target


def format_decision_document(report: dict[str, Any]) -> str:
    generated_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# NuGet package version decisions",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Source file: `{report['file']}`",
        f"- Target framework: `{report['targetFramework']}`",
        f"- Wrote package file: `{report['write']}`",
        f"- Restore validation: `{report['restoreValidation']}`",
        f"- Safety validation: `{report['safetyValidation']}`",
        "",
        "## Decision policy",
        "",
        "- Use only stable NuGet versions.",
        "- Reject prerelease, unlisted, deprecated, and vulnerable candidate versions.",
        "- Validate candidate package metadata through NuGet Registration API.",
        "- Cross-check vulnerability ranges through NuGet VulnerabilityInfo API when the source exposes it.",
        "- Respect locks and pins declared in `Directory.Packages.props`.",
        "- Do not use MCP or manual version selection for this package update workflow.",
        "",
        "## Summary",
        "",
        f"- Package declarations analyzed: `{report['packageCount']}`",
        f"- Updated: `{report['updatedCount']}`",
        f"- Unchanged: `{report['unchangedCount']}`",
        f"- Locked: `{report['lockedCount']}`",
        f"- Skipped: `{report['skippedCount']}`",
        f"- Errors: `{report['errorCount']}`",
        "",
        "## Package decisions",
        "",
        "| Package | Current | Current safety | Latest stable | Selected | Decision | Compatibility | Reason |",
        "|---|---:|---|---:|---:|---|---|---|",
    ]

    for package in report["packages"]:
        current_safety = []
        if package.get("current_version_deprecated"):
            current_safety.append("deprecated")
        if package.get("current_version_vulnerable"):
            current_safety.append("vulnerable")
        if not current_safety:
            current_safety.append("no known issue" if package.get("current_version_deprecated") is not None else "unknown")
        compatibility = package.get("compatible")
        compatibility_text = "not checked" if compatibility is None else str(compatibility).lower()
        reason = package.get("reason") or package.get("lock_reason") or ""
        lines.append(
            "| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} |".format(
                _md_cell(package.get("package_id")),
                _md_cell(package.get("current_version")),
                _md_cell(", ".join(current_safety)),
                _md_cell(package.get("latest_stable_version")),
                _md_cell(package.get("selected_version")),
                _md_cell(package.get("action")),
                _md_cell(compatibility_text),
                _md_cell(reason),
            )
        )

    lines.extend(["", "## Details", ""])
    for package in report["packages"]:
        lines.extend(
            [
                f"### `{_md_cell(package.get('package_id'))}`",
                "",
                f"- Line: `{package.get('line')}`",
                f"- Current version: `{_md_cell(package.get('current_version'))}`",
                f"- Latest stable version considered: `{_md_cell(package.get('latest_stable_version'))}`",
                f"- Selected version: `{_md_cell(package.get('selected_version'))}`",
                f"- Action: `{_md_cell(package.get('action'))}`",
                f"- Reason: `{_md_cell(package.get('reason') or package.get('lock_reason') or '')}`",
                f"- Candidate count: `{package.get('candidate_count')}`",
                f"- Safe candidate count: `{package.get('safe_candidate_count')}`",
                f"- Validated candidate count: `{package.get('validated_candidates')}`",
                f"- Source: `{_md_cell(package.get('source'))}`",
                "",
            ]
        )
        vulnerabilities = package.get("vulnerabilities") or []
        if vulnerabilities:
            lines.append("Known vulnerabilities on selected candidate:")
            for vuln in vulnerabilities:
                advisory = vuln.get("advisory_url") or vuln.get("url") or ""
                version_range = vuln.get("version_range") or ""
                lines.append(
                    f"- severity `{_md_cell(vuln.get('severity'))}`, range `{_md_cell(version_range)}`, advisory `{_md_cell(advisory)}`"
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def emit_report(report: dict[str, Any], args: argparse.Namespace) -> None:
    if args.report_format == "markdown":
        rendered = format_markdown(report)
    else:
        rendered = json.dumps(report, indent=2, ensure_ascii=False)

    print(rendered)

    if args.report:
        Path(args.report).write_text(rendered, encoding="utf-8")


def add_shared_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file", help="Path to Directory.Packages.props. Defaults to auto-discovery.")
    parser.add_argument("--target-framework", default=DEFAULT_TARGET_FRAMEWORK)
    parser.add_argument("--source", action="append", default=[], help="NuGet source/service index. Can be repeated.")
    parser.add_argument("--package", action="append", default=[], help="Only process this package ID. Can be repeated.")
    parser.add_argument("--ignore-package", action="append", default=[], help="Skip this package ID. Can be repeated.")
    parser.add_argument("--versions-file", help="Offline JSON map of package IDs to versions. Useful for smoke tests only.")
    parser.add_argument("--allow-untrusted-versions-file", action="store_true", help="Allow versions-file candidates to pass metadata trust checks. Use only in tests.")
    parser.add_argument("--allow-major", action="store_true", help="Allow major version upgrades.")
    parser.add_argument("--no-minor", dest="allow_minor", action="store_false", help="Disallow minor version upgrades.")
    parser.add_argument("--no-patch", dest="allow_patch", action="store_false", help="Disallow patch version upgrades.")
    parser.add_argument("--allow-downgrade", action="store_true", help="Allow selecting lower versions.")
    parser.add_argument("--disable-restore-validation", action="store_true", help="Do not run dotnet restore compatibility checks. Use only for offline dry-runs/tests.")
    parser.add_argument("--disable-safety-validation", action="store_true", help="Disable deprecation, vulnerability, unlisted, and trusted metadata checks. Use only for tests.")
    parser.add_argument("--allow-deprecated", dest="reject_deprecated", action="store_false", help="Allow deprecated package versions. Not recommended.")
    parser.add_argument("--allow-vulnerable", dest="reject_vulnerable", action="store_false", help="Allow vulnerable package versions. Not recommended.")
    parser.add_argument("--allow-unlisted", dest="reject_unlisted", action="store_false", help="Allow unlisted package versions. Not recommended.")
    parser.add_argument("--allow-untrusted-metadata", dest="require_trusted_metadata", action="store_false", help="Allow candidates whose registration metadata could not be confirmed. Not recommended.")
    parser.add_argument("--vulnerability-severity-threshold", default="low", choices=["low", "moderate", "high", "critical"], help="Reject vulnerabilities at or above this severity. Default: low.")
    parser.add_argument("--http-timeout", type=int, default=30)
    parser.add_argument("--restore-timeout", type=int, default=120)
    parser.add_argument("--max-candidates", type=int, default=30, help="Maximum safe candidate versions to validate per package. 0 means all.")
    parser.add_argument("--report-format", choices=["json", "markdown"], default="json")
    parser.add_argument("--report", help="Optional path to write the generated report.")
    parser.add_argument("--write-decision-doc", action="store_true", help="Write a human decision record under docs/pkgs-versions by default.")
    parser.add_argument("--decision-doc-dir", default="docs/pkgs-versions", help="Directory for decision Markdown documents. Relative paths are resolved from the Directory.Packages.props folder.")
    parser.add_argument("--decision-doc-name", help="Optional decision Markdown file name. Defaults to a UTC timestamped file.")
    parser.add_argument("--fail-on-incompatible", action="store_true")
    parser.add_argument("--fail-on-outdated", action="store_true")
    parser.set_defaults(
        allow_minor=True,
        allow_patch=True,
        reject_deprecated=True,
        reject_vulnerable=True,
        reject_unlisted=True,
        require_trusted_metadata=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safely update Directory.Packages.props using stable compatible NuGet versions.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ["scan", "check", "update"]:
        sub = subparsers.add_parser(command)
        add_shared_arguments(sub)
        if command == "update":
            sub.add_argument("--write", action="store_true", help="Actually write updates to Directory.Packages.props.")
        else:
            sub.set_defaults(write=False)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.source:
        args.source = [DEFAULT_SOURCE]

    try:
        return run(args)
    except subprocess.TimeoutExpired as exc:
        print(json.dumps({"error": f"command timed out: {exc}"}, indent=2), file=sys.stderr)
        return EXIT_TECHNICAL_ERROR
    except Exception as exc:  # noqa: BLE001 - CLI top-level reporting.
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return EXIT_TECHNICAL_ERROR


if __name__ == "__main__":
    sys.exit(main())
