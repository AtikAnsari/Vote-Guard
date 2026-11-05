import re

with open('Final_Project_Report/build_50page_report.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Define Chapter 4 block to move from toc2 to toc1
ch4_rows = '''        [Paragraph("<b>CHAPTER 4</b>", s_tbl_cell_bold), Paragraph("<b>IMPLEMENTATION / DEVELOPMENT</b>", s_tbl_cell_bold), Paragraph("<b>27</b>", s_tbl_cell_center)],
        [Paragraph("4.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Methodology & Engineering Lifecycle", s_tbl_cell), Paragraph("27", s_tbl_cell_center)],
        [Paragraph("4.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Project Development Steps", s_tbl_cell), Paragraph("27", s_tbl_cell_center)],
        [Paragraph("4.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Diagram / Schematic & Interfacing Circuitry", s_tbl_cell), Paragraph("28", s_tbl_cell_center)],
        [Paragraph("4.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Hardware Implementation & Pinout Mapping", s_tbl_cell), Paragraph("29", s_tbl_cell_center)],
        [Paragraph("4.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Software / Programming / Control Logic", s_tbl_cell), Paragraph("30", s_tbl_cell_center)],
        [Paragraph("4.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2FA KYC Voter Registration Workflow", s_tbl_cell), Paragraph("31", s_tbl_cell_center)],
        [Paragraph("4.8", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Database Schema Design & Normalization", s_tbl_cell), Paragraph("32", s_tbl_cell_center)],
        [Paragraph("4.9", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;System Interaction Flow (UML Sequence)", s_tbl_cell), Paragraph("33", s_tbl_cell_center)],
        [Paragraph("4.10", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Prototype Development & Frontend Web Portals", s_tbl_cell), Paragraph("34", s_tbl_cell_center)],
        [Paragraph("4.11", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Safety, Tamper Resistance & Operational Security", s_tbl_cell), Paragraph("36", s_tbl_cell_center)],'''

# Remove Chapter 4 rows from toc2
text = text.replace(ch4_rows + '\n', '')

# Append Chapter 4 rows to the end of toc1
old_toc1_tail = '''        [Paragraph("3.9", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Design Calculations (Power Budget & Antenna Link)", s_tbl_cell), Paragraph("26", s_tbl_cell_center)]'''
new_toc1_tail = '''        [Paragraph("3.9", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Design Calculations (Power Budget & Antenna Link)", s_tbl_cell), Paragraph("26", s_tbl_cell_center)],\n''' + ch4_rows

text = text.replace(old_toc1_tail, new_toc1_tail)

with open('Final_Project_Report/build_50page_report.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Moved Chapter 4 to Page 10 TOC. TOC is now perfectly balanced!')

