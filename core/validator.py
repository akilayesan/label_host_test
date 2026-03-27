import unicodedata
import re


# ------------------------------------------------
# NORMALIZE TEXT
# ------------------------------------------------

def normalize(text):

    if not text:
        return ""

    text = unicodedata.normalize("NFKC", str(text))
    text = text.lower()

    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", text)

    return text


def contains(job_value, label_text):

    if not job_value:
        return True

    return normalize(job_value) in normalize(label_text)


def find_matched_text(job_value, label_text):

    if not job_value:
        return None

    if contains(job_value, label_text):
        return job_value

    return None


# ------------------------------------------------
# FIBRE CHECK
# ------------------------------------------------

def fibre_check(job_fibre_text, label_text):

    if not job_fibre_text:
        return True, [], [], ""

    label_norm = normalize(label_text)

    missing_parts = []
    found_parts = []
    found_text_parts = []

    lines = [line.strip() for line in job_fibre_text.split("\n") if line.strip()]

    for line in lines:

        line_norm = normalize(line)

        if "%" in line:

            if line_norm in label_norm:
                found_parts.append(line)
                found_text_parts.append(line)
            else:
                missing_parts.append(line)

        else:

            parts = [p.strip() for p in line.split("/") if p.strip()]
            found_line_parts = []

            for part in parts:

                if normalize(part) in label_norm:
                    found_parts.append(part)
                    found_line_parts.append(part)
                else:
                    missing_parts.append(part)

            if found_line_parts:
                found_text_parts.append("/".join(found_line_parts))

    found_text = " ".join(found_text_parts) if found_text_parts else ""

    return len(missing_parts) == 0, missing_parts, found_parts, found_text


# ------------------------------------------------
# ADDITIONAL INFORMATION
# ------------------------------------------------

def find_additional_information(job_data, label_text):

    job_text = " ".join(str(v) for v in job_data.values() if v)

    job_norm = normalize(job_text)

    additional = []

    tokens = re.findall(r"[A-Za-z0-9]+", label_text)

    for token in tokens:

        if normalize(token) not in job_norm:
            additional.append(token)

    additional = list(dict.fromkeys(additional))

    return additional


# ------------------------------------------------
# MISSING INFORMATION
# ------------------------------------------------

def find_missing_information(job_data, label_text):

    label_norm = normalize(label_text)

    missing = []

    for key, value in job_data.items():

        # ❗ Skip size list
        if key == "Size/Age Breakdown":
            continue

        if not value:
            continue

        if isinstance(value, list):
            values = value
        else:
            values = [value]

        for item in values:

            if normalize(item) not in label_norm:
                missing.append(item)

    missing = list(dict.fromkeys(missing))

    return missing


# ------------------------------------------------
# MAIN VALIDATION
# ------------------------------------------------

def validate(job_data, label_data):

    label_text = label_data.get("raw_text", "")

    result = {
        "fields": {},
        "raw_label_text": label_text
    }

    overall_pass = True


    # ------------------------------------------------
    # SIMPLE FIELDS
    # ------------------------------------------------

    simple_fields = [
        "Silhouette",
        "VSD",
        "RN",
        "CA",
        "Factory ID",
        "Date of MFR",
        "Country Of Origin",
        "Additional Instructions"
    ]

    for field in simple_fields:

        job_val = job_data.get(field)

        match = contains(job_val, label_text)

        result["fields"][field] = {
            "jobcard": job_val,
            "label": find_matched_text(job_val, label_text),
            "match": match,
            "type": "contains"
        }

        if not match:
            overall_pass = False


    # ------------------------------------------------
    # FIBRE VALIDATION
    # ------------------------------------------------

    fibre_text = job_data.get("Garment Components & Fibre Contents")

    fibre_match, missing, found, found_text = fibre_check(
        fibre_text,
        label_text
    )

    result["fields"]["Garment Components & Fibre Contents"] = {
        "jobcard": fibre_text,
        "label_found_parts": found,
        "missing_parts": missing,
        "label_found_text": found_text,
        "match": fibre_match,
        "type": "multi_line_contains"
    }

    if not fibre_match:
        overall_pass = False


    # ------------------------------------------------
    # SIZE VALIDATION
    # ------------------------------------------------

    job_sizes = job_data.get("Size/Age Breakdown", [])

    found_sizes = []

    for size in job_sizes:

        if contains(size, label_text):
            found_sizes.append(size)

    size_match = len(found_sizes) == 1

    result["fields"]["Size/Age Breakdown"] = {
        "expected_sizes": job_sizes,
        "label_found_sizes": found_sizes,
        "match": size_match,
        "type": "single_valid_size_required"
    }

    if not size_match:
        overall_pass = False


    # ------------------------------------------------
    # ADDITIONAL INFORMATION
    # ------------------------------------------------

    additional = find_additional_information(job_data, label_text)

    result["additional_information"] = additional


    # ------------------------------------------------
    # MISSING INFORMATION
    # ------------------------------------------------

    missing_info = find_missing_information(job_data, label_text)

    result["missing_information"] = missing_info


    result["overall_pass"] = overall_pass

    return result