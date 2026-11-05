import re

with open('Final_Project_Report/build_final_docx.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update set_cell_margins and set_cell_borders with proper schema sorting
new_cell_helpers = '''TCPR_SCHEMA_ORDER = [
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

def add_native_page_number(paragraph):
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
    r_end.font.bold = True
'''

# Replace from def set_cell_margins up to def create_report
pattern_helpers = re.compile(r'def set_cell_margins\(.*?def create_report\(\):', re.DOTALL)
new_helpers_replacement = new_cell_helpers + '\n\ndef create_report():'
text = pattern_helpers.sub(new_helpers_replacement, text)

# 2. Replace Footer setup in create_report
old_footer_pattern = re.compile(r'# Setup Footer.*?# Style Helpers', re.DOTALL)
new_footer_code = '''# Setup Footer for All Pages: 100% Native Standard Word Footer with Right Tab Stop
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
    p_ftr.add_run('\\t')
    
    # Add dynamic page number
    add_native_page_number(p_ftr)

    # Style Helpers'''

text = old_footer_pattern.sub(new_footer_code, text)

# 3. Add global post-generation schema normalization before saving doc.save()
save_pattern = re.compile(r'doc\.save\([\'"]Final_Project_Report/VoteGuard_Final_Project_Report\.docx[\'"]\)')
new_save_code = '''# Global Schema Normalization to ensure 100% ECMA-376 compliance
    for part in doc.part.related_parts.values():
        if hasattr(part, '_element') and part._element is not None:
            for tcPr in part._element.iter(f'{{{nsdecls("w").split("=")[-1].strip(\'"\')}}}tcPr'):
                sort_tcPr(tcPr)
    for tcPr in doc._body._element.iter(f'{{{nsdecls("w").split("=")[-1].strip(\'"\')}}}tcPr'):
        sort_tcPr(tcPr)
        
    doc.save('Final_Project_Report/VoteGuard_Final_Project_Report.docx')'''

text = save_pattern.sub(new_save_code, text)

with open('Final_Project_Report/build_final_docx.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('build_final_docx.py updated with schema-compliant cell handlers and native footer.')

