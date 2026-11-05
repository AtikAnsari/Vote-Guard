import os
import re

print("=========================================================")
print("  APPLYING FINAL FACULTY CORRECTIONS TO MASTER GENERATORS")
print("=========================================================")

# ==============================================================================
# 1. UPDATE build_50page_report.py (PDF Generator)
# ==============================================================================
pdf_gen_path = 'Final_Project_Report/build_50page_report.py'
with open(pdf_gen_path, 'r', encoding='utf-8') as f:
    pdf_code = f.read()

# 1.1 Update on_page for Section 1 (No header/footer on Page 1), Section 2 (Roman i..v), Section 3 (Arabic 1..44)
old_on_page = """    def on_page(canvas, doc):
        canvas.saveState()
        page_num = canvas.getPageNumber()
        
        # 1. Official Dual-Logo Header Banner at TOP CENTER of EVERY PAGE (Pages 1 to 50)
        if os.path.exists(hdr_logo_path):
            img_w = 340.0
            img_h = 42.0
            canvas.drawImage(hdr_logo_path, (page_w - img_w) / 2.0, page_h - top_m + 16, width=img_w, height=img_h, mask='auto')
            
        # Top black divider rule below header logos
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(0.6)
        canvas.line(left_m, page_h - top_m + 8, page_w - right_m, page_h - top_m + 8)
        
        # Bottom footer rule
        canvas.line(left_m, bottom_m - 12, page_w - right_m, bottom_m - 12)
        
        # Footer text
        canvas.setFont('Times-Italic', 8)
        canvas.setFillColor(colors.HexColor('#2D3748'))
        canvas.drawString(left_m, bottom_m - 24, 'Silver Oak University | Department of Computer Science and Engineering | PBL-I')
        
        # Automatic Page Number: BOTTOM RIGHT of every page (zero overlap with footer text)
        canvas.setFont('Times-Bold', 9)
        canvas.setFillColor(colors.black)
        canvas.drawRightString(page_w - right_m, bottom_m - 24, f'- {page_num} -')
        canvas.restoreState()"""

new_on_page = """    def on_page(canvas, doc):
        page_num = canvas.getPageNumber()
        
        # SECTION 1: Page 1 (Title / First Page)
        # Strictly NO header banner, NO top divider line, NO bottom divider line, NO footer text, NO page number!
        if page_num == 1:
            return
            
        canvas.saveState()
        
        # Official Dual-Logo Header Banner: Preserving exact native aspect ratio of p5_img0_X21.png (1073 x 232 -> ratio = 4.625)
        if os.path.exists(hdr_logo_path):
            img_w = 205.0
            img_h = 205.0 / (1073.0 / 232.0)  # = 44.32 pt (exact aspect ratio, not stretched)
            canvas.drawImage(hdr_logo_path, (page_w - img_w) / 2.0, page_h - top_m + 12, width=img_w, height=img_h, mask='auto')
            
        # Top black divider rule below header logos
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(0.6)
        canvas.line(left_m, page_h - top_m + 8, page_w - right_m, page_h - top_m + 8)
        
        # Bottom footer rule
        canvas.line(left_m, bottom_m - 12, page_w - right_m, bottom_m - 12)
        
        # Footer text
        canvas.setFont('Times-Italic', 8)
        canvas.setFillColor(colors.HexColor('#2D3748'))
        canvas.drawString(left_m, bottom_m - 24, 'Silver Oak University | Department of Computer Science and Engineering | PBL-I')
        
        # Automatic Dynamic Page Numbering System:
        canvas.setFont('Times-Bold', 9)
        canvas.setFillColor(colors.black)
        
        # SECTION 2: Certificate through Keywords & Research Scope Summary (Pages 2 to 6)
        # Sequence: Lowercase Roman numerals i, ii, iii, iv, v
        if 2 <= page_num <= 6:
            roman_map = {2: 'i', 3: 'ii', 4: 'iii', 5: 'iv', 6: 'v'}
            disp_pn = roman_map.get(page_num, 'i')
            canvas.drawRightString(page_w - right_m, bottom_m - 24, f'- {disp_pn} -')
            
        # SECTION 3: List of Figures to Final Page (Pages 7 to 50)
        # Sequence: Normal Arabic numbering 1, 2, 3, 4, 5... starting with 1 on List of Figures (Page 7)
        elif page_num >= 7:
            arabic_pn = page_num - 6  # Page 7 becomes 1, Page 8 becomes 2, Page 50 becomes 44
            canvas.drawRightString(page_w - right_m, bottom_m - 24, f'- {arabic_pn} -')
            
        canvas.restoreState()"""

