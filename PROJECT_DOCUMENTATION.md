# AUTOMATED LABEL VERIFICATION SYSTEM - COMPLETE PROJECT DOCUMENTATION

## PROJECT OVERVIEW

The Automated Label Verification System is a Python-based application that extracts information from job card PDFs and label PDFs, then validates whether the label information matches the job card requirements. The system uses OCR (Optical Character Recognition) to extract text from label images and compares them against expected values from the job card.

**Key Features:**
- Extracts job card data from PDF files using regex patterns
- Detects and crops label images from PDF pages
- Uses OCR (OCR.Space API) to extract text from label images
- Validates label content against job card requirements
- Generates PDF validation reports
- Provides a Streamlit web interface for easy use
- Outputs JSON files with extracted and validation data

**Technologies Used:**
- Python 3.x
- pdfplumber: PDF text extraction
- PyMuPDF (fitz): PDF to image conversion
- OpenCV (cv2): Image processing and contour detection
- Pillow (PIL): Image manipulation
- OCR.Space API: Optical Character Recognition
- reportlab: PDF report generation
- Streamlit: Web interface
- pandas: Data manipulation for display

---

## PROJECT STRUCTURE

```
Automated-Label-Verification-System/
├── main.py                          # CLI entry point
├── streamlit_app.py                 # Web interface entry point
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (API key)
├── core/
│   ├── jobcard_extractor.py        # Job card PDF parsing
│   ├── label_detector.py           # Label detection from PDF pages
│   ├── label_extractor.py          # OCR text extraction from labels
│   ├── validator.py                # Validation logic
│   ├── report_generator.py         # PDF report generation
│   └── utils.py                    # Utility functions
├── input/
│   ├── job_card.pdf                # Input job card PDF
│   └── SW02132230W.pdf             # Input label PDF
└── output/
    ├── labels/                      # Extracted label images
    ├── jobcard_data.json           # Extracted job card data
    ├── label_data.json             # Extracted label text data
    ├── validation_result.json      # Validation results
    └── validation_report.pdf       # PDF report
```

---

## DEPENDENCIES & REQUIREMENTS

### Python Packages (from requirements.txt):
```
certifi==2026.2.25
charset-normalizer==3.4.4
idna==3.11
requests==2.32.5
urllib3==2.6.3
streamlit==1.30.0
pandas==2.2.3
python-dotenv==1.1.1
pdfplumber (required, not in requirements.txt - install separately)
PyMuPDF (fitz) (required, not in requirements.txt - install separately)
opencv-python (cv2) (required, not in requirements.txt - install separately)
Pillow (PIL) (required, not in requirements.txt - install separately)
reportlab (required, not in requirements.txt - install separately)
numpy (required, not in requirements.txt - install separately)
```

### Environment Setup:
Create a `.env` file in the project root with:
```
OCR_SPACE_API_KEY=your_ocr_space_api_key_here
```

Get your free API key from: https://ocr.space/ocrapi

---

## MODULE DOCUMENTATION

### 1. MAIN.PY - CLI Entry Point

**Purpose:** Command-line interface to run the validation pipeline

**Functions:**
- `main()` - Main execution function that orchestrates the entire pipeline

**Pipeline Steps:**
1. **STEP 1: Extract Job Card** 
   - Calls `extract_required_fields(JOB_CARD_PATH)`
   - Saves to `jobcard_data.json`
   
2. **STEP 2: Detect Labels**
   - Calls `detect_labels(LABEL_PDF_PATH, LABEL_IMAGE_FOLDER)`
   - Extracts label regions from PDF and saves as PNG images
   
3. **STEP 3: Extract Label Data**
   - For each detected label image, calls `extract_label_data(img_path)`
   - Uses OCR to extract text from label images
   - Saves all labels to `label_data.json`
   
4. **STEP 4: Validate Labels**
   - For each label, calls `validate(job_data, label_data)`
   - Compares extracted label text against job card requirements
   - Saves results to `validation_result.json`
   
5. **STEP 5: Generate PDF Report**
   - Calls `generate_validation_report(validation_results, REPORT_OUTPUT_PATH)`
   - Creates detailed PDF report with all validation results

**Output:**
- Summary statistics (Total labels, Passed, Failed)
- Location of output folder

