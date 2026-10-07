#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def render(pdf: str, out_dir: Path, dpi: int, timeout_seconds: float) -> dict:
    script = Path(__file__).with_name("render_pdf.py")
    proc = subprocess.run(
        [sys.executable, str(script), pdf, str(out_dir), "--dpi", str(dpi), "--subprocess-timeout", str(timeout_seconds)],
        text=True,
        capture_output=True,
        timeout=timeout_seconds + 30.0,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout.strip() or proc.stderr.strip() or "render failed")
    return json.loads(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render two PDFs with the same backend settings and compare pixels.")
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--max-component-change-ratio", type=float, default=0.0)
    parser.add_argument("--json-output")
    parser.add_argument("--subprocess-timeout", type=float, default=120.0, help="Timeout in seconds for each renderer process")
    args = parser.parse_args()
    if args.subprocess_timeout <= 0:
        print(json.dumps({"status":"error","error":"--subprocess-timeout must be > 0"}, indent=2))
        return 2
    try:
        from PIL import Image, ImageChops
    except ImportError:
        print(json.dumps({"status":"blocked","error":"Pillow is required for pixel comparison"}, indent=2))
        return 2

    with tempfile.TemporaryDirectory(prefix="pdf-compare-") as tmp:
        root = Path(tmp)
        try:
            a = render(args.before, root / "a", args.dpi, args.subprocess_timeout)
            b = render(args.after, root / "b", args.dpi, args.subprocess_timeout)
        except Exception as exc:
            print(json.dumps({"status":"error","error":str(exc)}, indent=2))
            return 1
        afiles = [Path(p) for p in a["files"]]
        bfiles = [Path(p) for p in b["files"]]
        pages = []
        status = "pass"
        if len(afiles) != len(bfiles):
            status = "fail"
        for idx in range(min(len(afiles), len(bfiles))):
            ia = Image.open(afiles[idx]).convert("RGB")
            ib = Image.open(bfiles[idx]).convert("RGB")
            if ia.size != ib.size:
                pages.append({"page":idx+1,"status":"fail","reason":"dimension-mismatch","before_size":ia.size,"after_size":ib.size})
                status = "fail"
                continue
            diff = ImageChops.difference(ia, ib)
            hist = diff.histogram()
            total_components = ia.size[0] * ia.size[1] * 3
            zero_components = hist[0] + hist[256] + hist[512]
            ratio = (total_components - zero_components) / total_components if total_components else 0.0
            page_status = "pass" if ratio <= args.max_component_change_ratio else "fail"
            if page_status == "fail":
                status = "fail"
            pages.append({"page":idx+1,"status":page_status,"component_change_ratio":ratio})
        result = {
            "schema_version":1,
            "status":status,
            "dpi":args.dpi,
            "page_count_before":len(afiles),
            "page_count_after":len(bfiles),
            "max_component_change_ratio":args.max_component_change_ratio,
            "pages":pages,
        }
        text = json.dumps(result, indent=2, sort_keys=True)
        print(text)
        if args.json_output:
            Path(args.json_output).write_text(text + "\n", encoding="utf-8")
        return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
