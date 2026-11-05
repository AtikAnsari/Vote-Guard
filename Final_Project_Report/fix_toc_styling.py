with open('Final_Project_Report/build_50page_report.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add compact TOC styles
style_def = '''    s_toc_cell = ParagraphStyle('TocCell', fontName='Times-Roman', fontSize=7.5, leading=9.5, alignment=0)
    s_toc_cell_bold = ParagraphStyle('TocCellBold', fontName='Times-Bold', fontSize=7.5, leading=9.5, alignment=0)
    s_toc_cell_center = ParagraphStyle('TocCellCenter', fontName='Times-Roman', fontSize=7.5, leading=9.5, alignment=1)
'''
target_style = "    s_ref_item = ParagraphStyle('RefItem'"
if "s_toc_cell = ParagraphStyle('TocCell'" not in text:
    text = text.replace(target_style, style_def + target_style)

# In toc1_data and toc2_data, replace s_tbl_cell with s_toc_cell
m1 = text.find('toc1_data = [')
m2 = text.find('return doc, pages')
if m1 != -1 and m2 != -1:
    toc_block = text[m1:m2]
    toc_block_new = toc_block.replace('s_tbl_cell_bold', 's_toc_cell_bold')
    toc_block_new = toc_block_new.replace('s_tbl_cell_center', 's_toc_cell_center')
    toc_block_new = toc_block_new.replace('s_tbl_cell', 's_toc_cell')

    # Adjust padding in t_toc1 and t_toc2
    toc_block_new = toc_block_new.replace("('TOPPADDING', (0,0), (-1,-1), 1.2),", "('TOPPADDING', (0,0), (-1,-1), 0.6),")
    toc_block_new = toc_block_new.replace("('BOTTOMPADDING', (0,0), (-1,-1), 1.2)", "('BOTTOMPADDING', (0,0), (-1,-1), 0.6)")

    text = text[:m1] + toc_block_new + text[m2:]

with open('Final_Project_Report/build_50page_report.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated TOC table styling successfully in build_50page_report.py.')