assert old_on_page in pdf_code, "Error: old_on_page not found in build_50page_report.py!"
pdf_code = pdf_code.replace(old_on_page, new_on_page)
print("[PDF] 1. Updated on_page header, footer, and 3-section pagination system.")

# 1.2 Centered logo on Page 1: Correct native aspect ratio (274 x 172 -> 1.593)
old_seal = """    seal_path = 'Final_Project_Report/assets/p1_img0_X7.png'
    if os.path.exists(seal_path):
        p.append(RLImage(seal_path, width=90, height=90))
        p.append(Spacer(1, 8))"""

new_seal = """    seal_path = 'Final_Project_Report/assets/p1_img0_X7.png'
    if os.path.exists(seal_path):
        seal_w = 110.0
        seal_h = seal_w / (274.0 / 172.0)  # = 69.05 pt (exact native aspect ratio: 1.593)
        p.append(RLImage(seal_path, width=seal_w, height=seal_h))
        p.append(Spacer(1, 10))"""

assert old_seal in pdf_code, "Error: old_seal not found in build_50page_report.py!"
pdf_code = pdf_code.replace(old_seal, new_seal)
print("[PDF] 2. Corrected centered logo proportions on Page 1 (Aspect ratio: 1.593).")

# 1.3 Page 1 Institutional Heading: Replace "Silver Oak College of Technology" with "College of Technology"
old_cov_inst = "<b>Department of Computer Science and Engineering</b><br/><b>Silver Oak College of Technology</b><br/><b>SILVER OAK UNIVERSITY</b><br/>Ahmedabad - 382481, Gujarat, India<br/><b>Academic Year: 2026-2027</b>"
new_cov_inst = "<b>Department of Computer Science and Engineering</b><br/><b>College of Technology</b><br/><b>SILVER OAK UNIVERSITY</b><br/>Ahmedabad - 382481, Gujarat, India<br/><b>Academic Year: 2026-2027</b>"

assert old_cov_inst in pdf_code, "Error: old_cov_inst not found in build_50page_report.py!"
pdf_code = pdf_code.replace(old_cov_inst, new_cov_inst)
print("[PDF] 3. Updated Page 1 institution text to 'College of Technology'.")

# 1.4 Certificate Page (Page 2):
# a) Replace "Silver Oak College of Technology" with "College of Technology" in signature block
old_cert_sig = """    t_sig = RLTable([
        [
            Paragraph("____________________________<br/><b>Prof. Urmil Mewada</b><br/>Internal Project Guide<br/>Assistant Professor, Department of Computer Engineering<br/>Silver Oak College of Technology", ParagraphStyle('SigL', fontName='Times-Roman', fontSize=9, leading=12.5, alignment=0)),
            Paragraph("____________________________<br/><b>[Head of Department]</b><br/>Head of Department<br/>Department of CSE<br/>Silver Oak College of Technology", ParagraphStyle('SigR', fontName='Times-Roman', fontSize=9, leading=12.5, alignment=2))
        ]
    ], colWidths=[210, 220])"""

new_cert_sig = """    t_sig = RLTable([
        [
            Paragraph("____________________________<br/><b>Prof. Urmil Mewada</b><br/>Internal Project Guide<br/>Assistant Professor, Department of Computer Engineering<br/>College of Technology", ParagraphStyle('SigL', fontName='Times-Roman', fontSize=9, leading=12.5, alignment=0)),
            Paragraph("____________________________<br/><b>[Head of Department]</b><br/>Head of Department<br/>Department of CSE<br/>College of Technology", ParagraphStyle('SigR', fontName='Times-Roman', fontSize=9, leading=12.5, alignment=2))
        ]
    ], colWidths=[210, 220])"""

