
import json
from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'SDR Lead Audit Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()

def generate_pdf_report(lead_data, output_dir='audit_data/pdf_reports'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.chapter_title(f"Company: {lead_data['company']}")
    pdf.chapter_body(f"Decision Maker: {lead_data['dm']} ({lead_data['title']})")
    pdf.chapter_body(f"Location: {lead_data['location']}")
    pdf.chapter_body(f"Website: {lead_data['website']}")
    if lead_data.get('linkedin_url'):
        pdf.chapter_body(f"LinkedIn: {lead_data['linkedin_url']}")
    pdf.chapter_body(f"Lead Score: {lead_data['lead_score']}/100")
    if lead_data.get('estimated_monthly_lost_revenue'):
        pdf.chapter_body(f"Estimated Monthly Lost Revenue: ${lead_data['estimated_monthly_lost_revenue']:,}")
    
    pdf.chapter_title("Pain Points:")
    if lead_data['pain_points']:
        for i, pp in enumerate(lead_data['pain_points'], 1):
            pdf.chapter_body(f"  {i}. {pp}")
    else:
        pdf.chapter_body("No major pain points identified.")

    pdf.chapter_title("Scoring Reasons:")
    if lead_data['scoring_reasons']:
        for i, reason in enumerate(lead_data['scoring_reasons'], 1):
            pdf.chapter_body(f"  {i}. {reason}")
    else:
        pdf.chapter_body("No specific scoring reasons provided.")

    output_filename = os.path.join(output_dir, f"{lead_data['company'].replace(' ', '_')}_Audit_Report.pdf")
    pdf.output(output_filename)
    return output_filename

if __name__ == '__main__':
    # Load scored leads
    with open('audit_data/scored_leads.json', 'r') as f:
        data = json.load(f)
        hot_leads = data['hot_leads']

    print("Generating PDF reports for hot leads...")
    generated_reports = []
    for lead in hot_leads:
        if lead['lead_score'] > 80:
            report_path = generate_pdf_report(lead)
            generated_reports.append(report_path)
            print(f"Generated: {report_path}")
    
    if not generated_reports:
        print("No hot leads (score > 80) found to generate reports.")
    else:
        print(f"\nSuccessfully generated {len(generated_reports)} PDF reports.")
