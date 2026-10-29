# College Mini-Project Report

**Project title:** Design and Development of a Digital Image Forensics Tool  
**Student name:** ____________________  
**PRN / Roll No.:** ____________________  
**Department:** Computer Engineering  
**College:** ____________________  
**Project guide:** ____________________  
**Academic year:** ____________________

> Use this Markdown document as the source outline for the report. The editable Word report is available separately in the ChatGPT conversation.

## Acknowledgment
We express our sincere gratitude to our project guide for guidance, encouragement, and useful suggestions during the planning and development of this mini-project. We are also thankful to the Head of Department and faculty members for providing the academic support and resources required for the work. We acknowledge the documentation and research behind the open-source tools used in the project.

## Abstract
This project develops a web application for preliminary forensic examination of digital images. The tool provides image metadata inspection, SHA-256 hashing, JPEG Error Level Analysis (ELA-style recompression visualization), basic file-header checks, and PDF report generation. It brings common checks into one user-friendly workflow. Metadata and ELA are indicators only: metadata may be missing or modified, and compression differences do not prove manipulation. SHA-256 helps verify byte-level identity against a trusted reference; it does not establish the truth or origin of the image.

## 1. Introduction
Digital images are widely shared and may be cropped, composited, retouched, resized, or recompressed. Image forensics examines technical properties and traces that may help explain a file's history. The proposed application combines accessible checks in one interface for educational and preliminary analysis.

### 1.1 Introduction
Manual image examination can require separate utilities for metadata extraction, hash calculation, and compression-difference visualization. This project provides a unified interface to improve accessibility and consistency.

### 1.2 Title
Design and Development of a Digital Image Forensics Tool.

### 1.3 Objectives
- Accept and validate image uploads.
- Extract image properties and available EXIF metadata.
- Generate ELA-style visualization for JPEG files.
- Calculate a SHA-256 hash from the uploaded file's exact bytes.
- Display basic file-header consistency observations.
- Generate a downloadable PDF report with findings and limitations.

## 2. Literature Survey
Metadata analysis can provide context about the device or software that wrote the file, but these fields can be removed or changed. JPEG compression analysis, including ELA, can highlight differences that deserve closer review, but output depends on image content and compression history. Cryptographic hashes provide reproducible identifiers for exact byte sequences, supporting integrity checks when compared with a trusted reference.

## 3. Methodological Details

### 3.1 Methodology
The user uploads an image; the application validates the extension and size and confirms that a decoder can open it. The tool reads image properties and EXIF fields, calculates SHA-256, checks selected file signatures, and generates ELA output when the decoded format is JPEG. The report generator combines the observations in PDF format.

### 3.2 Dataset Description
For evaluation, use self-created or appropriately licensed images. Include original images, JPEGs recompressed at different quality settings, and controlled edited derivatives such as cropped, resized, or text-overlaid copies. Keep a manifest of the original source and transformations. Do not claim detection accuracy without a properly labelled test dataset and recorded experiments.

### 3.3 Implementation
The application uses Python and Flask for routing, Pillow for image decoding and EXIF access, the Python standard-library hashing module for SHA-256, and ReportLab for PDF creation. HTML and CSS provide the interface. The application enforces a 12 MB upload limit and processes files locally by default.

## 4. Result and Discussion
Expected outputs include image format, dimensions, color mode, file size, available EXIF fields, a SHA-256 digest, basic file-header observations, an ELA visualization for JPEG files, and a downloadable PDF. Tests should include valid JPEG/PNG files, unsupported extensions, malformed images, missing EXIF data, repeat hashing, changed file bytes, and report downloads. Record actual test results after running the application; do not present planned tests as completed results.

### 4.1 Result and Discussion
The application consolidates preliminary checks and explains each result. ELA differences require expert interpretation; metadata absence does not imply tampering; and a hash provides byte-level comparison only.

### 4.2 Conclusion
The project demonstrates a practical workflow for preliminary digital image examination with metadata review, ELA, SHA-256, basic validation, and PDF reporting. It is an educational prototype rather than a certified forensic suite.

### 4.3 Future Scope
Future work may add copy-move detection, splicing detection, batch processing, evidence notes, audit logs, richer file-format analysis, and ML-based detection evaluated against a documented benchmark.

## 5. References
1. H. Farid, “Image Forgery Detection,” *IEEE Signal Processing Magazine*, vol. 26, no. 2, pp. 16–25, 2009.
2. A. C. Popescu and H. Farid, “Exposing Digital Forgeries by Detecting Traces of Resampling,” *IEEE Transactions on Signal Processing*, vol. 53, no. 2, pp. 758–767, 2005.
3. NIST, *Secure Hash Standard (SHS)*, FIPS PUB 180-4. https://csrc.nist.gov/pubs/fips/180-4/upd1/final
4. Python documentation, hashlib. https://docs.python.org/3/library/hashlib.html
5. Pillow documentation. https://pillow.readthedocs.io/
6. Flask documentation. https://flask.palletsprojects.com/
7. ReportLab documentation. https://www.reportlab.com/docs/reportlab-userguide.pdf
8. JPEG standards and information. https://jpeg.org/
