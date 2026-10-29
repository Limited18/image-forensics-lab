import os
import uuid
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, render_template, request, send_file, abort, url_for
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags, ImageChops, ImageEnhance, UnidentifiedImageError
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
GENERATED_DIR = BASE_DIR / "static" / "generated"
REPORT_DIR = BASE_DIR / "reports"
for folder in (UPLOAD_DIR, GENERATED_DIR, REPORT_DIR):
    folder.mkdir(parents=True, exist_ok=True)

MAX_FILE_BYTES = 12 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_BYTES
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_exif(image):
    result = {}
    try:
        for key, value in image.getexif().items():
            name = ExifTags.TAGS.get(key, str(key))
            if isinstance(value, bytes):
                value = f"<binary value: {len(value)} bytes>"
            result[name] = str(value)[:300]
    except Exception as exc:
        result["EXIF note"] = f"Could not read EXIF: {type(exc).__name__}"
    return result


def inspect_file_structure(path: Path, file_size: int):
    """Basic header triage only; this is not a full embedded-payload scanner."""
    suffix = path.suffix.lower()
    head = path.read_bytes()[:32]
    signatures = {
        ".jpg": head.startswith(b"\xff\xd8\xff"),
        ".jpeg": head.startswith(b"\xff\xd8\xff"),
        ".png": head.startswith(b"\x89PNG\r\n\x1a\n"),
        ".tif": head[:4] in (b"II*\x00", b"MM\x00*"),
        ".tiff": head[:4] in (b"II*\x00", b"MM\x00*"),
        ".bmp": head.startswith(b"BM"),
        ".webp": len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP",
    }
    findings = []
    if suffix in signatures and not signatures[suffix]:
        findings.append("File extension and header signature may not match.")
    if file_size == 0:
        findings.append("File is empty.")
    if not findings:
        findings.append("No issue found by the basic header checks. This is not a full forensic validation.")
    return findings


def make_ela(source_path: Path, output_path: Path, quality=90):
    """Generate an ELA-style recompression difference visualization for JPEG only."""
    with Image.open(source_path) as original:
        if original.format != "JPEG":
            return None, "ELA is available only for JPEG images in this version."
        rgb = original.convert("RGB")
        temp_path = output_path.with_name(output_path.stem + "_recompressed.jpg")
        rgb.save(temp_path, "JPEG", quality=quality)
        with Image.open(temp_path) as recompressed:
            difference = ImageChops.difference(rgb, recompressed.convert("RGB"))
            extrema = difference.getextrema()
            max_diff = max((pair[1] for pair in extrema), default=1)
            scale = 1 if max_diff == 0 else min(20, 255 / max_diff)
            ImageEnhance.Brightness(difference).enhance(scale).save(output_path, "PNG")
        temp_path.unlink(missing_ok=True)
    return output_path.name, f"ELA-style difference image generated after JPEG recompression at quality {quality}. Bright regions are clues for review, not proof of editing."


