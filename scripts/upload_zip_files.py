#!/usr/bin/env python3
"""Upload ZIP files to the ChatGPT skills upload endpoint."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_URL = "https://chatgpt.com/backend-api/hazelnuts/uploads/create"
DEFAULT_DELAY_SECONDS = 1.0
DEFAULT_HEADERS = {
    "accept": "*/*",
    "oai-client-build-number": "11018478",
    "oai-client-version": "prod-51404fa88033510cc879b69b6499ac2cf384ae62",
    "oai-language": "en-US",
    "origin": "https://chatgpt.com",
    "referer": "https://chatgpt.com/skills",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36 Edg/153.0.0.0",
    "x-openai-target-path": "/backend-api/hazelnuts/uploads/create",
    "x-openai-target-route": "/backend-api/hazelnuts/uploads/create",
    "x-openai-web-frontend": "core_web",
}
REQUIRED_HEADER_ENV = {
    "authorization": "CHATGPT_AUTH_TOKEN",
    "chatgpt-account-id": "CHATGPT_ACCOUNT_ID",
    "cookie": "CHATGPT_COOKIE",
    "oai-device-id": "CHATGPT_DEVICE_ID",
    "oai-session-id": "CHATGPT_SESSION_ID",
    "x-oai-is-client-observation": "CHATGPT_CLIENT_OBSERVATION",
}
FORM_FIELDS = {
    "apply_resolution": "true",
    "force_update": "true",
}
MAX_RESPONSE_CHARS = 16_384


@dataclass(frozen=True)
class UploadResult:
    status: int | None
    response: str
    error: str | None = None


def normalize_headers(values: Mapping[object, object]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for raw_name, raw_value in values.items():
        name = str(raw_name).strip().lower()
        value = str(raw_value)
        if not name or "\r" in value or "\n" in value:
            raise ValueError("header names and values must be non-empty and single-line")
        headers[name] = value
    return headers


def load_header_file(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read headers file {path}: {exc}") from exc
    if isinstance(data, dict) and isinstance(data.get("headers"), dict):
        data = data["headers"]
    if not isinstance(data, dict):
        raise ValueError("headers file must contain a JSON object")
    return normalize_headers(data)


def load_env_file(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read env file {path}: {exc}") from exc

    values: dict[str, str] = {}
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[7:].lstrip()
        if "=" not in stripped:
            raise ValueError(f"invalid env entry at {path}:{line_number}")
        name, value = stripped.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not name or not name.replace("_", "").isalnum() or name[0].isdigit():
            raise ValueError(f"invalid env variable name at {path}:{line_number}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[name] = value
    return values


def build_headers(headers_file: Path | None, env_file: Path | None) -> dict[str, str]:
    headers = dict(DEFAULT_HEADERS)
    if headers_file:
        headers.update(load_header_file(headers_file))
    env_values = load_env_file(env_file) if env_file else {}

    for header, environment_name in REQUIRED_HEADER_ENV.items():
        if header not in headers:
            value = os.environ.get(environment_name)
            if value is None:
                value = env_values.get(environment_name)
            if value:
                headers[header] = value

    authorization = headers.get("authorization")
    if authorization and not authorization.lower().startswith("bearer "):
        headers["authorization"] = f"Bearer {authorization}"

    missing = [
        f"{header} (set {environment_name}, --env-file, or provide it in --headers-file)"
        for header, environment_name in REQUIRED_HEADER_ENV.items()
        if not headers.get(header)
    ]
    if missing:
        raise ValueError("missing required upload headers: " + ", ".join(missing))

    headers.pop("content-type", None)
    headers.pop("content-length", None)
    return headers


def iter_zip_files(source: Path, recursive: bool) -> list[Path]:
    source = source.resolve()
    if source.is_file():
        if source.suffix.lower() != ".zip":
            raise ValueError(f"source file is not a ZIP: {source}")
        return [source]
    if not source.is_dir():
        raise ValueError(f"source is not a file or directory: {source}")

    candidates = source.rglob("*.zip") if recursive else source.glob("*.zip")
    return sorted(path for path in candidates if path.is_file() and not path.is_symlink())


def safe_filename(path: Path) -> str:
    return path.name.replace('"', "_").replace("\r", "_").replace("\n", "_")


def build_multipart_body(zip_path: Path, boundary: str) -> bytes:
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"file is not a valid ZIP: {zip_path}")

    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("ascii"))
    body.extend(
        (
            f'Content-Disposition: form-data; name="file"; filename="{safe_filename(zip_path)}"\r\n'
            "Content-Type: application/x-zip-compressed\r\n\r\n"
        ).encode("utf-8")
    )
    body.extend(zip_path.read_bytes())
    body.extend(b"\r\n")

    for name, value in FORM_FIELDS.items():
        body.extend(f"--{boundary}\r\n".encode("ascii"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii"))
        body.extend(value.encode("ascii"))
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("ascii"))
    return bytes(body)


def response_text(data: bytes) -> str:
    text = data.decode("utf-8", errors="replace")
    if len(text) > MAX_RESPONSE_CHARS:
        return text[:MAX_RESPONSE_CHARS] + "\n...[response truncated]"
    return text


def upload_zip(zip_path: Path, url: str, headers: Mapping[str, str], timeout: float) -> UploadResult:
    boundary = f"----PythonUploadBoundary{uuid.uuid4().hex}"
    body = build_multipart_body(zip_path, boundary)
    request_headers = dict(headers)
    request_headers["content-type"] = f"multipart/form-data; boundary={boundary}"
    request_headers["content-length"] = str(len(body))
    request = Request(url, data=body, headers=request_headers, method="POST")

    try:
        with urlopen(request, timeout=timeout) as response:
            return UploadResult(response.status, response_text(response.read()))
    except HTTPError as exc:
        return UploadResult(exc.code, response_text(exc.read()), f"HTTP {exc.code}")
    except URLError as exc:
        return UploadResult(None, "", f"network error: {exc.reason}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload ZIP files as binary multipart payloads.")
    parser.add_argument("--path", required=True, type=Path, help="A ZIP file or directory containing ZIP files.")
    parser.add_argument("--recursive", action="store_true", help="Search for ZIP files below the source directory.")
    parser.add_argument("--limit", type=int, default=1, help="Maximum files to upload; 0 means all (default: 1).")
    parser.add_argument("--start-after", help="Start after this ZIP filename in sorted order.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Upload endpoint URL.")
    parser.add_argument("--env-file", type=Path, help="Local .env file; defaults to .env when present.")
    parser.add_argument("--headers-file", type=Path, help="JSON file with request headers; keep it outside the repository.")
    parser.add_argument("--timeout", type=float, default=120.0, help="Per-upload timeout in seconds.")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY_SECONDS, help="Seconds to wait between uploads (default: 1).")
    parser.add_argument("--dry-run", action="store_true", help="List selected ZIPs without reading credentials or making requests.")
    parser.add_argument("--show-response", action="store_true", help="Print the response body for each upload.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.limit < 0:
        print("ERROR: --limit cannot be negative", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("ERROR: --timeout must be greater than zero", file=sys.stderr)
        return 2
    if args.delay < 0:
        print("ERROR: --delay cannot be negative", file=sys.stderr)
        return 2

    try:
        files = iter_zip_files(args.path, args.recursive)
        if args.start_after:
            try:
                start_index = next(index for index, path in enumerate(files) if path.name == args.start_after)
            except StopIteration as exc:
                raise ValueError(f"ZIP filename not found: {args.start_after}") from exc
            files = files[start_index + 1 :]
        selected = files if args.limit == 0 else files[: args.limit]
        if not selected:
            raise ValueError(f"no ZIP files found in: {args.path.resolve()}")

        if args.dry_run:
            for path in selected:
                print(f"would upload {path}")
            return 0

        headers_file = args.headers_file.resolve() if args.headers_file else None
        env_file = args.env_file.resolve() if args.env_file else Path(".env").resolve()
        if not env_file.is_file() and args.env_file:
            raise ValueError(f"env file does not exist: {env_file}")
        headers = build_headers(headers_file, env_file if env_file.is_file() else None)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    failed = False
    for index, path in enumerate(selected):
        try:
            result = upload_zip(path, args.url, headers, args.timeout)
        except (OSError, ValueError) as exc:
            print(f"{path.name}: {exc}", file=sys.stderr)
            failed = True
        else:
            if result.error:
                print(f"{path.name}: {result.error}", file=sys.stderr)
                failed = True
            elif result.status is None or not 200 <= result.status < 300:
                print(f"{path.name}: unexpected HTTP status {result.status}", file=sys.stderr)
                failed = True
            else:
                print(f"{path.name}: uploaded (HTTP {result.status})")

            if args.show_response and result.response:
                print(result.response)

        if index + 1 < len(selected) and args.delay:
            time.sleep(args.delay)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())