import os
import json
import sys

from core.label_detector import detect_labels
from core.label_extractor import extract_label_data
from core.jobcard_extractor import extract_required_fields
from core.validator import validate
from core.report_generator import generate_validation_report


# ============================
# PATH CONFIGURATION
# ============================

JOB_CARD_PATH = "input/job_card.pdf"
LABEL_PDF_PATH = "input/SW02132230W.pdf"

OUTPUT_FOLDER = "output"
LABEL_IMAGE_FOLDER = os.path.join(OUTPUT_FOLDER, "labels")

JOB_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, "jobcard_data.json")
LABEL_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, "label_data.json")
VALIDATION_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, "validation_result.json")
REPORT_OUTPUT_PATH = os.path.join(OUTPUT_FOLDER, "validation_report.pdf")


# ============================
# MAIN EXECUTION
# ============================

def main():

    try:
        print("\n🔹 STEP 1: Extracting Job Card...")
        job_data = extract_required_fields(JOB_CARD_PATH)

        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        with open(JOB_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=4, ensure_ascii=False)

        print("   ✅ Job card extracted")


        print("\n🔹 STEP 2: Detecting Labels...")
        label_images = detect_labels(LABEL_PDF_PATH, LABEL_IMAGE_FOLDER)

        if not label_images:
            print("   ⚠ No labels detected.")
            return

        print(f"   ✅ {len(label_images)} labels detected")


        print("\n🔹 STEP 3: Extracting Label Data...")
        all_label_data = {}

        for img_path in label_images:
            structured = extract_label_data(img_path)
            label_name = os.path.basename(img_path)
            all_label_data[label_name] = structured

        with open(LABEL_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(all_label_data, f, indent=4, ensure_ascii=False)

        print("   ✅ Label data extracted")


        print("\n🔹 STEP 4: Validating Labels...")
        validation_results = {}

        for label_name, label_data in all_label_data.items():
            validation_results[label_name] = validate(job_data, label_data)

        with open(VALIDATION_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(validation_results, f, indent=4, ensure_ascii=False)

        print("   ✅ Validation completed")


        print("\n🔹 STEP 5: Generating PDF Report...")
        generate_validation_report(validation_results, REPORT_OUTPUT_PATH)

        print("   ✅ PDF report generated")


        # ---------------- SUMMARY ----------------

        passed = sum(1 for v in validation_results.values() if v["overall_pass"])
        failed = len(validation_results) - passed

        print("\n==============================")
        print("🚀 PROCESS COMPLETED")
        print("==============================")
        print(f"Total Labels : {len(validation_results)}")
        print(f"Passed       : {passed}")
        print(f"Failed       : {failed}")
        print(f"\n📁 Output Folder: {OUTPUT_FOLDER}")
        print("==============================\n")


    except Exception as e:
        print("\n❌ ERROR OCCURRED")
        print(str(e))
        sys.exit(1)


# ============================
# ENTRY POINT
# ============================

if __name__ == "__main__":
    main()