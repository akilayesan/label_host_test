import os
import tempfile
import json

import streamlit as st
import pandas as pd
import requests

from core.jobcard_extractor import extract_required_fields
from core.label_detector import detect_labels
from core.label_extractor import extract_label_data
from core.validator import validate


OUTPUT_FOLDER = "output"
LABEL_IMAGE_FOLDER = os.path.join(OUTPUT_FOLDER, "labels")


# -------------------------------------------------------
# INTERNET CHECK
# -------------------------------------------------------

def is_connected(url="https://www.google.com/", timeout=3):

    try:
        requests.get(url, timeout=timeout)
        return True
    except requests.RequestException:
        return False


# -------------------------------------------------------
# PIPELINE
# -------------------------------------------------------

def run_pipeline(job_card_path, label_pdf_path, progress=None):

    def _update(pct, msg=""):
        if progress:
            progress(pct, msg)

    # clean labels folder
    if os.path.exists(LABEL_IMAGE_FOLDER):
        for f in os.listdir(LABEL_IMAGE_FOLDER):
            try:
                os.remove(os.path.join(LABEL_IMAGE_FOLDER, f))
            except:
                pass

    os.makedirs(LABEL_IMAGE_FOLDER, exist_ok=True)

    # ---------------------------------------------------
    # STEP 1 — JOB CARD EXTRACTION
    # ---------------------------------------------------

    _update(0.05, "Extracting job card...")
    job_data = extract_required_fields(job_card_path)

    _update(0.15, "Job card extracted")


    # ---------------------------------------------------
    # STEP 2 — LABEL DETECTION
    # ---------------------------------------------------

    _update(0.2, "Detecting labels...")

    label_images = detect_labels(label_pdf_path, LABEL_IMAGE_FOLDER)

    if not label_images:
        raise RuntimeError("No labels detected in the uploaded artwork.")

    _update(0.3, f"{len(label_images)} labels detected")


    # ---------------------------------------------------
    # STEP 3 — OCR EXTRACTION
    # ---------------------------------------------------

    all_label_data = {}
    total = len(label_images)

    for idx, img_path in enumerate(label_images, start=1):

        _update(0.3 + 0.3 * (idx / total), f"Extracting label {idx}/{total}")

        structured = extract_label_data(img_path)

        label_name = os.path.basename(img_path)

        # 🚨 STOP immediately if OCR failed
        if structured is None or not structured.get("raw_text"):

            raise RuntimeError(
                f"OCR failed after 3 attempts.\n\n"
                f"Failed label: {label_name}\n\n"
                "Please check internet connection or OCR API."
            )

        all_label_data[label_name] = structured


    _update(0.6, "Label text extracted")


    # ---------------------------------------------------
    # STEP 4 — VALIDATION
    # ---------------------------------------------------

    validation_results = {}

    for idx, (label_name, label_data) in enumerate(all_label_data.items(), start=1):

        validation_results[label_name] = validate(job_data, label_data)

        _update(0.6 + 0.4 * (idx / total), f"Validating label {idx}/{total}")


    _update(1.0, "Validation completed")


    # ---------------------------------------------------
    # SAVE OUTPUT JSON FILES
    # ---------------------------------------------------

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    with open(os.path.join(OUTPUT_FOLDER, "jobcard_data.json"), "w", encoding="utf-8") as f:
        json.dump(job_data, f, indent=4, ensure_ascii=False)

    with open(os.path.join(OUTPUT_FOLDER, "label_data.json"), "w", encoding="utf-8") as f:
        json.dump(all_label_data, f, indent=4, ensure_ascii=False)

    with open(os.path.join(OUTPUT_FOLDER, "validation_result.json"), "w", encoding="utf-8") as f:
        json.dump(validation_results, f, indent=4, ensure_ascii=False)

    return job_data, all_label_data, validation_results, label_images


# -------------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------------

def main():

    st.set_page_config(
        page_title="Automated Label Verification System",
        layout="wide"
    )

    st.title("Automated Label Verification System")

    st.write(
        "Upload a **Job Card PDF** and **Label Artwork PDF** "
        "to run automated validation."
    )

    job_file = st.file_uploader("Upload Job Card PDF", type=["pdf"])
    label_file = st.file_uploader("Upload Label Artwork PDF", type=["pdf"])


    if st.button("Extract and Validate"):

        if not job_file or not label_file:
            st.warning("Please upload both PDFs.")
            return

        if not is_connected():
            st.error("Internet connection required for OCR.")
            return


        job_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        job_tmp.write(job_file.read())
        job_tmp.close()

        label_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        label_tmp.write(label_file.read())
        label_tmp.close()


        progress_bar = st.progress(0)
        status_text = st.empty()

        def progress_callback(fraction, message=""):

            progress_bar.progress(min(max(int(fraction * 100), 0), 100))
            status_text.text(message)


        try:

            job_data, all_label_data, validation_results, label_images = run_pipeline(
                job_tmp.name,
                label_tmp.name,
                progress=progress_callback
            )

        except RuntimeError as e:

            st.error(str(e))
            return

        finally:

            try:
                os.unlink(job_tmp.name)
            except:
                pass

            try:
                os.unlink(label_tmp.name)
            except:
                pass


        # ---------------------------------------------------
        # SHOW RESULTS
        # ---------------------------------------------------

        for label_name, result in validation_results.items():

            st.markdown("---")

            cols = st.columns([1, 2])

            img_path = os.path.join(LABEL_IMAGE_FOLDER, label_name)

            if os.path.exists(img_path):
                cols[0].image(img_path, caption=label_name)

            cols[1].subheader(f"Label: {label_name}")

            rows = []

            for field, field_data in result["fields"].items():

                if field == "Size/Age Breakdown":

                    expected = ", ".join(field_data.get("expected_sizes", []))
                    label_val = ", ".join(field_data.get("label_found_sizes", []))

                elif field == "Garment Components & Fibre Contents":

                    expected = str(field_data.get("jobcard", ""))
                    label_val = str(field_data.get("label_found_text", ""))

                else:

                    expected = str(field_data.get("jobcard", ""))
                    label_val = str(field_data.get("label", ""))


                status = "✅" if field_data.get("match") else "❌"

                rows.append([field, expected, label_val, status])


            additional = result.get("additional_information", [])

            if additional:
                rows.append([
                    "Additional Information",
                    "-",
                    ", ".join(additional),
                    "⚠️"
                ])


            missing = result.get("missing_information", [])

            if missing:
                rows.append([
                    "Missing Information",
                    "-",
                    ", ".join(missing),
                    "❓"
                ])


            df = pd.DataFrame(
                rows,
                columns=[
                    "Field",
                    "Job Card Requirement",
                    "Label Extracted",
                    "Status"
                ]
            )

            cols[1].table(df)


    st.markdown("---")
    st.write("Streamlit Interface")


if __name__ == "__main__":
    main()