def build_pdf(report_path: Path, result: dict):
    styles = getSampleStyleSheet()
    story = [Paragraph("Digital Image Forensics - Analysis Report", styles["Title"]),
             Spacer(1, 4 * mm),
             Paragraph(f"Generated: {result['analysis_time']}", styles["Normal"]),
             Spacer(1, 4 * mm), Paragraph("File Summary", styles["Heading2"])]
    rows = [["Property", "Value"], ["Original filename", result["original_name"]],
            ["Detected format", result["format"]], ["Dimensions", result["dimensions"]],
            ["File size", f"{result['file_size']:,} bytes"], ["SHA-256", result["sha256"]]]
    table = Table(rows, colWidths=[42 * mm, 125 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7edf5")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("WORDWRAP", (0, 0), (-1, -1), True),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]))
    story.extend([table, Spacer(1, 5 * mm), Paragraph("Analysis Findings", styles["Heading2"])])
    for item in result["findings"]:
        story.extend([Paragraph("• " + item, styles["BodyText"]), Spacer(1, 1.5 * mm)])
    story.extend([Spacer(1, 3 * mm), Paragraph("Metadata", styles["Heading2"])])
    if result["metadata"]:
        meta_rows = [["Field", "Value"]]
        meta_rows.extend([[str(k)[:80], str(v)[:250]] for k, v in list(result["metadata"].items())[:40]])
        meta_table = Table(meta_rows, colWidths=[42 * mm, 125 * mm], repeatRows=1)
        meta_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7edf5")),
                                        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                        ("FONTSIZE", (0, 0), (-1, -1), 7)]))
        story.append(meta_table)
    else:
        story.append(Paragraph("No EXIF metadata was available or readable.", styles["BodyText"]))
    story.extend([Spacer(1, 6 * mm), Paragraph("Important limitations", styles["Heading2"]),
                  Paragraph("This report provides preliminary triage only. Metadata can be missing or altered. ELA may show differences caused by ordinary compression or editing and does not prove manipulation. SHA-256 identifies the exact file bytes but does not establish image authenticity or origin. Preserve the original and seek expert review for consequential decisions.", styles["BodyText"])])
    SimpleDocTemplate(str(report_path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                      topMargin=16*mm, bottomMargin=16*mm).build(story)


@app.errorhandler(413)
def too_large(_error):
    return render_template("index.html", error="File is too large. Maximum upload size is 12 MB."), 413


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    uploaded = request.files.get("image")
    if not uploaded or not uploaded.filename:
        return render_template("index.html", error="Choose an image file first."), 400
    original_name = secure_filename(uploaded.filename) or "uploaded_image"
    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return render_template("index.html", error="Unsupported extension. Use JPG, JPEG, PNG, TIFF, BMP, or WEBP."), 400
    unique = uuid.uuid4().hex
    saved_path = UPLOAD_DIR / f"{unique}{suffix}"
    uploaded.save(saved_path)
    file_size = saved_path.stat().st_size
    if file_size == 0 or file_size > MAX_FILE_BYTES:
        saved_path.unlink(missing_ok=True)
        return render_template("index.html", error="The file is empty or exceeds the 12 MB limit."), 400
    try:
        with Image.open(saved_path) as image:
            image.verify()
        with Image.open(saved_path) as image:
            image_format = image.format or suffix.lstrip(".").upper()
            dimensions = f"{image.width} × {image.height}"
            mode = image.mode
            metadata = get_exif(image)
    except (UnidentifiedImageError, OSError, ValueError):
        saved_path.unlink(missing_ok=True)
        return render_template("index.html", error="The file could not be decoded as a valid supported image."), 400
    digest = sha256_file(saved_path)
    findings = inspect_file_structure(saved_path, file_size)
    findings.append(f"SHA-256 calculated for the uploaded file: {digest}.")
    if metadata:
        findings.append(f"Metadata reader found {len(metadata)} EXIF field(s). Their presence does not verify authenticity.")
    else:
        findings.append("No EXIF metadata was available or readable; this is common and does not by itself indicate tampering.")
    ela_filename = None
    ela_note = "ELA was not generated."
    if image_format.upper() in {"JPEG", "JPG"} or suffix in {".jpg", ".jpeg"}:
        try:
            ela_filename, ela_note = make_ela(saved_path, GENERATED_DIR / f"{unique}_ela.png")
            findings.append(ela_note)
        except Exception as exc:
            ela_note = f"ELA generation failed safely ({type(exc).__name__})."
            findings.append(ela_note)
    else:
        findings.append("ELA was skipped because the uploaded image is not JPEG.")
    analysis_time = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    result = {"id": unique, "original_name": original_name, "format": image_format,
              "dimensions": dimensions, "mode": mode, "file_size": file_size, "sha256": digest,
              "metadata": metadata, "findings": findings, "ela_filename": ela_filename,
              "ela_note": ela_note, "analysis_time": analysis_time}
    (REPORT_DIR / f"{unique}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    build_pdf(REPORT_DIR / f"{unique}.pdf", result)
    ela_url = url_for("static", filename=f"generated/{ela_filename}") if ela_filename else None
    return render_template("results.html", result=result, ela_url=ela_url,
                           report_url=url_for("download_report", report_id=unique))


@app.route("/report/<report_id>", methods=["GET"])
def download_report(report_id):
    if not report_id.isalnum() or len(report_id) != 32:
        abort(404)
    path = REPORT_DIR / f"{report_id}.pdf"
    if not path.exists():
        abort(404)
    return send_file(path, as_attachment=True,
                     download_name=f"image_forensics_report_{report_id[:8]}.pdf",
                     mimetype="application/pdf")


if __name__ == "__main__":
    # Local development only. Do not expose Flask's built-in server publicly.
    app.run(debug=False, host="127.0.0.1", port=5000)
