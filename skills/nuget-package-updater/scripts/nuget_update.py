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
import hashlib
import html
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable

DEFAULT_SOURCE = "https://api.nuget.org/v3/index.json"
DEFAULT_TARGET_FRAMEWORK = "net10.0"
TOOL_CONTRACT_VERSION = 4
EVIDENCE_SCHEMA_VERSION = 1
RECEIPT_SCHEMA_VERSION = 1

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
_FETCH_EVIDENCE: dict[str, dict[str, Any]] = {}
_METADATA_REPLAY: dict[str, str] | None = None
_METADATA_REPLAY_SOURCE: str | None = None
_OFFLINE_VERSIONS_EVIDENCE: dict[str, Any] | None = None


class UpdaterError(RuntimeError):
    def __init__(self, code: str, message: str, *, stage: str = "runtime", evidence: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.stage = stage
        self.evidence = evidence or {}


@dataclasses.dataclass(frozen=True, order=True)
class NuGetVersion:
    sort_key: tuple[int, int, int, int, int, tuple[tuple[int, int | str], ...]]
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
    condition: str | None = None


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
    source_candidates: tuple[str, ...] = ()


@dataclasses.dataclass(frozen=True)
class NuGetConfigModel:
    path: Path
    sha256: str
    package_sources: tuple[tuple[str, str], ...]
    mappings: tuple[tuple[str, tuple[str, ...]], ...]
    mapping_identity: str


@dataclasses.dataclass
class CompatibilityResult:
    compatible: bool
    kind: str
    output: str
    command: list[str] = dataclasses.field(default_factory=list)
    exit_code: int | None = None
    output_sha256: str | None = None


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
    reason_code: str | None = None
    candidate_provenance: dict[str, Any] | None = None
    compatibility_evidence: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    current_metadata_sha256: str | None = None
    selected_vulnerability_metadata_sha256: str | None = None
    candidate_rejections: list[dict[str, Any]] = dataclasses.field(default_factory=list)


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
        stable_rank = 0
        prerelease_key = tuple(_parse_prerelease_piece(p) for p in prerelease.split("."))
    else:
        prerelease = None
        stable_rank = 1
        prerelease_key = ()

    return NuGetVersion(
        sort_key=(numbers[0], numbers[1], numbers[2], numbers[3], stable_rank, prerelease_key),
        original=value.strip(),
        major=numbers[0],
        minor=numbers[1],
        patch=numbers[2],
        revision=numbers[3],
        prerelease=prerelease,
    )


def _parse_prerelease_piece(value: str) -> tuple[int, int | str]:
    if value.isdigit():
        return (0, int(value))
    return (1, value.lower())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: Any) -> str:
    return sha256_text(canonical_json(value))


