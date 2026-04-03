import os
from fpdf import FPDF


class ReadinessPDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Placement Readiness Report | Indira College of Commerce and Science', 0, 1, 'C')
        self.line(10, 15, 200, 15)
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')


def generate_readiness_pdf(student: dict, analysis: dict, comparison: dict, output_dir: str) -> str:
    pdf = ReadinessPDFReport()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Title Page
    pdf.add_page()
    pdf.ln(20)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 12, 'Placement Readiness Report', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(52, 73, 94)
    pdf.cell(0, 10, f'Student: {student["name"]}', 0, 1, 'C')
    pdf.cell(0, 10, f'Branch: {student["branch"]} | Status: {student["year"]}', 0, 1, 'C')
    pdf.ln(10)

    # Overall Score
    pdf.set_font('Helvetica', 'B', 16)
    score = analysis['overall_score']
    if score >= 75:
        pdf.set_text_color(39, 174, 96)
    elif score >= 55:
        pdf.set_text_color(243, 156, 18)
    elif score >= 35:
        pdf.set_text_color(230, 126, 34)
    else:
        pdf.set_text_color(231, 76, 60)
    pdf.cell(0, 12, f'Overall Readiness Score: {score}%', 0, 1, 'C')
    pdf.set_font('Helvetica', 'B', 13)
    pdf.cell(0, 10, f'Prediction: {analysis["predicted_placement"]} Chance of Placement', 0, 1, 'C')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, f'Estimated Salary Range: {analysis["salary_range"][0]:.1f} - {analysis["salary_range"][1]:.1f} LPA', 0, 1, 'C')

    # Student Info
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(44, 62, 80)
    pdf.set_fill_color(236, 240, 241)
    pdf.cell(0, 10, 'Student Information', 0, 1, 'L', fill=True)
    pdf.ln(3)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    info_items = [
        f'CGPA: {student["cgpa"]} | 12th: {student["pct_12"]}% | 10th: {student["pct_10"]}%',
        f'DSA: {student["dsa"]}/5 | OOPS: {student["oops"]}/5 | Coding Problems: {student["coding_solved"]}',
        f'Languages: {student["languages"]}',
        f'Backend: {student["backend"]} | Frontend: {student["frontend"]} | DB: {student["database"]}',
        f'System Design: {student["system_design"]} | Projects: {student["projects"]} | Full-Stack: {student["fullstack_project"]}',
        f'Internship: {student["internship"]} | Open Source: {student["opensource"]}',
        f'Communication: {student["communication"]}/5 | English: {student["english"]}/5 | Confidence: {student["confidence"]}/5',
    ]
    for item in info_items:
        pdf.multi_cell(0, 6, item)
        pdf.ln(1)

    # Category Scores
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(44, 62, 80)
    pdf.set_fill_color(236, 240, 241)
    pdf.cell(0, 10, 'Category-wise Breakdown', 0, 1, 'L', fill=True)
    pdf.ln(3)

    for category, data in analysis['scores'].items():
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(52, 73, 94)
        pdf.cell(0, 7, f'{category}: {data["score"]}%', 0, 1, 'L')
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 0, 0)
        for detail_name, detail in data['details'].items():
            label_str = f' ({detail["label"]})' if detail.get('label') else ''
            pdf.cell(10)
            pdf.cell(0, 5.5, f'- {detail_name}: {detail["value"]}{label_str}', 0, 1)
        pdf.ln(2)

    # Strengths
    if analysis['strengths']:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(39, 174, 96)
        pdf.set_fill_color(212, 237, 218)
        pdf.cell(0, 10, 'Your Strengths', 0, 1, 'L', fill=True)
        pdf.ln(3)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 0, 0)
        for s in analysis['strengths']:
            pdf.cell(8)
            pdf.cell(5, 5.5, '+', 0, 0)
            pdf.multi_cell(0, 5.5, s)
            pdf.ln(1)

    # Weaknesses
    if analysis['weaknesses']:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(231, 76, 60)
        pdf.set_fill_color(248, 215, 218)
        pdf.cell(0, 10, 'Areas of Concern', 0, 1, 'L', fill=True)
        pdf.ln(3)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 0, 0)
        for w in analysis['weaknesses']:
            pdf.cell(8)
            pdf.cell(5, 5.5, '!', 0, 0)
            pdf.multi_cell(0, 5.5, w)
            pdf.ln(1)

    # Suggestions
    if analysis['suggestions']:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(44, 62, 80)
        pdf.set_fill_color(236, 240, 241)
        pdf.cell(0, 10, 'Personalized Suggestions', 0, 1, 'L', fill=True)
        pdf.ln(3)
        for i, s in enumerate(analysis['suggestions'], 1):
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(52, 73, 94)
            pdf.cell(0, 6, f'[{i}] {s["title"]}', 0, 1)
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(8)
            pdf.multi_cell(0, 5.5, s['text'])
            pdf.ln(2)

    # Priorities
    if analysis.get('priorities'):
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(44, 62, 80)
        pdf.set_fill_color(255, 243, 205)
        pdf.cell(0, 10, 'Top 3 Priority Actions', 0, 1, 'L', fill=True)
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(0, 0, 0)
        for i, p in enumerate(analysis['priorities'], 1):
            pdf.cell(0, 7, f'{i}. Focus on: {p}', 0, 1)

    # Comparison
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(44, 62, 80)
    pdf.set_fill_color(236, 240, 241)
    pdf.cell(0, 10, f'How You Compare (vs {comparison["total_students"]} students)', 0, 1, 'L', fill=True)
    pdf.ln(3)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)

    for key in ['cgpa', 'dsa', 'communication', 'confidence']:
        c = comparison[key]
        pdf.multi_cell(0, 6,
            f'{key.upper()}: Your {c["yours"]} vs Placed Avg {c["placed_avg"]} - {c["status"]} average')
        pdf.ln(1)

    c_sal = comparison['expected_salary']
    pdf.multi_cell(0, 6,
        f'Expected Salary: Your {c_sal["yours"]} LPA vs Placed Avg {c_sal["placed_avg"]} LPA')

    import uuid
    filename = f'readiness_report_{uuid.uuid4().hex[:8]}.pdf'
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath
