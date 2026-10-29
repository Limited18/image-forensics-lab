# Test Plan and Test Cases

Install dependencies with `pip install -r requirements.txt`, then run the automated tests with:

```bash
python -m unittest discover -s tests -v
```

## Manual test cases

| ID | Scenario | Steps | Expected result |
|---|---|---|---|
| TC-01 | Open landing page | Visit `http://127.0.0.1:5000` | Upload form and feature summary appear |
| TC-02 | No file selected | Submit without selecting a file | Clear validation message |
| TC-03 | Unsupported extension | Upload a `.txt` file | Request rejected with supported-format message |
| TC-04 | Valid PNG | Upload a valid PNG | Properties and SHA-256 displayed; ELA skipped |
| TC-05 | Valid JPEG | Upload a valid JPEG | Properties, SHA-256, ELA and report available |
| TC-06 | Missing EXIF | Upload image without EXIF | App states metadata is unavailable |
| TC-07 | Invalid image bytes | Give image extension to non-image bytes | File rejected as invalid/corrupted |
| TC-08 | PDF download | Click download report after analysis | PDF downloads with summary/findings/limitations |
| TC-09 | Repeat hash | Analyze same file twice | SHA-256 values match |
| TC-10 | Modified file | Change bytes and analyze again | SHA-256 normally differs |
| TC-11 | Large upload | Upload file above 12 MB | Request rejected |
| TC-12 | ELA interpretation | Compare original and edited JPEG outputs | Visualization generated with cautious interpretation |

## Automated test coverage
The test suite covers landing page rendering, unsupported extension handling, corrupt image rejection, PNG analysis/PDF download, and JPEG ELA output. Also open a generated PDF once manually to verify its layout.

## Reporting results
Record actual Pass/Fail results and note the browser, operating system, Python version, and installed package versions. Do not claim detection accuracy unless a labelled benchmark and reproducible evaluation have been completed.