**Configuration Constants:**
```python
JOB_CARD_PATH = "input/job_card.pdf"
LABEL_PDF_PATH = "input/SW02132230W.pdf"
OUTPUT_FOLDER = "output"
LABEL_IMAGE_FOLDER = os.path.join(OUTPUT_FOLDER, "labels")
JOB_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, "jobcard_data.json")
LABEL_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, "label_data.json")
VALIDATION_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, "validation_result.json")
REPORT_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, "validation_report.pdf")
```

---

### 2. STREAMLIT_APP.PY - Web Interface

**Purpose:** Provides web-based user interface for the validation system

**Key Functions:**

#### `is_connected(url: str = "https://www.google.com/", timeout: float = 3.0) -> bool`
- Checks internet connectivity
- Returns True if network request succeeds, False otherwise
- Used to verify API access before running pipeline

#### `run_pipeline(job_card_path: str, label_pdf_path: str, progress=None)`
- Orchestrates the complete validation pipeline
- `job_card_path`: Path to job card PDF
- `label_pdf_path`: Path to label PDF
- `progress`: Optional callback function for progress updates
  - Takes arguments: `(fraction: float 0-1, message: str)`
- Returns: `(job_data, all_label_data, validation_results, label_images)`

**Pipeline Steps in run_pipeline:**
1. Clean and prepare output/labels directory
2. Extract job card data
3. Detect labels in PDF
4. Extract text from each label using OCR
5. Validate each label against job card
6. Save JSON files (jobcard_data.json, label_data.json, validation_result.json)

#### `main()` - Streamlit UI
- Sets page configuration (title, layout)
- Creates file upload widgets for PDF files
- Displays progress bar during processing
- Shows validation results in table format with label images
- Handles temporary file cleanup

**UI Features:**
- Two PDF file uploaders (job card and label PDF)
- "Extract and validate" button
- Progress bar and status messages
- Connectivity check before processing
- Displays label images alongside validation results
- Results table with columns: Field, Job Card Requirement, Label Extracted, Status
- Color-coded status (PASS = green, FAIL = red)

**Output Files Generated:**
- `output/jobcard_data.json` - Extracted job card fields
- `output/label_data.json` - Extracted label text for each image
- `output/validation_result.json` - Validation results for each label
- `output/labels/` - Extracted label images

---

### 3. CORE/JOBCARD_EXTRACTOR.PY - Job Card PDF Parsing

**Purpose:** Extract required fields from job card PDF

**Main Function:**
#### `extract_required_fields(pdf_path) -> dict`
- Extracts all required fields from a job card PDF
- Parameter: `pdf_path` - Path to the PDF file
- Returns: Dictionary with the following keys:

**Extracted Fields:**
```python
{
    "Silhouette": str or None,           # e.g., "bikini/bikini"
    "Size/Age Breakdown": [list],        # e.g., ["XS/XP/ECH/165/64A", "S/P/ICH/170/68A"]
    "VSD": str or None,                  # VSD number
    "VSS": str or None,                  # VSS number
    "RN": str or None,                   # RN registration number
    "CA": str or None,                   # CA number
    "Factory ID": str or None,           # Factory identification
    "Date of MFR": str or None,          # Manufacturing date
    "Country Of Origin": str or None,    # Country information
    "Additional Instructions": str or None,  # Care/usage instructions
    "Garment Components & Fibre Contents": str or None  # Composition
}
```

**Extraction Logic:**
1. Opens PDF with pdfplumber
2. Extracts all text from all pages
3. Uses regex patterns to find specific fields:
   - "Silhouette" pattern: `r"Silhouette:\s*(.+)"`
   - "VSD#" pattern: `r"VSD#:\s*(\d+)"`
   - "RN#" pattern: `r"RN#:\s*(\d+)"`
   - "CA#" pattern: `r"CA#:\s*(\d+)"`
   - "Factory ID" pattern: `r"Factory ID:\s*(\d+)"`
   - "Date of MFR#" pattern: `r"Date of MFR#:\s*([\d\s]+)"`
   - "Country Of Origin" pattern: `r"Country Of Origin\s*(.+)"`
   - "Additional Instructions" pattern: `r"Additional Instructions:\s*(.+)"`

4. **Size/Age Breakdown Extraction:**
   - Uses regex to find section between "Size/Age Breakdown:" and next field
   - Extracts all sizes matching pattern: `r"\b(?:XS|S|M|L|XL|XXL)(?:/[A-Z]{1,4}){0,3}/\d{3}/\d{2}A\b"`
   - Returns as list

