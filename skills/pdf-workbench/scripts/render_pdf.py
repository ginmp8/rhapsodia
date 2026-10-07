#!/usr/bin/env python3
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _render_pdfium(pdf: Path, out_dir: Path, dpi: int, first: int, last: int | None) -> list[str]:
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(pdf))
    end = min(len(doc), last if last is not None else len(doc))
    files = []
    scale = dpi / 72.0
    for idx in range(first - 1, end):
        page = doc[idx]
        image = page.render(scale=scale).to_pil()
        target = out_dir / f"page-{idx + 1:04d}.png"
        image.save(target, "PNG")
        files.append(str(target))
    return files


def _render_pdftoppm(pdf: Path, out_dir: Path, dpi: int, first: int, last: int | None, executable: str, timeout_seconds: float) -> list[str]:
    prefix = out_dir / "page"
    cmd = [executable, "-png", "-r", str(dpi), "-f", str(first)]
    if last is not None:
        cmd += ["-l", str(last)]
    cmd += [str(pdf), str(prefix)]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout_seconds)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "pdftoppm failed")
    files = sorted(str(p) for p in out_dir.glob("page-*.png"))
    if not files:
        raise RuntimeError("pdftoppm produced no PNG files")
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG using an available portable backend.")
    parser.add_argument("pdf")
    parser.add_argument("out_dir")
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int)
    parser.add_argument("--backend", choices=["auto", "pdfium", "pdftoppm"], default="auto")
    parser.add_argument("--subprocess-timeout", type=float, default=120.0, help="Timeout in seconds for the pdftoppm backend")
    args = parser.parse_args()
    pdf = Path(args.pdf)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if not pdf.is_file():
        print(json.dumps({"status":"error","error":"input file not found","file":str(pdf)}, indent=2))
        return 2
    if args.first < 1 or (args.last is not None and args.last < args.first):
        print(json.dumps({"status":"error","error":"invalid page range"}, indent=2))
        return 2

    if args.subprocess_timeout <= 0:
        print(json.dumps({"status":"error","error":"--subprocess-timeout must be > 0"}, indent=2))
        return 2

    pdfium_available = importlib.util.find_spec("pypdfium2") is not None
    pdftoppm = shutil.which("pdftoppm")
    poppler_available = pdftoppm is not None
    backend = args.backend
    if backend == "auto":
        backend = "pdfium" if pdfium_available else "pdftoppm" if poppler_available else ""
    if backend == "pdfium" and not pdfium_available:
        print(json.dumps({"status":"blocked","error":"pypdfium2 is not available"}, indent=2))
        return 2
    if backend == "pdftoppm" and not poppler_available:
        print(json.dumps({"status":"blocked","error":"pdftoppm is not available"}, indent=2))
        return 2
    if not backend:
        print(json.dumps({"status":"blocked","error":"no supported renderer is available; this helper does not install or download dependencies automatically"}, indent=2))
        return 2

    try:
        files = _render_pdfium(pdf, out_dir, args.dpi, args.first, args.last) if backend == "pdfium" else _render_pdftoppm(pdf, out_dir, args.dpi, args.first, args.last, pdftoppm, args.subprocess_timeout)
    except Exception as exc:
        print(json.dumps({"status":"error","backend":backend,"error":f"{type(exc).__name__}: {exc}"}, indent=2))
        return 1
    print(json.dumps({"status":"ok","backend":backend,"dpi":args.dpi,"pages":len(files),"files":files}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
