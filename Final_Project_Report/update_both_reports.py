import re

# =========================================================================
# 1. UPDATE build_50page_report.py
# =========================================================================
with open('Final_Project_Report/build_50page_report.py', 'r', encoding='utf-8') as f:
    pdf_text = f.read()

# Replace unicode symbols that can cause glyph issues in ReportLab Type 1 fonts
pdf_text = pdf_text.replace('\u20b9', 'Rs. ')
pdf_text = pdf_text.replace('\u2013', '-')
pdf_text = pdf_text.replace('\u2014', ' -- ')

# Clean up any residual non-ASCII or broken characters on Title Page
pdf_text = re.sub(r'Ahmedabad\s*[^\w\s]\s*382481', 'Ahmedabad - 382481', pdf_text)
pdf_text = re.sub(r'2026\s*[^\w\s]\s*2027', '2026-2027', pdf_text)
pdf_text = re.sub(r'2026\s*[^\w\s]\s*27', '2026-2027', pdf_text)

# Exact clean compact Student table on Page 1 (Title Page)
old_p1_pattern = re.compile(r'p\.append\(Paragraph\("<b>Submitted by:</b>",\s*s_cov_sublbl\)\).*?p\.append\(t_p1_team\)\s*p\.append\(Spacer\(1,\s*10\)\)', re.DOTALL)
new_p1_code = '''p.append(Paragraph("<b>Submitted by:</b>", s_cov_sublbl))
    p1_team_data = [
        [Paragraph("Ansari Mo.Atik", ParagraphStyle('StudN1', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=2)),
         Paragraph("(En. No: 2502031830031)", ParagraphStyle('StudE1', fontName='Times-Roman', fontSize=10.5, leading=14, alignment=0))],
        [Paragraph("Shaikh Sakib Ahmed", ParagraphStyle('StudN2', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=2)),
         Paragraph("(En. No: 2502031830033)", ParagraphStyle('StudE2', fontName='Times-Roman', fontSize=10.5, leading=14, alignment=0))],
        [Paragraph("Shaikh Sejan", ParagraphStyle('StudN3', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=2)),
         Paragraph("(En. No: 2502031830053)", ParagraphStyle('StudE3', fontName='Times-Roman', fontSize=10.5, leading=14, alignment=0))]
    ]
    t_p1_team = RLTable(p1_team_data, colWidths=[150, 160])
    t_p1_team.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (0,-1), 0),
        ('RIGHTPADDING', (0,0), (0,-1), 8),
        ('LEFTPADDING', (1,0), (1,-1), 8),
        ('RIGHTPADDING', (1,0), (1,-1), 0)
    ]))
    p.append(t_p1_team)
    p.append(Spacer(1, 10))'''

if old_p1_pattern.search(pdf_text):
    pdf_text = old_p1_pattern.sub(new_p1_code, pdf_text)
    print("Updated Page 1 student layout in build_50page_report.py")
else:
    print("Warning: old_p1_pattern not found, attempting direct string replace")

# Ensure Guide Designation is Assistant Professor, Department of Computer Engineering
pdf_text = pdf_text.replace(
    'Assistant Professor, Department of Computer Science and Engineering',
    'Assistant Professor, Department of Computer Engineering'
)
pdf_text = pdf_text.replace(
    'Assistant Professor, Dept. of CSE<br/>Silver Oak College of Technology',
    'Assistant Professor, Department of Computer Engineering<br/>Silver Oak College of Technology'
)

# Ensure Bottom Right Page Number
if 'canvas.drawRightString(page_w - right_m, bottom_m - 24' not in pdf_text:
    old_pn = "canvas.drawCentredString(printable_center_x, bottom_m - 24, f'- {page_num} -')"
    new_pn = "canvas.drawRightString(page_w - right_m, bottom_m - 24, f'- {page_num} -')"
    pdf_text = pdf_text.replace(old_pn, new_pn)

with open('Final_Project_Report/build_50page_report.py', 'w', encoding='utf-8') as f:
    f.write(pdf_text)
print("build_50page_report.py successfully updated and saved.")