5. **Garment Components & Fibre Contents Extraction:**
   - Finds section between "Garment Components" and "Care Instructions"
   - Removes headers and formatting
   - Removes "100% (Total)" line
   - Cleans extra whitespace
   - Returns multi-line composition data

---

### 4. CORE/LABEL_DETECTOR.PY - Label Detection from PDF

**Purpose:** Detect and extract label regions from PDF pages

**Key Functions:**

#### `remove_red_color(image) -> ndarray`
- Removes red-colored pixels by converting them to white
- Converts image to HSV color space
- Creates masks for red color ranges:
  - Range 1: `[0, 50, 50]` to `[10, 255, 255]`
  - Range 2: `[170, 50, 50]` to `[180, 255, 255]`
- Sets masked pixels to white `[255, 255, 255]`
- Returns cleaned image

#### `detect_labels(pdf_path, output_folder, min_area=20000) -> list`
- Detects label regions in PDF pages and saves them as images
- Parameters:
  - `pdf_path`: Path to the label PDF file
  - `output_folder`: Directory to save extracted label images
  - `min_area`: Minimum contour area to be considered a label (default 20000 pixels)
- Returns: List of paths to saved label images

**Detection Algorithm:**
1. Opens PDF with PyMuPDF (fitz)
2. For each page in PDF:
   - Renders page to high-resolution image (300 DPI)
   - Converts RGBA to RGB if needed
   - Removes red colors (see `remove_red_color`)
   
3. **Image Processing:**
   - Converts to grayscale
   - Applies Gaussian blur (kernel 5x5)
   - Applies Canny edge detection (thresholds 50, 150)
   - Applies morphological closing (5x5 kernel)
   
4. **Contour Detection & Filtering:**
   - Finds all contours in the processed image
   - Filters by minimum area (20000 pixels default)
   - Approximates contours to polygons
   - Keeps only 4-sided shapes (rectangles)
   - Filters by aspect ratio: 1.2 < width/height < 3.5
   
5. **Saving:**
   - Crops the original image at the detected rectangle
   - Saves as PNG file: `label_1.png`, `label_2.png`, etc.
   - Appends path to results list

---

### 5. CORE/LABEL_EXTRACTOR.PY - OCR Text Extraction

**Purpose:** Extract text from label images using OCR.Space API

**Configuration Constants:**
```python
OCR_URL = "https://api.ocr.space/parse/image"
MAX_WIDTH = 1500                # Max image width to prevent timeout
RETRY_COUNT = 3                 # Number of API retry attempts
DELAY_BETWEEN_IMAGES = 2        # Delay in seconds between image processing
```

**Key Functions:**

#### `resize_image_if_needed(image_path, max_width=MAX_WIDTH) -> BytesIO`
- Resizes image to prevent API timeout
- If image width > max_width:
  - Calculates resize ratio
  - Resizes maintaining aspect ratio
  - Uses LANCZOS interpolation for quality
- Saves to BytesIO buffer as PNG
- Returns: In-memory PNG buffer ready for API submission

#### `extract_text_from_image(image_path, retries=RETRY_COUNT) -> str or None`
- Extracts text from image using OCR.Space API
- Parameters:
  - `image_path`: Path to the label image
  - `retries`: Number of retry attempts on timeout
- Returns: Extracted text or None if extraction fails

**API Request Details:**
```python
POST https://api.ocr.space/parse/image
Files: PNG image buffer
Data:
  - apikey: OCR_SPACE_API_KEY (from .env)
  - language: "eng" (English)
  - isOverlayRequired: False
  - OCREngine: 3 (Google Tesseract v4)
Timeout: 30 seconds
```

**Retry Logic:**
- If API returns error:
  - If "Timed out" in error message: Sleep 3 seconds and retry
  - Otherwise: Return None (extraction failed)
- If network exception: Sleep 3 seconds and retry
- Returns None after all retries exhausted

#### `normalize_text(text) -> str`
- Normalizes extracted text
- Applies NFKC Unicode normalization
- Strips whitespace
- Returns cleaned text

#### `extract_label_data(image_path) -> dict or None`
- Main function for processing a single label image
- Steps:
  1. Extracts raw text via `extract_text_from_image()`
  2. Normalizes text via `normalize_text()`
  3. Returns dictionary or None if extraction fails
