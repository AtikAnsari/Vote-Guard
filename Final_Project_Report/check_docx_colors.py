import re

with open('Final_Project_Report/build_final_docx.py', 'r', encoding='utf-8') as f:
    text = f.read()

fills = re.findall(r'fill="([^"]+)"', text)
print('Fills in docx generator:', set(fills))

colors = re.findall(r"color='([^']+)'", text)
print('Colors in docx generator:', set(colors))

