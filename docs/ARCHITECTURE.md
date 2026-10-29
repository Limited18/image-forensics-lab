# System Architecture — Image Forensics Lab

## Architecture overview

```text
User / Browser
      |
      v
Flask Web Interface (upload + results pages)
      |
      v
Input Validation
  - extension allow-list
  - upload size limit
  - image decoder verification
      |
      +-------------------+--------------------+
      |                   |                    |
      v                   v                    v
Metadata Analyzer    SHA-256 Module       Basic File Checks
(Pillow / EXIF)      (hashlib)             (header signature)
      |
      +------------------------+
                               |
                               v
                     JPEG ELA Module
                 (recompress + pixel diff)
                               |
                               v
                      Findings Aggregator
                               |
                  +------------+-------------+
                  |                          |
                  v                          v
             Results Page              PDF Generator
             (Flask/Jinja)             (ReportLab)
```

## Main modules
- **Web layer (`app.py`, `templates/`)**: accepts an image, displays results, and serves the PDF download.
- **Validation layer**: checks allowed extensions, upload size, and whether Pillow can decode the file.
- **Metadata analyzer**: extracts image dimensions, format, mode, and available EXIF fields.
- **Integrity module**: calculates SHA-256 over the exact uploaded bytes.
- **ELA module**: for JPEG images, recompresses at a documented quality and generates an amplified difference image.
- **Basic file checks**: compares common file signatures with the extension. It is not a full file-structure scanner.
- **Report generator**: writes a PDF containing file properties, findings, metadata, and caveats.

## Data flow and evidence handling
The uploaded original is retained unchanged during analysis. The ELA visualization is a separate derived output. A hash is calculated from the uploaded original bytes. The app stores uploaded files, generated images, and reports locally; delete these artifacts after testing if they are no longer needed.

## Limitations
The application performs preliminary triage. ELA anomalies do not prove manipulation, metadata can be absent or modified, and a hash only identifies byte-level content when compared with a trusted reference. This prototype is not a certified forensic suite and does not implement a complete chain-of-custody system.