- Returns:
  ```python
  {
      "raw_text": "extracted and normalized text..."
  }
  ```

#### `process_folder(folder_path) -> dict`
- Batch process all images in a folder
- Iterates through PNG/JPG/JPEG files
- Calls `extract_label_data()` for each
- Applies `DELAY_BETWEEN_IMAGES` delay between processing
- Returns: Dictionary mapping filename to extraction results

---

### 6. CORE/VALIDATOR.PY - Validation Logic

**Purpose:** Compare label text against job card requirements

**Key Functions:**

#### `normalize(text) -> str`
- Normalizes text for comparison
- Steps:
  1. Converts to NFKC Unicode normalization
  2. Converts to lowercase
  3. Replaces multiple spaces with single space
  4. Strips leading/trailing whitespace
- Used for case-insensitive and format-insensitive comparison

#### `find_matched_text(job_value, label_text) -> str or None`
- Checks if job_value exists in label_text
- Normalizes both strings for comparison
- Returns original job_value if normalized job_value found in normalized label_text
- Returns None if not found

#### `contains(job_value, label_text) -> bool`
- Simple boolean check if job_value is in label_text
- Returns True if job_value is None (optional field)
- Returns True/False based on normalized string containment

#### `fibre_check(job_fibre_text, label_text) -> tuple`
- Complex validation of fibre/composition content
- Returns: `(match: bool, missing_parts: list, found_parts: list, found_text: str)`
- If job_fibre_text is None: Returns `(True, [], [], "")`

**Fibre Check Logic:**
1. Normalizes both job and label text
2. Splits job text into lines
3. For each line:
   - If contains "%": Checks if entire line found in label
   - If contains "/": Splits by "/" and checks each part individually
4. Tracks missing and found parts separately
5. Reconstructs found text with original formatting (slashes preserved):
   - Example: "body/gusset/corps/..." instead of "body, gusset, corps"
6. Returns all metrics for reporting

#### `validate(job_data, label_data) -> dict`
- Main validation function
- Parameters:
  - `job_data`: Dictionary from job card extraction
  - `label_data`: Dictionary from label text extraction
- Returns: Validation result dictionary

**Validation Result Structure:**
```python
{
    "fields": {
        "Silhouette": {
            "jobcard": "value from job card",
            "label": "matched value from label",
            "match": bool,
            "type": "contains"
        },
        "Garment Components & Fibre Contents": {
            "jobcard": "composition from job card",
            "label_found_parts": [...],      # Individual parts found
            "missing_parts": [...],          # Parts not found
            "label_found_text": "...",       # Reconstructed with slashes
            "match": bool,
            "type": "multi_line_contains"
        },
        "Size/Age Breakdown": {
            "expected_sizes": [...],         # All possible sizes
            "label_found_sizes": [...],      # Only matching sizes found
            "match": bool,                   # True if exactly 1 size found
            "type": "single_valid_size_required"
        }
    },
    "overall_pass": bool,                    # True only if all fields match
    "raw_label_text": "..."                  # Complete extracted label text
}
```

**Validation Fields (9 fields total):**

1. **Simple Contains Fields** (8 fields):
   - Silhouette, VSD, RN, CA, Factory ID, Date of MFR, Country Of Origin, Additional Instructions
   - Each checks if job value exists in label text
   - Sets overall_pass to False if not found

2. **Fibre Field**:
   - Uses `fibre_check()` for complex multi-part validation
   - Validates composition content
   - Sets overall_pass to False if any part missing

3. **Size Field**:
   - Requires exactly 1 size from the expected sizes list
   - Returns False if 0 or 2+ sizes found
   - Sets overall_pass to False if not exactly 1

---

### 7. CORE/REPORT_GENERATOR.PY - PDF Report Generation

**Purpose:** Generate professional PDF validation reports

#### `generate_validation_report(validation_results, output_path)`
- Creates a PDF report with validation results
- Parameters:
  - `validation_results`: Dictionary from validation process
  - `output_path`: Path where PDF should be saved

**Report Structure (for each label):**
1. Label filename
2. Overall status (PASS/FAIL in color)
3. Results table with columns:
   - Field: Field name
   - Expected (Job Card): Expected value
   - Extracted (Label): Value found in label
   - Status: PASS or FAIL (color-coded)

**Table Details:**
- Header row: White text on grey background
- Data rows: Black text on white background
- Status column text colored:
  - Green for PASS
  - Red for FAIL
