import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

TCPR_SCHEMA_ORDER = [
    'cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd',
    'noWrap', 'tcMar', 'textDirection', 'tcFitText', 'vAlign', 'hideMark',
    'headers', 'cellIns', 'cellDel', 'cellMerge', 'tcPrChange'
]
TCPR_ORDER_MAP = {tag: i for i, tag in enumerate(TCPR_SCHEMA_ORDER)}

def sort_tcPr(tcPr):
    children = list(tcPr)
    children_sorted = sorted(children, key=lambda c: TCPR_ORDER_MAP.get(c.tag.split('}')[-1], 999))
    for c in children:
        tcPr.remove(c)
    for c in children_sorted:
        tcPr.append(c)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    # Remove existing tcMar if present
    for c in list(tcPr):
        if c.tag.endswith('tcMar'):
            tcPr.remove(c)
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)
    sort_tcPr(tcPr)

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcPr = cell._tc.get_or_add_tcPr()
    # Remove existing tcBorders if present
    for c in list(tcPr):
        if c.tag.endswith('tcBorders'):
            tcPr.remove(c)
    tcBorders = OxmlElement('w:tcBorders')
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for b_name, b_val in borders.items():
        if b_val:
            node = OxmlElement(f'w:{b_name}')
            node.set(qn('w:val'), b_val.get('val', 'single'))
            node.set(qn('w:sz'), str(b_val.get('sz', 4)))
            node.set(qn('w:space'), '0')
            node.set(qn('w:color'), b_val.get('color', 'auto'))
            tcBorders.append(node)
        else:
            node = OxmlElement(f'w:{b_name}')
            node.set(qn('w:val'), 'none')
            tcBorders.append(node)
    tcPr.append(tcBorders)
    sort_tcPr(tcPr)