assert old_cert_sig in pdf_code, "Error: old_cert_sig not found in build_50page_report.py!"
pdf_code = pdf_code.replace(old_cert_sig, new_cert_sig)

# b) Certificate Date and Place format: DATE: ____________________ \n\n PLACE: ____________________
old_cert_date = """    p.append(Paragraph("<b>Date:</b> [DD/MM/YYYY]<br/><b>Place:</b> Ahmedabad", ParagraphStyle('CertDate', fontName='Times-Roman', fontSize=9.5, leading=13.5)))"""
new_cert_date = """    p.append(Paragraph("<b>DATE:</b> ____________________<br/><br/><b>PLACE:</b> ____________________", ParagraphStyle('CertDate', fontName='Times-Roman', fontSize=9.5, leading=14)))"""

assert old_cert_date in pdf_code, "Error: old_cert_date not found in build_50page_report.py!"
pdf_code = pdf_code.replace(old_cert_date, new_cert_date)
print("[PDF] 4. Updated Certificate signature to 'College of Technology' and blank DATE / PLACE format.")

# 1.5 Declaration Page (Page 3):
# a) Remove Date and Place completely
old_dec_date_block = """    p.append(Spacer(1, 30))
    p.append(Paragraph("<b>Place:</b> Ahmedabad<br/><b>Date:</b> [DD/MM/YYYY]", ParagraphStyle('DecDate', fontName='Times-Roman', fontSize=9.5, leading=13.5)))"""

assert old_dec_date_block in pdf_code, "Error: old_dec_date_block not found in build_50page_report.py!"
pdf_code = pdf_code.replace(old_dec_date_block, "")

# b) Update Declaration guide institution to "College of Technology"
old_dec_inst = "Silver Oak College of Technology, Silver Oak University, Ahmedabad."
new_dec_inst = "College of Technology, Silver Oak University, Ahmedabad."
pdf_code = pdf_code.replace(old_dec_inst, new_dec_inst)
print("[PDF] 5. Completely removed Place and Date from Declaration page.")

# 1.6 Acknowledgement Page (Page 4):
# Update guide institution to "College of Technology"
old_ack_inst = "Silver Oak College of Technology, for his"
new_ack_inst = "College of Technology, for his"
pdf_code = pdf_code.replace(old_ack_inst, new_ack_inst)
print("[PDF] 6. Updated Acknowledgement guide institution text.")

# 1.7 Table of Contents Headings (Pages 10 and 11):
# Remove "PART 1" and "PART 2" -> Both pages titled simply "TABLE OF CONTENTS"
old_toc1 = 'p.append(Paragraph("TABLE OF CONTENTS (PART 1)", ParagraphStyle(\'TocTitle1\', fontName=\'Times-Bold\', fontSize=15, leading=19, alignment=1, spaceBefore=4, spaceAfter=8, textColor=colors.black)))'
new_toc1 = 'p.append(Paragraph("TABLE OF CONTENTS", ParagraphStyle(\'TocTitle1\', fontName=\'Times-Bold\', fontSize=15, leading=19, alignment=1, spaceBefore=4, spaceAfter=8, textColor=colors.black)))'

old_toc2 = 'p.append(Paragraph("TABLE OF CONTENTS (PART 2)", ParagraphStyle(\'TocTitle2\', fontName=\'Times-Bold\', fontSize=15, leading=19, alignment=1, spaceBefore=4, spaceAfter=8, textColor=colors.black)))'
new_toc2 = 'p.append(Paragraph("TABLE OF CONTENTS", ParagraphStyle(\'TocTitle2\', fontName=\'Times-Bold\', fontSize=15, leading=19, alignment=1, spaceBefore=4, spaceAfter=8, textColor=colors.black)))'

assert old_toc1 in pdf_code, "Error: old_toc1 not found in build_50page_report.py!"
assert old_toc2 in pdf_code, "Error: old_toc2 not found in build_50page_report.py!"
pdf_code = pdf_code.replace(old_toc1, new_toc1)
pdf_code = pdf_code.replace(old_toc2, new_toc2)
print("[PDF] 7. Updated Table of Contents headings: Removed 'PART 1' and 'PART 2', both titled simply 'TABLE OF CONTENTS'.")

