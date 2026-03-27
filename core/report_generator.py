from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


def generate_validation_report(validation_results, output_path):

    doc = SimpleDocTemplate(output_path)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph("LABEL VALIDATION REPORT", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    for label_name, result in validation_results.items():

        overall = "PASS" if result["overall_pass"] else "FAIL"

        elements.append(Paragraph(f"<b>Label:</b> {label_name}", normal_style))
        elements.append(Paragraph(
            f"<b>Overall Status:</b> "
            f"<font color={'green' if result['overall_pass'] else 'red'}>{overall}</font>",
            normal_style
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # ---- TABLE HEADER ----
        table_data = [["Field", "Expected (Job Card)", "Extracted (Label)", "Status"]]

        for field, field_data in result["fields"].items():

            status = "PASS" if field_data["match"] else "FAIL"

            # ---------------- SIZE FIELD ----------------
            if field == "Size/Age Breakdown":

                expected = ", ".join(field_data.get("expected_sizes", []))
                label_val = ", ".join(field_data.get("label_found_sizes", []))

            # ---------------- FIBRE FIELD ----------------
            elif field == "Garment Components & Fibre Contents":

                expected = str(field_data.get("jobcard", ""))
                label_val = str(field_data.get("label_found_text", ""))

            # ---------------- SIMPLE FIELDS ----------------
            else:

                expected = str(field_data.get("jobcard", ""))
                label_val = str(field_data.get("label", ""))

            table_data.append([field, expected, label_val, status])

        # ---- CREATE TABLE ----
        table = Table(
            table_data,
            colWidths=[1.8 * inch, 2.2 * inch, 2.2 * inch, 0.8 * inch]
        )

        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]

        # Color PASS / FAIL column
        for i in range(1, len(table_data)):
            field_status = result["fields"][table_data[i][0]]["match"]
            row_color = colors.green if field_status else colors.red
            style_commands.append(('TEXTCOLOR', (3, i), (3, i), row_color))

        table.setStyle(TableStyle(style_commands))

        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(PageBreak())

    doc.build(elements)