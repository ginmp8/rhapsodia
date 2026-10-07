import ast
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_script(name, *args, cwd=None):
    cmd = [sys.executable, str(SCRIPTS / name), *map(str, args)]
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=180)


def make_pdf(path: Path, texts):
    c = canvas.Canvas(str(path), pagesize=letter)
    for text in texts:
        c.drawString(72, 720, text)
        c.showPage()
    c.save()


def make_table_pdf(path: Path):
    doc = SimpleDocTemplate(str(path), pagesize=letter)
    data = [["Name", "Value"], ["Alpha", "10"], ["Beta", "20"]]
    table = Table(data)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ]))
    doc.build([table])


def make_image_only_pdf(path: Path):
    img = Image.new("RGB", (1600, 500), "white")
    draw = ImageDraw.Draw(img)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 100)
    draw.text((80, 160), "HELLO OCR", fill="black", font=font)
    img.save(str(path), "PDF", resolution=150.0)


class PdfEditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_merge_preserves_input_order(self):
        a = self.d / "a.pdf"
        b = self.d / "b.pdf"
        out = self.d / "merged.pdf"
        make_pdf(a, ["A"])
        make_pdf(b, ["B"])
        r = run_script("pdf_edit.py", "merge", a, b, "-o", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        reader = PdfReader(str(out))
        self.assertEqual(len(reader.pages), 2)
        self.assertIn("A", reader.pages[0].extract_text())
        self.assertIn("B", reader.pages[1].extract_text())

    def test_split_creates_one_output_per_page(self):
        src = self.d / "source.pdf"
        out_dir = self.d / "split"
        make_pdf(src, ["ONE", "TWO", "THREE"])
        r = run_script("pdf_edit.py", "split", src, "--out_dir", out_dir)
        self.assertEqual(r.returncode, 0, r.stderr)
        outputs = sorted(out_dir.glob("*.pdf"))
        self.assertEqual(len(outputs), 3)
        self.assertIn("ONE", PdfReader(str(outputs[0])).pages[0].extract_text())
        self.assertIn("THREE", PdfReader(str(outputs[2])).pages[0].extract_text())

    def test_select_extracts_requested_pages_in_requested_order(self):
        src = self.d / "source.pdf"
        out = self.d / "selected.pdf"
        make_pdf(src, ["ONE", "TWO", "THREE"])
        r = run_script("pdf_edit.py", "select", src, "--pages", "3,1", "-o", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        reader = PdfReader(str(out))
        self.assertEqual(len(reader.pages), 2)
        self.assertIn("THREE", reader.pages[0].extract_text())
        self.assertIn("ONE", reader.pages[1].extract_text())

    def test_rotate_sets_rotation_on_target_page_only(self):
        src = self.d / "source.pdf"
        out = self.d / "rotated.pdf"
        make_pdf(src, ["ONE", "TWO"])
        r = run_script("pdf_edit.py", "rotate", src, "--angle", "90", "--pages", "2", "-o", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        reader = PdfReader(str(out))
        self.assertEqual(int(reader.pages[0].get("/Rotate", 0)), 0)
        self.assertEqual(int(reader.pages[1].get("/Rotate", 0)), 90)

    def test_crop_changes_cropbox_without_changing_mediabox(self):
        src = self.d / "source.pdf"
        out = self.d / "cropped.pdf"
        make_pdf(src, ["ONE"])
        before = PdfReader(str(src)).pages[0]
        before_media = tuple(map(float, before.mediabox))
        r = run_script("pdf_edit.py", "crop", src, "--inset", "10pt", "-o", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        page = PdfReader(str(out)).pages[0]
        self.assertEqual(tuple(map(float, page.mediabox)), before_media)
        self.assertAlmostEqual(float(page.cropbox.left), before_media[0] + 10, places=3)
        self.assertAlmostEqual(float(page.cropbox.bottom), before_media[1] + 10, places=3)

    def test_encrypt_and_decrypt_round_trip(self):
        src = self.d / "source.pdf"
        enc = self.d / "encrypted.pdf"
        dec = self.d / "decrypted.pdf"
        make_pdf(src, ["SECRET DOC"])
        password_file = self.d / "password.txt"
        password_file.write_text("test-pass\n", encoding="utf-8")
        r1 = run_script("pdf_edit.py", "encrypt", src, "-o", enc, "--user-password-file", password_file)
        self.assertEqual(r1.returncode, 0, r1.stderr)
        encrypted = PdfReader(str(enc))
        self.assertTrue(encrypted.is_encrypted)
        r2 = run_script("pdf_edit.py", "decrypt", enc, "-o", dec, "--password-file", password_file)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        reader = PdfReader(str(dec))
        self.assertFalse(reader.is_encrypted)
        self.assertIn("SECRET DOC", reader.pages[0].extract_text())

    def test_watermark_overlays_content(self):
        src = self.d / "source.pdf"
        wm = self.d / "wm.pdf"
        out = self.d / "watermarked.pdf"
        make_pdf(src, ["BODY"])
        make_pdf(wm, ["WATERMARK"])
        r = run_script("pdf_edit.py", "watermark", src, "--watermark", wm, "-o", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        text = PdfReader(str(out)).pages[0].extract_text()
        self.assertIn("BODY", text)
        self.assertIn("WATERMARK", text)


class PdfExtractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_text_extracts_native_text(self):
        src = self.d / "source.pdf"
        out = self.d / "text.txt"
        make_pdf(src, ["EXTRACT ME"])
        r = run_script("pdf_extract.py", "text", src, "--method", "pdfplumber", "--out", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("EXTRACT ME", out.read_text(encoding="utf-8"))

    def test_images_extracts_embedded_image(self):
        src = self.d / "image.pdf"
        out_dir = self.d / "images"
        make_image_only_pdf(src)
        r = run_script("pdf_extract.py", "images", src, "--out_dir", out_dir)
        self.assertEqual(r.returncode, 0, r.stderr)
        outputs = [p for p in out_dir.iterdir() if p.is_file()]
        self.assertTrue(outputs, f"no image output; stdout={r.stdout!r} stderr={r.stderr!r}")

    def test_tables_extracts_detected_table_to_json(self):
        src = self.d / "table.pdf"
        out_dir = self.d / "tables"
        make_table_pdf(src)
        r = run_script("pdf_extract.py", "tables", src, "--out_dir", out_dir, "--format", "json")
        self.assertEqual(r.returncode, 0, r.stderr)
        json_files = list(out_dir.glob("*.json"))
        self.assertTrue(json_files, f"no table json produced; stdout={r.stdout!r} stderr={r.stderr!r}")
        payload = json.loads(json_files[0].read_text(encoding="utf-8"))
        serialized = json.dumps(payload)
        self.assertIn("Alpha", serialized)
        self.assertIn("20", serialized)


class OcrAndRedactionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fallback_ocr_creates_searchable_pdf(self):
        src = self.d / "scan.pdf"
        out = self.d / "searchable.pdf"
        make_image_only_pdf(src)
        r = run_script("ocr_pdf.py", src, "-o", out, "--lang", "eng", "--fallback", "--dpi", "200")
        self.assertEqual(r.returncode, 0, r.stderr)
        text = "\n".join((page.extract_text() or "") for page in PdfReader(str(out)).pages)
        self.assertIn("HELLO OCR", text.upper())

    def test_true_redaction_removes_underlying_text(self):
        src = self.d / "source.pdf"
        out = self.d / "redacted.pdf"
        make_pdf(src, ["PUBLIC TOP SECRET DATA"])
        r = run_script("pdf_redact.py", "text", src, out, "--text", "TOP SECRET")
        self.assertEqual(r.returncode, 0, r.stderr)
        text = "\n".join((page.extract_text() or "") for page in PdfReader(str(out)).pages)
        self.assertNotIn("TOP SECRET", text)
        self.assertIn("PUBLIC", text)


class CapabilityInventoryTests(unittest.TestCase):
    def test_ocr_fallback_capability_accounts_for_tesseract_and_renderer(self):
        r = run_script("inspect_capabilities.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        payload = json.loads(r.stdout)
        self.assertIn("tesseract", payload["executables"])
        expected = bool(payload["executables"].get("ocrmypdf")) or (
            bool(payload["executables"].get("tesseract"))
            and bool(payload["executables"].get("pdftoppm"))
        )
        self.assertEqual(payload["capabilities"]["ocr_searchable_pdf"], expected)


class CapabilityCoverageTests(unittest.TestCase):
    def test_advertised_capabilities_have_executable_path_or_tested_example(self):
        r = run_script("validate_capability_coverage.py", "--root", ROOT, "--json")
        self.assertEqual(r.returncode, 0, r.stderr or r.stdout)
        payload = json.loads(r.stdout)
        self.assertEqual(payload["status"], "pass")
        required = {"merge", "split", "rotate", "crop", "watermark", "ocr", "text", "tables", "images", "redaction"}
        self.assertTrue(required.issubset(set(payload["covered_operations"])))


class SecurityRegressionTests(unittest.TestCase):
    def test_subprocess_calls_are_bounded_and_never_use_shell(self):
        for path in SCRIPTS.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if not isinstance(node.func.value, ast.Name) or node.func.value.id != "subprocess":
                    continue
                if node.func.attr not in {"run", "call", "check_call", "check_output"}:
                    continue
                keywords = {kw.arg: kw.value for kw in node.keywords if kw.arg}
                self.assertIn("timeout", keywords, f"unbounded subprocess call in {path}:{node.lineno}")
                shell = keywords.get("shell")
                if isinstance(shell, ast.Constant):
                    self.assertFalse(shell.value, f"shell=True in {path}:{node.lineno}")

    def test_no_literal_password_cli_or_auto_install_instruction(self):
        inspected = list(SCRIPTS.glob("*.py")) + [ROOT / "SKILL.md"] + list((ROOT / "references").glob("*.md"))
        unsafe_flag = re.compile(r"--(?:user_|owner_)?password(?=[\s'\"=]|$)")
        for path in inspected:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(unsafe_flag.search(text), f"literal password CLI flag remains in {path}")
            self.assertNotIn("python -m pip install", text, f"automatic-install suggestion remains in {path}")


if __name__ == "__main__":
    unittest.main()