def _fsync_directory(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        _fsync_directory(path.parent)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def atomic_write_text(path: Path, content: str) -> None:
    atomic_write_bytes(path, content.encode("utf-8"))


def write_text(path: Path, content: str) -> None:
    atomic_write_text(path, content)


def reset_runtime_state() -> None:
    global _METADATA_REPLAY, _METADATA_REPLAY_SOURCE, _OFFLINE_VERSIONS_EVIDENCE
    _SERVICE_INDEX_CACHE.clear()
    _REGISTRATION_CACHE.clear()
    _VULNERABILITY_INFO_CACHE.clear()
    _FETCH_EVIDENCE.clear()
    _METADATA_REPLAY = None
    _METADATA_REPLAY_SOURCE = None
    _OFFLINE_VERSIONS_EVIDENCE = None


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
        condition = attrs.get("condition")

        entries.append(
            PackageEntry(
                package_id=package_id,
                current_version=current_version,
                version_start=version_start,
                version_end=version_end,
                line=line,
                locked=lock_reason is not None,
                lock_reason=lock_reason,
                condition=condition,
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


def normalized_sources(sources: Iterable[str]) -> list[str]:
    return [normalize_source(source) for source in sources]


def _xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def load_nuget_config(path: Path) -> NuGetConfigModel:
    resolved = path.resolve()
    if not resolved.is_file():
        raise UpdaterError("nuget-config-not-found", f"NuGet.Config not found: {resolved}", stage="input")
    try:
        root = ET.fromstring(resolved.read_bytes())
    except ET.ParseError as exc:
        raise UpdaterError("nuget-config-invalid", f"invalid NuGet.Config XML: {exc}", stage="input") from exc

    sources: list[tuple[str, str]] = []
    mappings: list[tuple[str, tuple[str, ...]]] = []
    for child in root.iter():
        name = _xml_local_name(child.tag)
        if name == "packagesources":
            current: list[tuple[str, str]] = []
            for item in child:
                item_name = _xml_local_name(item.tag)
                if item_name == "clear":
                    current.clear()
                elif item_name == "add":
                    key = (item.attrib.get("key") or "").strip()
                    value = (item.attrib.get("value") or "").strip()
                    if key and value:
                        current.append((key, value))
            sources = current
        elif name == "packagesourcemapping":
            current_mappings: list[tuple[str, tuple[str, ...]]] = []
            for source_node in child:
                if _xml_local_name(source_node.tag) != "packagesource":
                    continue
                key = (source_node.attrib.get("key") or "").strip()
                patterns = tuple(
                    (node.attrib.get("pattern") or "").strip()
                    for node in source_node
                    if _xml_local_name(node.tag) == "package" and (node.attrib.get("pattern") or "").strip()
                )
                if key and patterns:
                    current_mappings.append((key, patterns))
            mappings = current_mappings

    normalized = tuple((key, normalize_source(value)) for key, value in sources)
    mapping_material = [{"sourceKey": key, "patterns": list(patterns)} for key, patterns in mappings]
    return NuGetConfigModel(
        path=resolved,
        sha256=sha256_file(resolved),
        package_sources=normalized,
        mappings=tuple(mappings),
        mapping_identity=canonical_sha256(mapping_material),
    )


def configure_nuget_inputs(args: argparse.Namespace) -> None:
    model = load_nuget_config(Path(args.nuget_config)) if getattr(args, "nuget_config", None) else None
    explicit_sources = list(args.source)
    if not explicit_sources:
        if model and model.package_sources:
            args.source = [value for _, value in model.package_sources]
        else:
            args.source = [DEFAULT_SOURCE]
    else:
        args.source = explicit_sources
    args._nuget_config_model = model
    args._nuget_sources_explicit = bool(explicit_sources)


def _mapping_match_rank(package_id: str, pattern: str) -> tuple[int, int] | None:
    package_key = package_id.lower()
    pattern_key = pattern.lower()
    if pattern_key == package_key:
        return (2, len(pattern_key))
    if pattern_key == "*":
        return (0, 0)
    if pattern_key.endswith("*") and "*" not in pattern_key[:-1]:
        prefix = pattern_key[:-1]
        if package_key.startswith(prefix):
            return (1, len(prefix))
        return None
    if "*" in pattern_key:
        raise UpdaterError(
            "source-mapping-pattern-unsupported",
            f"unsupported Package Source Mapping pattern: {pattern}",
            stage="input",
        )
    return None


def sources_for_package(package_id: str, args: argparse.Namespace) -> list[str]:
    model: NuGetConfigModel | None = getattr(args, "_nuget_config_model", None)
    if model is None or not model.mappings:
        selected = list(args.source)
        for source in selected:
            if urllib.parse.urlparse(source).scheme.lower() not in {"http", "https"}:
                raise UpdaterError(
                    "unsupported-nuget-source",
                    f"metadata discovery supports HTTP(S) NuGet V3 sources only: {source}",
                    stage="input",
                    evidence={"packageId": package_id},
                )
        return selected
    by_key = {key: value for key, value in model.package_sources}
    ranked: list[tuple[tuple[int, int], str]] = []
    for key, patterns in model.mappings:
        best: tuple[int, int] | None = None
        for pattern in patterns:
            rank = _mapping_match_rank(package_id, pattern)
            if rank is not None and (best is None or rank > best):
                best = rank
        if best is not None:
            ranked.append((best, key))
    if not ranked:
        raise UpdaterError(
            "source-mapping-no-match",
            f"Package Source Mapping has no eligible source for {package_id}",
            stage="policy",
            evidence={"packageId": package_id, "mappingIdentity": model.mapping_identity},
        )
    best_rank = max(rank for rank, _ in ranked)
    selected_keys = [key for rank, key in ranked if rank == best_rank]
    mapped = [by_key[key] for key in selected_keys if key in by_key]
    if getattr(args, "_nuget_sources_explicit", False):
        allowed = set(normalized_sources(args.source))
        mapped = [source for source in mapped if normalize_source(source) in allowed]
    if not mapped:
        raise UpdaterError(
            "source-mapping-no-match",
            f"Package Source Mapping resolved no configured HTTP source for {package_id}",
            stage="policy",
            evidence={"packageId": package_id, "sourceKeys": selected_keys},
        )
    for source in mapped:
        if urllib.parse.urlparse(source).scheme.lower() not in {"http", "https"}:
            raise UpdaterError(
                "unsupported-nuget-source",
                f"metadata discovery supports HTTP(S) NuGet V3 sources only: {source}",
                stage="input",
                evidence={"packageId": package_id},
            )
    return mapped


def configure_metadata_replay(path: Path | None) -> None:
    global _METADATA_REPLAY, _METADATA_REPLAY_SOURCE
    if path is None:
        _METADATA_REPLAY = None
        _METADATA_REPLAY_SOURCE = None
        return

    payload = json.loads(read_text(path))
    if payload.get("schemaVersion") != EVIDENCE_SCHEMA_VERSION:
        raise UpdaterError(
            "metadata-snapshot-version-unsupported",
            f"unsupported metadata snapshot schema: {payload.get('schemaVersion')}",
            stage="input",
        )

    replay: dict[str, str] = {}
    for record in payload.get("records", []):
        url = record.get("url")
        body = record.get("body")
        expected_hash = record.get("rawSha256")
        if not isinstance(url, str) or not isinstance(body, str) or not isinstance(expected_hash, str):
            raise UpdaterError("metadata-snapshot-invalid", "metadata snapshot record is incomplete", stage="input")
        observed_hash = sha256_text(body)
        if observed_hash != expected_hash:
            raise UpdaterError(
                "metadata-snapshot-hash-mismatch",
                f"metadata snapshot body hash mismatch for {url}",
                stage="input",
                evidence={"url": url, "expected": expected_hash, "observed": observed_hash},
            )
        replay[url] = body

    _METADATA_REPLAY = replay
    _METADATA_REPLAY_SOURCE = str(path.resolve())


def get_json(url: str, timeout: int) -> dict[str, Any]:
    if _METADATA_REPLAY is not None:
        if url not in _METADATA_REPLAY:
            raise UpdaterError(
                "metadata-snapshot-miss",
                f"metadata snapshot does not contain {url}",
                stage="metadata",
                evidence={"snapshot": _METADATA_REPLAY_SOURCE, "url": url},
            )
        body = _METADATA_REPLAY[url]
        transport = "replay"
    else:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "nuget-package-updater-skill/3.0",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, identity",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
                encoding = response.headers.get("Content-Encoding", "").lower()
                if "gzip" in encoding:
                    raw = gzip.decompress(raw)
        except urllib.error.HTTPError as exc:
            if exc.code in {401, 403}:
                raise UpdaterError(
                    "authenticated-source-credentials-required",
                    f"NuGet source requires authentication ({exc.code}); use the host NuGet credential-provider flow and do not pass secrets to this tool",
                    stage="metadata",
                    evidence={"url": url, "statusCode": exc.code},
                ) from exc
            raise
        body = raw.decode("utf-8")
        transport = "live"

    raw_hash = sha256_text(body)
    payload = json.loads(body)
    canonical_hash = canonical_sha256(payload)
    previous = _FETCH_EVIDENCE.get(url)
    if previous is not None and previous.get("rawSha256") != raw_hash:
        raise UpdaterError(
            "metadata-changed-during-run",
            f"metadata response changed during the same run: {url}",
            stage="metadata",
            evidence={"url": url, "before": previous.get("rawSha256"), "after": raw_hash},
        )
    _FETCH_EVIDENCE[url] = {
        "url": url,
        "transport": transport,
        "capturedAt": utc_now_iso(),
        "rawSha256": raw_hash,
        "canonicalSha256": canonical_hash,
        "body": body,
    }
    return payload


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
    global _OFFLINE_VERSIONS_EVIDENCE
    raw = path.read_bytes()
    payload = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(payload, dict):
        raise RuntimeError("versions file must be a JSON object mapping package IDs to arrays")

    _OFFLINE_VERSIONS_EVIDENCE = {
        "path": str(path.resolve()),
        "sha256": sha256_bytes(raw),
        "capturedAt": utc_now_iso(),
    }

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
            candidates.append(Candidate(parsed, metadata, "versions-file", ("versions-file",)))
        candidates.sort(key=lambda c: c.version, reverse=True)
        return candidates, "versions-file"

    errors: list[str] = []
    observations: dict[str, list[tuple[NuGetVersion, PackageMetadata, str]]] = {}
    first_source: str | None = None

    for source in sources:
        normalized_source = normalize_source(source)
        try:
            versions = fetch_autocomplete_versions(package_id, normalized_source, timeout)
            metadata_by_version = fetch_registration_metadata(package_id, normalized_source, timeout)
            package_advisories = fetch_vulnerability_info_for_package(package_id, normalized_source, timeout)
            if versions and first_source is None:
                first_source = normalized_source

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
                        source=normalized_source,
                        trusted=False,
                    )
                metadata = enrich_metadata_with_vulnerability_info(metadata, parsed, package_advisories)
                observations.setdefault(parsed.original.lower(), []).append((parsed, metadata, normalized_source))
        except UpdaterError:
            raise
        except Exception as exc:  # noqa: BLE001 - report source-specific failures.
            errors.append(f"{normalized_source}: {exc}")

    if not observations and errors:
        raise RuntimeError("No versions could be read. " + " | ".join(errors))

    candidates: list[Candidate] = []
    source_order = {normalize_source(value): index for index, value in enumerate(sources)}
    for items in observations.values():
        ordered = sorted(items, key=lambda item: (source_order.get(item[2], len(source_order)), item[2].lower()))
        parsed, metadata, representative_source = ordered[0]
        source_candidates = tuple(item[2] for item in ordered)
        candidates.append(Candidate(parsed, metadata, representative_source, source_candidates))
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


@dataclasses.dataclass(frozen=True)
class Rejection:
    code: str
    message: str


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


def safety_rejection_reason(candidate: Candidate, args: argparse.Namespace) -> Rejection | None:
    if len(candidate.source_candidates) > 1 and not getattr(args, "allow_source_ambiguity", False):
        return Rejection(
            "candidate-source-ambiguous",
            "the same package version is available from multiple eligible sources; configure Package Source Mapping or explicitly accept ambiguity",
        )
    if args.disable_safety_validation:
        return None

    metadata = candidate.metadata
    if metadata is None:
        return Rejection("candidate-metadata-missing", "missing trusted NuGet metadata")

    if args.require_trusted_metadata and not metadata.trusted:
        return Rejection("candidate-metadata-untrusted", "metadata is not trusted")

    if args.reject_unlisted and metadata.listed is False:
        return Rejection("candidate-unlisted", "candidate version is unlisted")

    if args.reject_deprecated and metadata.deprecated:
        detail = f": {metadata.deprecation_message}" if metadata.deprecation_message else ""
        return Rejection("candidate-deprecated", f"candidate version is deprecated{detail}")

    if args.reject_vulnerable:
        threshold = vulnerability_threshold_rank(args.vulnerability_severity_threshold)
        matching = [v for v in metadata.vulnerabilities if v.severity_rank >= threshold]
        if matching:
            severities = ", ".join(sorted({v.severity for v in matching}))
            return Rejection(
                "candidate-vulnerable",
                f"candidate version has known vulnerabilities at or above {args.vulnerability_severity_threshold}: {severities}",
            )

    return None


def has_dotnet() -> bool:
    return shutil.which("dotnet") is not None


def validate_package_compatibility(
    package_id: str,
    version: str,
    target_framework: str,
    sources: list[str],
    timeout: int,
    nuget_config: Path | None = None,
) -> CompatibilityResult:
    if not has_dotnet():
        return CompatibilityResult(
            compatible=False,
            kind="dotnet-not-found",
            output="dotnet CLI was not found in PATH",
            command=["dotnet", "restore"],
            exit_code=None,
            output_sha256=sha256_text("dotnet CLI was not found in PATH"),
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
        if nuget_config is not None:
            command.extend(["--configfile", str(nuget_config.resolve())])
        else:
            for source in sources:
                command.extend(["--source", source])

        env = os.environ.copy()
        env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
        env["DOTNET_NOLOGO"] = "1"
        env["NUGET_PACKAGES"] = str((Path(tmp) / "global-packages").resolve())
        env["NUGET_HTTP_CACHE_PATH"] = str((Path(tmp) / "http-cache").resolve())

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
        return CompatibilityResult(
            True,
            "compatible",
            output,
            command=command,
            exit_code=completed.returncode,
            output_sha256=sha256_text(output),
        )

    lowered = output.lower()
    if "nu1202" in lowered:
        kind = "incompatible"
    elif "netsdk1045" in lowered or "targeting .net" in lowered:
        kind = "sdk-does-not-support-target-framework"
    else:
        kind = "restore-failed"

    return CompatibilityResult(
        False,
        kind,
        output,
        command=command,
        exit_code=completed.returncode,
        output_sha256=sha256_text(output),
    )


def package_metadata_identity(metadata: PackageMetadata | None) -> str | None:
    if metadata is None:
        return None
    return canonical_sha256(dataclasses.asdict(metadata))


def candidate_provenance(candidate: Candidate | None, sources: list[str]) -> dict[str, Any] | None:
    if candidate is None:
        return None
    source_index = None
    if candidate.source and candidate.source != "versions-file":
        normalized = normalize_source(candidate.source)
        for index, source in enumerate(sources):
            if normalize_source(source) == normalized:
                source_index = index
                break
    return {
        "version": candidate.version.original,
        "source": candidate.source,
        "sourceIndex": source_index,
        "sourceCandidates": list(candidate.source_candidates),
        "sourceAmbiguous": len(candidate.source_candidates) > 1,
        "metadataSha256": package_metadata_identity(candidate.metadata),
    }


def compatibility_evidence(result: CompatibilityResult, version: str) -> dict[str, Any]:
    return {
        "version": version,
        "compatible": result.compatible,
        "kind": result.kind,
        "command": result.command,
        "exitCode": result.exit_code,
        "outputSha256": result.output_sha256,
    }


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
    reason_code: str | None = None,
    selected_candidate: Candidate | None = None,
    sources: list[str] | None = None,
    compatibility_attempts: list[dict[str, Any]] | None = None,
    candidate_rejections: list[dict[str, Any]] | None = None,
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
        reason_code=reason_code,
        candidate_provenance=candidate_provenance(selected_candidate, sources or []),
        compatibility_evidence=list(compatibility_attempts or []),
        current_metadata_sha256=package_metadata_identity(current_metadata),
        selected_vulnerability_metadata_sha256=(
            None
            if selected_metadata is None
            else canonical_sha256(vulnerability_dicts(selected_metadata))
        ),
        candidate_rejections=list(candidate_rejections or []),
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
            reason_code="current-version-nonliteral",
            candidate_count=0,
            safe_candidate_count=0,
            validated_candidates=0,
            source=None,
        )

    overrides = getattr(args, "_version_overrides", {}).get(entry.package_id.lower(), [])
    if overrides:
        return make_decision(
            entry=entry,
            current_metadata=None,
            latest_stable=None,
            selected_version=None,
            target_framework=args.target_framework,
            compatible=None,
            action="skipped",
            reason="one or more projects use VersionOverride for this centrally managed package",
            reason_code="version-override-active",
            candidate_count=0,
            safe_candidate_count=0,
            validated_candidates=0,
            source=None,
        )

    try:
        eligible_sources = sources_for_package(entry.package_id, args)
    except UpdaterError as exc:
        return make_decision(
            entry=entry, current_metadata=None, latest_stable=None, selected_version=None,
            target_framework=args.target_framework, compatible=None, action="skipped", reason=str(exc),
            reason_code=exc.code, candidate_count=0, safe_candidate_count=0, validated_candidates=0, source=None,
        )

    current_metadata = get_current_metadata(
        entry.package_id,
        entry.current_version,
        eligible_sources,
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
            reason_code="package-locked",
            candidate_count=0,
            safe_candidate_count=0,
            validated_candidates=0,
            source=None,
        )

    try:
        candidates, source = fetch_candidates(
            entry.package_id,
            eligible_sources,
            args.http_timeout,
            versions_by_package,
            args.allow_untrusted_versions_file,
        )
    except Exception as exc:  # noqa: BLE001 - return per-package error.
        reason_code = exc.code if isinstance(exc, UpdaterError) else "metadata-unavailable"
        return make_decision(
            entry=entry,
            current_metadata=current_metadata,
            latest_stable=None,
            selected_version=None,
            target_framework=args.target_framework,
            compatible=None,
            action="error",
            reason=str(exc),
            reason_code=reason_code,
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
    first_safety_rejection: Rejection | None = None
    candidate_rejections: list[dict[str, Any]] = []
    for candidate in allowed_by_version_policy:
        rejection = safety_rejection_reason(candidate, args)
        if rejection is None:
            safe_candidates.append(candidate)
        else:
            candidate_rejections.append(
                {
                    "version": candidate.version.original,
                    "code": rejection.code,
                    "message": rejection.message,
                    "source": candidate.source,
                    "sourceCandidates": list(candidate.source_candidates),
                    "metadataSha256": package_metadata_identity(candidate.metadata),
                }
            )
            if first_safety_rejection is None:
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
            reason_code="no-policy-allowed-newer-version",
            candidate_count=len(stable_candidates),
            safe_candidate_count=0,
            validated_candidates=0,
            source=source,
            candidate_rejections=candidate_rejections,
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
            reason=first_safety_rejection.message if first_safety_rejection else "no safe candidate after metadata policy",
            reason_code=first_safety_rejection.code if first_safety_rejection else "no-safe-candidate",
            candidate_count=len(stable_candidates),
            safe_candidate_count=0,
            validated_candidates=0,
            source=source,
            candidate_rejections=candidate_rejections,
        )

    validated = 0
    first_failure: CompatibilityResult | None = None
    compatibility_attempts: list[dict[str, Any]] = []

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
                reason_code="safe-update-selected" if action == "update" else "already-selected",
                candidate_count=len(stable_candidates),
                safe_candidate_count=len(safe_candidates),
                validated_candidates=validated,
                source=source,
                selected_metadata=candidate.metadata,
                selected_candidate=candidate,
                sources=eligible_sources,
                compatibility_attempts=compatibility_attempts,
                candidate_rejections=candidate_rejections,
            )

        validated += 1
        compatibility = validate_package_compatibility(
            entry.package_id,
            candidate.version.original,
            args.target_framework,
            eligible_sources,
            args.restore_timeout,
            nuget_config=(getattr(args, "_nuget_config_model", None).path if getattr(args, "_nuget_config_model", None) else None),
        )
        compatibility_attempts.append(compatibility_evidence(compatibility, candidate.version.original))
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
                reason_code="safe-compatible-update" if action == "update" else "already-selected",
                candidate_count=len(stable_candidates),
                safe_candidate_count=len(safe_candidates),
                validated_candidates=validated,
                source=source,
                selected_metadata=candidate.metadata,
                selected_candidate=candidate,
                sources=eligible_sources,
                compatibility_attempts=compatibility_attempts,
                candidate_rejections=candidate_rejections,
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
        reason_code="no-compatible-candidate",
        candidate_count=len(stable_candidates),
        safe_candidate_count=len(safe_candidates),
        validated_candidates=validated,
        source=source,
        compatibility_attempts=compatibility_attempts,
        candidate_rejections=candidate_rejections,
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


def dotnet_sdk_identity() -> dict[str, Any]:
    executable = shutil.which("dotnet")
    if executable is None:
        return {"available": False, "path": None, "version": None}
    try:
        completed = subprocess.run(
            [executable, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=15,
            check=False,
        )
        version = completed.stdout.strip() if completed.returncode == 0 else None
    except Exception:
        version = None
    return {"available": True, "path": executable, "version": version}


def build_metadata_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    records = [dict(record) for _, record in sorted(_FETCH_EVIDENCE.items())]
    identity_records = [
        {
            "url": record["url"],
            "rawSha256": record["rawSha256"],
            "canonicalSha256": record["canonicalSha256"],
        }
        for record in records
    ]
    identity_material = {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "sources": normalized_sources(args.source),
        "records": identity_records,
        "offlineVersions": None
        if _OFFLINE_VERSIONS_EVIDENCE is None
        else {
            "path": _OFFLINE_VERSIONS_EVIDENCE["path"],
            "sha256": _OFFLINE_VERSIONS_EVIDENCE["sha256"],
        },
    }
    return {
        "schemaVersion": EVIDENCE_SCHEMA_VERSION,
        "toolContractVersion": TOOL_CONTRACT_VERSION,
        "capturedAt": utc_now_iso(),
        "replayedFrom": _METADATA_REPLAY_SOURCE,
        "sources": normalized_sources(args.source),
        "sourceIdentity": canonical_sha256(normalized_sources(args.source)),
        "offlineVersions": _OFFLINE_VERSIONS_EVIDENCE,
        "records": records,
        "snapshotSha256": canonical_sha256(identity_material),
    }


def lock_pin_identity(entries: list[PackageEntry]) -> tuple[str, list[dict[str, Any]]]:
    records = [
        {
            "packageId": entry.package_id,
            "line": entry.line,
            "locked": entry.locked,
            "reason": entry.lock_reason,
        }
        for entry in entries
    ]
    return canonical_sha256(records), records


def build_write_preview(
    content: str,
    entries: list[PackageEntry],
    decisions: list[PackageDecision],
    baseline_hash: str,
) -> dict[str, Any]:
    updated_content = apply_updates(content, entries, decisions)
    changed = updated_content != content
    updates = [
        {
            "packageId": decision.package_id,
            "from": decision.current_version,
            "to": decision.selected_version,
            "reasonCode": decision.reason_code,
        }
        for decision in decisions
        if decision.action == "update" and decision.selected_version and not decision.locked
    ]
    return {
        "changed": changed,
        "inputSha256": baseline_hash,
        "outputSha256": sha256_text(updated_content) if changed else baseline_hash,
        "updates": updates,
        "content": updated_content,
    }


def decision_identity_material(report: dict[str, Any], metadata_snapshot: dict[str, Any]) -> dict[str, Any]:
    package_fields = []
    for package in report["packages"]:
        package_fields.append(
            {
                "package_id": package.get("package_id"),
                "current_version": package.get("current_version"),
                "selected_version": package.get("selected_version"),
                "action": package.get("action"),
                "reason_code": package.get("reason_code"),
                "locked": package.get("locked"),
                "lock_reason": package.get("lock_reason"),
                "candidate_provenance": package.get("candidate_provenance"),
                "candidate_rejections": [
                    {
                        "version": item.get("version"),
                        "code": item.get("code"),
                        "source": item.get("source"),
                        "sourceCandidates": item.get("sourceCandidates"),
                        "metadataSha256": item.get("metadataSha256"),
                    }
                    for item in package.get("candidate_rejections") or []
                ],
                "compatibility_evidence": [
                    {
                        "version": item.get("version"),
                        "compatible": item.get("compatible"),
                        "kind": item.get("kind"),
                        "exitCode": item.get("exitCode"),
                    }
                    for item in package.get("compatibility_evidence") or []
                ],
            }
        )
    return {
        "baselineSha256": report["identities"]["directoryPackagesPropsBaselineSha256"],
        "targetFramework": report["targetFramework"],
        "sourceIdentity": report["identities"]["nugetSourceIdentity"],
        "nugetConfigSha256": report["identities"].get("nugetConfigSha256"),
        "packageSourceMappingIdentity": report["identities"].get("packageSourceMappingIdentity"),
        "repositoryModelIdentity": report["identities"].get("repositoryModelIdentity"),
        "lockPinIdentity": report["identities"]["lockPinIdentity"],
        "metadataSnapshotSha256": metadata_snapshot["snapshotSha256"],
        "policy": report["policy"],
        "packages": package_fields,
        "writePreview": {
            "changed": report["writePreview"]["changed"],
            "inputSha256": report["writePreview"]["inputSha256"],
            "outputSha256": report["writePreview"]["outputSha256"],
            "updates": report["writePreview"]["updates"],
        },
    }


def build_decision_receipt(report: dict[str, Any], metadata_snapshot: dict[str, Any]) -> dict[str, Any]:
    material = decision_identity_material(report, metadata_snapshot)
    decision_identity = canonical_sha256(material)
    return {
        "receiptVersion": RECEIPT_SCHEMA_VERSION,
        "receiptType": "nuget-package-decision",
        "toolContractVersion": TOOL_CONTRACT_VERSION,
        "status": "planned",
        "createdAt": utc_now_iso(),
        "decisionIdentity": decision_identity,
        "subject": report["file"],
        "baselineSha256": report["identities"]["directoryPackagesPropsBaselineSha256"],
        "targetFramework": report["targetFramework"],
        "targetFrameworkIdentity": report["identities"]["targetFrameworkIdentity"],
        "nugetSourceIdentity": report["identities"]["nugetSourceIdentity"],
        "nugetConfigSha256": report["identities"].get("nugetConfigSha256"),
        "packageSourceMappingIdentity": report["identities"].get("packageSourceMappingIdentity"),
        "repositoryModelIdentity": report["identities"].get("repositoryModelIdentity"),
        "lockPinIdentity": report["identities"]["lockPinIdentity"],
        "metadataSnapshotSha256": metadata_snapshot["snapshotSha256"],
        "writePreview": {key: value for key, value in report["writePreview"].items() if key != "content"},
        "packages": report["packages"],
        "identityMaterialSha256": canonical_sha256(material),
    }


def resolve_sidecar_path(file_path: Path, requested: str | None, default_name: str) -> Path:
    if requested:
        path = Path(requested)
        if not path.is_absolute():
            path = file_path.parent / path
        return path.resolve()
    return (file_path.parent / "docs" / "pkgs-versions" / default_name).resolve()


def preflight_sidecar_paths(file_path: Path, paths: list[Path], protected_inputs: Iterable[Path] | None = None) -> None:
    protected = {file_path.resolve()}
    for value in protected_inputs or []:
        protected.add(Path(value).resolve())
    seen: set[Path] = set()
    for path in paths:
        canonical = path.resolve()
        if canonical in protected:
            raise UpdaterError("output-aliases-input", f"output aliases an input/protected file: {canonical}", stage="precondition")
        if canonical in seen:
            raise UpdaterError("output-alias-collision", f"outputs alias one another: {canonical}", stage="precondition")
        seen.add(canonical)


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def with_payload_hash(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["payloadSha256"] = canonical_sha256(payload)
    return result


def verify_expected_decision_receipt(path: Path, current: dict[str, Any]) -> None:
    expected = json.loads(read_text(path))
    expected_identity = expected.get("decisionIdentity")
    current_identity = current.get("decisionIdentity")
    if expected_identity != current_identity:
        raise UpdaterError(
            "decision-receipt-mismatch",
            "current package decision does not match the expected decision receipt",
            stage="precondition",
            evidence={
                "expectedReceipt": str(path.resolve()),
                "expectedDecisionIdentity": expected_identity,
                "currentDecisionIdentity": current_identity,
                "expectedMetadataSnapshotSha256": expected.get("metadataSnapshotSha256"),
                "currentMetadataSnapshotSha256": current.get("metadataSnapshotSha256"),
            },
        )


def preserve_last_known_good(file_path: Path, baseline_hash: str, args: argparse.Namespace) -> Path:
    root = Path(args.last_known_good_dir)
    if not root.is_absolute():
        root = file_path.parent / root
    root.mkdir(parents=True, exist_ok=True)
    target = root / f"{file_path.name}.{baseline_hash}.bak"
    if target.exists():
        if sha256_file(target) != baseline_hash:
            raise UpdaterError(
                "last-known-good-hash-mismatch",
                f"existing last-known-good file has unexpected bytes: {target}",
                stage="precondition",
            )
        return target
    atomic_write_bytes(target, file_path.read_bytes())
    if sha256_file(target) != baseline_hash:
        raise UpdaterError("last-known-good-write-failed", "last-known-good hash verification failed", stage="write")
    return target


def commit_package_update(
    file_path: Path,
    updated_content: str,
    baseline_hash: str,
    expected_output_hash: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    current_hash = sha256_file(file_path)
    if current_hash != baseline_hash:
        raise UpdaterError(
            "input-changed-before-write",
            "Directory.Packages.props changed after analysis and before write",
            stage="precondition",
            evidence={"expected": baseline_hash, "observed": current_hash},
        )
    lkg = preserve_last_known_good(file_path, baseline_hash, args)
    try:
        atomic_write_text(file_path, updated_content)
    except Exception as exc:
        raise UpdaterError(
            "atomic-write-failed",
            f"atomic package write failed: {exc}",
            stage="write",
            evidence={"lastKnownGood": str(lkg)},
        ) from exc
    written_hash = sha256_file(file_path)
    if written_hash != expected_output_hash:
        rollback_package_update(file_path, lkg, baseline_hash)
        raise UpdaterError(
            "post-write-hash-mismatch",
            "written Directory.Packages.props did not match the preview hash; rollback completed",
            stage="write",
            evidence={"expected": expected_output_hash, "observed": written_hash, "lastKnownGood": str(lkg)},
        )
    return {
        "status": "committed",
        "baselineSha256": baseline_hash,
        "writtenSha256": written_hash,
        "lastKnownGoodPath": str(lkg.resolve()),
        "lastKnownGoodSha256": sha256_file(lkg),
    }


def rollback_package_update(file_path: Path, lkg: Path, baseline_hash: str) -> dict[str, Any]:
    try:
        atomic_write_bytes(file_path, lkg.read_bytes())
        observed = sha256_file(file_path)
        if observed != baseline_hash:
            raise RuntimeError(f"rollback hash mismatch: {observed}")
        return {"status": "rolled-back", "restoredSha256": observed, "source": str(lkg.resolve())}
    except Exception as exc:
        raise UpdaterError(
            "rollback-failed",
            f"rollback failed: {exc}",
            stage="rollback",
            evidence={"lastKnownGood": str(lkg.resolve()), "expectedSha256": baseline_hash},
        ) from exc


def analyze_restore_audit_output(output: str, threshold: str) -> dict[str, Any]:
    threshold_rank = vulnerability_threshold_rank(threshold)
    warning_severity = {"NU1901": 0, "NU1902": 1, "NU1903": 2, "NU1904": 3}
    observed: list[dict[str, Any]] = []
    for code, rank in warning_severity.items():
        count = len(re.findall(rf"\b{code}\b", output, flags=re.IGNORECASE))
        if count:
            observed.append({"code": code, "severity": SEVERITY_LABELS[rank], "count": count})
    audit_source_unavailable = bool(re.search(r"\bNU1905\b", output, flags=re.IGNORECASE))
    prune_count = len(re.findall(r"\bNU1510\b", output, flags=re.IGNORECASE))
    blocking = [item for item in observed if SEVERITY_ORDER[item["severity"]] >= threshold_rank]
    return {
        "status": "fail" if blocking or audit_source_unavailable else "pass",
        "threshold": threshold,
        "vulnerabilityWarningCount": sum(item["count"] for item in observed),
        "blockingVulnerabilityWarningCount": sum(item["count"] for item in blocking),
        "warnings": observed,
        "auditSourceUnavailable": audit_source_unavailable,
        "pruneWarningCount": prune_count,
    }


def configured_validation_commands(args: argparse.Namespace) -> list[tuple[str, list[str]]]:
    configured: list[str] = list(args.validation_command)
    if getattr(args, "audit_repository", False) and configured:
        raise UpdaterError(
            "audit-custom-validation-unsupported",
            "--audit-repository requires the built-in repository validation sequence",
            stage="input",
        )
    if args.validate_repository and not configured:
        restore = "dotnet restore"
        if getattr(args, "audit_repository", False):
            restore += (
                " -p:NuGetAudit=true -p:NuGetAuditMode=all"
                f" -p:NuGetAuditLevel={args.vulnerability_severity_threshold}"
            )
        configured = [
            f"restore::{restore}",
            "build::dotnet build --no-restore",
            "test::dotnet test --no-build",
        ]
    result: list[tuple[str, list[str]]] = []
    for raw in configured:
        if "::" not in raw:
            raise UpdaterError(
                "validation-command-invalid",
                "validation commands must use label::command syntax",
                stage="input",
                evidence={"value": raw},
            )
        label, command_text = raw.split("::", 1)
        command = shlex.split(command_text)
        if not label.strip() or not command:
            raise UpdaterError("validation-command-invalid", "validation command is empty", stage="input")
        result.append((label.strip(), command))
    return result


def run_repository_validation(file_path: Path, args: argparse.Namespace) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for label, command in configured_validation_commands(args):
        started = utc_now_iso()
        try:
            completed = subprocess.run(
                command,
                cwd=getattr(args, "_repository_root", file_path.parent),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=args.validation_timeout,
                check=False,
                env={**os.environ, "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"},
            )
            output = completed.stdout or ""
            audit = analyze_restore_audit_output(output, args.vulnerability_severity_threshold) if label.lower() == "restore" and getattr(args, "audit_repository", False) else None
            status = "pass" if completed.returncode == 0 and (audit is None or audit["status"] == "pass") else "fail"
            record = {
                "label": label,
                "command": command,
                "startedAt": started,
                "completedAt": utc_now_iso(),
                "exitCode": completed.returncode,
                "status": status,
                "outputSha256": sha256_text(output),
                "audit": audit,
            }
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
            record = {
                "label": label,
                "command": command,
                "startedAt": started,
                "completedAt": utc_now_iso(),
                "exitCode": None,
                "status": "timeout",
                "outputSha256": sha256_text(output),
            }
        except OSError as exc:
            output = str(exc)
            record = {
                "label": label,
                "command": command,
                "startedAt": started,
                "completedAt": utc_now_iso(),
                "exitCode": None,
                "status": "fail",
                "errorType": type(exc).__name__,
                "outputSha256": sha256_text(output),
            }
        evidence.append(record)
        if record["status"] != "pass":
            break
    return evidence


def build_report(
    file_path: Path,
    args: argparse.Namespace,
    entries: list[PackageEntry],
    decisions: list[PackageDecision],
    wrote_file: bool,
) -> dict[str, Any]:
    return {
        "toolContractVersion": TOOL_CONTRACT_VERSION,
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
            "allowSourceAmbiguity": getattr(args, "allow_source_ambiguity", False),
            "auditRepository": getattr(args, "audit_repository", False),
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
        f"- Baseline SHA-256: `{report.get('identities', {}).get('directoryPackagesPropsBaselineSha256', '')}`",
        f"- Metadata snapshot SHA-256: `{report.get('metadataSnapshot', {}).get('snapshotSha256', '')}`",
        f"- Decision identity: `{report.get('decisionIdentity', '')}`",
        f"- Write status: `{report.get('writeStatus', '')}`",
        f"- Final file SHA-256: `{report.get('finalFileSha256', '')}`",
        f"- Decision receipt: `{report.get('decisionReceiptPath', '')}`",
        f"- Package-update receipt: `{report.get('packageUpdateReceiptPath', '')}`",
        f"- Updated: `{report['updatedCount']}`",
        f"- Unchanged: `{report['unchangedCount']}`",
        f"- Locked: `{report['lockedCount']}`",
        f"- Skipped: `{report['skippedCount']}`",
        f"- Errors: `{report['errorCount']}`",
        "",
        "| Package | Current | Selected | Latest stable | Action | Reason code | Safe candidates | Locked | Reason |",
        "|---|---:|---:|---:|---|---|---:|---|---|",
    ]

    for package in report["packages"]:
        reason = package.get("reason") or ""
        locked = package.get("lock_reason") or ""
        lines.append(
            "| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} |".format(
                _md_cell(package.get("package_id")),
                _md_cell(package.get("current_version")),
                _md_cell(package.get("selected_version")),
                _md_cell(package.get("latest_stable_version")),
                _md_cell(package.get("action")),
                _md_cell(package.get("reason_code")),
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


REPOSITORY_SKIP_DIRS = {".git", ".vs", ".nuget-updater", "bin", "obj", "node_modules"}
PACKAGE_REFERENCE_TAG_RE = re.compile(r"<PackageReference\b(?P<attrs>[^>]*)>", re.IGNORECASE | re.DOTALL)


def validate_selected_cpm_complexity(entries: list[PackageEntry]) -> None:
    conditional = [entry for entry in entries if entry.condition]
    if conditional:
        raise UpdaterError(
            "conditional-package-version-unsupported",
            "selected PackageVersion declarations contain Condition; evaluate the effective MSBuild model before changing them",
            stage="policy",
            evidence={"packages": sorted({entry.package_id for entry in conditional})},
        )
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry.package_id.lower()] = counts.get(entry.package_id.lower(), 0) + 1
    duplicates = sorted(key for key, count in counts.items() if count > 1)
    if duplicates:
        raise UpdaterError(
            "duplicate-package-version-declarations",
            "selected package IDs have multiple PackageVersion declarations; text mutation is ambiguous",
            stage="policy",
            evidence={"packages": duplicates},
        )


def _walk_repository_files(root: Path, names: set[str] | None = None, suffixes: set[str] | None = None) -> list[Path]:
    result: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in REPOSITORY_SKIP_DIRS)
        base = Path(current)
        for name in sorted(files):
            path = base / name
            if names is not None and name in names:
                result.append(path)
            elif suffixes is not None and path.suffix.lower() in suffixes:
                result.append(path)
    return result


def find_project_version_overrides(root: Path, package_ids: set[str]) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    for project in _walk_repository_files(root, suffixes={".csproj", ".fsproj", ".vbproj"}):
        try:
            text = read_text(project)
        except (OSError, UnicodeError):
            continue
        for tag in PACKAGE_REFERENCE_TAG_RE.finditer(text):
            attrs = parse_attributes(tag.group("attrs"))
            package_id = (attrs.get("include") or attrs.get("update") or "").strip()
            override = (attrs.get("versionoverride") or "").strip()
            if package_id and override and package_id.lower() in package_ids:
                result.setdefault(package_id.lower(), []).append(
                    {"project": str(project.relative_to(root)), "packageId": package_id, "versionOverride": override}
                )
    return result


def _lock_content_identity(raw: bytes) -> str | None:
    try:
        payload = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError):
        return None
    dependencies = payload.get("dependencies", {}) if isinstance(payload, dict) else {}
    records: list[dict[str, Any]] = []
    if isinstance(dependencies, dict):
        for framework, packages in sorted(dependencies.items()):
            if not isinstance(packages, dict):
                continue
            for package_id, value in sorted(packages.items()):
                if not isinstance(value, dict):
                    continue
                records.append({
                    "framework": framework,
                    "packageId": package_id,
                    "resolved": value.get("resolved"),
                    "contentHash": value.get("contentHash"),
                    "type": value.get("type"),
                })
    return canonical_sha256(records)


def capture_lock_file_state(root: Path) -> dict[str, Any]:
    files = []
    byte_map: dict[str, bytes] = {}
    for path in _walk_repository_files(root, names={"packages.lock.json"}):
        rel = path.relative_to(root).as_posix()
        raw = path.read_bytes()
        byte_map[rel] = raw
        files.append({"path": rel, "sha256": sha256_bytes(raw), "contentIdentity": _lock_content_identity(raw)})
    public = {"root": str(root), "files": files}
    public["identity"] = canonical_sha256(files)
    public["_bytes"] = byte_map
    return public


def public_lock_file_state(state: dict[str, Any]) -> dict[str, Any]:
    return {"root": state.get("root"), "files": state.get("files", []), "identity": state.get("identity")}


def preserve_lock_file_state(root: Path, state: dict[str, Any], backup_root: Path) -> dict[str, str]:
    backups: dict[str, str] = {}
    for rel, raw in state.get("_bytes", {}).items():
        target = (backup_root / rel).resolve()
        try:
            target.relative_to(backup_root.resolve())
        except ValueError as exc:
            raise UpdaterError("lockfile-backup-path-invalid", f"invalid lockfile backup path: {rel}", stage="precondition") from exc
        atomic_write_bytes(target, raw)
        backups[rel] = str(target)
    return backups


def restore_lock_file_state(root: Path, before: dict[str, Any], backups: dict[str, str]) -> dict[str, Any]:
    expected = set(before.get("_bytes", {}))
    current = {path.relative_to(root).as_posix(): path for path in _walk_repository_files(root, names={"packages.lock.json"})}
    restored: list[str] = []
    removed: list[str] = []
    for rel, backup in backups.items():
        target = (root / rel).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise UpdaterError("lockfile-rollback-path-invalid", f"invalid lockfile rollback path: {rel}", stage="rollback") from exc
        atomic_write_bytes(target, Path(backup).read_bytes())
        restored.append(rel)
    for rel, path in current.items():
        if rel not in expected:
            resolved = path.resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                continue
            if path.is_file() and not path.is_symlink():
                path.unlink()
                removed.append(rel)
    after = capture_lock_file_state(root)
    if after["identity"] != before["identity"]:
        raise UpdaterError(
            "lockfile-rollback-failed",
            "lock files did not return to the pre-validation identity",
            stage="rollback",
            evidence={"expected": before["identity"], "observed": after["identity"]},
        )
    return {"status": "rolled-back", "restored": sorted(restored), "removedCreated": sorted(removed), "identity": after["identity"]}


def protected_input_paths(file_path: Path, args: argparse.Namespace, repository_model: dict[str, Any]) -> list[Path]:
    result = [file_path]
    for attr in ["nuget_config", "versions_file", "metadata_snapshot_input", "expected_decision_receipt"]:
        value = getattr(args, attr, None)
        if value:
            result.append(Path(value))
    root = Path(repository_model["root"])
    for record in repository_model.get("lockFiles", {}).get("files", []):
        rel = record.get("path")
        if rel:
            result.append(root / rel)
    return result


def build_repository_model(file_path: Path, entries: list[PackageEntry], args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repository_root).resolve() if getattr(args, "repository_root", None) else file_path.parent.resolve()
    try:
        file_path.resolve().relative_to(root)
    except ValueError as exc:
        raise UpdaterError("repository-root-invalid", "Directory.Packages.props must be inside --repository-root", stage="input") from exc
    args._repository_root = root
    validate_selected_cpm_complexity(entries)
    package_ids = {entry.package_id.lower() for entry in entries}
    overrides = find_project_version_overrides(root, package_ids)
    args._version_overrides = overrides
    dpps = [path.relative_to(root).as_posix() for path in _walk_repository_files(root, names={"Directory.Packages.props"})]
    locks = capture_lock_file_state(root)
    material = {
        "root": str(root),
        "directoryPackagesProps": dpps,
        "versionOverrides": overrides,
        "lockFiles": public_lock_file_state(locks),
    }
    identity_material = {
        "directoryPackagesProps": dpps,
        "versionOverrides": overrides,
        "lockFiles": {
            "files": material["lockFiles"]["files"],
            "identity": material["lockFiles"]["identity"],
        },
    }
    material["identity"] = canonical_sha256(identity_material)
    args._lock_file_state_before = locks
    return material


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
    reset_runtime_state()
    configure_nuget_inputs(args)
    if getattr(args, "audit_repository", False):
        args.validate_repository = True
    configure_metadata_replay(Path(args.metadata_snapshot_input).resolve() if args.metadata_snapshot_input else None)

    file_path = resolve_file_path(args)
    if not file_path.exists():
        raise UpdaterError("input-file-not-found", f"file not found: {file_path}", stage="input")

    baseline_hash = sha256_file(file_path)
    if args.expected_baseline_sha256 and args.expected_baseline_sha256.lower() != baseline_hash.lower():
        raise UpdaterError(
            "baseline-hash-mismatch",
            "Directory.Packages.props does not match the expected baseline hash",
            stage="precondition",
            evidence={"expected": args.expected_baseline_sha256, "observed": baseline_hash},
        )

    content = read_text(file_path)
    entries = parse_package_entries(content)
    selected_entries = select_entries(entries, args)
    repository_model = build_repository_model(file_path, selected_entries, args)
    lock_identity, lock_records = lock_pin_identity(selected_entries)
    sdk_identity = dotnet_sdk_identity()
    config_model: NuGetConfigModel | None = getattr(args, "_nuget_config_model", None)
    source_identity = canonical_sha256({
        "sources": normalized_sources(args.source),
        "nugetConfigSha256": None if config_model is None else config_model.sha256,
        "packageSourceMappingIdentity": None if config_model is None else config_model.mapping_identity,
    })

    versions_by_package = load_versions_file(Path(args.versions_file).resolve()) if args.versions_file else None

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
                reason_code="package-locked" if e.locked else "package-found",
                candidate_count=0,
                safe_candidate_count=0,
                validated_candidates=0,
                source=None,
            )
            for e in selected_entries
        ]
        report = build_report(file_path, args, selected_entries, decisions, wrote_file=False)
        report["identities"] = {
            "directoryPackagesPropsBaselineSha256": baseline_hash,
            "targetFrameworkIdentity": canonical_sha256({"tfm": args.target_framework, "dotnetSdk": sdk_identity}),
            "dotnetSdk": sdk_identity,
            "nugetSourceIdentity": source_identity,
            "nugetSources": normalized_sources(args.source),
            "nugetConfigSha256": None if config_model is None else config_model.sha256,
            "packageSourceMappingIdentity": None if config_model is None else config_model.mapping_identity,
            "repositoryModelIdentity": repository_model["identity"],
            "repositoryModel": repository_model,
            "lockPinIdentity": lock_identity,
            "lockPinRecords": lock_records,
        }
        if args.report:
            report_path = resolve_sidecar_path(file_path, args.report, "unused-report.json")
            preflight_sidecar_paths(file_path, [report_path], protected_input_paths(file_path, args, repository_model))
            args._report_path = report_path
        emit_report(report, args)
        return EXIT_OK

    decisions = [decide_package_update(entry, args, versions_by_package) for entry in selected_entries]
    preview = build_write_preview(content, selected_entries, decisions, baseline_hash)
    metadata_snapshot = build_metadata_snapshot(args)

    report = build_report(file_path, args, selected_entries, decisions, wrote_file=False)
    report["identities"] = {
        "directoryPackagesPropsBaselineSha256": baseline_hash,
        "targetFrameworkIdentity": canonical_sha256({"tfm": args.target_framework, "dotnetSdk": sdk_identity}),
        "dotnetSdk": sdk_identity,
        "nugetSourceIdentity": source_identity,
        "nugetSources": normalized_sources(args.source),
        "nugetConfigSha256": None if config_model is None else config_model.sha256,
        "packageSourceMappingIdentity": None if config_model is None else config_model.mapping_identity,
        "repositoryModelIdentity": repository_model["identity"],
        "repositoryModel": repository_model,
        "lockPinIdentity": lock_identity,
        "lockPinRecords": lock_records,
    }
    report["metadataSnapshot"] = {
        "capturedAt": metadata_snapshot["capturedAt"],
        "snapshotSha256": metadata_snapshot["snapshotSha256"],
        "recordCount": len(metadata_snapshot["records"]),
        "replayedFrom": metadata_snapshot["replayedFrom"],
        "offlineVersions": metadata_snapshot["offlineVersions"],
    }
    report["writePreview"] = {key: value for key, value in preview.items() if key != "content"}

    decision_receipt = with_payload_hash(build_decision_receipt(report, metadata_snapshot))
    report["decisionIdentity"] = decision_receipt["decisionIdentity"]

    if args.expected_decision_receipt:
        verify_expected_decision_receipt(Path(args.expected_decision_receipt).resolve(), decision_receipt)

    if args.command == "update" and args.write:
        configured_validation_commands(args)

    metadata_path = None
    decision_receipt_path = None
    package_receipt_path = None
    declared_outputs: list[Path] = []
    if args.report:
        args._report_path = resolve_sidecar_path(file_path, args.report, "unused-report.json")
        declared_outputs.append(args._report_path)
    if args.write_decision_doc:
        args._decision_doc_path = resolve_decision_document_path(file_path, args, report)
        declared_outputs.append(args._decision_doc_path)
    if args.write_evidence:
        short_id = decision_receipt["decisionIdentity"][:16]
        metadata_path = resolve_sidecar_path(
            file_path, args.metadata_snapshot_output, f"nuget-metadata-snapshot-{metadata_snapshot['snapshotSha256'][:16]}.json"
        )
        decision_receipt_path = resolve_sidecar_path(
            file_path, args.decision_receipt, f"nuget-decision-receipt-{short_id}.json"
        )
        declared_outputs.extend([metadata_path, decision_receipt_path])
        if args.command == "update" and args.write:
            package_receipt_path = resolve_sidecar_path(
                file_path, args.package_update_receipt, f"nuget-package-update-receipt-{short_id}.json"
            )
            declared_outputs.append(package_receipt_path)
    if declared_outputs:
        preflight_sidecar_paths(file_path, declared_outputs, protected_input_paths(file_path, args, repository_model))

    if args.write_evidence:
        assert metadata_path is not None and decision_receipt_path is not None
        write_json_atomic(metadata_path, metadata_snapshot)
        write_json_atomic(decision_receipt_path, decision_receipt)
        report["metadataSnapshotPath"] = str(metadata_path)
        report["decisionReceiptPath"] = str(decision_receipt_path)
        report["decisionReceiptSha256"] = sha256_file(decision_receipt_path)

    write_evidence: dict[str, Any] | None = None
    validation_evidence: list[dict[str, Any]] = []
    rollback_evidence: dict[str, Any] | None = None
    write_status = "not-requested"
    wrote_file = False

    if args.command == "update" and args.write:
        if preview["changed"]:
            lock_state_before = getattr(args, "_lock_file_state_before", capture_lock_file_state(args._repository_root))
            lkg_preflight = preserve_last_known_good(file_path, baseline_hash, args)
            lock_backup_root = lkg_preflight.parent / "lock-files"
            lock_backups = preserve_lock_file_state(args._repository_root, lock_state_before, lock_backup_root)
            write_evidence = commit_package_update(
                file_path,
                preview["content"],
                baseline_hash,
                preview["outputSha256"],
                args,
            )
            write_evidence["lockFilesBefore"] = public_lock_file_state(lock_state_before)
            wrote_file = True
            write_status = "committed"
            validation_evidence = run_repository_validation(file_path, args)
            lock_state_after = capture_lock_file_state(args._repository_root)
            write_evidence["lockFilesAfterValidation"] = public_lock_file_state(lock_state_after)
            if validation_evidence and validation_evidence[-1]["status"] != "pass":
                file_rollback = rollback_package_update(
                    file_path,
                    Path(write_evidence["lastKnownGoodPath"]),
                    baseline_hash,
                )
                lock_rollback = restore_lock_file_state(args._repository_root, lock_state_before, lock_backups)
                rollback_evidence = {"packageFile": file_rollback, "lockFiles": lock_rollback}
                wrote_file = False
                write_status = "rolled-back-validation-failure"
        else:
            write_status = "no-change"

    report["write"] = wrote_file
    report["writeStatus"] = write_status
    report["writeEvidence"] = write_evidence
    report["validationEvidence"] = validation_evidence
    report["rollbackEvidence"] = rollback_evidence
    report["finalFileSha256"] = sha256_file(file_path)

    if args.write_evidence and package_receipt_path is not None:
        package_receipt = with_payload_hash(
            {
                "receiptVersion": RECEIPT_SCHEMA_VERSION,
                "receiptType": "nuget-package-update",
                "toolContractVersion": TOOL_CONTRACT_VERSION,
                "status": write_status,
                "completedAt": utc_now_iso(),
                "subject": str(file_path),
                "decisionIdentity": decision_receipt["decisionIdentity"],
                "decisionReceiptSha256": report.get("decisionReceiptSha256"),
                "metadataSnapshotSha256": metadata_snapshot["snapshotSha256"],
                "baselineSha256": baseline_hash,
                "previewOutputSha256": preview["outputSha256"],
                "finalFileSha256": report["finalFileSha256"],
                "writeEvidence": write_evidence,
                "validationEvidence": validation_evidence,
                "rollbackEvidence": rollback_evidence,
            }
        )
        write_json_atomic(package_receipt_path, package_receipt)
        report["packageUpdateReceiptPath"] = str(package_receipt_path)
        report["packageUpdateReceiptSha256"] = sha256_file(package_receipt_path)

    if args.write_decision_doc:
        decision_doc_path = write_decision_document(file_path, args, report)
        report["decisionDocument"] = str(decision_doc_path)
        report["decisionDocumentSha256"] = sha256_file(decision_doc_path)

    emit_report(report, args)

    if report["errorCount"] > 0:
        return EXIT_TECHNICAL_ERROR
    if write_status == "rolled-back-validation-failure":
        return EXIT_POLICY_FAILURE
    if args.fail_on_incompatible and any(d.compatible is False for d in decisions):
        return EXIT_POLICY_FAILURE
    if args.fail_on_outdated and any(d.action == "update" for d in decisions):
        return EXIT_POLICY_FAILURE
    return EXIT_OK

def resolve_decision_document_path(file_path: Path, args: argparse.Namespace, report: dict[str, Any]) -> Path:
    output_dir = Path(args.decision_doc_dir)
    if not output_dir.is_absolute():
        output_dir = file_path.parent / output_dir
    if args.decision_doc_name:
        requested = Path(args.decision_doc_name)
        if requested.name != args.decision_doc_name or requested.suffix.lower() != ".md":
            raise UpdaterError(
                "decision-doc-name-invalid",
                "--decision-doc-name must be a simple .md filename without path separators",
                stage="input",
            )
        file_name = args.decision_doc_name
    else:
        identity = report.get("decisionIdentity") or "unidentified"
        file_name = f"nuget-package-update-decisions-{identity[:16]}.md"
    return (output_dir / file_name).resolve()


def write_decision_document(file_path: Path, args: argparse.Namespace, report: dict[str, Any]) -> Path:
    target = Path(getattr(args, "_decision_doc_path", resolve_decision_document_path(file_path, args, report)))
    atomic_write_text(target, format_decision_document(report))
    return target


def format_decision_document(report: dict[str, Any]) -> str:
    generated_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# NuGet package version decisions",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Source file: `{report['file']}`",
        f"- Source file baseline SHA-256: `{report.get('identities', {}).get('directoryPackagesPropsBaselineSha256', '')}`",
        f"- Target framework: `{report['targetFramework']}`",
        f"- Target framework identity: `{report.get('identities', {}).get('targetFrameworkIdentity', '')}`",
        f"- NuGet source identity: `{report.get('identities', {}).get('nugetSourceIdentity', '')}`",
        f"- NuGet.Config SHA-256: `{report.get('identities', {}).get('nugetConfigSha256', '')}`",
        f"- Package Source Mapping identity: `{report.get('identities', {}).get('packageSourceMappingIdentity', '')}`",
        f"- Repository model identity: `{report.get('identities', {}).get('repositoryModelIdentity', '')}`",
        f"- Lock/pin identity: `{report.get('identities', {}).get('lockPinIdentity', '')}`",
        f"- Metadata snapshot SHA-256: `{report.get('metadataSnapshot', {}).get('snapshotSha256', '')}`",
        f"- Decision identity: `{report.get('decisionIdentity', '')}`",
        f"- Wrote package file: `{report['write']}`",
        f"- Write status: `{report.get('writeStatus', '')}`",
        f"- Final package file SHA-256: `{report.get('finalFileSha256', '')}`",
        f"- Restore validation: `{report['restoreValidation']}`",
        f"- Safety validation: `{report['safetyValidation']}`",
        f"- Decision receipt: `{report.get('decisionReceiptPath', '')}`",
        f"- Package-update receipt: `{report.get('packageUpdateReceiptPath', '')}`",
        "",
        "## Decision policy",
        "",
        "- Use only stable NuGet versions.",
        "- Reject prerelease, unlisted, deprecated, and vulnerable candidate versions.",
        "- Validate candidate package metadata through NuGet Registration API.",
        "- Cross-check vulnerability ranges through NuGet VulnerabilityInfo API when the source exposes it.",
        "- Respect locks and pins declared in `Directory.Packages.props`.",
        "- Treat the same exact version from multiple eligible sources as ambiguous unless explicitly overridden.",
        "- Apply Package Source Mapping from an explicit `NuGet.Config` when supplied.",
        "- Repository audit evidence is separate from the package-level compatibility probe.",
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
        "| Package | Current | Current safety | Latest stable | Selected | Decision | Reason code | Compatibility | Reason |",
        "|---|---:|---|---:|---:|---|---|---|---|",
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
            "| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} |".format(
                _md_cell(package.get("package_id")),
                _md_cell(package.get("current_version")),
                _md_cell(", ".join(current_safety)),
                _md_cell(package.get("latest_stable_version")),
                _md_cell(package.get("selected_version")),
                _md_cell(package.get("action")),
                _md_cell(package.get("reason_code")),
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
                f"- Reason code: `{_md_cell(package.get('reason_code'))}`",
                f"- Reason: `{_md_cell(package.get('reason') or package.get('lock_reason') or '')}`",
                f"- Candidate count: `{package.get('candidate_count')}`",
                f"- Safe candidate count: `{package.get('safe_candidate_count')}`",
                f"- Validated candidate count: `{package.get('validated_candidates')}`",
                f"- Source: `{_md_cell(package.get('source'))}`",
                f"- Candidate provenance: `{_md_cell(json.dumps(package.get('candidate_provenance'), sort_keys=True, ensure_ascii=False))}`",
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
        target = getattr(args, "_report_path", None) or Path(args.report).resolve()
        atomic_write_text(Path(target), rendered)


def add_shared_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file", help="Path to Directory.Packages.props. Defaults to auto-discovery.")
    parser.add_argument("--target-framework", default=DEFAULT_TARGET_FRAMEWORK)
    parser.add_argument("--source", action="append", default=[], help="NuGet source/service index. Can be repeated. When omitted, an explicit --nuget-config packageSources section is used, otherwise nuget.org.")
    parser.add_argument("--nuget-config", help="Explicit NuGet.Config used for packageSources, Package Source Mapping identity, and compatibility restore configuration.")
    parser.add_argument("--repository-root", help="Repository root used to discover projects, VersionOverride declarations, and packages.lock.json. Defaults to the Directory.Packages.props directory.")
    parser.add_argument("--package", action="append", default=[], help="Only process this package ID. Can be repeated.")
    parser.add_argument("--ignore-package", action="append", default=[], help="Skip this package ID. Can be repeated.")
    parser.add_argument("--versions-file", help="Offline JSON map of package IDs to versions. Useful for smoke tests only.")
    parser.add_argument("--metadata-snapshot-input", help="Replay exact NuGet JSON responses from a previously captured metadata snapshot. Missing URLs fail closed.")
    parser.add_argument("--metadata-snapshot-output", help="Optional metadata snapshot output path used with --write-evidence.")
    parser.add_argument("--decision-receipt", help="Optional decision receipt output path used with --write-evidence.")
    parser.add_argument("--expected-decision-receipt", help="Require the current decision identity to match this prior receipt before writing.")
    parser.add_argument("--package-update-receipt", help="Optional package-update receipt output path used with --write-evidence.")
    parser.add_argument("--write-evidence", action="store_true", help="Write metadata snapshot and decision/package receipts with hashes under docs/pkgs-versions by default.")
    parser.add_argument("--expected-baseline-sha256", help="Require Directory.Packages.props to match this SHA-256 before analysis/write.")
    parser.add_argument("--last-known-good-dir", default=".nuget-updater/last-known-good", help="Directory used to preserve exact pre-write bytes for rollback.")
    parser.add_argument("--validate-repository", action="store_true", help="After a write, run restore, build --no-restore, and test --no-build; rollback package and lock-file state on first failure.")
    parser.add_argument("--audit-repository", action="store_true", help="With built-in repository validation, enable transitive NuGetAudit and fail on NU1905 or vulnerabilities at/above the configured threshold.")
    parser.add_argument("--validation-command", action="append", default=[], help="Ordered post-write command in label::command form. Executed without a shell; rollback on first failure.")
    parser.add_argument("--validation-timeout", type=int, default=600, help="Timeout in seconds for each post-write validation command.")
    parser.add_argument("--allow-untrusted-versions-file", action="store_true", help="Allow versions-file candidates to pass metadata trust checks. Use only in tests.")
    parser.add_argument("--allow-source-ambiguity", action="store_true", help="Allow the same exact version from multiple eligible sources. Diagnostic escape hatch; Package Source Mapping is preferred.")
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

    try:
        return run(args)
    except UpdaterError as exc:
        print(
            json.dumps(
                {
                    "error": str(exc),
                    "code": exc.code,
                    "stage": exc.stage,
                    "evidence": exc.evidence,
                },
                indent=2,
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return EXIT_TECHNICAL_ERROR
    except subprocess.TimeoutExpired as exc:
        print(json.dumps({"error": f"command timed out: {exc}"}, indent=2), file=sys.stderr)
        return EXIT_TECHNICAL_ERROR
    except Exception as exc:  # noqa: BLE001 - CLI top-level reporting.
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return EXIT_TECHNICAL_ERROR


if __name__ == "__main__":
    sys.exit(main())
