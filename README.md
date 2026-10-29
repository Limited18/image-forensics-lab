# Image Forensics Lab

A student mini-project: a local Flask web application for preliminary digital image examination.

## Features
- Metadata and available EXIF extraction
- SHA-256 hashing of the original uploaded file
- JPEG Error Level Analysis (ELA-style recompression difference visualization)
- Basic file extension/header consistency checks
- Downloadable PDF analysis report
- Responsive dashboard and manual/automated test documentation

## Requirements
Python 3.10 or newer recommended.

## Run on Windows
1. Download or clone this repository.
2. Open Command Prompt in the project folder.
3. Run:
   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
4. Open http://127.0.0.1:5000 in your browser.

You can also run `run_windows.bat` to create the virtual environment, install dependencies, and start the application.

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then visit http://127.0.0.1:5000.

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Project structure
- `app.py` — Flask app and analysis workflow
- `templates/` — upload and results views
- `static/css/style.css` — UI styling
- `tests/test_app.py` — automated tests
- `docs/ARCHITECTURE.md` — architecture and data flow
- `docs/TEST_CASES.md` — test plan and manual scenarios
- `Digital_Image_Forensics_Mini_Project_Report.docx` — editable college report

## Important limitations
This is a student prototype for preliminary triage, not a certified forensic suite. ELA differences are not proof of manipulation. Metadata may be missing or edited. SHA-256 identifies the exact file bytes and should be compared with a trusted reference value; it does not establish image authenticity or origin. Keep original evidence unchanged and document handling when used in a formal context.

## Local file storage and security
The application stores uploaded files under `uploads/`, derived ELA output under `static/generated/`, and PDF/JSON reports under `reports/`. Delete files when they are no longer needed. The app binds to `127.0.0.1` by default and should not be exposed to the public internet without additional security review. Do not commit private evidence images or generated reports.