# =========================================================================
# 2. UPDATE build_final_docx.py
# =========================================================================
with open('Final_Project_Report/build_final_docx.py', 'r', encoding='utf-8') as f:
    docx_text = f.read()

# Replace unicode symbols
docx_text = docx_text.replace('\u20b9', 'Rs. ')
docx_text = docx_text.replace('\u2013', '-')
docx_text = docx_text.replace('\u2014', ' -- ')

docx_text = re.sub(r'2026\s*[^\w\s]\s*2027', '2026-2027', docx_text)
docx_text = re.sub(r'2026\s*[^\w\s]\s*27', '2026-2027', docx_text)

# Update Footer in docx: replace centered paragraph footer with 2-column borderless table
old_docx_ftr = '''    # Setup Footer for Pages 2+
    footer = sec.footer
    p_ftr = footer.paragraphs[0]
    p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ftr.paragraph_format.space_before = Pt(6)
    p_ftr.paragraph_format.space_after = Pt(0)
    r_ftxt = p_ftr.add_run('Silver Oak University | Department of Computer Science and Engineering | Problem Based Learning 1\\n')
    r_ftxt.font.name = 'Times New Roman'
    r_ftxt.font.size = Pt(8.5)
    r_ftxt.font.italic = True
    r_ftxt.font.color.rgb = RGBColor(100, 100, 100)
    
    r_pnum = p_ftr.add_run('- ')
    r_pnum.font.name = 'Times New Roman'
    r_pnum.font.size = Pt(9.5)
    r_pnum.font.bold = True
    add_page_number_field(r_pnum)
    r_pend = p_ftr.add_run(' -')
    r_pend.font.name = 'Times New Roman'
    r_pend.font.size = Pt(9.5)
    r_pend.font.bold = True'''

new_docx_ftr = '''    # Setup Footer for All Pages: 2-Column Table (Left: Inst info, Right: Bottom-Right Page Number)
    footer = sec.footer
    p_ftr_init = footer.paragraphs[0]
    footer._element.remove(p_ftr_init._element)
    
    t_ftr = footer.add_table(rows=1, cols=2, width=Inches(6.02))
    t_ftr.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_ftr.autofit = False
    
    c_fl = t_ftr.cell(0, 0)
    c_fl.width = Inches(4.5)
    p_fl = c_fl.paragraphs[0]
    p_fl.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_fl.paragraph_format.space_before = Pt(0)
    p_fl.paragraph_format.space_after = Pt(0)
    r_ftxt = p_fl.add_run('Silver Oak University | Department of Computer Science and Engineering | PBL-I')
    r_ftxt.font.name = 'Times New Roman'
    r_ftxt.font.size = Pt(8.5)
    r_ftxt.font.italic = True
    r_ftxt.font.color.rgb = RGBColor(100, 100, 100)
    
    c_fr = t_ftr.cell(0, 1)
    c_fr.width = Inches(1.52)
    p_fr = c_fr.paragraphs[0]
    p_fr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_fr.paragraph_format.space_before = Pt(0)
    p_fr.paragraph_format.space_after = Pt(0)
    r_pnum = p_fr.add_run('- ')
    r_pnum.font.name = 'Times New Roman'
    r_pnum.font.size = Pt(9.5)
    r_pnum.font.bold = True
    add_page_number_field(r_pnum)
    r_pend = p_fr.add_run(' -')
    r_pend.font.name = 'Times New Roman'
    r_pend.font.size = Pt(9.5)
    r_pend.font.bold = True
    
    set_cell_borders(c_fl)
    set_cell_borders(c_fr)
    set_cell_margins(c_fl, top=20, bottom=20, left=0, right=0)
    set_cell_margins(c_fr, top=20, bottom=20, left=0, right=0)'''

if old_docx_ftr in docx_text:
    docx_text = docx_text.replace(old_docx_ftr, new_docx_ftr)
    print("Updated footer to 2-column table with bottom-right page numbering in build_final_docx.py")
else:
    print("Warning: old_docx_ftr not matched directly.")

