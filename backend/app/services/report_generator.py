"""
CBAM Report Generator
Generates XML (CBAM Transitional Registry format) and PDF reports.
"""
import os
from datetime import datetime
from typing import Any
from lxml import etree
from app.config import settings


def generate_xml(
    period: str,
    declarant_name: str,
    eori: str,
    declarant_country: str,
    goods_lines: list[dict[str, Any]],
) -> str:
    """Generate CBAM XML report. Returns file path."""
    root = etree.Element("CBAMReport")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("version", "1.0")

    etree.SubElement(root, "ReportingPeriod").text = period
    etree.SubElement(root, "GeneratedAt").text = datetime.utcnow().isoformat()

    declarant = etree.SubElement(root, "DeclarantDetails")
    etree.SubElement(declarant, "Name").text = declarant_name
    etree.SubElement(declarant, "EORI").text = eori
    etree.SubElement(declarant, "Country").text = declarant_country

    goods_el = etree.SubElement(root, "GoodsLines")
    total_emissions = 0.0

    for line in goods_lines:
        gl = etree.SubElement(goods_el, "GoodsLine")
        etree.SubElement(gl, "CNCode").text = str(line.get("cn_code", ""))
        etree.SubElement(gl, "CountryOfOrigin").text = str(line.get("country_of_origin", ""))

        qty_el = etree.SubElement(gl, "Quantity")
        qty_el.set("unit", str(line.get("unit", "tonne")))
        qty_el.text = str(line.get("quantity", "0"))

        ee_el = etree.SubElement(gl, "EmbeddedEmissions")
        ee_el.set("unit", "tCO2e")
        embedded = float(line.get("embedded_emissions", 0))
        ee_el.text = f"{embedded:.6f}"
        total_emissions += embedded

        ei_el = etree.SubElement(gl, "EmissionIntensity")
        ei_el.set("unit", "tCO2e/tonne")
        ei_el.text = f"{float(line.get('emission_intensity', 0)):.6f}"

        etree.SubElement(gl, "ProductionRoute").text = str(line.get("production_route", ""))
        etree.SubElement(gl, "SupplierInstallation").text = str(line.get("installation_id", ""))
        etree.SubElement(gl, "EFApplied").text = str(line.get("calculation_method", "default"))
        etree.SubElement(gl, "SupplierName").text = str(line.get("supplier_name", ""))

    total_el = etree.SubElement(root, "TotalEmbeddedEmissions")
    total_el.set("unit", "tCO2e")
    total_el.text = f"{total_emissions:.6f}"

    os.makedirs(settings.report_storage_path, exist_ok=True)
    filename = f"cbam_report_{period}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.xml"
    filepath = os.path.join(settings.report_storage_path, filename)

    tree = etree.ElementTree(root)
    tree.write(filepath, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    return filepath


def generate_pdf(
    period: str,
    declarant_name: str,
    eori: str,
    declarant_country: str,
    goods_lines: list[dict[str, Any]],
    validation_score: int | None = None,
    validation_issues: list[dict] | None = None,
) -> str:
    """Generate CBAM PDF report. Returns file path."""
    from weasyprint import HTML

    total_emissions = sum(float(l.get("embedded_emissions", 0)) for l in goods_lines)
    estimated_cost = total_emissions * 75.36  # EU ETS carbon price placeholder

    rows_html = ""
    for i, line in enumerate(goods_lines, 1):
        rows_html += f"""
        <tr>
            <td>{i}</td>
            <td>{line.get('cn_code', '')}</td>
            <td>{line.get('country_of_origin', '')}</td>
            <td>{float(line.get('quantity', 0)):,.2f} {line.get('unit', 't')}</td>
            <td>{float(line.get('embedded_emissions', 0)):,.4f}</td>
            <td>{float(line.get('emission_intensity', 0)):,.4f}</td>
            <td>{line.get('calculation_method', 'default')}</td>
        </tr>"""

    issues_html = ""
    if validation_issues:
        for issue in validation_issues:
            sev = issue.get("severity", "INFO")
            color = {"ERROR": "#FF4444", "WARNING": "#FFB300", "INFO": "#8888AA"}.get(sev, "#8888AA")
            issues_html += f'<li style="color:{color}"><strong>[{sev}]</strong> {issue.get("rule_id")} — {issue.get("message")}</li>'

    score_color = "#00C851" if (validation_score or 0) >= 80 else "#FFB300" if (validation_score or 0) >= 60 else "#FF4444"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #111; font-size: 12px; }}
        h1 {{ color: #0066CC; border-bottom: 2px solid #0066CC; padding-bottom: 8px; }}
        h2 {{ color: #0066CC; margin-top: 24px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
        th {{ background: #0066CC; color: white; padding: 6px 8px; text-align: left; font-size: 11px; }}
        td {{ padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 11px; }}
        tr:nth-child(even) {{ background: #f5f5f5; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px; }}
        .summary-card {{ border: 1px solid #ddd; padding: 12px; border-radius: 4px; }}
        .summary-card .value {{ font-size: 20px; font-weight: bold; color: #0066CC; }}
        .score {{ font-size: 24px; font-weight: bold; color: {score_color}; }}
        .footer {{ margin-top: 40px; font-size: 10px; color: #666; border-top: 1px solid #ddd; padding-top: 8px; }}
        ul {{ margin: 8px 0; padding-left: 20px; }}
    </style>
    </head>
    <body>
    <h1>CBAM Compliance Report</h1>
    <p><strong>Reporting Period:</strong> {period} &nbsp;&nbsp;
       <strong>Generated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>

    <h2>1. Declarant Details</h2>
    <table>
        <tr><td><strong>Name</strong></td><td>{declarant_name}</td></tr>
        <tr><td><strong>EORI</strong></td><td>{eori}</td></tr>
        <tr><td><strong>Country</strong></td><td>{declarant_country}</td></tr>
    </table>

    <h2>2. Executive Summary</h2>
    <div class="summary-grid">
        <div class="summary-card">
            <div>Total Shipments</div>
            <div class="value">{len(goods_lines)}</div>
        </div>
        <div class="summary-card">
            <div>Total Embedded Emissions</div>
            <div class="value">{total_emissions:,.2f} tCO₂e</div>
        </div>
        <div class="summary-card">
            <div>Est. CBAM Cost (€75.36/t)</div>
            <div class="value">€{estimated_cost:,.0f}</div>
        </div>
    </div>
    {"<div class='summary-card' style='margin-top:12px'><div>Validation Score</div><div class='score'>" + str(validation_score) + "/100</div></div>" if validation_score is not None else ""}

    <h2>3. Goods Lines</h2>
    <table>
        <thead>
            <tr>
                <th>#</th><th>CN Code</th><th>Country of Origin</th>
                <th>Quantity</th><th>Embedded Emissions (tCO₂e)</th>
                <th>Intensity (tCO₂e/t)</th><th>Method</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
        <tfoot>
            <tr style="font-weight:bold;background:#e8f0fe">
                <td colspan="4">TOTAL</td>
                <td>{total_emissions:,.4f}</td>
                <td>—</td><td>—</td>
            </tr>
        </tfoot>
    </table>

    <h2>4. Calculation Methodology</h2>
    <p>Calculations follow EU MRR (Monitoring, Reporting, Regulation) methodology as per
    EU Regulation 2023/956 (CBAM) and Commission Implementing Regulation (EU) 2023/1773.</p>
    <p>Formula: <em>Embedded Emissions = Direct Emissions + (Electricity Consumption × Electricity Emission Factor)</em></p>

    {"<h2>5. Validation Results</h2><p>Score: <span class='score'>" + str(validation_score) + "/100</span></p><ul>" + issues_html + "</ul>" if validation_issues else ""}

    <div class="footer">
        <p>Generated by CBAM Assistant — Open-source EU CBAM compliance tool.
        This report is for informational purposes. Verify all data before submission to the EU CBAM Transitional Registry.</p>
        <p>EU CBAM Regulation: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R0956</p>
    </div>
    </body>
    </html>
    """

    os.makedirs(settings.report_storage_path, exist_ok=True)
    filename = f"cbam_report_{period}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(settings.report_storage_path, filename)

    HTML(string=html_content).write_pdf(filepath)
    return filepath
