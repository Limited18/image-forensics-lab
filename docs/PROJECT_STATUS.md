# Project status

The initial source files, Flask templates, dependencies, architecture notes, test cases, and college report outline have been committed to the repository.

## Current implementation status
- Metadata and image-property inspection: implemented in `app.py`
- SHA-256 of uploaded file: implemented
- JPEG ELA-style difference output: implemented
- PDF report generation: implemented
- Manual and automated test definitions: included
- Live runtime validation: must still be run on a machine with dependencies installed
- Editable DOCX report: download separately from the ChatGPT conversation and upload via GitHub's web interface if desired

## Run locally
See `README.md`. Install dependencies first, then run:
```bash
python -m unittest discover -s tests -v
python app.py
```

Do not treat planned tests as passed until the commands have been executed and results recorded.