with open(pdf_gen_path, 'w', encoding='utf-8') as f:
    f.write(pdf_code)
print("Successfully saved updated build_50page_report.py\n")


# ==============================================================================
# 2. UPDATE build_final_docx.py (Master Editable DOCX Generator)
# ==============================================================================
docx_gen_path = 'Final_Project_Report/build_final_docx.py'
with open(docx_gen_path, 'r', encoding='utf-8') as f:
    docx_code = f.read()

# 2.1 Add schema-safe sort_sectPr and set_section_page_numbering helpers
sectpr_helpers = """SECTPR_SCHEMA_ORDER = [
    'headerReference', 'footerReference', 'footnotePr', 'endnotePr', 'type',
    'pgSz', 'pgMar', 'paperSrc', 'pgBorders', 'lnNumType', 'pgNumType',
    'cols', 'formProt', 'vAlign', 'noEndnote', 'titlePg', 'textDirection',
    'bidi', 'rtlGutter', 'docGrid', 'printerSettings', 'sectPrChange'
]
SECTPR_ORDER_MAP = {tag: i for i, tag in enumerate(SECTPR_SCHEMA_ORDER)}

def sort_sectPr(sectPr):
    children = list(sectPr)
    children_sorted = sorted(children, key=lambda c: SECTPR_ORDER_MAP.get(c.tag.split('}')[-1], 999))
    for c in children:
        sectPr.remove(c)
    for c in children_sorted:
        sectPr.append(c)

def set_section_page_numbering(section, fmt="decimal", start=1):
    sectPr = section._sectPr
    for c in list(sectPr):
        if c.tag.endswith('pgNumType'):
            sectPr.remove(c)
    pgNumType = OxmlElement('w:pgNumType')
    pgNumType.set(qn('w:fmt'), fmt)
    if start is not None:
        pgNumType.set(qn('w:start'), str(start))
    sectPr.append(pgNumType)
    sort_sectPr(sectPr)
"""

old_add_pn = """def add_native_page_number(paragraph):
    # Standard OpenXML compliant dynamic page numbering with w:fldChar
    r_start = paragraph.add_run('- ')
    r_start.font.name = 'Times New Roman'
    r_start.font.size = Pt(9.5)
    r_start.font.bold = True
    
    r_b = paragraph.add_run()
    fc_b = OxmlElement('w:fldChar')
    fc_b.set(qn('w:fldCharType'), 'begin')
    r_b._r.append(fc_b)
    
    r_i = paragraph.add_run()
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = ' PAGE '
    r_i._r.append(it)
    
    r_s = paragraph.add_run()
    fc_s = OxmlElement('w:fldChar')
    fc_s.set(qn('w:fldCharType'), 'separate')
    r_s._r.append(fc_s)
    
    r_v = paragraph.add_run('1')
    r_v.font.name = 'Times New Roman'
    r_v.font.size = Pt(9.5)
    r_v.font.bold = True
    
    r_e = paragraph.add_run()
    fc_e = OxmlElement('w:fldChar')
    fc_e.set(qn('w:fldCharType'), 'end')
    r_e._r.append(fc_e)
    
    r_end = paragraph.add_run(' -')
    r_end.font.name = 'Times New Roman'
    r_end.font.size = Pt(9.5)
    r_end.font.bold = True"""

