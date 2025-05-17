# src/analysis/report.py

import pandas as pd
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import matplotlib.pyplot as plt

def generate_report(final_df, validated_df, output_dir="output", logger=None):
    # Crea carpeta por día
    dt = datetime.now()
    folder_name = f"{output_dir}/{dt.strftime('%Y%m%d')}"
    os.makedirs(folder_name, exist_ok=True)
    report_file = f"{folder_name}/report_ex_{dt.strftime('%Y%m%d_%H%M')}.pdf"

    # 1. Resumen de escenarios
    summary = validated_df['violation_type'].value_counts().reset_index()
    summary.columns = ['Scenario', 'Count']

    # 2. Gráfico de pastel
    plt.figure(figsize=(6, 6))
    plt.pie(summary['Count'], labels=summary['Scenario'], autopct='%1.1f%%', colors=plt.cm.Set3.colors)
    plt.title('POI Scenarios Distribution')
    pie_chart_path = f"{folder_name}/pie_chart.png"
    plt.savefig(pie_chart_path)
    plt.close()

    # 3. Crea el PDF
    c = canvas.Canvas(report_file, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, "POI Quality Assurance Report")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Execution Date: {dt.strftime('%Y-%m-%d %H:%M')}")
    c.drawString(40, height - 85, f"Total POIs processed: {len(validated_df)}")

    # Table header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 120, "Scenario Summary:")

    # Table
    c.setFont("Helvetica", 10)
    y = height - 140
    c.setFillColor(colors.grey)
    c.rect(40, y, 200, 18, fill=True)
    c.setFillColor(colors.white)
    c.drawString(45, y + 4, "Scenario")
    c.drawString(150, y + 4, "Count")
    c.setFillColor(colors.black)
    y -= 20

    for _, row in summary.iterrows():
        c.drawString(45, y, str(row['Scenario']))
        c.drawString(150, y, str(row['Count']))
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50

    # Add pie chart
    c.drawImage(pie_chart_path, 300, height - 320, width=250, height=250)

    # Section: Details
    c.setFont("Helvetica-Bold", 12)
    y = y - 20 if y > 150 else height - 340
    c.drawString(40, y, "Scenario Details:")
    c.setFont("Helvetica", 10)
    y -= 20

    scenario_dict = {
        "NO_STREET_MATCH": "Street not found in street dataset. Likely error in street naming.",
        "WRONG_SIDE_OR_SEGMENT": "POI is associated with a street but the segment/link_id does not match.",
        "MULTIDIGIT_ERROR": "Segment found but multidigit field was incorrect and was corrected.",
        "LEGIT_EXCEPTION": "POI exception considered as valid (e.g., special case: hospitals, schools, etc).",
        "OK": "POI validated with no issues."
    }

    for scen, desc in scenario_dict.items():
        c.setFont("Helvetica-Bold", 10)
        c.drawString(45, y, scen)
        c.setFont("Helvetica", 10)
        c.drawString(150, y, desc)
        y -= 15

    c.save()
    if logger:
        logger.info(f"PDF report generated: {report_file}")

    # Limpia el gráfico temporal
    if os.path.exists(pie_chart_path):
        os.remove(pie_chart_path)