# Update Title Page Student Layout in docx
old_docx_p1_stud = '''    p_stud = doc.add_paragraph()
    p_stud.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_stud.paragraph_format.line_spacing = 1.3
    p_stud.paragraph_format.space_after = Pt(20)
    
    students = [
        ('Ansari Mo.Atik', '2502031830031'),
        ('Shaikh Sakib Ahmed', '2502031830033'),
        ('Shaikh Sejan', '2502031830053')
    ]
    for name, enr in students:
        r = p_stud.add_run(f'{name} - {enr}\\n')
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True'''

new_docx_p1_stud = '''    students = [
        ('Ansari Mo.Atik', '2502031830031'),
        ('Shaikh Sakib Ahmed', '2502031830033'),
        ('Shaikh Sejan', '2502031830053')
    ]
    t_stud = doc.add_table(rows=3, cols=2)
    t_stud.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_stud.autofit = False
    for r_idx, (name, enr) in enumerate(students):
        c0 = t_stud.cell(r_idx, 0)
        c0.width = Inches(2.2)
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(name)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(11.5)
        r0.font.bold = True
        
        c1 = t_stud.cell(r_idx, 1)
        c1.width = Inches(2.2)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(f'  (En. No: {enr})')
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(11.5)
        
        set_cell_borders(c0)
        set_cell_borders(c1)
        set_cell_margins(c0, top=30, bottom=30, left=40, right=60)
        set_cell_margins(c1, top=30, bottom=30, left=60, right=40)
    
    p_space_after_stud = doc.add_paragraph()
    p_space_after_stud.paragraph_format.space_before = Pt(4)
    p_space_after_stud.paragraph_format.space_after = Pt(10)'''

if old_docx_p1_stud in docx_text:
    docx_text = docx_text.replace(old_docx_p1_stud, new_docx_p1_stud)
    print("Updated Page 1 student layout in build_final_docx.py")
else:
    print("Warning: old_docx_p1_stud not matched directly.")

# Update Guide details in build_final_docx.py
docx_text = docx_text.replace(
    "r_gd = p_g.add_run('Assistant Professor, Department of Computer Science and Engineering')",
    "r_gd = p_g.add_run('Assistant Professor, Department of Computer Engineering')"
)

docx_text = docx_text.replace(
    "r1 = p1.add_run('____________________________\\nFaculty Guide\\nProf. Urmil Mewada\\nDepartment of Computer Science and Engineering')",
    "r1 = p1.add_run('____________________________\\nFaculty Guide\\nProf. Urmil Mewada\\nAssistant Professor, Department of Computer Engineering')"
)

docx_text = docx_text.replace(
    "Prof. Urmil Mewada, Assistant Professor, Department of Computer Science and Engineering",
    "Prof. Urmil Mewada, Assistant Professor, Department of Computer Engineering"
)

docx_text = docx_text.replace(
    "under the guidance of Prof. Urmil Mewada.",
    "under the guidance of Prof. Urmil Mewada, Assistant Professor, Department of Computer Engineering."
)

docx_text = docx_text.replace(
    "under the supervision of internal faculty guide Prof. Urmil Mewada. Table 6.1 outlines",
    "under the supervision of internal faculty guide Prof. Urmil Mewada (Assistant Professor, Department of Computer Engineering). Table 6.1 outlines"
)

docx_text = docx_text.replace(
    "internal guide Prof. Urmil Mewada conducted periodic milestone reviews",
    "internal guide Prof. Urmil Mewada (Assistant Professor, Department of Computer Engineering) conducted periodic milestone reviews"
)

docx_text = docx_text.replace(
    "bi-weekly with internal guide Prof. Urmil Mewada. Feedback was documented",
    "bi-weekly with internal guide Prof. Urmil Mewada (Department of Computer Engineering). Feedback was documented"
)

# Ensure p_head2 heading color is strictly RGBColor(0, 0, 0)
docx_text = docx_text.replace("RGBColor(20, 20, 20)", "RGBColor(0, 0, 0)")

with open('Final_Project_Report/build_final_docx.py', 'w', encoding='utf-8') as f:
    f.write(docx_text)
print("build_final_docx.py successfully updated and saved.")