new_add_pn = sectpr_helpers + """
def add_native_page_number(paragraph, default_val='1'):
    # Standard OpenXML compliant dynamic page numbering with w:fldChar
    r_start = paragraph.add_run('- ')
    r_start.font.name = 'Times New Roman'
    r_start.font.size = Pt(9.5)
    r_start.font.bold = True
    
    r_b = paragraph.add_run()
    fc_b = OxmlElement('w:fldChar')
    fc_b.set(qn('w:fldCharType'), 'begin')
    r_b._r.append(fc_b)
    
    r_i = paragraph.add_run()
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = ' PAGE '
    r_i._r.append(it)
    
    r_s = paragraph.add_run()
    fc_s = OxmlElement('w:fldChar')
    fc_s.set(qn('w:fldCharType'), 'separate')
    r_s._r.append(fc_s)
    
    r_v = paragraph.add_run(default_val)
    r_v.font.name = 'Times New Roman'
    r_v.font.size = Pt(9.5)
    r_v.font.bold = True
    
    r_e = paragraph.add_run()
    fc_e = OxmlElement('w:fldChar')
    fc_e.set(qn('w:fldCharType'), 'end')
    r_e._r.append(fc_e)
    
    r_end = paragraph.add_run(' -')
    r_end.font.name = 'Times New Roman'
    r_end.font.size = Pt(9.5)
    r_end.font.bold = True"""

assert old_add_pn in docx_code, "Error: old_add_pn not found in build_final_docx.py!"
docx_code = docx_code.replace(old_add_pn, new_add_pn)
print("[DOCX] 1. Added sort_sectPr and set_section_page_numbering helpers.")

# 2.2 Update Section 1 initialization: Leave Header and Footer EMPTY for Page 1!
old_sec1_init = """    # Page Setup: A4 (8.27 x 11.69 inches)
    # Margins: Left = 1.25 in (binding), Right = 1.0 in, Top = 1.0 in, Bottom = 1.0 in
    sec = doc.sections[0]
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    sec.top_margin = Inches(1.0)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(1.25)
    sec.right_margin = Inches(1.0)
    sec.different_first_page_header_footer = False
    
    # Setup Header for Pages 2+
    header = sec.header
    p_hdr = header.paragraphs[0]
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hdr.paragraph_format.space_after = Pt(4)
    p_hdr.paragraph_format.space_before = Pt(0)
    r_hdr = p_hdr.add_run()
    if os.path.exists('Final_Project_Report/assets/p5_img0_X21.png'):
        r_hdr.add_picture('Final_Project_Report/assets/p5_img0_X21.png', width=Inches(5.2))
        
    # Setup Footer for All Pages: 100% Native Standard Word Footer with Right Tab Stop
    footer = sec.footer
    p_ftr = footer.paragraphs[0]
    p_ftr.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_ftr.paragraph_format.space_before = Pt(6)
    p_ftr.paragraph_format.space_after = Pt(0)
    p_ftr.paragraph_format.line_spacing = 1.0
    
    # Add native right-aligned tab stop at 6.02 inches (8669 dxa) matching right margin exactly
    from docx.enum.text import WD_TAB_ALIGNMENT
    p_ftr.paragraph_format.tab_stops.add_tab_stop(Inches(6.02), WD_TAB_ALIGNMENT.RIGHT)
    
    r_ftxt = p_ftr.add_run('Silver Oak University | Department of Computer Science and Engineering | PBL-I')
    r_ftxt.font.name = 'Times New Roman'
    r_ftxt.font.size = Pt(8.5)
    r_ftxt.font.italic = True
    r_ftxt.font.color.rgb = RGBColor(100, 100, 100)
    
    # Jump tab directly to right margin
    p_ftr.add_run('\t')
    
    # Add dynamic page number
    add_native_page_number(p_ftr)"""

new_sec1_init = """    from docx.enum.text import WD_TAB_ALIGNMENT
    from docx.enum.section import WD_SECTION_START

    # Page Setup: A4 (8.27 x 11.69 inches)
    # Margins: Left = 1.25 in (binding), Right = 1.0 in, Top = 1.0 in, Bottom = 1.0 in
    # SECTION 1: FIRST PAGE (Title Page)
    # Strictly NO header banner, NO footer text, NO page number!
    sec = doc.sections[0]
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    sec.top_margin = Inches(1.0)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(1.25)
    sec.right_margin = Inches(1.0)
    sec.different_first_page_header_footer = False
    
    # Ensure Section 1 has empty header and empty footer
    sec.header.paragraphs[0].text = ""
    sec.footer.paragraphs[0].text = ""
    sort_sectPr(sec._sectPr)"""