- Preserves original text formatting with slashes
- Grid: 0.5pt black borders
- Vertical alignment: Top

**Field-Specific Display:**
- **Size/Age Breakdown**: Comma-separated list
- **Garment Components**: Original formatting with slashes (e.g., "body/gusset/corps/...")
- **Other fields**: String representation

---

## DATA FLOW & PROCESS

```
Input PDFs
    ↓
Job Card PDF ──→ Job Card Extractor ──→ job_data (dict)
                                              ↓
                                        Validator (part 1)
                                              ↓
Label PDF ──→ Label Detector ──→ Label Images (PNG files)
                    ↓
                Each Image ──→ Label Extractor (OCR) ──→ label_data (dict)
                                                          ↓
                                                    Validator (part 2)
                                                          ↓
                                        validation_results (dict)
                                              ↓
                                      Report Generator ──→ PDF Report
                                              ↓
                                        Output JSON Files
```

### Data Structure Flow:

**job_data** (from jobcard_extractor.py):
```python
{
    "Silhouette": "bikini/bikini",
    "VSD": "415968",
    "RN": "54867",
    # ... other fields
    "Size/Age Breakdown": ["XS/XP/ECH/165/64A", "S/P/ICH/170/68A", ...],
    "Garment Components & Fibre Contents": "body/gusset/corps/... 57% cotton/cotton/... 38% modal/... 5% elastane/..."
}
```

**all_label_data** (from label_extractor.py):
```python
{
    "label_1.png": {
        "raw_text": "INTELLIGENT LABEL SOLUTIONS bikini/bikini made in Sri Lanka/... body/gusset/corps/... 57% cotton/coton/..."
    },
    "label_2.png": {
        "raw_text": "..."
    }
}
```

**validation_results** (from validator.py):
```python
{
    "label_1.png": {
        "fields": {
            "Silhouette": {
                "jobcard": "bikini/bikini",
                "label": "bikini/bikini",
                "match": true,
                "type": "contains"
            },
            # ... 8 more simple fields
            "Garment Components & Fibre Contents": {
                "jobcard": "body/gusset/...",
                "label_found_parts": ["body", "gusset", ...],
                "missing_parts": [],
                "label_found_text": "body/gusset/...",
                "match": true,
                "type": "multi_line_contains"
            },
            "Size/Age Breakdown": {
                "expected_sizes": ["XS/XP/ECH/165/64A", ...],
                "label_found_sizes": ["XXL/XXG/EEG/170/96A"],
                "match": true,
                "type": "single_valid_size_required"
            }
        },
        "overall_pass": true,
        "raw_label_text": "..."
    },
    "label_2.png": { ... }
}
```

---

## OUTPUT FILES

### 1. jobcard_data.json
- **Location**: `output/jobcard_data.json`
- **Created**: Step 1 of pipeline
- **Contents**: Extracted job card fields
- **Format**: JSON dictionary with all extracted fields

### 2. label_data.json
- **Location**: `output/label_data.json`
- **Created**: Step 3 of pipeline
- **Contents**: Extracted text from each label image
- **Format**: JSON dictionary mapping image filename to extraction result

### 3. validation_result.json
- **Location**: `output/validation_result.json`
- **Created**: Step 4 of pipeline
- **Contents**: Complete validation results for each label
- **Format**: JSON dictionary with detailed validation for each label

### 4. validation_report.pdf
- **Location**: `output/validation_report.pdf`
- **Created**: Step 5 of pipeline
- **Contents**: Professional PDF report with tables and results
- **Format**: PDF document (ReportLab)

### 5. label_*.png
- **Location**: `output/labels/label_1.png`, `label_2.png`, etc.
- **Created**: Step 2 of pipeline
- **Contents**: Extracted label images from the PDF

---

## RUNNING THE APPLICATION

### CLI Method (main.py):
```bash
python main.py
```

**Requirements:**
- Input files must exist: `input/job_card.pdf` and `input/SW02132230W.pdf`
- Will auto-create output folder
- Saves all JSON files and PDF report to output folder

### Web Interface Method (streamlit_app.py):
```bash
streamlit run streamlit_app.py
```

**Interface:**
- Upload job card PDF file
- Upload label PDF file
- Click "Extract and validate"
- View results with images and validation table
- JSON files automatically saved to output folder

---

## KEY ALGORITHMS & TECHNIQUES

