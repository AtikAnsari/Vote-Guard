import re

with open('Final_Project_Report/build_50page_report.py', 'r', encoding='utf-8') as f:
    text = f.read()

hex_colors = set(re.findall(r'HexColor\([\'"]([^\'"]+)[\'"]\)', text))
print('HexColors in PDF generator:', hex_colors)
named_colors = set(re.findall(r'colors\.([a-zA-Z0-9_]+)', text))
print('Named colors in PDF generator:', named_colors)