assert old_sec1_init in docx_code, "Error: old_sec1_init not found in build_final_docx.py!"
docx_code = docx_code.replace(old_sec1_init, new_sec1_init)
print("[DOCX] 2. Configured Section 1 (Title Page): Strictly NO header logo and NO footer/page number.")

# 2.3 Section 2 Break before Certificate (Page 2):
# Creates Section 2, sets unlinked header (with logo) and unlinked footer (with lowerRoman page number restart at 1)
old_p1_end = """        ('Ahmedabad, Gujarat\\n', 12, False),
        ('Academic Year: 2026-2027', 12, True)
    ]
    for text, sz, bld in runs_inst:
        r = p_inst.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(sz)
        r.font.bold = bld
        
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 2: CERTIFICATE"""

new_p1_end = """        ('Ahmedabad, Gujarat\\n', 12, False),
        ('Academic Year: 2026-2027', 12, True)
    ]
    for text, sz, bld in runs_inst:
        r = p_inst.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(sz)
        r.font.bold = bld
        
    # SECTION 2: CERTIFICATE TO KEYWORDS & RESEARCH SCOPE SUMMARY
    # Sequence: Lowercase Roman numerals i, ii, iii, iv, v...
    sec2 = doc.add_section(WD_SECTION_START.NEW_PAGE)
    sec2.page_width = Inches(8.27)
    sec2.page_height = Inches(11.69)
    sec2.top_margin = Inches(1.0)
    sec2.bottom_margin = Inches(1.0)
    sec2.left_margin = Inches(1.25)
    sec2.right_margin = Inches(1.0)
    sec2.header.is_linked_to_previous = False
    sec2.footer.is_linked_to_previous = False
    
    # Header for Section 2 with logo banner (aspect ratio 4.625 preserved)
    p_hdr2 = sec2.header.paragraphs[0]
    p_hdr2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hdr2.paragraph_format.space_after = Pt(4)
    p_hdr2.paragraph_format.space_before = Pt(0)
    r_hdr2 = p_hdr2.add_run()
    if os.path.exists('Final_Project_Report/assets/p5_img0_X21.png'):
        r_hdr2.add_picture('Final_Project_Report/assets/p5_img0_X21.png', width=Inches(4.2))
        
    # Footer for Section 2 with lowercase Roman dynamic page numbering
    p_ftr2 = sec2.footer.paragraphs[0]
    p_ftr2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_ftr2.paragraph_format.space_before = Pt(6)
    p_ftr2.paragraph_format.space_after = Pt(0)
    p_ftr2.paragraph_format.line_spacing = 1.0
    p_ftr2.paragraph_format.tab_stops.add_tab_stop(Inches(6.02), WD_TAB_ALIGNMENT.RIGHT)
    
    r_ftxt2 = p_ftr2.add_run('Silver Oak University | Department of Computer Science and Engineering | PBL-I')
    r_ftxt2.font.name = 'Times New Roman'
    r_ftxt2.font.size = Pt(8.5)
    r_ftxt2.font.italic = True
    r_ftxt2.font.color.rgb = RGBColor(100, 100, 100)
    
    p_ftr2.add_run('\\t')
    add_native_page_number(p_ftr2, default_val='i')
    set_section_page_numbering(sec2, fmt='lowerRoman', start=1)

    # -------------------------------------------------------------
    # PAGE 2: CERTIFICATE"""

assert old_p1_end in docx_code, "Error: old_p1_end not found in build_final_docx.py!"
docx_code = docx_code.replace(old_p1_end, new_p1_end)
print("[DOCX] 3. Created Section 2 with lowerRoman page numbering (i..v) and aspect-ratio-corrected header logo.")

# 2.4 Certificate Date and Place format: DATE: ____________________ \n\n PLACE: ____________________
old_docx_cert_meta = """    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(30)
    p_meta.paragraph_format.space_after = Pt(40)
    r = p_meta.add_run('Date: _________________________\\n\\nPlace: Ahmedabad')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True"""

new_docx_cert_meta = """    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(30)
    p_meta.paragraph_format.space_after = Pt(40)
    r = p_meta.add_run('DATE: ____________________\\n\\nPLACE: ____________________')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True"""

