import pdfplumber
import re
import json


def extract_required_fields(pdf_path):
    data = {
        "Silhouette": None,
        "Size/Age Breakdown": [],
        "VSD": None,
        "VSS": None,
        "RN": None,
        "CA": None,
        "Factory ID": None,
        "Date of MFR": None,
        "Country Of Origin": None,
        "Additional Instructions": None,
        "Garment Components & Fibre Contents": None
    }

    # ---------------------------
    # Extract Full Text
    # ---------------------------
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    # ---------------------------
    # Basic Fields
    # ---------------------------

    patterns = {
        "Silhouette": r"Silhouette:\s*(.+)",
        "VSD": r"VSD#:\s*(\d+)",
        "VSS": r"VSS#:\s*(\d+)",
        "RN": r"RN#:\s*(\d+)",
        "CA": r"CA#:\s*(\d+)",
        "Factory ID": r"Factory ID:\s*(\d+)",
        "Date of MFR": r"Date of MFR#:\s*([\d\s]+)",
        "Country Of Origin": r"Country Of Origin\s*(.+)",
        "Additional Instructions": r"Additional Instructions:\s*(.+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, full_text)

        if not match:
            continue

        value = match.group(1).strip()

        # normalize numeric identifiers with prefixes
        if key == "RN":
            value = f"RN{value}"

        elif key == "CA":
            value = f"CA{value}"

        elif key == "Factory ID":
            value = f"ID{value}"

        elif key == "VSD":
            value = f"{value}"

        elif key == "VSS":
            value = f"VSS{value}"

        data[key] = value

    # ---------------------------
    # Size/Age Breakdown
    # ---------------------------

    size_block = re.search(
        r"Size/Age Breakdown:(.*?)(?:VSD#|VSS#)",
        full_text,
        re.DOTALL
    )

    if size_block:

        sizes = re.findall(
            r"\b(?:XS|S|M|L|XL|XXL)(?:/[A-Z]{1,4}){0,3}/\d{3}/\d{2}A\b",
            size_block.group(1)
        )

        data["Size/Age Breakdown"] = sizes

    # ---------------------------
    # Garment Components & Fibre Contents
    # ---------------------------

    start = full_text.find("Garment Components")
    end = full_text.find("Care Instructions")

    if start != -1 and end != -1:

        block = full_text[start:end]

        block = re.sub(r"Garment Components\s*&?", "", block)
        block = re.sub(r"Fibre Contents:", "", block)

        block = re.sub(r"100\s*%\s*\(Total\)", "", block, flags=re.IGNORECASE)

        block = block.replace(":", "")

        lines = [line.strip() for line in block.split("\n") if line.strip()]

        cleaned_block = "\n".join(lines)

        data["Garment Components & Fibre Contents"] = cleaned_block

    return data


# ---------------------------
# RUN
# ---------------------------

if __name__ == "__main__":

    pdf_path = "job_card.pdf"

    extracted_data = extract_required_fields(pdf_path)

    print(json.dumps(extracted_data, indent=4, ensure_ascii=False))