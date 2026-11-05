with open('Final_Project_Report/build_final_docx.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Enable header on Page 1 as well
text = text.replace('sec.different_first_page_header_footer = True', 'sec.different_first_page_header_footer = False')

# 2. Change all blue heading colors to black
text = text.replace('RGBColor(0, 51, 102)', 'RGBColor(0, 0, 0)')

with open('Final_Project_Report/build_final_docx.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("build_final_docx.py successfully updated to black headings and header on all pages.")