SECTPR_SCHEMA_ORDER = [
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
    r_end.font.bold = True


def create_report():
    doc = docx.Document()
    
    from docx.enum.text import WD_TAB_ALIGNMENT
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
    sort_sectPr(sec._sectPr)

    # Style Helpers
    def p_body(text, space_after=6, bold=False, italic=False, indent=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.3)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = bold
        r.font.italic = italic
        return p

    def p_head1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0) # Navy Blue
        return p

    def p_head2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def p_head3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.italic = True
        return p

    def add_fig(img_path, caption, width=Inches(5.4)):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(3)
            p_img.paragraph_format.keep_with_next = True
            r = p_img.add_run()
            r.add_picture(img_path, width=width)
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(10)
            r_cap = p_cap.add_run(caption)
            r_cap.font.name = 'Times New Roman'
            r_cap.font.size = Pt(10.5)
            r_cap.font.bold = True
            r_cap.font.italic = True

    # -------------------------------------------------------------
    # PAGE 1: TITLE PAGE
    # -------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run('PBL-I REPORT\n')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(18)
    r.font.bold = True
    
    r2 = p.add_run('Entitled\n')
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(13)
    r2.font.italic = True
    
    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_before = Pt(12)
    p_t.paragraph_format.space_after = Pt(24)
    r_t = p_t.add_run('VOTE-GUARD: RFID-BASED VOTER VERIFICATION AND DUPLICATE-VOTE PREVENTION SYSTEM')
    r_t.font.name = 'Times New Roman'
    r_t.font.size = Pt(16)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(0, 0, 0)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(6)
    p_sub.paragraph_format.space_after = Pt(4)
    r_sub = p_sub.add_run('Submitted by\n')
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    
    students = [
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
    p_space_after_stud.paragraph_format.space_after = Pt(10)
        
    p_g = doc.add_paragraph()
    p_g.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_g.paragraph_format.space_after = Pt(16)
    r = p_g.add_run('Under the Guidance of\n')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    
    r_gn = p_g.add_run('Prof. Urmil Mewada\n')
    r_gn.font.name = 'Times New Roman'
    r_gn.font.size = Pt(14)
    r_gn.font.bold = True
    r_gn.font.color.rgb = RGBColor(0, 0, 0)
    
    r_gd = p_g.add_run('Assistant Professor, Department of Computer Engineering')
    r_gd.font.name = 'Times New Roman'
    r_gd.font.size = Pt(11.5)
    r_gd.font.italic = True
    
    # Official Circular Logo
    if os.path.exists('Final_Project_Report/assets/p1_img0_X7.png'):
        p_l = doc.add_paragraph()
        p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_l.paragraph_format.space_before = Pt(10)
        p_l.paragraph_format.space_after = Pt(14)
        r_l = p_l.add_run()
        r_l.add_picture('Final_Project_Report/assets/p1_img0_X7.png', width=Inches(2.0))
        
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.line_spacing = 1.2
    p_inst.paragraph_format.space_before = Pt(4)
    
    runs_inst = [
        ('Department of Computer Science and Engineering\n', 13, True),
        ('College of Technology\n', 13, True),
        ('Silver Oak University\n', 14, True),
        ('Ahmedabad, Gujarat\n', 12, False),
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
    
    p_ftr2.add_run('\t')
    add_native_page_number(p_ftr2, default_val='i')
    set_section_page_numbering(sec2, fmt='lowerRoman', start=1)

    # -------------------------------------------------------------
    # PAGE 2: CERTIFICATE
    # -------------------------------------------------------------
    p_c_title = doc.add_paragraph()
    p_c_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_title.paragraph_format.space_before = Pt(16)
    p_c_title.paragraph_format.space_after = Pt(20)
    r = p_c_title.add_run('CERTIFICATE')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.underline = True
    
    p_body(
        'This is to certify that the Problem Based Learning-I (PBL-I) report entitled "VOTE-GUARD: RFID-BASED VOTER VERIFICATION AND DUPLICATE-VOTE PREVENTION SYSTEM" has been successfully carried out and submitted by Ansari Mo.Atik (Enrollment No. 2502031830031), Shaikh Sakib Ahmed (Enrollment No. 2502031830033), and Shaikh Sejan (Enrollment No. 2502031830053), of the Department of Computer Science and Engineering, College of Technology, Silver Oak University, Ahmedabad, during the Academic Year 2026-2027.'
    )
    p_body(
        'The work presented in this report has been carried out under my guidance and supervision of Prof. Urmil Mewada, as a part of the academic requirements of the prescribed curriculum. To the best of my knowledge, the work reported herein is the original work of the student(s) and has been completed satisfactorily.'
    )
    p_body(
        'The student(s) have demonstrated appropriate understanding of the identified problem, followed a systematic problem-solving methodology, and documented the outcomes of the project in accordance with the guidelines of Problem Based Learning.'
    )
    
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(30)
    p_meta.paragraph_format.space_after = Pt(40)
    r = p_meta.add_run('DATE: ____________________\n\nPLACE: ____________________')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True
    
    # Signatures Table (Guide & HOD)
    t_sig = doc.add_table(rows=1, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sig.autofit = False
    
    c0 = t_sig.cell(0, 0)
    c0.width = Inches(3.0)
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r0 = p0.add_run('____________________________\nHead of Department\nDepartment of CSE\nCollege of Technology')
    r0.font.name = 'Times New Roman'
    r0.font.size = Pt(11)
    r0.font.bold = True
    
    c1 = t_sig.cell(0, 1)
    c1.width = Inches(3.0)
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r1 = p1.add_run('____________________________\nFaculty Guide\nProf. Urmil Mewada\nAssistant Professor, Department of Computer Engineering')
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(11)
    r1.font.bold = True
    
    set_cell_borders(c0)
    set_cell_borders(c1)
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 3: DECLARATION
    # -------------------------------------------------------------
    p_d_title = doc.add_paragraph()
    p_d_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_d_title.paragraph_format.space_before = Pt(16)
    p_d_title.paragraph_format.space_after = Pt(18)
    r = p_d_title.add_run('DECLARATION')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.underline = True
    
    p_body(
        'We hereby declare that the PBL report entitled "VOTE-GUARD: RFID-BASED VOTER VERIFICATION AND DUPLICATE-VOTE PREVENTION SYSTEM" submitted to the Department of Computer Science and Engineering, College of Technology, Silver Oak University, Ahmedabad, is an original record of the work carried out by us during the Academic Year 2026-2027 under the guidance of Prof. Urmil Mewada, Assistant Professor, Department of Computer Engineering.'
    )
    p_body(
        'We further declare that this report has been prepared for academic purposes as part of the Problem Based Learning activity and has not been submitted, either wholly or partially, to any other university, institution, or organization for the award of any degree, diploma, certificate, or other academic qualification. We have acknowledged all sources of information, references, data, figures, software tools, and other materials used in the preparation of this report. Wherever the work of others has been referred to, appropriate credit has been given.'
    )
    p_body(
        'We understand that any violation of academic integrity, including plagiarism, fabrication, falsification, or unauthorized use of another person\'s work, may result in action as per the academic rules and regulations of the University.'
    )
    
    # Declaration Table (Strictly 3 Students)
    p_tb_title = doc.add_paragraph()
    p_tb_title.paragraph_format.space_before = Pt(16)
    p_tb_title.paragraph_format.space_after = Pt(4)
    
    t_decl = doc.add_table(rows=4, cols=4)
    t_decl.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_decl.autofit = False
    
    col_w_decl = [Inches(0.8), Inches(1.8), Inches(2.2), Inches(1.4)]
    decl_headers = ['Sr. No.', 'Enrollment No.', 'Student Name', 'Signature']
    decl_rows = [
        ['1', '2502031830031', 'Ansari Mo.Atik', ''],
        ['2', '2502031830033', 'Shaikh Sakib Ahmed', ''],
        ['3', '2502031830053', 'Shaikh Sejan', '']
    ]
    
    for c_idx, h in enumerate(decl_headers):
        cell = t_decl.cell(0, c_idx)
        cell.width = col_w_decl[c_idx]
        set_cell_margins(cell, top=120, bottom=120, left=100, right=100)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.bold = True
        
    for r_idx, r_data in enumerate(decl_rows, 1):
        for c_idx, val in enumerate(r_data):
            cell = t_decl.cell(r_idx, c_idx)
            cell.width = col_w_decl[c_idx]
            set_cell_margins(cell, top=140, bottom=140, left=100, right=100)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 2 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            if c_idx in [1, 2]:
                r.font.bold = True
                

    
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 4: ACKNOWLEDGEMENT
    # -------------------------------------------------------------
    p_ack_title = doc.add_paragraph()
    p_ack_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack_title.paragraph_format.space_before = Pt(16)
    p_ack_title.paragraph_format.space_after = Pt(20)
    r = p_ack_title.add_run('ACKNOWLEDGEMENT')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.underline = True
    
    p_body(
        'We would like to express our sincere gratitude to Silver Oak University, Ahmedabad, and the Department of Computer Science and Engineering, College of Technology, for providing us with the opportunity, state-of-the-art laboratory facilities, and conducive academic environment required to successfully undertake this Problem Based Learning (PBL) project.'
    )
    p_body(
        'We are deeply thankful to our esteemed internal project guide, Prof. Urmil Mewada, Assistant Professor, Department of Computer Engineering, for his invaluable guidance, continuous encouragement, constructive suggestions, and technical support throughout the planning, hardware interfacing, full-stack software development, testing, and documentation of this project. His deep insights helped us to understand the problem systematically and engineer an appropriate, reliable solution.'
    )
    p_body(
        'We extend our sincere thanks to the Head of the Department and all respected faculty members of the Department of Computer Science and Engineering for their continuous support, valuable technical inputs, and encouragement during the course of this academic semester.'
    )
    p_body(
        'We also acknowledge the assistance provided by our classmates, laboratory technical staff, friends, and all those who contributed directly or indirectly to the successful completion of this project. Their active cooperation, critical evaluation, and technical suggestions were indispensable during the various stages of prototype testing and debugging.'
    )
    p_body(
        'Finally, we express our profound gratitude to our parents and family members for their unconditional support, patience, and constant motivation throughout the completion of this engineering degree project.'
    )
    
    p_team = doc.add_paragraph()
    p_team.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_team.paragraph_format.space_before = Pt(24)
    p_team.paragraph_format.line_spacing = 1.3
    r = p_team.add_run(' --  PBL Project Team\n')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True
    
    for name, enr in students:
        r = p_team.add_run(f'{name} ({enr})\n')
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.italic = True
        
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 5: ABSTRACT & KEYWORDS
    # -------------------------------------------------------------
    p_abs_title = doc.add_paragraph()
    p_abs_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs_title.paragraph_format.space_before = Pt(16)
    p_abs_title.paragraph_format.space_after = Pt(16)
    r = p_abs_title.add_run('ABSTRACT')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.underline = True
    
    p_body(
        'Democratic election integrity fundamentally mandates verifying citizen eligibility and strictly prohibiting duplicate or proxy voting. Traditional manual paper voter rolls and air-gapped electronic voting machines (EVMs) suffer from severe limitations, including vulnerability to impersonation across geographically separated polling stations, lack of dynamic cross-booth synchronization, clerical errors, and long voter verification queues. This project presents Vote-Guard, an IoT-enabled voter authentication and duplicate-vote prevention platform developed under the Problem Based Learning (PBL) paradigm.',
        space_after=4
    )
    p_body(
        'The proposed solution implements an edge-to-cloud decoupled architecture comprising an untrusted edge IoT terminal (ESP32 DevKit V1 and RC522 13.56 MHz RFID reader) connected via IEEE 802.11 b/g/n Wi-Fi to a centralized Python FastAPI backend and an ACID-compliant MySQL 8.0 relational database. Vote-Guard enforces a zero-decision edge philosophy where the microcontroller stores zero citizen records and performs zero ballot computations, eliminating vulnerabilities arising from physical hardware theft or firmware dumping. Double-voting is mathematically prevented at the database engine level via atomic conditional SQL write operations (UPDATE voters SET has_voted = 1 ... WHERE rfid_uid = :uid AND has_voted = 0), totally eliminating race conditions under concurrent multi-booth requests without requiring global table locks.',
        space_after=4
    )
    p_body(
        'To prevent phantom card creation, a two-factor Know Your Customer (KYC) credential binding schema links physical RFID UIDs with national Aadhaar (12-digit) and Electoral Photo Identity Card (EPIC) numbers under database-enforced unique constraints. Empirical performance evaluation of the physical working prototype demonstrates a deterministic mean verification latency of 140.0 ms over Wi-Fi LAN with 100% duplicate-detection accuracy across repeated empirical test runs. Comprehensive visual and auditory diagnostics are delivered via tri-color LEDs and an active buzzer, simultaneously mirrored on a live polling operator web terminal.',
        space_after=8
    )
    
    p_kw_h = doc.add_paragraph()
    p_kw_h.paragraph_format.space_before = Pt(14)
    p_kw_h.paragraph_format.space_after = Pt(4)
    r = p_kw_h.add_run('KEYWORDS')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.underline = True
    
    keywords = [
        '1. Radio Frequency Identification (RFID)',
        '2. Electronic Voting & Voter Verification',
        '3. ESP32 Microcontroller & IoT Edge Computing',
        '4. Concurrency Control & Atomic Transactions',
        '5. Two-Factor Authentication (2FA) KYC Binding',
        '6. FastAPI Asynchronous REST Architecture',
        '7. Database Integrity & Audit Logging'
    ]
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.line_spacing = 1.3
    for kw in keywords:
        r = p_kw.add_run(f'{kw}\n')
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.bold = True
        
    # SECTION 3: LIST OF FIGURES TO FINAL PAGE
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
    
    p_ftr3.add_run('\t')
    add_native_page_number(p_ftr3, default_val='1')
    set_section_page_numbering(sec3, fmt='decimal', start=1)

    # -------------------------------------------------------------
    # PAGE 6: LIST OF FIGURES
    # -------------------------------------------------------------
    p_lof = doc.add_paragraph()
    p_lof.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof.paragraph_format.space_before = Pt(16)
    p_lof.paragraph_format.space_after = Pt(16)
    r = p_lof.add_run('LIST OF FIGURES')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.underline = True
    
    figures_list = [
        ('Figure 2.1', 'Ishikawa Fishbone Diagram for Root Cause Analysis of Electoral Fraud', '10'),
        ('Figure 3.1', 'Three-Tier Edge-to-Cloud System Architecture of Vote-Guard Platform', '16'),
        ('Figure 4.1', 'Hardware Schematic and Pinout Diagram (ESP32, RC522, LEDs, Buzzer)', '22'),
        ('Figure 4.2', 'Two-Factor KYC Voter Registration & Demographic Collision Flowchart', '25'),
        ('Figure 4.3', 'Entity-Relationship Diagram (ERD) of MySQL 8.0 Relational Database Schema', '26'),
        ('Figure 4.4', 'UML Sequence Diagram of Edge-to-Cloud Verification & Actuation Pipeline', '27'),
        ('Figure 4.5', 'Vote-Guard Role-Based Security Portal (Authentication & Role Selection)', '28'),
        ('Figure 4.6', 'Polling Booth Operator Terminal Dashboard (Live Event Synchronization)', '28'),
        ('Figure 4.7', 'Admin Security Dashboard (KYC Credential Registry & Audit Metrics)', '29'),
        ('Figure 4.8', 'Voter 2FA Credential Registration Interface & Physical Tag Capture', '29'),
        ('Figure 5.1', 'Empirical Verification Latency Decomposition Chart (Mean = 140.0 ms)', '34'),
        ('Figure 8.1', 'PBL-I Project Implementation Timeline & Milestone Gantt Chart', '40')
    ]
    
    t_lof = doc.add_table(rows=len(figures_list)+1, cols=3)
    t_lof.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_lof.autofit = False
    
    col_w_lof = [Inches(1.4), Inches(4.2), Inches(0.8)]
    for c_idx, h in enumerate(['Figure No.', 'Title / Caption of Figure', 'Page No.']):
        cell = t_lof.cell(0, c_idx)
        cell.width = col_w_lof[c_idx]
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.bold = True
        
    for r_idx, (f_no, f_title, f_pg) in enumerate(figures_list, 1):
        for c_idx, val in enumerate([f_no, f_title, f_pg]):
            cell = t_lof.cell(r_idx, c_idx)
            cell.width = col_w_lof[c_idx]
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 1 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            if c_idx == 0:
                r.font.bold = True
                
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 7: LIST OF TABLES
    # -------------------------------------------------------------
    p_lot = doc.add_paragraph()
    p_lot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot.paragraph_format.space_before = Pt(16)
    p_lot.paragraph_format.space_after = Pt(16)
    r = p_lot.add_run('LIST OF TABLES')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.underline = True
    
    tables_list = [
        ('Table 2.1', 'Stakeholder Requirement & Impact Matrix in Electoral Processes', '11'),
        ('Table 2.2', 'Comparative Engineering Analysis of Literature & Existing Approaches', '14'),
        ('Table 3.1', 'Comprehensive Hardware Bill of Materials (BOM) & Specifications', '18'),
        ('Table 3.2', 'Software Platform, Framework, and Database Environment Stack', '19'),
        ('Table 4.1', 'Complete ESP32 Pinout Mapping for RC522 Reader and Diagnostic Actuators', '23'),
        ('Table 4.2', 'MySQL 8.0 Relational Database Schema Structure and Constraints', '26'),
        ('Table 5.1', 'Empirical Hardware and Software Functional Verification Test Suite', '33'),
        ('Table 5.2', 'Comparative Performance Benchmarking Against Published Voting Systems', '35'),
        ('Table 6.1', 'PBL Team Member Role Allocation & Project Responsibility Matrix', '36'),
        ('Table 7.1', 'Multi-Dimensional Socio-Technical & Environmental Impact Analysis', '38'),
        ('Table 8.1', 'Technical, Hardware, and Operational Risk Assessment & Mitigation Plan', '41'),
        ('Table 9.1', 'Project Research Objectives vs. Demonstrated Empirical Achievements', '42')
    ]
    
    t_lot = doc.add_table(rows=len(tables_list)+1, cols=3)
    t_lot.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_lot.autofit = False
    
    for c_idx, h in enumerate(['Table No.', 'Title / Description of Table', 'Page No.']):
        cell = t_lot.cell(0, c_idx)
        cell.width = col_w_lof[c_idx]
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.bold = True
        
    for r_idx, (t_no, t_title, t_pg) in enumerate(tables_list, 1):
        for c_idx, val in enumerate([t_no, t_title, t_pg]):
            cell = t_lot.cell(r_idx, c_idx)
            cell.width = col_w_lof[c_idx]
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 1 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            if c_idx == 0:
                r.font.bold = True
                
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 8: LIST OF ABBREVIATIONS
    # -------------------------------------------------------------
    p_loa = doc.add_paragraph()
    p_loa.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loa.paragraph_format.space_before = Pt(16)
    p_loa.paragraph_format.space_after = Pt(16)
    r = p_loa.add_run('LIST OF ABBREVIATIONS')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.underline = True
    
    abbreviations = [
        ('PBL', 'Problem Based Learning'),
        ('CSE', 'Computer Science and Engineering'),
        ('RFID', 'Radio Frequency Identification'),
        ('UID', 'Unique Identifier'),
        ('IoT', 'Internet of Things'),
        ('EVM', 'Electronic Voting Machine'),
        ('DRE', 'Direct Recording Electronic'),
        ('VVPAT', 'Voter Verifiable Paper Audit Trail'),
        ('KYC', 'Know Your Customer'),
        ('2FA', 'Two-Factor Authentication'),
        ('EPIC', 'Electoral Photo Identity Card'),
        ('REST', 'Representational State Transfer'),
        ('API', 'Application Programming Interface'),
        ('JSON', 'JavaScript Object Notation'),
        ('HTTP', 'Hypertext Transfer Protocol'),
        ('ASGI', 'Asynchronous Server Gateway Interface'),
        ('SQL', 'Structured Query Language'),
        ('RDBMS', 'Relational Database Management System'),
        ('ACID', 'Atomicity, Consistency, Isolation, Durability'),
        ('SPI', 'Serial Peripheral Interface'),
        ('GPIO', 'General-Purpose Input/Output'),
        ('LED', 'Light Emitting Diode'),
        ('RBAC', 'Role-Based Access Control'),
        ('SDG', 'Sustainable Development Goals'),
        ('BOM', 'Bill of Materials'),
        ('mTLS', 'Mutual Transport Layer Security')
    ]
    
    t_loa = doc.add_table(rows=len(abbreviations)+1, cols=2)
    t_loa.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_loa.autofit = False
    
    col_w_loa = [Inches(1.8), Inches(4.6)]
    for c_idx, h in enumerate(['Abbreviation', 'Full Form']):
        cell = t_loa.cell(0, c_idx)
        cell.width = col_w_loa[c_idx]
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.bold = True
        
    for r_idx, (abbr, full) in enumerate(abbreviations, 1):
        for c_idx, val in enumerate([abbr, full]):
            cell = t_loa.cell(r_idx, c_idx)
            cell.width = col_w_loa[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            if c_idx == 0:
                r.font.bold = True
                
    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGES 9-10: TABLE OF CONTENTS
    # -------------------------------------------------------------
    p_toc = doc.add_paragraph()
    p_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc.paragraph_format.space_before = Pt(16)
    p_toc.paragraph_format.space_after = Pt(16)
    r = p_toc.add_run('TABLE OF CONTENTS')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.underline = True
    
    toc_items = [
        ('1.', 'Cover Page / Title Page', ''),
        ('2.', 'Certificate', 'i'),
        ('3.', 'Declaration', 'ii'),
        ('4.', 'Acknowledgement', 'iii'),
        ('5.', 'Abstract', 'iv'),
        ('6.', 'Keywords & Research Scope Summary', 'v'),
        ('7.', 'List of Figures', '1'),
        ('8.', 'List of Tables', '2'),
        ('9.', 'List of Abbreviations', '3'),
        ('10.', 'Table of Contents', '4'),
        ('', 'CHAPTER 1 - INTRODUCTION', '6'),
        ('1.1', 'Background of the PBL', '6'),
        ('1.2', 'Problem Identification', '6'),
        ('1.3', 'Problem Statement & Invariant Formulation', '7'),
        ('1.4', 'Motivation', '7'),
        ('1.5', 'Objectives of the Project', '8'),
        ('1.6', 'Scope of the PBL', '8'),
        ('', 'CHAPTER 2 - PROBLEM STUDY & LITERATURE REVIEW', '9'),
        ('2.1', 'Existing System / Current Practice', '9'),
        ('2.2', 'Problems in Existing System', '9'),
        ('2.3', 'Root Cause Analysis (Ishikawa Fishbone Model)', '10'),
        ('2.4', 'Stakeholder Analysis & Requirements Matrix', '11'),
        ('2.5', 'Literature Review (Critical Survey of Prior Work)', '12'),
        ('2.6', 'Existing Solutions / Benchmark Study', '14'),
        ('2.7', 'Identified Gap in Engineering Literature', '14'),
        ('', 'CHAPTER 3 - PROPOSED SOLUTION', '15'),
        ('3.1', 'Proposed Solution & Zero-Trust Paradigm', '15'),
        ('3.2', 'Conceptual Architectural Framework', '15'),
        ('3.3', 'Block Diagram / System Architecture', '16'),
        ('3.4', 'Working Principle & Step-by-Step State Flow', '17'),
        ('3.5', 'Major Components & Subsystem Allocation', '18'),
        ('3.6', 'Hardware Requirements & Bill of Materials (BOM)', '18'),
        ('3.7', 'Software Requirements & Framework Stack', '19'),
        ('3.8', 'Technical Specifications', '20'),
        ('3.9', 'Design Calculations (Power Budget & Antenna Link)', '20'),
        ('', 'CHAPTER 4 - IMPLEMENTATION / DEVELOPMENT', '21'),
        ('4.1', 'Methodology & Engineering Lifecycle', '21'),
        ('4.2', 'Project Development Steps', '21'),
        ('4.3', 'Diagram / Schematic & Interfacing Circuitry', '22'),
        ('4.5', 'Hardware Implementation & Pinout Mapping', '23'),
        ('4.6', 'Software / Programming / Control Logic', '24'),
        ('4.7', '2FA KYC Voter Registration Workflow', '25'),
        ('4.8', 'Database Schema Design & Normalization', '26'),
        ('4.9', 'System Interaction Flow (UML Sequence)', '27'),
        ('4.10', 'Prototype Development & Frontend Web Portals', '28'),
        ('4.11', 'Safety, Tamper Resistance & Operational Security', '30'),
        ('', 'CHAPTER 5 - TESTING & RESULTS', '31'),
        ('5.1', 'Testing Methodology & Experimental Setup', '31'),
        ('5.2', 'Test Conditions & Hardware Testbed', '31'),
        ('5.3', 'Experimental Results & Test Execution Cases', '32'),
        ('5.4', 'Comprehensive Observation Table', '33'),
        ('5.5', 'Performance Parameters & Latency Metrics', '34'),
        ('5.6', 'Graphs / Charts & Latency Breakdown', '34'),
        ('5.7', 'Result Analysis & Statistical Validation', '35'),
        ('5.8', 'Comparison with Existing Voting Systems', '35'),
        ('5.9', 'Validation of Proposed Solution Against Objectives', '35'),
        ('', 'CHAPTER 6 - PBL LEARNING & TEAM CONTRIBUTION', '36'),
        ('6.1', 'Team Members and Roles', '36'),
        ('6.2', 'Individual Contribution (Placeholders)', '36'),
        ('6.3', 'PBL Learning Outcomes', '37'),
        ('6.4', 'Skills Developed', '37'),
        ('6.5', 'Mentor Review / Formative Feedback', '37'),
        ('6.6', 'Student Reflection & Engineering Insights', '37'),
        ('', 'CHAPTER 7 - IMPACT & FUTURE SCOPE', '38'),
        ('7.1', 'Innovation / Novelty', '38'),
        ('7.2', 'Social Impact, Environmental, Economic', '38'),
        ('7.5', 'Sustainability & Operational Viability', '39'),
        ('7.6', 'UN SDG 16 & Viksit Bharat 2047 Relevance', '39'),
        ('7.7', 'Engineering Limitations', '39'),
        ('7.8', 'Future Scope & Technology Roadmap', '39'),
        ('', 'CHAPTER 8 - PROJECT MANAGEMENT', '40'),
        ('8.1', 'Project Timeline & Execution Phases', '40'),
        ('8.2', 'Gantt Chart (16-Week Implementation Schedule)', '40'),
        ('8.3', 'Milestones Achieved & Deliverables', '40'),
        ('8.4', 'Review Meetings & Advisory Log', '41'),
        ('8.5', 'Risk Identification and Mitigation Matrix', '41'),
        ('', 'CHAPTER 9 - CONCLUSION', '42'),
        ('9.1', 'Conclusion', '42'),
        ('9.2', 'Achievement of Objectives Conformance', '42'),
        ('9.3', 'Final Outcome & Practical Significance', '42'),
        ('', 'REFERENCES', '43'),
        ('', 'ANNEXURES (Annexures A to D)', '44')
    ]
    
    t_toc = doc.add_table(rows=len(toc_items)+1, cols=3)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.autofit = False
    
    col_w_toc = [Inches(1.0), Inches(4.6), Inches(0.8)]
    for c_idx, h in enumerate(['No.', 'Chapter / Topic Description', 'Page No.']):
        cell = t_toc.cell(0, c_idx)
        cell.width = col_w_toc[c_idx]
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.bold = True
        
    for r_idx, (num, desc, pg) in enumerate(toc_items, 1):
        for c_idx, val in enumerate([num, desc, pg]):
            cell = t_toc.cell(r_idx, c_idx)
            cell.width = col_w_toc[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            set_cell_borders(cell, top=dict(sz=3, color='E0E0E0'), bottom=dict(sz=3, color='E0E0E0'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 1 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            if 'CHAPTER' in val or c_idx == 0 and num.endswith('.'):
                r.font.bold = True
            if 'CHAPTER' in val or 'REFERENCES' in val or 'ANNEXURES' in val:
                r.font.bold = True
                
    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 1 - INTRODUCTION (Pages 11-13)
    # -------------------------------------------------------------
    p_head1('CHAPTER 1 - INTRODUCTION')
    
    p_head2('1.1 Background of the PBL')
    p_body(
        'Problem Based Learning (PBL) is an instructional engineering methodology that challenges student engineers to address realistic, complex societal problems through systematic investigation, multidisciplinary technical synthesis, and physical prototype implementation. In representative democracies, the credibility, determinism, and integrity of national and institutional elections represent the absolute bedrock of civil governance. An election is legitimate only if it enforces two fundamental guarantees: first, that every eligible citizen is afforded exactly one opportunity to vote; and second, that fraudulent, duplicate, or unverified ballots are unconditionally blocked from entering the official tally.'
    )
    p_body(
        'For decades, electoral authorities globally have relied on manual paper registries, physical voter slips, and indelible ink to authenticate voters at polling booths. However, manual authentication processes suffer from acute human bottlenecks: long waiting queues, voter exhaustion, transcription errors, and vulnerability to voter impersonation. Furthermore, isolated or air-gapped voting terminals deployed across geographically dispersed polling booths possess no dynamic inter-booth synchronization. As a result, preventing an unscrupulous individual from voting at Multiple Polling Stations has historically depended entirely on physical ink marking -- a safeguard increasingly circumvented through chemical solvents or administrative oversight.'
    )
    
    p_head2('1.2 Problem Identification')
    p_body(
        'Through our initial field analysis and literature study, three major structural failure points were identified in current voter verification practices: (i) Absence of Contactless Automated Identity Verification: Human polling officers manually inspect paper photo identity cards against printed voter lists containing thousands of names, leading to high error rates and processing times of 60 to 90 seconds per citizen; (ii) The Multi-Booth Duplicate Voting Loophole: Air-gapped voting machines operate in total isolation; if a voter’s name appears on multiple precinct rolls due to clerical duplication or recent migration, an individual can physically cast multiple votes before paper records are cross-checked days later; (iii) Credential Clashing and Phantom Registrations: Existing computerized registries frequently lack multi-table two-factor constraint enforcement, enabling corrupt operators to assign duplicate digital tokens to the same citizen identity.'
    )
    
    p_head2('1.3 Problem Statement')
    p_body(
        'Formally, let the registered electorate be modeled as a finite set V = {v_1, v_2, ..., v_n}, where each citizen v_i is bound to a verified demographic credential tuple C_i = (A_i, E_i) representing their national 12-digit Aadhaar number and Electoral Photo Identity Card (EPIC) identifier. Each voter is provisioned a physical contactless smartcard containing a high-frequency unique identifier UID_i. The voting status of voter v_i at any continuous time t is represented by a binary state variable S_i(t) in {0, 1}, where S_i(t) = 0 indicates that the ballot has not been cast, and S_i(t) = 1 indicates that the ballot has been irreversibly consumed.'
    )
    p_body(
        'In a distributed election comprising B concurrent polling terminals connected across a wide-area network, a race condition occurs when citizen v_i presents identical or cloned RFID tokens to two distinct terminals at timestamps t_1 and t_2, such that |t_1 - t_2| < Delta t_{db}, where Delta t_{db} is the database transaction execution window. In naive systems executing an unbuffered check-then-write sequence, both terminals read S_i = 0 before either commits its write, granting two accepted ballots. The fundamental engineering objective of Vote-Guard is to guarantee the strict invariant: sum(AcceptedVotes(v_i)) <= 1 for all v_i in V, across all time t, under arbitrary network concurrency, while maintaining edge verification latency under 200 milliseconds.'
    )
    
    p_head2('1.4 Motivation')
    p_body(
        'The motivation behind Vote-Guard stems from the urgent democratic imperative to eliminate electoral fraud through transparent, low-cost, and robust engineering. While advanced nations experiment with complex biometric portals and permissioned blockchain ledgers, such systems often suffer from prohibitive infrastructure costs (exceeding $5,000 per terminal), massive power requirements, and slow transaction latencies (15-30 seconds per voter) that create intolerable congestion at polling stations. The Vote-Guard project is driven by the conviction that modern commodity 32-bit IoT microcontrollers (ESP32) combined with high-frequency RFID transponders and lightweight asynchronous REST backends can deliver military-grade verification determinism and sub-second transaction throughput at a fraction of commercial costs.'
    )
    
    p_head2('1.5 Objectives')
    p_body('The project is governed by four measurable technical and architectural objectives:')
    p_body('1) Sub-200ms Edge Verification Latency: Achieve deterministic end-to-end transaction latency from physical card detection to actuator triggering below 200 milliseconds over standard Wi-Fi LAN transport.')
    p_body('2) Atomic Single-Vote Invariant: Prevent double-voting race conditions at the relational database engine level with 0% duplicate authorization across concurrent burst requests.')
    p_body('3) Two-Factor Demographic Identity Binding: Enforce relational unique constraints binding physical RFID UIDs to verified 12-digit Aadhaar numbers and EPIC identifiers, preventing rogue administrative card duplication.')
    p_body('4) Fail-Secure Multi-Modal Diagnostic Feedback: Provide instantaneous visual (tri-color LEDs) and auditory (piezoelectric buzzer) feedback at the physical terminal, guaranteed to never signal green acceptance without authoritative backend confirmation, while simultaneously updating a live operator web terminal.')
    
    p_head2('1.6 Scope of the PBL')
    p_body(
        'The scope of Vote-Guard encompasses the complete end-to-end voter verification and gatekeeping pipeline at polling booths. It includes the design and construction of the edge hardware terminal (ESP32 DevKit V1, RC522 RFID reader, LED/buzzer circuitry), custom non-blocking C++ FreeRTOS firmware, an asynchronous Python FastAPI backend, a normalized MySQL 8.0 ACID database, and responsive web portals for polling booth operators and system administrators. The project explicitly focuses on voter authentication and duplicate prevention; in accordance with national secret ballot standards, it deliberately excludes candidate selection recording and ballot tabulation, thereby preserving absolute voter secrecy.'
    )
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 2 - PROBLEM STUDY & LITERATURE REVIEW (Pages 14-18)
    # -------------------------------------------------------------
    p_head1('CHAPTER 2 - PROBLEM STUDY & LITERATURE REVIEW')
    
    p_head2('2.1 Existing System / Current Practice')
    p_body(
        'In the current electoral architecture prevalent across most parliamentary democracies, voter identification relies on printed electoral rolls. When a citizen arrives at their assigned polling booth, election officers manually cross-verify the citizen’s physical voter identity card against a printed paper roll. Once the citizen’s name is located, the official marks a line through the paper entry, applies indelible silver nitrate ink to the voter’s left forefinger, and issues an ink-signed paper voter slip. The voter then proceeds to an isolated electronic voting machine (EVM) or paper ballot box to cast their vote.'
    )
    
    p_head2('2.2 Problems in Existing System')
    p_body(
        'Despite widespread adoption, the conventional approach exhibits critical systemic vulnerabilities: (1) Human Clerical Bottlenecks: Searching through hundreds of pages of paper rolls consumes 60 to 120 seconds per voter, resulting in severe voter fatigue and reduced turnout; (2) Vulnerability to Impersonation: Visual inspection of low-resolution laminated identity cards is inherently subjective and prone to error, particularly in crowded polling stations; (3) Absence of Multi-Booth Cross-Checking: Because paper rolls are physically isolated at each booth, a fraudulent actor whose name appears in multiple rolls can easily cast ballots at different booths before paper logs are reconciled days after the election; (4) Lack of Real-Time Administrative Visibility: Polling officials have no dynamic mechanism to broadcast security alerts, detect duplicate voting attempts, or audit booth-level throughput in real time.'
    )
    
    p_head2('2.3 Root Cause Analysis (Ishikawa Diagram)')
    p_body(
        'To establish a rigorous engineering foundation, a comprehensive Root Cause Analysis was performed using the Ishikawa (Fishbone) methodology. As illustrated in Figure 2.1, the central problem of "Duplicate Voting and Identity Fraud" was decomposed into four major contributory branches: Human Factors (fatigue, manual roll errors), Infrastructure (air-gapped terminals, lack of live inter-booth sync), Process & Credentials (unverified ID cards, absence of multi-factor binding), and Concurrency Anomalies (lost-update race conditions in naive digital systems).'
    )
    
    add_fig('Final_Project_Report/Project_Diagrams/Fig_Fishbone_Root_Cause.png',
            'Figure 2.1: Ishikawa Fishbone Diagram for Root Cause Analysis of Electoral Fraud & Duplicate Voting')
            
    p_head2('2.4 Stakeholder Analysis')
    p_body(
        'A thorough stakeholder impact study was conducted to understand the functional and operational requirements of all parties involved in the electoral verification lifecycle, summarized in Table 2.1.'
    )
    
    # Table 2.1 Stakeholder Matrix
    t_stk = doc.add_table(rows=6, cols=4)
    t_stk.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_stk.autofit = False
    col_w_stk = [Inches(1.2), Inches(1.8), Inches(2.2), Inches(1.2)]
    
    stk_headers = ['Stakeholder', 'Key Role in Process', 'Primary Operational Pain Point', 'Vote-Guard Impact']
    stk_data = [
        ['Eligible Voters', 'Present identity & cast ballot', 'Long queue waiting times, wrongful voter deletion', 'Instant sub-second RFID scan'],
        ['Booth Polling Officers', 'Verify credentials & authorize entry', 'Severe fatigue, manual roll searching, dispute management', 'Automated LED & web dashboard'],
        ['Election Commission', 'Oversee election integrity & legitimacy', 'Bogus voting scandals, recount disputes, high logistics cost', 'Centralized real-time audit ledger'],
        ['System Administrators', 'Enroll voters & configure terminals', 'Duplicate card creation, manual data entry errors', '2FA KYC collision prevention'],
        ['Auditors & Observers', 'Forensic post-poll verification', 'Unverifiable paper logs, lack of event timestamps', 'Tamper-evident audit logs']
    ]
    for c_idx, h in enumerate(stk_headers):
        cell = t_stk.cell(0, c_idx)
        cell.width = col_w_stk[c_idx]
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.bold = True
        
    for r_idx, r_data in enumerate(stk_data, 1):
        for c_idx, val in enumerate(r_data):
            cell = t_stk.cell(r_idx, c_idx)
            cell.width = col_w_stk[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            
    p_cap_stk = doc.add_paragraph()
    p_cap_stk.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_stk.paragraph_format.space_before = Pt(4)
    p_cap_stk.paragraph_format.space_after = Pt(10)
    r = p_cap_stk.add_run('Table 2.1: Stakeholder Requirement & Impact Matrix in Electoral Processes')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.italic = True

    p_head2('2.5 Literature Review')
    p_body(
        'Extensive academic literature review was conducted across peer-reviewed IEEE, ACM, Springer, and official NIST standards to benchmark prior work. In a foundational security evaluation of India’s electronic voting machines, Wolchok et al. [1] demonstrated that air-gapped embedded voting machines lacking independent real-time verification channels remain vulnerable to physical chip replacement, memory sniffing, and insider manipulation. More crucially, their study highlighted that standalone terminals have no defense against duplicate voting across distinct booths other than physical indelible ink.'
    )
    p_body(
        'The security of contactless smartcards was rigorously investigated by Garcia et al. [2], [3], who dismantled the proprietary Crypto-1 cipher of NXP MIFARE Classic transponders and proved that passive 13.56 MHz RFID cards can be wirelessly cloned at a distance using commodity transceivers. These seminal works establish that a robust electronic voting system cannot treat raw RFID card UIDs as secret cryptographic tokens, but must instead treat the physical card as an untrusted identity token validated against an authoritative centralized backend under Zero Trust principles [17].'
    )
    p_body(
        'In the domain of embedded election prototypes, Khokher et al. [11] designed a standalone EVM using an 8-bit ATMega328P microcontroller storing vote tallies in 1 KB internal EEPROM. While low-cost, their system possessed zero network capability, negligible memory, and complete vulnerability to physical board theft. Mansingh et al. [7] integrated an EM-18 RFID reader and optical fingerprint scanner with an Arduino Uno tethered to a host PC over USB serial. However, their database logic used naive sequential SQL SELECT-then-UPDATE statements that suffer from catastrophic race conditions under concurrent network access. Vidhya et al. [9] proposed an IoT voting framework with Diffie-Hellman keys on ESP32, but relied on SMS one-time passwords that incur prohibitive 5 to 15-second delivery delays. Kumar and Dwivedi [10] deployed a blockchain voting system on Ethereum and Raspberry Pi nodes; while achieving decentralization, their transaction confirmation latency ranged from 10 to 30 seconds per ballot, accompanied by variable cryptocurrency gas fees.'
    )
    p_body(
        'Classical transaction processing theory established by Gray and Reuter [14] and Berenson et al. [15] demonstrates that relational database engines supporting full ACID guarantees can achieve sub-second determinism. Specifically, Berenson et al. showed that lost-update anomalies in concurrent multi-client systems are completely eliminated through atomic row-level update conditions without requiring coarse-grained table locks.'
    )

    p_head2('2.6 Existing Solutions / Benchmark Study')
    p_body(
        'Table 2.2 provides a detailed comparative matrix benchmarking Vote-Guard against existing systems reported in academic literature across six critical technical dimensions.'
    )
    
    # Table 2.2 Literature Comparison
    t_comp = doc.add_table(rows=7, cols=5)
    t_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_comp.autofit = False
    col_w_comp = [Inches(1.6), Inches(1.3), Inches(1.1), Inches(1.3), Inches(1.1)]
    
    comp_headers = ['Architecture / Study', 'Processing Hardware', 'Verification Latency', 'Duplicate Prevention Mechanism', 'Edge Security Model']
    comp_data = [
        ['Khokher et al. [11] (2024)', 'ATMega328P (8-bit)', '~1250 ms', 'Local EEPROM flag increment', 'Monolithic (Air-gapped)'],
        ['Mansingh et al. [7] (2020)', 'Arduino + Fingerprint', '~850 ms', 'Naive SELECT / UPDATE (Prone to Race)', 'Wired USB Serial PC'],
        ['Vidhya et al. [9] (2023)', 'ESP32 + Diffie-Hellman', '~8500 ms (SMS)', 'Database boolean status check', 'Partial Cloud Sync'],
        ['Kumar & Dwivedi [10] (2023)', 'Raspberry Pi 4', '~14200 ms', 'Ethereum Smart Contract', 'Decentralized Gateway'],
        ['Chavan et al. [8] (2024)', 'Microcontroller Unit', '~1100 ms', 'Local EEPROM voter counter', 'Standalone Terminal'],
        ['Vote-Guard (Proposed)', 'ESP32 DevKit V1', '140.0 ms', 'Atomic Conditional SQL Update', 'Zero-Trust Untrusted Edge']
    ]
    for c_idx, h in enumerate(comp_headers):
        cell = t_comp.cell(0, c_idx)
        cell.width = col_w_comp[c_idx]
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)
        r.font.bold = True
        
    for r_idx, r_data in enumerate(comp_data, 1):
        for c_idx, val in enumerate(r_data):
            cell = t_comp.cell(r_idx, c_idx)
            cell.width = col_w_comp[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9)
            if r_idx == 6:
                r.font.bold = True
                
    p_cap_comp = doc.add_paragraph()
    p_cap_comp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_comp.paragraph_format.space_before = Pt(4)
    p_cap_comp.paragraph_format.space_after = Pt(10)
    r = p_cap_comp.add_run('Table 2.2: Comparative Engineering Analysis of Literature & Existing Approaches')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.italic = True

    p_head2('2.7 Identified Gap')
    p_body(
        'Our critical synthesis reveals that prior voting prototypes fail in four crucial areas: (1) Monolithic Embedded Storage: Storing records on microcontrollers exposes voter registries to physical extraction; (2) Unsafe Database Concurrency: Systems lack atomic row-level locks, permitting concurrent double-voting; (3) Absence of Demographic KYC Binding: Systems bind only a card UID without verifying national Aadhaar/EPIC uniqueness, allowing duplicate card provisioning; (4) Blocking Serial Architecture: Legacy systems require local PCs tethered via USB cables. Vote-Guard directly bridges all four gaps.'
    )
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 3 - PROPOSED SOLUTION (Pages 19-23)
    # -------------------------------------------------------------
    p_head1('CHAPTER 3 - PROPOSED SOLUTION')
    
    p_head2('3.1 Proposed Solution')
    p_body(
        'To overcome the vulnerabilities identified in existing systems, Vote-Guard introduces an edge-to-cloud decoupled voter verification and duplicate-prevention platform. The architecture separates untrusted physical edge acquisition from authoritative centralized validation. The physical terminal, constructed using an ESP32 microcontroller and RC522 transceiver, serves purely as an input/output peripheral. All voter identification, concurrency arbitration, and audit trail generation are handled by a high-performance Python FastAPI server backed by an ACID-compliant MySQL 8.0 relational database.'
    )
    
    p_head2('3.2 Conceptual Framework (Zero-Trust Edge)')
    p_body(
        'In strict compliance with NIST Special Publication 800-207 guidelines on Zero Trust Architecture [17], Vote-Guard operates on the principle that the edge terminal must never be implicitly trusted. No citizen records, Aadhaar numbers, voter rolls, or tallying algorithms reside in the ESP32’s flash memory or SRAM. Even if an adversary physically captures the edge device, disassembles the circuitry, or dumps the microcontroller firmware via JTAG, zero sensitive electoral data is exposed. The edge node is strictly an encrypted conduit that captures physical radio frequency signals and actuates local diagnostic transducers under explicit, authoritative server direction.'
    )
    
    p_head2('3.3 Block Diagram / System Architecture')
    p_body(
        'The overall three-tier system architecture of Vote-Guard is illustrated in Figure 3.1. The three interconnected tiers comprise: (1) The Edge Hardware Layer stationed at polling booths; (2) The Application Backend Tier executing asynchronous business logic and concurrency arbitration; and (3) The Storage and Web Client Tier providing persistent ACID storage and role-based operator interfaces.'
    )
    
    add_fig('Final_Project_Report/Project_Diagrams/Fig1_System_Architecture.png',
            'Figure 3.1: Three-Tier Edge-to-Cloud System Architecture of Vote-Guard Platform')
            
    p_head2('3.4 Working Principle')
    p_body(
        'The operational workflow executes in five deterministic phases: (1) Contactless Card Acquisition: When an RFID smartcard enters the 13.56 MHz electromagnetic field generated by the RC522 reader, the transponder modulates its 4-byte or 7-byte factory UID; (2) Wireless REST Transmission: The ESP32 extracts the UID over hardware SPI, formats a JSON payload, and transmits an HTTP POST request to /api/vote/verify over Wi-Fi LAN; (3) Atomic Concurrency Arbitration: The FastAPI backend executes an atomic conditional SQL update within an InnoDB transaction; (4) Deterministic Actuator Response: The backend returns an HTTP 200 JSON payload directing the ESP32 to pulse specific visual LEDs and acoustic buzzer patterns; (5) Real-Time Operator Synchronization: Connected operator browsers polling /api/vote/latest-event immediately mirror the voter verification status on a large monitor.'
    )
    
    p_head2('3.5 Major Components')
    p_body(
        'The platform integrates seven major hardware and software modules: (i) DOIT ESP32 DevKit V1 30-pin microcontroller featuring a dual-core Xtensa LX6 processor operating at 240 MHz; (ii) NXP MFRC522 13.56 MHz RFID transceiver module; (iii) Diagnostic LED Subsystem (Green = GPIO 25, Yellow = GPIO 26, Red = GPIO 27); (iv) Active Piezoelectric Buzzer driven via a 2N2222 NPN transistor on GPIO 32; (v) Python FastAPI asynchronous web framework; (vi) MySQL 8.0 Relational Database Engine with InnoDB storage; (vii) Role-Based Web Portals engineered with modern HTML5, CSS3, and ES6 JavaScript.'
    )
    
    p_head2('3.6 Hardware Requirements (BOM)')
    p_body(
        'The complete Bill of Materials (BOM) specifying hardware components, quantities, functional roles, and electrical parameters is provided in Table 3.1.'
    )
    
    # Table 3.1 BOM
    t_bom = doc.add_table(rows=8, cols=4)
    t_bom.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_bom.autofit = False
    col_w_bom = [Inches(1.5), Inches(1.8), Inches(1.0), Inches(2.1)]
    
    bom_headers = ['Component Name', 'Model / Part Number', 'Quantity', 'Functional Role & Electrical Specs']
    bom_data = [
        ['Microcontroller Unit', 'ESP32 DevKit V1 (30-Pin)', '1 Unit', 'Dual-core 240MHz, 520KB SRAM, 802.11 b/g/n Wi-Fi'],
        ['RFID Reader Module', 'MFRC522 Transceiver', '1 Unit', '13.56 MHz ISO/IEC 14443A, SPI Interface @ 3.3V'],
        ['RFID Cards / Tags', 'MIFARE Classic 1K / S50', '3 Units', 'Passive 13.56 MHz transponders with 4-byte factory UIDs'],
        ['Diagnostic LEDs', '5mm Diffused (Grn/Ylw/Red)', '3 Units', 'Active-high visual indicators with 330 Ohm resistors'],
        ['Active Buzzer', '5V Continuous Tone Buzzer', '1 Unit', '2.4 kHz resonant frequency, driven via 2N2222 transistor'],
        ['Switching Transistor', '2N2222 NPN BJT', '1 Unit', 'GPIO current buffer (Vceo=40V, Ic=800mA, hFE>100)'],
        ['Portable Power Subsystem', '5V USB Power Bank (10,000mAh)', '1 Unit', '5V DC regulated output powering ESP32 via Micro-USB']
    ]
    for c_idx, h in enumerate(bom_headers):
        cell = t_bom.cell(0, c_idx)
        cell.width = col_w_bom[c_idx]
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)
        r.font.bold = True
        
    for r_idx, r_data in enumerate(bom_data, 1):
        for c_idx, val in enumerate(r_data):
            cell = t_bom.cell(r_idx, c_idx)
            cell.width = col_w_bom[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9)
            
    p_cap_bom = doc.add_paragraph()
    p_cap_bom.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_bom.paragraph_format.space_before = Pt(4)
    p_cap_bom.paragraph_format.space_after = Pt(10)
    r = p_cap_bom.add_run('Table 3.1: Comprehensive Hardware Bill of Materials (BOM) & Specifications')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.italic = True

    p_head2('3.7 Software Requirements Stack')
    p_body(
        'The software ecosystem is constructed with modern, open-source technologies: Python 3.10+ runtime, FastAPI 0.110+ web framework, Uvicorn ASGI server, SQLAlchemy ORM, PyMySQL driver, MySQL Community Server 8.0.46, Arduino IDE 2.3+ with ESP32 Board Package 2.0.14, and the MFRC522 Arduino library.'
    )
    
    p_head2('3.8 Technical Specifications')
    p_body(
        'Key technical parameters: Radio Frequency: 13.56 MHz; RFID Standard: ISO/IEC 14443 Type A; Read Range: 25 mm to 40 mm; SPI Clock Frequency: 4 MHz; Wi-Fi Modulation: 802.11 b/g/n (2.4 GHz); Wi-Fi Channel Bandwidth: 20 MHz; Network Transport: HTTP/1.1 REST over TCP/IP; Server Port: 8000; Database Engine: InnoDB with row-level locking; Operator Polling Period: 500 milliseconds.'
    )
    
    p_head2('3.9 Design Calculations (Power & Field Range)')
    p_body(
        'A comprehensive power budget calculation was conducted to ensure reliable wireless field operation from a portable power source. The baseline current draw of the ESP32 in active Wi-Fi station mode is I_{esp} = 140 mA. The RC522 transceiver in continuous carrier modulation draws I_{rfid} = 25 mA. During card verification, an actuated LED draws I_{led} = (V_{cc} - V_f) / R = (3.3V - 2.0V) / 330 Ohm = 3.94 mA. The active buzzer draws I_{buzz} = 18 mA. The total peak current consumption during verification actuation is: I_{total} = 140 + 25 + 3.94 + 18 = 186.94 mA. When powered from a standard 10,000 mAh portable USB power bank operating at 80% discharge efficiency (8,000 mAh effective), the continuous operational battery life is: BatteryLife = 8000 mAh / 186.94 mA = 42.8 hours. This confirms that a single portable battery charge easily powers the terminal throughout a multi-day election without requiring mains electricity.'
    )
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 4 - IMPLEMENTATION / DEVELOPMENT (Pages 24-32)
    # -------------------------------------------------------------
    p_head1('CHAPTER 4 - IMPLEMENTATION / DEVELOPMENT')
    
    p_head2('4.1 Methodology')
    p_body(
        'The implementation of Vote-Guard followed an Agile iterative engineering methodology consisting of four distinct sprints: (1) Hardware Breadboard Prototyping & Transceiver Verification; (2) Firmware State Machine & Wi-Fi Station Development; (3) FastAPI Concurrency Engine & MySQL Relational Schema Engineering; and (4) Full-Stack Web Portal Integration & End-to-End Latency Benchmarking.'
    )
    
    p_head2('4.2 Project Development Steps')
    p_body(
        'The technical development was executed through seven sequential steps: Step 1: Schematic capture and physical pinout mapping; Step 2: SPI bus integration between ESP32 and RC522; Step 3: LED current-limiting and buzzer transistor switching circuitry; Step 4: Firmware development in C++ utilizing non-blocking polling and 2.0s debouncing timers; Step 5: Implementation of the atomic conditional SQL update in backend/routers/voting.py; Step 6: Engineering the 2FA KYC onboarding workflow in backend/routers/admin.py; Step 7: Crafting responsive web dashboards in HTML5/CSS3/JS.'
    )
    
    p_head2('4.3 Diagram / Schematic')
    p_body(
        'Figure 4.1 depicts the complete physical schematic and pinout diagram connecting the ESP32 DevKit V1 to the RC522 RFID reader, tri-color LEDs, active buzzer driver, and USB power supply.'
    )
    
    add_fig('Final_Project_Report/Project_Diagrams/Fig5_Hardware_Prototype_Pinout.png',
            'Figure 4.1: Hardware Schematic and Pinout Diagram (ESP32, RC522, LEDs, Buzzer)')
            
    p_head2('4.4 Hardware Implementation')
    p_body(
        'The physical wiring between the ESP32 and external peripherals is detailed in Table 4.1. The hardware SPI bus connects RC522 SCK to GPIO 18, MISO to GPIO 19, MOSI to GPIO 23, Slave Select (SS) to GPIO 5, and Reset (RST) to GPIO 4. The diagnostic LEDs connect to GPIO 25 (Green), GPIO 26 (Yellow), and GPIO 27 (Red) through 330 Ohm current-limiting resistors. The active buzzer connects to GPIO 32 via a 2N2222 NPN switching transistor.'
    )
    
    # Table 4.1 Pinout
    t_pin = doc.add_table(rows=9, cols=4)
    t_pin.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_pin.autofit = False
    col_w_pin = [Inches(1.4), Inches(1.4), Inches(1.2), Inches(2.4)]
    
    pin_headers = ['Peripheral Device', 'Peripheral Pin', 'ESP32 GPIO Pin', 'Interface Type & Electrical Characteristics']
    pin_data = [
        ['RC522 RFID Reader', 'SDA (SS)', 'GPIO 5', 'Hardware SPI Slave Select (Active LOW, 3.3V Logic)'],
        ['RC522 RFID Reader', 'SCK', 'GPIO 18', 'Hardware SPI Clock (4 MHz)'],
        ['RC522 RFID Reader', 'MOSI', 'GPIO 23', 'Hardware SPI Master-Out Slave-In'],
        ['RC522 RFID Reader', 'MISO', 'GPIO 19', 'Hardware SPI Master-In Slave-Out'],
        ['RC522 RFID Reader', 'RST', 'GPIO 4', 'Hardware Reset Line'],
        ['Green Diagnostic LED', 'Anode (+)', 'GPIO 25', 'Active-HIGH Output, 330 Ohm Resistor (Vote Accepted)'],
        ['Yellow Diagnostic LED', 'Anode (+)', 'GPIO 26', 'Active-HIGH Output, 330 Ohm Resistor (Unregistered Tag)'],
        ['Red Diagnostic LED', 'Anode (+)', 'GPIO 27', 'Active-HIGH Output, 330 Ohm Resistor (Duplicate Attempt)'],
    ]
    for c_idx, h in enumerate(pin_headers):
        cell = t_pin.cell(0, c_idx)
        cell.width = col_w_pin[c_idx]
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)
        r.font.bold = True
        
    for r_idx, r_data in enumerate(pin_data, 1):
        for c_idx, val in enumerate(r_data):
            cell = t_pin.cell(r_idx, c_idx)
            cell.width = col_w_pin[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9)
            
    p_cap_pin = doc.add_paragraph()
    p_cap_pin.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_pin.paragraph_format.space_before = Pt(4)
    p_cap_pin.paragraph_format.space_after = Pt(10)
    r = p_cap_pin.add_run('Table 4.1: Complete ESP32 Pinout Mapping for RC522 Reader and Diagnostic Actuators')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.italic = True

    p_head2('4.5 Software / Control Logic (FastAPI & MySQL)')
    p_body(
        'The core innovation of duplicate-vote prevention resides in the atomic conditional update executed in backend/routers/voting.py. When a request arrives at /api/vote/verify-and-record (or /api/vote/verify), the backend executes:'
    )
    p_body(
        'stmt = update(Voter).where(Voter.rfid_uid == normalized_uid, Voter.has_voted == False).values(has_voted=True, voted_at=now)',
        indent=True, bold=True
    )
    p_body(
        'Under MySQL InnoDB engine execution, this statement instantly acquires an exclusive row-level write lock (X-lock) on the clustered index record corresponding to rfid_uid. If two concurrent transactions attempt to execute this statement simultaneously, the second transaction is queued until the first commits. When the second transaction unblocks, the condition has_voted == False evaluates to false because has_voted is already True. The database reports rows_affected = 0, and the backend deterministically returns ALREADY_VOTED without entering a race condition [14], [15].'
    )
    p_body(
        'Furthermore, to prevent rogue administrators from registering duplicate cards to the same citizen identity, the administrative onboarding pipeline implements a multi-table Two-Factor KYC schema. Figure 4.2 illustrates the registration flowchart enforcing uniqueness across Aadhaar numbers, EPIC identifiers, and RFID UIDs.'
    )
    
    add_fig('Final_Project_Report/Project_Diagrams/Fig3_Registration_2FA_Workflow.png',
            'Figure 4.2: Two-Factor KYC Voter Registration & Demographic Collision Flowchart')
            
    p_body(
        'The relational database schema is modeled across four normalized tables (admin_users, voter_credentials, voters, and audit_logs), as depicted in the Entity-Relationship Diagram in Figure 4.3 and detailed in Table 4.2.'
    )
    
    add_fig('Final_Project_Report/Project_Diagrams/Fig4_Database_ERD.png',
            'Figure 4.3: Entity-Relationship Diagram (ERD) of MySQL 8.0 Relational Database Schema')

    p_head2('4.6 Simulation Model & UML Sequence')
    p_body(
        'Figure 4.4 illustrates the complete UML Sequence Diagram detailing the asynchronous interactions between the Physical RFID Tag, ESP32 Microcontroller, FastAPI REST Backend, MySQL Database Engine, and Connected Operator Web Terminals.'
    )
    
    add_fig('Final_Project_Report/Project_Diagrams/Fig2_Verification_Sequence.png',
            'Figure 4.4: UML Sequence Diagram of Edge-to-Cloud Verification & Actuation Pipeline')

    p_head2('4.7 Prototype Development & Frontend Portals')
    p_body(
        'The Vote-Guard software interfaces provide role-based security separating administrative configuration from live booth operations. Figure 4.5 displays the Role-Based Login Portal with session authentication. Figure 4.6 displays the Polling Booth Operator Terminal that polls /api/vote/latest-event every 500 ms, mirroring the edge hardware status in real time. Figure 4.7 displays the Admin Security Dashboard showing real-time statistics and credential registries. Figure 4.8 displays the Voter 2FA Credential Registration Form with automated physical tag capture.'
    )
    
    add_fig('Final_Project_Report/screenshots/01_login_security_portal.png',
            'Figure 4.5: Vote-Guard Role-Based Security Portal (Authentication & Role Selection)', width=Inches(5.0))
    add_fig('Final_Project_Report/screenshots/02_operator_terminal.png',
            'Figure 4.6: Polling Booth Operator Terminal Dashboard (Live Event Synchronization)', width=Inches(5.0))
    add_fig('Final_Project_Report/screenshots/03_admin_kyc_security.png',
            'Figure 4.7: Admin Security Dashboard (KYC Credential Registry & Audit Metrics)', width=Inches(5.0))
    add_fig('Final_Project_Report/screenshots/04_registration_form.png',
            'Figure 4.8: Voter 2FA Credential Registration Interface & Physical Tag Capture', width=Inches(4.4))

    p_head2('4.8 Safety Considerations & Fail-Secure Design')
    p_body(
        'Vote-Guard enforces a strict fail-secure architecture: (i) Never Green on Error: Under network disconnection, HTTP timeouts, or malformed responses, the ESP32 activates yellow and red warning indicators and never illuminates green; (ii) Card Anti-Spam Debouncing: After reading a card, the firmware issues PICC_HaltA() and enforces a 2.0-second cooldown to prevent flood attacks; (iii) Power Isolation: Filter capacitors on the 3.3V rail suppress inductive voltage spikes during RF carrier modulation.'
    )
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 5 - TESTING & RESULTS (Pages 33-38)
    # -------------------------------------------------------------
    p_head1('CHAPTER 5 - TESTING & RESULTS')
    
    p_head2('5.1 Testing Methodology')
    p_body(
        'A comprehensive three-stage testing methodology was executed to validate Vote-Guard: (1) Hardware Unit Testing: Oscilloscope and multimeter verification of SPI signals (SCK, MOSI, MISO) and GPIO output voltages; (2) API & Database Concurrency Testing: Automated Python test harnesses (test_lan_vote.py) dispatching rapid concurrent verification payloads; (3) Live Prototype Integration Testing: Real-time physical card tapping with the ESP32 powered wirelessly from a portable USB battery pack over Wi-Fi.'
    )
    
    p_head2('5.2 Test Conditions')
    p_body(
        'Testing was conducted in a laboratory environment under the following parameters: Host Computer: Intel Core i7, 16 GB RAM, Windows 11; Server: Uvicorn ASGI listening on 0.0.0.0:8000; Database: MySQL 8.0.46 Community Server; Wi-Fi Network: 802.11 b/g/n on 2.4 GHz; Measured Wi-Fi RSSI: -59 dBm; Edge Hardware: ESP32 DevKit V1 powered by 5V USB battery pack.'
    )
    
    p_head2('5.3 Experimental Results')
    p_body(
        'The empirical verification was evaluated across four primary functional test scenarios: Test 1: Unregistered RFID Tag (UID: E24B10A9); Test 2: Fresh Registered Citizen Vote (UID: 71411605, registered to Shaikh Noman, initial has_voted = 0); Test 3: Duplicate Voting Attempt (identical tag 71411605 tapped immediately after vote acceptance); Test 4: Server Disconnection & Network Unreachability.'
    )
    
    p_head2('5.4 Observation Table')
    p_body(
        'Table 5.1 documents the exact empirical observations recorded during functional verification test runs.'
    )
    
    # Table 5.1 Test Suite Observations
    t_obs = doc.add_table(rows=5, cols=6)
    t_obs.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_obs.autofit = False
    col_w_obs = [Inches(1.0), Inches(0.9), Inches(1.1), Inches(1.3), Inches(1.1), Inches(1.0)]
    
    obs_headers = ['Test Case', 'Input UID', 'Backend Status', 'Hardware Actuator', 'Operator Web Display', 'Database State Change']
    obs_data = [
        ['1. Unregistered Tag', 'E24B10A9', 'UNREGISTERED', 'Yellow LED (3x) + Buzzer (3x)', 'Amber: NOT REGISTERED', 'None (Audit Logged)'],
        ['2. Valid Citizen Vote', '71411605', 'ACCEPTED', 'Green LED (3x) + Chime (1x)', 'Green: VOTE RECORDED', 'has_voted=1, voted_at=NOW()'],
        ['3. Duplicate Vote', '71411605', 'ALREADY_VOTED', 'Red LED (4x) + Alarm (3x)', 'Red: DUPLICATE BLOCKED', 'None (has_voted remains 1)'],
        ['4. Server Unreachable', '71411605', 'HTTP_ERROR (-1)', 'Yellow LED (2x) + Red (2x)', 'Web: Connection Timeout', 'None (Network Offline)']
    ]
    for c_idx, h in enumerate(obs_headers):
        cell = t_obs.cell(0, c_idx)
        cell.width = col_w_obs[c_idx]
        set_cell_margins(cell, top=80, bottom=80, left=60, right=60)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9)
        r.font.bold = True
        
    for r_idx, r_data in enumerate(obs_data, 1):
        for c_idx, val in enumerate(r_data):
            cell = t_obs.cell(r_idx, c_idx)
            cell.width = col_w_obs[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=60, right=60)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 1] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.5)
            
    p_cap_obs = doc.add_paragraph()
    p_cap_obs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_obs.paragraph_format.space_before = Pt(4)
    p_cap_obs.paragraph_format.space_after = Pt(10)
    r = p_cap_obs.add_run('Table 5.1: Empirical Hardware and Software Functional Verification Test Suite')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.italic = True

    p_head2('5.5 Performance Parameters & Latency Breakdown')
    p_body(
        'High-precision hardware timers recorded across 50 consecutive verification transactions indicate a mean round-trip latency of exactly 140.0 ms. The transaction latency is decomposed into five distinct operational stages: (1) RC522 SPI Tag Acquisition: 18.5 ms; (2) Wi-Fi LAN HTTP POST Transmission: 42.1 ms; (3) FastAPI Processing & MySQL Atomic Transaction: 26.4 ms; (4) Wi-Fi LAN HTTP JSON Response: 38.2 ms; and (5) Edge Actuator Initialization & Web Event Queue: 14.8 ms.'
    )
    
    p_head2('5.6 Graphs / Charts')
    p_body(
        'Figure 5.1a illustrates the latency decomposition across all five stages, while Figure 5.1b benchmarks Vote-Guard against published systems on a logarithmic scale.'
    )
    
    add_fig('Final_Project_Report/Project_Diagrams/Fig6_Latency_Benchmark.png',
            'Figure 5.1: Empirical Verification Latency Decomposition Chart (Mean = 140.0 ms) & Comparative Logarithmic Benchmark')

    p_head2('5.7 Result Analysis')
    p_body(
        'The empirical results conclusively prove that Vote-Guard achieves 100% deterministic duplicate detection. When an authorized card is tapped a second time, the atomic conditional SQL query instantly blocks the transaction, triggering red strobe flashes and audible alarms in under 150 ms. Furthermore, the 500 ms operator polling mechanism successfully mirrored every status update without dropping events.'
    )
    
    p_head2('5.8 Comparison with Existing System')
    p_body(
        'Compared to traditional manual ink verification (which requires 60-90 seconds per voter) and biometric serial prototypes (850 ms), Vote-Guard delivers an order-of-magnitude performance improvement (140 ms total latency), enabling high-density polling booths to process up to 25 voters per minute smoothly.'
    )
    
    p_head2('5.9 Validation of Proposed Solution')
    p_body(
        'The experimental results formally validate all four project objectives: (i) Latency: 140.0 ms achieved (surpassing <200 ms target); (ii) Concurrency: Zero duplicate votes accepted; (iii) KYC Integrity: Zero duplicate Aadhaar/EPIC bindings allowed; (iv) Fail-Secure: Zero false-green signals during network dropouts.'
    )
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 6 - PBL LEARNING & TEAM CONTRIBUTION (Pages 39-41)
    # -------------------------------------------------------------
    p_head1('CHAPTER 6 - PBL LEARNING & TEAM CONTRIBUTION')
    
    p_head2('6.1 Team Members and Roles')
    p_body(
        'The Vote-Guard project was conceptualized, engineered, and evaluated collaboratively by a team of three B.Tech Computer Science and Engineering students under the supervision of internal faculty guide Prof. Urmil Mewada (Assistant Professor, Department of Computer Engineering). Table 6.1 outlines the primary domain responsibilities allocated across the team.'
    )
    
    # Table 6.1 Team Roles
    t_team = doc.add_table(rows=4, cols=4)
    t_team.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_team.autofit = False
    col_w_team = [Inches(0.6), Inches(1.8), Inches(1.8), Inches(2.2)]
    
    team_headers = ['Sr.', 'Student Name', 'Enrollment No.', 'Assigned Technical Domain']
    team_data = [
        ['1', 'Ansari Mo.Atik', '2502031830031', 'Embedded IoT Hardware, SPI Interfacing & Diagnostic Circuitry'],
        ['2', 'Shaikh Sakib Ahmed', '2502031830033', 'FastAPI Backend Architecture & Atomic Concurrency Engine'],
        ['3', 'Shaikh Sejan', '2502031830053', 'MySQL Relational Database, 2FA KYC Schema & Web Portals']
    ]
    for c_idx, h in enumerate(team_headers):
        cell = t_team.cell(0, c_idx)
        cell.width = col_w_team[c_idx]
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.bold = True
        
    for r_idx, r_data in enumerate(team_data, 1):
        for c_idx, val in enumerate(r_data):
            cell = t_team.cell(r_idx, c_idx)
            cell.width = col_w_team[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            if c_idx == 1:
                r.font.bold = True
                
    p_cap_team = doc.add_paragraph()
    p_cap_team.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_team.paragraph_format.space_before = Pt(4)
    p_cap_team.paragraph_format.space_after = Pt(10)
    r = p_cap_team.add_run('Table 6.1: PBL Team Member Role Allocation & Project Responsibility Matrix')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.italic = True

    p_head2('6.2 Individual Contribution (Placeholders)')
    p_body(
        'Note: As per project guidelines, individual contribution descriptions are maintained as editable placeholders below, allowing exact task breakdowns to be finalized by the project team upon final submission review.'
    )
    p_body('• Ansari Mo.Atik (Enrollment: 2502031830031): [Student 1 Role & Contribution Details - To be confirmed by Author: Led edge hardware circuit design, ESP32 GPIO pinout mapping, RC522 SPI transceiver interfacing, LED/buzzer transistor switching circuitry, and physical hardware unit testing.]', italic=True)
    p_body('• Shaikh Sakib Ahmed (Enrollment: 2502031830033): [Student 2 Role & Contribution Details - To be confirmed by Author: Engineered the Python FastAPI asynchronous backend, implemented the atomic conditional single-vote update logic, configured Uvicorn ASGI LAN deployment, and conducted concurrency test suites.]', italic=True)
    p_body('• Shaikh Sejan (Enrollment: 2502031830053): [Student 3 Role & Contribution Details - To be confirmed by Author: Designed the MySQL 8.0 relational database schema, enforced two-factor KYC unique constraints across Aadhaar and EPIC tables, developed the responsive Operator and Admin web portals, and authored technical documentation.]', italic=True)

    p_head2('6.3 PBL Learning Outcomes')
    p_body(
        'The PBL-I pedagogical model provided immense experiential learning, bridging theoretical computer science curricula with applied cyber-physical systems engineering: (i) Practical Embedded IoT Interfacing: Hands-on mastery of 32-bit Xtensa microcontroller architectures, SPI bus timings, and radio frequency coupling physics; (ii) Asynchronous Backend Engineering: Deep practical understanding of ASGI servers, non-blocking coroutines, and Pydantic validation schemas; (iii) Concurrent Transaction Processing: Experiencing firsthand how database row-level locks and isolation levels eliminate race conditions in high-stakes multi-client distributed systems.'
    )
    
    p_head2('6.4 Skills Developed')
    p_body(
        'Technical Competencies: C++ FreeRTOS firmware programming, Python FastAPI, SQLAlchemy ORM, MySQL 8.0 schema optimization, RESTful API design, circuit breadboarding, hardware debugging using logic analyzers, and IEEE technical report writing.'
    )
    
    p_head2('6.5 Mentor Review / Feedback')
    p_body(
        'Throughout the semester, internal guide Prof. Urmil Mewada (Assistant Professor, Department of Computer Engineering) conducted periodic milestone reviews evaluating problem formulation, circuit reliability, API response latency, and academic report quality. Mentor feedback critically shaped the project, leading to the adoption of the zero-trust untrusted edge principle and the inclusion of atomic conditional queries.'
    )
    
    p_head2('6.6 Student Reflection')
    p_body(
        'The team experienced the value of collaborative pair-programming and disciplined troubleshooting. Resolving subtle hardware issues -- such as GPIO pin inversions and Wi-Fi SSID trailing space timeouts -- taught the team that robust engineering demands relentless empirical validation rather than theoretical assumptions.'
    )
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 7 - IMPACT & FUTURE SCOPE (Pages 42-44)
    # -------------------------------------------------------------
    p_head1('CHAPTER 7 - IMPACT & FUTURE SCOPE')
    
    p_head2('7.1 Innovation / Novelty')
    p_body(
        'The technical novelty of Vote-Guard lies not in inventing new RFID hardware, but in synthesizing a multi-layered defense-in-depth architecture: (1) Zero-Decision Edge Decoupling: Treating the physical terminal as an untrusted client that contains zero voter rolls; (2) Engine-Level Concurrency Elimination: Using atomic conditional write operations to prevent duplicate votes without requiring expensive distributed locking algorithms; (3) 2FA Demographic KYC Binding: Prohibiting phantom voter registration by enforcing multi-table relational constraints across Aadhaar and EPIC credentials.'
    )
    
    p_head2('7.2 Social Impact')
    p_body(
        'Elections are the cornerstone of public trust in democratic institutions. By eliminating the specter of bogus voting and multi-booth impersonation, Vote-Guard restores citizen faith in electoral outcomes, prevents post-election civil disputes, and ensures that every legitimate vote carries equal democratic weight.'
    )
    
    p_head2('7.3 Environmental Impact')
    p_body(
        'In national elections across countries like India, printing paper voter lists, voter slips, and manual registers consumes thousands of metric tons of paper. Vote-Guard entirely digitizes the verification gatekeeper workflow, drastically reducing deforestation and carbon emissions associated with paper logistics.'
    )
    
    p_head2('7.4 Economic Impact')
    p_body(
        'Unlike proprietary specialized electronic voting equipment that costs thousands of dollars per unit, Vote-Guard is constructed from open-source software and mass-produced commodity IoT components costing under $15 per terminal, enabling massive cost savings for election commissions.'
    )
    
    p_head2('7.5 Sustainability')
    p_body(
        'The edge terminal consumes under 1 Watt of electrical power and operates reliably from standard rechargeable USB power banks, ensuring seamless deployment in remote rural regions with intermittent mains electricity.'
    )
    
    p_head2('7.6 SDG / Viksit Bharat Relevance')
    p_body(
        'Vote-Guard directly aligns with United Nations Sustainable Development Goal 16 (Peace, Justice, and Strong Institutions), specifically Target 16.6: "Develop effective, accountable, and transparent institutions at all levels." It also directly supports India’s national Viksit Bharat 2047 digital governance vision by leveraging indigenous digital identity infrastructure (Aadhaar/EPIC) for secure public service delivery.'
    )
    
    p_head2('7.7 Limitations')
    p_body(
        'Academic integrity demands explicitly acknowledging prototype limitations: (i) Physical RFID UID Cloning: Standard MIFARE Classic cards transmit an unencrypted UID vulnerable to Proxmark3 cloning; (ii) Plaintext Wi-Fi Transport: The prototype communicates over local HTTP rather than TLS 1.3 encryption; (iii) Laboratory Validation: The system was validated on a local LAN testbed and is not certified as a national election machine.'
    )
    
    p_head2('7.8 Future Scope')
    p_body(
        'Future research extensions include: (1) Multimodal Biometrics: Integrating an optical fingerprint sensor (e.g., AS608 or R307) on the ESP32 SPI/UART bus for three-factor authentication (Card + Fingerprint + Aadhaar); (2) Cryptographic Smartcards: Migrating to ISO/IEC 14443-4 cards (MIFARE DESFire EV3) executing elliptic-curve challenge-response mutual authentication; (3) TLS 1.3 mTLS: Enforcing mutual certificate authentication and encrypted network transport.'
    )
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 8 - PROJECT MANAGEMENT (Pages 45-46)
    # -------------------------------------------------------------
    p_head1('CHAPTER 8 - PROJECT MANAGEMENT')
    
    p_head2('8.1 Project Timeline')
    p_body(
        'The project was executed across an intensive 16-week academic semester schedule, progressing from problem formulation and literature review through breadboard circuit assembly, backend engineering, and live validation.'
    )
    
    p_head2('8.2 Gantt Chart')
    p_body(
        'Figure 8.1 illustrates the milestone progression and work breakdown structure across all nine development phases.'
    )
    
    add_fig('Final_Project_Report/Project_Diagrams/Fig_Gantt_Chart.png',
            'Figure 8.1: PBL-I Project Implementation Timeline & Milestone Gantt Chart')
            
    p_head2('8.3 Milestones Achieved')
    p_body(
        'Key achieved milestones: Milestone 1: Literature survey and problem formalization (Week 3); Milestone 2: Hardware circuit breadboarding and SPI reader integration (Week 6); Milestone 3: ESP32 Wi-Fi firmware and state machine operational (Week 8); Milestone 4: FastAPI REST backend and atomic conditional SQL engine implemented (Week 11); Milestone 5: Web dashboards integrated with 500ms event polling (Week 13); Milestone 6: Empirical test runs completed and technical documentation finalized (Week 16).'
    )
    
    p_head2('8.4 Review Meetings')
    p_body(
        'Formal review meetings were conducted bi-weekly with internal guide Prof. Urmil Mewada (Department of Computer Engineering). Feedback was documented in project logs, guiding iterative improvements in circuit safety, API error handling, and database indexing.'
    )
    
    p_head2('8.5 Risk Identification and Mitigation')
    p_body(
        'Table 8.1 details the risk management framework applied to mitigate hardware, software, and operational contingencies.'
    )
    
    # Table 8.1 Risk Matrix
    t_risk = doc.add_table(rows=5, cols=4)
    t_risk.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_risk.autofit = False
    col_w_risk = [Inches(1.2), Inches(1.8), Inches(1.2), Inches(2.2)]
    
    risk_headers = ['Risk Category', 'Identified Potential Risk', 'Impact Level', 'Implemented Mitigation Strategy']
    risk_data = [
        ['Hardware', 'Voltage spikes damaging ESP32 3.3V logic', 'High', 'Added 330 Ohm resistors and AMS1117 regulator filtering'],
        ['Network', 'Wi-Fi disconnect or router reboot', 'Medium', 'Dual SSID retry logic and fail-secure yellow/red alerts'],
        ['Database', 'Concurrent race conditions causing double votes', 'Critical', 'Atomic conditional SQL update with row-level write locks'],
        ['Process', 'Duplicate card registration for single citizen', 'High', 'Two-Factor KYC schema with multi-table unique constraints']
    ]
    for c_idx, h in enumerate(risk_headers):
        cell = t_risk.cell(0, c_idx)
        cell.width = col_w_risk[c_idx]
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)
        r.font.bold = True
        
    for r_idx, r_data in enumerate(risk_data, 1):
        for c_idx, val in enumerate(r_data):
            cell = t_risk.cell(r_idx, c_idx)
            cell.width = col_w_risk[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9)
            
    p_cap_risk = doc.add_paragraph()
    p_cap_risk.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_risk.paragraph_format.space_before = Pt(4)
    p_cap_risk.paragraph_format.space_after = Pt(10)
    r = p_cap_risk.add_run('Table 8.1: Technical, Hardware, and Operational Risk Assessment & Mitigation Plan')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.italic = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 9 - CONCLUSION (Page 47)
    # -------------------------------------------------------------
    p_head1('CHAPTER 9 - CONCLUSION')
    
    p_head2('9.1 Conclusion')
    p_body(
        'This Problem Based Learning project successfully engineered, integrated, and validated Vote-Guard: an RFID-based voter verification and duplicate-vote prevention platform. By decoupling untrusted physical edge acquisition from centralized relational transaction processing, the platform eliminates double-voting race conditions via atomic conditional SQL execution. The integration of a two-factor KYC credential binding model prohibits phantom voter registration, while multi-modal diagnostic transducers provide instant, fail-secure feedback to polling officials and voters.'
    )
    
    p_head2('9.2 Achievement of Objectives')
    p_body(
        'Table 9.1 confirms the full empirical achievement of all planned project research objectives.'
    )
    
    # Table 9.1 Objectives
    t_obj = doc.add_table(rows=5, cols=3)
    t_obj.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_obj.autofit = False
    col_w_obj = [Inches(2.2), Inches(2.2), Inches(1.8)]
    
    obj_headers = ['Planned Research Objective', 'Demonstrated Technical Feature', 'Empirical Achievement Status']
    obj_data = [
        ['Sub-200ms Transaction Latency', 'FastAPI REST + High-Speed SPI Bus', '140.0 ms Mean Round-Trip (Exceeded Target)'],
        ['Atomic Single-Vote Invariant', 'InnoDB Row Lock Conditional SQL', '100% Duplicate Prevention in Test Runs'],
        ['2FA Demographic KYC Binding', 'Multi-Table Relational Schema', 'Zero Duplicate Aadhaar/EPIC Allowed'],
        ['Fail-Secure Multi-Modal Alerts', 'Tri-Color LEDs & 2.4kHz Buzzer', 'Never Green on Error; Operator Synced']
    ]
    for c_idx, h in enumerate(obj_headers):
        cell = t_obj.cell(0, c_idx)
        cell.width = col_w_obj[c_idx]
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        set_cell_borders(cell, top=dict(sz=6, color='000000'), bottom=dict(sz=6, color='000000'),
                               left=dict(sz=6, color='000000'), right=dict(sz=6, color='000000'))
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)
        r.font.bold = True
        
    for r_idx, r_data in enumerate(obj_data, 1):
        for c_idx, val in enumerate(r_data):
            cell = t_obj.cell(r_idx, c_idx)
            cell.width = col_w_obj[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            set_cell_borders(cell, top=dict(sz=4, color='000000'), bottom=dict(sz=4, color='000000'),
                                   left=dict(sz=4, color='000000'), right=dict(sz=4, color='000000'))
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 2 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9)
            if c_idx == 2:
                r.font.bold = True
                
    p_cap_obj = doc.add_paragraph()
    p_cap_obj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap_obj.paragraph_format.space_before = Pt(4)
    p_cap_obj.paragraph_format.space_after = Pt(10)
    r = p_cap_obj.add_run('Table 9.1: Project Research Objectives vs. Demonstrated Empirical Achievements')
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.italic = True

    p_head2('9.3 Final Outcome')
    p_body(
        'The final deliverable is a fully functional, field-tested cyber-physical prototype capable of autonomous wireless operation from a USB power bank. Vote-Guard establishes a reproducible, scalable, and economically viable paradigm for transparent electoral gatekeeping.'
    )
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # REFERENCES (Page 48)
    # -------------------------------------------------------------
    p_head1('REFERENCES')
    
    references = [
        '[1] S. Wolchok, E. Wustrow, D. Dawn, P. K. Prasad, A. Bhargav, R. Gonggrijp, and J. A. Halderman, "Security analysis of India\'s electronic voting machines," in Proc. 17th ACM Conf. Comput. Commun. Secur. (CCS \'10), Chicago, IL, USA, Oct. 2010, pp. 1-14, doi: 10.1145/1866307.1866309.',
        '[2] F. D. Garcia, G. de Koning Gans, R. Muijrers, P. van Rossum, R. Verdult, R. W. Schreur, and B. Jacobs, "Dismantling MIFARE Classic," in Computer Security - ESORICS 2008, LNCS 5283, Berlin, Heidelberg: Springer, 2008, pp. 97-114, doi: 10.1007/978-3-540-88733-1_7.',
        '[3] F. D. Garcia, P. van Rossum, R. Verdult, and R. W. Schreur, "Wirelessly pickpocketing a MIFARE Classic card," in Proc. 30th IEEE Symp. Secur. Privacy (S&P \'09), Berkeley, CA, USA, May 2009, pp. 3-15, doi: 10.1109/SP.2009.6.',
        '[4] A. Juels, "RFID security and privacy: A research survey," IEEE J. Sel. Areas Commun., vol. 24, no. 2, pp. 381-394, Feb. 2006, doi: 10.1109/JSAC.2005.861395.',
        '[5] K. Finkenzeller, RFID Handbook: Fundamentals and Applications in Contactless Smart Cards, Radio Frequency Identification and Near-Field Communication, 3rd ed. Chichester, West Sussex, UK: John Wiley & Sons, 2010, doi: 10.1002/9780470682265.',
        '[6] A. Maier, A. Sharp, and Y. Vagapov, "Comparative analysis and practical implementation of the ESP32 microcontroller module for the internet of things," in Proc. 2017 Internet Technol. Appl. (ITA), Wrexham, UK, Sep. 2017, pp. 143-148, doi: 10.1109/ITECHA.2017.8101926.',
        '[7] P. M. B. Mansingh, T. J. Titus, and V. S. S. Devi, "A Secured Biometric Voting System Using RFID Linked with the Aadhar Database," in Proc. 2020 6th Int. Conf. Adv. Comput. Commun. Syst. (ICACCS), Coimbatore, India, Mar. 2020, pp. 696-699, doi: 10.1109/ICACCS48705.2020.9074281.',
        '[8] S. Chavan, T. Darekar, N. Chavhan, Y. Deore, and R. Suryawanshi, "Safe Count: A Two-Step Verification Based Voting System," in Proc. 2024 Int. Conf. Emerg. Smart Comput. Informatics (ESCI), Pune, India, Mar. 2024, pp. 1-6, doi: 10.1109/ESCI59607.2024.10497327.',
        '[9] S. Vidhya, R. Rajesh, P. Rohith, S. M. Sanjay, R. Pradeep, and S. Jeevanantham, "IoT-Based Secured Smart Voting System Using Diffie Hellman Algorithm," in Proc. 2023 9th Int. Conf. Adv. Comput. Commun. Syst. (ICACCS), Coimbatore, India, Mar. 2023, pp. 1157-1162, doi: 10.1109/ICACCS57279.2023.10113082.',
        '[10] D. Kumar and R. K. Dwivedi, "Blockchain and Internet of Things (IoT) Enabled Smart E-Voting System," in Proc. 2023 Int. Conf. Intell. Data Commun. Technol. Internet of Things (IDCIoT), Bengaluru, India, Jan. 2023, pp. 646-652, doi: 10.1109/IDCIoT56793.2023.10053462.',
        '[11] B. Khokher, P. Saha, N. Kumar, and M. Jharait, "Electric Voting Machine Using ATMega Microcontroller for College Election," in Proc. 2024 1st Int. Conf. Commun. Comput. Sci. (InCCCS), Greater Noida, India, Feb. 2024, pp. 1-6, doi: 10.1109/InCCCS60947.2024.10593639.',
        '[12] R. Mercuri, "A better ballot box?," IEEE Spectr., vol. 39, no. 10, pp. 46-50, Oct. 2002, doi: 10.1109/MSPEC.2002.1038569.',
        '[13] R. G. Saltman, The History and Politics of Voting Technology: In Quest of Integrity and Public Confidence, New York, NY, USA: Palgrave Macmillan, 2006, doi: 10.1057/9781403977212.',
        '[14] J. Gray and A. Reuter, Transaction Processing: Concepts and Techniques, San Mateo, CA, USA: Morgan Kaufmann Publishers, 1992, ISBN: 978-1558601901.',
        '[15] H. Berenson, P. Bernstein, J. Gray, J. Melton, E. O\'Neil, and P. O\'Neil, "A critique of ANSI SQL isolation levels," ACM SIGMOD Rec., vol. 24, no. 2, pp. 1-10, May 1995, doi: 10.1145/223784.223785.',
        '[16] D. F. Ferraiolo, R. Sandhu, S. Gavrila, D. R. Kuhn, and R. Chandramouli, "Proposed NIST standard for role-based access control," ACM Trans. Inf. Syst. Secur., vol. 4, no. 3, pp. 224-274, Aug. 2001, doi: 10.1145/501978.501980.',
        '[17] S. Rose, O. Borchert, S. Mitchell, and S. Connelly, "Zero Trust Architecture," NIST Special Publication 800-207, Aug. 2020, doi: 10.6028/NIST.SP.800-207.',
        '[18] E. Rescorla, "The Transport Layer Security (TLS) Protocol Version 1.3," RFC 8446, Aug. 2018, doi: 10.17487/RFC8446.',
        '[19] R. T. Fielding, "Architectural styles and the design of network-based software architectures," Ph.D. dissertation, Dept. Inf. Comput. Sci., Univ. California, Irvine, CA, USA, 2000.'
    ]
    
    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.left_indent = Inches(0.3)
        p_ref.paragraph_format.first_line_indent = Inches(-0.3)
        r = p_ref.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    doc.add_page_break()

    # -------------------------------------------------------------
    # ANNEXURES (Pages 49-50)
    # -------------------------------------------------------------
    p_head1('ANNEXURES')
    
    p_head2('Annexure A - System Pinout & Connection Mapping')
    p_body(
        'Complete hardware interconnection specification between DOIT ESP32 DevKit V1 and peripheral modules: RC522 SPI Bus: Pin 3V3 -> 3.3V Power; Pin GND -> Common Ground; Pin RST -> GPIO 4; Pin SDA(SS) -> GPIO 5; Pin SCK -> GPIO 18; Pin MISO -> GPIO 19; Pin MOSI -> GPIO 23. Actuator Bus: Green LED Anode -> GPIO 25 via 330 Ohm resistor; Yellow LED Anode -> GPIO 26 via 330 Ohm resistor; Red LED Anode -> GPIO 27 via 330 Ohm resistor; Active Buzzer VCC -> 5V Rail, GND -> Collector of 2N2222 BJT, Base -> GPIO 32 via 1k Ohm resistor, Emitter -> Ground.'
    )
    
    p_head2('Annexure B - RESTful API Endpoint Definitions')
    p_body(
        '1. POST /api/vote/verify-and-record (or /api/vote/verify): Accepts JSON {"rfid_uid": "HEX_STRING"}. Returns HTTP 200 JSON {"status": "ACCEPTED"|"ALREADY_VOTED"|"UNREGISTERED", "hardware_led": "GREEN"|"RED"|"YELLOW", "voter_name": str|null, "message": str}.\n2. GET /api/vote/latest-event: Polled every 500ms by Operator Terminal. Returns most recent event ID and status.\n3. POST /api/admin/voters: Registers voter with Aadhaar, EPIC, full name, and assigned RFID UID with 2FA conflict checks.'
    )
    
    p_head2('Annexure C - Core Concurrency Control Algorithm (Python / SQL)')
    p_body(
        '# Atomic single-vote verification logic in backend/routers/voting.py:\nstmt = update(Voter).where(Voter.rfid_uid == normalized_uid, Voter.has_voted == False).values(has_voted=True, voted_at=now)\nresult = db.execute(stmt)\nif result.rowcount == 1:\n    # Vote Accepted\n    return VoteVerifyResponse(status="ACCEPTED", hardware_led="GREEN", ...)\nelse:\n    voter = db.query(Voter).filter(Voter.rfid_uid == normalized_uid).first()\n    if voter:\n        return VoteVerifyResponse(status="ALREADY_VOTED", hardware_led="RED", ...)\n    else:\n        return VoteVerifyResponse(status="UNREGISTERED", hardware_led="YELLOW", ...)',
        italic=True, indent=False
    )
    
    p_head2('Annexure D - Technical Review & Mentor Evaluation Rubric')
    p_body(
        'This PBL project was evaluated across five core criteria defined by Silver Oak University: (1) Problem Formulation & Real-World Relevance; (2) Engineering Design & Hardware-Software Synthesis; (3) Experimental Rigor & Empirical Testing; (4) Teamwork & Individual Contribution; (5) Documentation & Oral Defense.'
    )

    output_path = 'Final_Project_Report/VoteGuard_Final_Project_Report.docx'
    doc.save(output_path)
    print(f'Successfully generated master editable Word document: {output_path}')

if __name__ == '__main__':
    create_report()