assert old_docx_cert_meta in docx_code, "Error: old_docx_cert_meta not found in build_final_docx.py!"
docx_code = docx_code.replace(old_docx_cert_meta, new_docx_cert_meta)
print("[DOCX] 4. Updated Certificate Date and Place format in DOCX.")

# 2.5 Declaration: Completely remove Date and Place block
old_docx_decl_meta = """    p_d_meta = doc.add_paragraph()
    p_d_meta.paragraph_format.space_before = Pt(28)
    r = p_d_meta.add_run('Date: _________________________\\n\\nPlace: Ahmedabad')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True"""

assert old_docx_decl_meta in docx_code, "Error: old_docx_decl_meta not found in build_final_docx.py!"
docx_code = docx_code.replace(old_docx_decl_meta, "")
print("[DOCX] 5. Completely removed Date and Place from Declaration in DOCX.")

# 2.6 Section 3 Break before List of Figures:
# Creates Section 3, sets unlinked header (with logo) and unlinked footer (with decimal page number restart at 1)
old_lof_start = """    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 6: LIST OF FIGURES"""

new_lof_start = """    # SECTION 3: LIST OF FIGURES TO FINAL PAGE
    # Sequence: Normal Arabic numbering 1, 2, 3, 4, 5... starting with 1 on List of Figures
    sec3 = doc.add_section(WD_SECTION_START.NEW_PAGE)
    sec3.page_width = Inches(8.27)
    sec3.page_height = Inches(11.69)
    sec3.top_margin = Inches(1.0)
    sec3.bottom_margin = Inches(1.0)
    sec3.left_margin = Inches(1.25)
    sec3.right_margin = Inches(1.0)
    sec3.header.is_linked_to_previous = False
    sec3.footer.is_linked_to_previous = False
    
    # Header for Section 3 with logo banner (aspect ratio 4.625 preserved)
    p_hdr3 = sec3.header.paragraphs[0]
    p_hdr3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hdr3.paragraph_format.space_after = Pt(4)
    p_hdr3.paragraph_format.space_before = Pt(0)
    r_hdr3 = p_hdr3.add_run()
    if os.path.exists('Final_Project_Report/assets/p5_img0_X21.png'):
        r_hdr3.add_picture('Final_Project_Report/assets/p5_img0_X21.png', width=Inches(4.2))
        
    # Footer for Section 3 with decimal dynamic page numbering restarting at 1
    p_ftr3 = sec3.footer.paragraphs[0]
    p_ftr3.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_ftr3.paragraph_format.space_before = Pt(6)
    p_ftr3.paragraph_format.space_after = Pt(0)
    p_ftr3.paragraph_format.line_spacing = 1.0
    p_ftr3.paragraph_format.tab_stops.add_tab_stop(Inches(6.02), WD_TAB_ALIGNMENT.RIGHT)
    
    r_ftxt3 = p_ftr3.add_run('Silver Oak University | Department of Computer Science and Engineering | PBL-I')
    r_ftxt3.font.name = 'Times New Roman'
    r_ftxt3.font.size = Pt(8.5)
    r_ftxt3.font.italic = True
    r_ftxt3.font.color.rgb = RGBColor(100, 100, 100)
    
    p_ftr3.add_run('\\t')
    add_native_page_number(p_ftr3, default_val='1')
    set_section_page_numbering(sec3, fmt='decimal', start=1)

    # -------------------------------------------------------------
    # PAGE 6: LIST OF FIGURES"""

assert old_lof_start in docx_code, "Error: old_lof_start not found in build_final_docx.py!"
docx_code = docx_code.replace(old_lof_start, new_lof_start)
print("[DOCX] 6. Created Section 3 with Arabic page numbering starting at 1 on List of Figures.")

with open(docx_gen_path, 'w', encoding='utf-8') as f:
    f.write(docx_code)
print("Successfully saved updated build_final_docx.py\n")

print("=========================================================")
print("  ALL CORRECTIONS APPLIED TO MASTER GENERATORS!")
print("=========================================================")
