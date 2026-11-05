import os

with open('Final_Project_Report/build_50page_report.py', 'r', encoding='utf-8') as f:
    text = f.read()

ch3_str = '''        [Paragraph("<b>CHAPTER 3</b>", s_tbl_cell_bold), Paragraph("<b>PROPOSED SOLUTION</b>", s_tbl_cell_bold), Paragraph("<b>21</b>", s_tbl_cell_center)],
        [Paragraph("3.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Proposed Solution & Zero-Trust Paradigm", s_tbl_cell), Paragraph("21", s_tbl_cell_center)],
        [Paragraph("3.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Conceptual Architectural Framework", s_tbl_cell), Paragraph("21", s_tbl_cell_center)],
        [Paragraph("3.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Block Diagram / System Architecture", s_tbl_cell), Paragraph("22", s_tbl_cell_center)],
        [Paragraph("3.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Working Principle & Step-by-Step State Flow", s_tbl_cell), Paragraph("23", s_tbl_cell_center)],
        [Paragraph("3.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Major Components & Subsystem Allocation", s_tbl_cell), Paragraph("24", s_tbl_cell_center)],
        [Paragraph("3.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Hardware Requirements & Bill of Materials (BOM)", s_tbl_cell), Paragraph("24", s_tbl_cell_center)],
        [Paragraph("3.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Software Requirements & Framework Stack", s_tbl_cell), Paragraph("25", s_tbl_cell_center)],
        [Paragraph("3.8", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Technical Specifications", s_tbl_cell), Paragraph("26", s_tbl_cell_center)],
        [Paragraph("3.9", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Design Calculations (Power Budget & Antenna Link)", s_tbl_cell), Paragraph("26", s_tbl_cell_center)],'''

# Remove ch3 from toc2
text = text.replace(ch3_str + '\n', '')

# Add ch3 to the end of toc1
old_toc1_end = '''        [Paragraph("2.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Identified Gap in Engineering Literature", s_tbl_cell), Paragraph("20", s_tbl_cell_center)]'''
new_toc1_end = '''        [Paragraph("2.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Identified Gap in Engineering Literature", s_tbl_cell), Paragraph("20", s_tbl_cell_center)],\n''' + ch3_str

text = text.replace(old_toc1_end, new_toc1_end)

# Also adjust padding in t_toc1 and t_toc2
text = text.replace("('TOPPADDING', (0,0), (-1,-1), 2.8),", "('TOPPADDING', (0,0), (-1,-1), 1.2),")
text = text.replace("('BOTTOMPADDING', (0,0), (-1,-1), 2.8)", "('BOTTOMPADDING', (0,0), (-1,-1), 1.2)")
text = text.replace("('TOPPADDING', (0,0), (-1,-1), 2.2),", "('TOPPADDING', (0,0), (-1,-1), 1.2),")
text = text.replace("('BOTTOMPADDING', (0,0), (-1,-1), 2.2)", "('BOTTOMPADDING', (0,0), (-1,-1), 1.2)")

with open('Final_Project_Report/build_50page_report.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('TOC updated and rebalanced successfully.')