### 1. Label Detection (OpenCV)
- Convert PDF pages to high-resolution images (300 DPI)
- Remove red coloring (preprocessing)
- Gaussian blur for smoothing
- Canny edge detection for boundary finding
- Morphological closing to connect edges
- Contour detection and filtering
- Aspect ratio validation for rectangular shapes

### 2. OCR (Optical Character Recognition)
- Uses OCR.Space API with Google Tesseract OCR engine v4
- Resizes images to prevent API timeout
- Retries failed requests with 3-second delay
- Supports multilingual text (Chinese, Arabic, French, Spanish, etc.)

### 3. Text Normalization & Matching
- Unicode NFKC normalization for character consistency
- Lowercase conversion for case-insensitive matching
- Space normalization (collapse multiple spaces)
- Substring containment checks for partial matching
- Special handling for fibre content with slash-separated components

### 4. Validation Logic
- **Simple fields**: Substring containment test
- **Fibre content**: Part-by-part checking with formatting preservation
- **Sizes**: Exactly-one match requirement
- **Overall pass**: All fields must match

---

## CONFIGURATION & CUSTOMIZATION

### To Change Input/Output Paths (in main.py):
```python
JOB_CARD_PATH = "your/path/job_card.pdf"
LABEL_PDF_PATH = "your/path/labels.pdf"
OUTPUT_FOLDER = "your/output/folder"
```

### To Change OCR Settings (in label_extractor.py):
```python
MAX_WIDTH = 1500                   # Increase for larger images
RETRY_COUNT = 3                    # More retries for flaky network
DELAY_BETWEEN_IMAGES = 2           # Longer delay to avoid rate limiting
```

### To Change Label Detection Sensitivity (in label_detector.py):
```python
min_area = 20000                   # Lower value = detect smaller labels
# In detect_labels call, can pass custom min_area
```

### To Change Validation Rules (in validator.py):
Modify `validate()` function:
- Add new validation fields
- Change matching logic
- Add custom validators for specific field types

---

## ERROR HANDLING & EDGE CASES

### Label Extraction Fails:
- OCR returns None if API fails or times out after 3 retries
- `extract_label_data()` returns None
- Validation skips None labels
- No validation result created for that label

### No Labels Detected:
- `detect_labels()` returns empty list
- Pipeline prints warning and exits after step 2
- No validation or report generated

### PDF Parsing Fails:
- pdfplumber/fitz exception caught in try-except
- Error message printed
- Program exits with status 1

### API Key Missing:
- `.env` file must have `OCR_SPACE_API_KEY`
- RuntimeError raised if key not found
- Check .env file if "API key not set" error appears

---

## TESTING & DEBUGGING

### Enable Debug Output:
- All functions include print statements
- Progress shown for each step
- Add `print()` statements for debugging

### Check Generated Files:
```bash
# View extracted job card
cat output/jobcard_data.json

# View label extractions
cat output/label_data.json

# View validation results
cat output/validation_result.json

# View label images
ls output/labels/
```

### Debug OCR Issues:
- Check if extracted text format matches expectations
- Verify label image quality in output/labels/
- Test with OCR.Space API directly: https://ocr.space/ocrapi

### Debug Validation Issues:
- Check normalized vs. original text
- Verify regex patterns in jobcard_extractor.py
- Look at individual field matches in validation_result.json

---

## DEPENDENCIES INSTALLATION

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install requirements
pip install -r requirements.txt

# Install additional dependencies
pip install pdfplumber PyMuPDF opencv-python Pillow reportlab numpy

# Verify installation
python -c "import streamlit, pandas, pdfplumber, cv2, reportlab; print('All dependencies installed')"
```

---

## ENVIRONMENT VARIABLES

### .env File Format:
```
OCR_SPACE_API_KEY=your_key_here
```

### Getting Free OCR API Key:
1. Visit https://ocr.space/ocrapi
2. Free tier: 25,000 requests/day
3. Register to get unlimited API key
4. Copy key to .env file

---

## SUMMARY

This project is a complete automation solution for validating apparel labels against job card specifications. It combines:
- PDF parsing (job cards)
- Computer vision (label detection)
- OCR (text extraction)
- Data validation (requirements checking)
- Report generation (PDF output)
- Web interface (user-friendly experience)

The system handles multilingual content, preserves original text formatting, and provides detailed validation reports in both web and PDF formats.
