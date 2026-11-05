import re

with open('Final_Project_Report/build_50page_report.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update on_page footer to draw page number at BOTTOM RIGHT (page_w - right_m)
old_page_num_center = '''        # Automatic Page Number: BOTTOM CENTER of every page
        canvas.setFont('Times-Bold', 9)
        canvas.setFillColor(colors.black)
        printable_center_x = (left_m + page_w - right_m) / 2.0
        canvas.drawCentredString(printable_center_x, bottom_m - 24, f'- {page_num} -')
        canvas.restoreState()'''

new_page_num_right = '''        # Automatic Page Number: BOTTOM RIGHT of every page (zero overlap with footer text)
        canvas.setFont('Times-Bold', 9)
        canvas.setFillColor(colors.black)
        canvas.drawRightString(page_w - right_m, bottom_m - 24, f'- {page_num} -')
        canvas.restoreState()'''

text = text.replace(old_page_num_center, new_page_num_right)

# 2. Update Page 1 Title Page Layout: Compact, neatly aligned student name and enrollment number
old_p1_team = '''    p.append(Paragraph("<b>Submitted by:</b><br/>"
                       "Ansari Mo.Atik &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; En. No: 2502031830031<br/>"
                       "Shaikh Sakib Ahmed &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; En. No: 2502031830033<br/>"
                       "Shaikh Sejan &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; En. No: 2502031830053", s_cov_team))'''

new_p1_team = '''    p.append(Paragraph("<b>Submitted by:</b>", s_cov_sublbl))
    p1_team_data = [
        [Paragraph("Ansari Mo.Atik", ParagraphStyle('StudN1', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=2)),
         Paragraph("–", ParagraphStyle('StudD1', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=1)),
         Paragraph("2502031830031", ParagraphStyle('StudE1', fontName='Times-Roman', fontSize=10.5, leading=14, alignment=0))],
        [Paragraph("Shaikh Sakib Ahmed", ParagraphStyle('StudN2', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=2)),
         Paragraph("–", ParagraphStyle('StudD2', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=1)),
         Paragraph("2502031830033", ParagraphStyle('StudE2', fontName='Times-Roman', fontSize=10.5, leading=14, alignment=0))],
        [Paragraph("Shaikh Sejan", ParagraphStyle('StudN3', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=2)),
         Paragraph("–", ParagraphStyle('StudD3', fontName='Times-Bold', fontSize=10.5, leading=14, alignment=1)),
         Paragraph("2502031830053", ParagraphStyle('StudE3', fontName='Times-Roman', fontSize=10.5, leading=14, alignment=0))]
    ]
    t_p1_team = RLTable(p1_team_data, colWidths=[160, 20, 110])
    t_p1_team.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5)
    ]))
    p.append(t_p1_team)
    p.append(Spacer(1, 10))'''

text = text.replace(old_p1_team, new_p1_team)

# 3. Update guide details on Cover Page: Department of Computer Engineering
text = text.replace("Assistant Professor, Department of Computer Science and Engineering",
                    "Assistant Professor, Department of Computer Engineering")

# 4. Remove extra institutional heading on Page 2 (Certificate)
old_p2_head = '''    p = pages[1]
    p.append(Spacer(1, 6))
    p.append(Paragraph("SILVER OAK COLLEGE OF TECHNOLOGY", ParagraphStyle('CertInst', fontName='Times-Bold', fontSize=13, leading=16, alignment=1, textColor=colors.black)))
    p.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", ParagraphStyle('CertDept', fontName='Times-Bold', fontSize=11, leading=14, alignment=1, spaceAfter=6)))
    p.append(hr())
    p.append(Paragraph("CERTIFICATE", ParagraphStyle('CertTitle', fontName='Times-Bold', fontSize=15, leading=19, alignment=1, spaceBefore=4, spaceAfter=12, textColor=colors.black)))'''

new_p2_head = '''    p = pages[1]
    p.append(Spacer(1, 14))
    p.append(Paragraph("CERTIFICATE", ParagraphStyle('CertTitle', fontName='Times-Bold', fontSize=16, leading=20, alignment=1, spaceBefore=4, spaceAfter=16, textColor=colors.black)))'''

text = text.replace(old_p2_head, new_p2_head)

# Also update guide department in Certificate signature block
text = text.replace("Assistant Professor, Dept. of CSE<br/>Silver Oak College of Technology",
                    "Assistant Professor, Department of Computer Engineering<br/>Silver Oak College of Technology")

# 5. Remove extra institutional heading on Page 3 (Declaration)
old_p3_head = '''    p = pages[2]
    p.append(Spacer(1, 6))
    p.append(Paragraph("SILVER OAK COLLEGE OF TECHNOLOGY", ParagraphStyle('DecInst', fontName='Times-Bold', fontSize=13, leading=16, alignment=1, textColor=colors.black)))
    p.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", ParagraphStyle('DecDept', fontName='Times-Bold', fontSize=11, leading=14, alignment=1, spaceAfter=6)))
    p.append(hr())
    p.append(Paragraph("DECLARATION", ParagraphStyle('DecTitle', fontName='Times-Bold', fontSize=15, leading=19, alignment=1, spaceBefore=4, spaceAfter=12, textColor=colors.black)))'''

new_p3_head = '''    p = pages[2]
    p.append(Spacer(1, 14))
    p.append(Paragraph("DECLARATION", ParagraphStyle('DecTitle', fontName='Times-Bold', fontSize=16, leading=20, alignment=1, spaceBefore=4, spaceAfter=16, textColor=colors.black)))'''

text = text.replace(old_p3_head, new_p3_head)

# Update guide department in Declaration text:
# "...under the academic supervision of Prof. Urmil Mewada, Assistant Professor, Department of Computer Engineering..."
old_dec_guide = '''of <b>Prof. Urmil Mewada</b>, Assistant Professor, Department of Computer Science and Engineering, '''
new_dec_guide = '''of <b>Prof. Urmil Mewada</b>, Assistant Professor, Department of Computer Engineering, '''
text = text.replace(old_dec_guide, new_dec_guide)

# 6. Remove extra institutional heading on Page 4 (Acknowledgement)
old_p4_head = '''    p = pages[3]
    p.append(Spacer(1, 6))
    p.append(Paragraph("SILVER OAK COLLEGE OF TECHNOLOGY", ParagraphStyle('AckInst', fontName='Times-Bold', fontSize=13, leading=16, alignment=1, textColor=colors.black)))
    p.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", ParagraphStyle('AckDept', fontName='Times-Bold', fontSize=11, leading=14, alignment=1, spaceAfter=6)))
    p.append(hr())
    p.append(Paragraph("ACKNOWLEDGEMENT", ParagraphStyle('AckTitle', fontName='Times-Bold', fontSize=15, leading=19, alignment=1, spaceBefore=4, spaceAfter=12, textColor=colors.black)))'''

new_p4_head = '''    p = pages[3]
    p.append(Spacer(1, 14))
    p.append(Paragraph("ACKNOWLEDGEMENT", ParagraphStyle('AckTitle', fontName='Times-Bold', fontSize=16, leading=20, alignment=1, spaceBefore=4, spaceAfter=16, textColor=colors.black)))'''

text = text.replace(old_p4_head, new_p4_head)

# Update guide department in Acknowledgement text:
old_ack_guide = '''Internal Project Guide, <b>Prof. Urmil Mewada</b>, "         "Assistant Professor, Department of Computer Science and Engineering, '''
new_ack_guide = '''Internal Project Guide, <b>Prof. Urmil Mewada</b>, "         "Assistant Professor, Department of Computer Engineering, '''
text = text.replace(old_ack_guide, new_ack_guide)

# 7. Update guide department in Section 6.5 & Section 8.4
text = text.replace("Internal Project Guide <b>Prof. Urmil Mewada</b> provided continuous",
                    "Internal Project Guide <b>Prof. Urmil Mewada</b> (Assistant Professor, Department of Computer Engineering) provided continuous")
text = text.replace("Internal Project Guide <b>Prof. Urmil Mewada</b> at key milestone junctures",
                    "Internal Project Guide <b>Prof. Urmil Mewada</b> (Department of Computer Engineering) at key milestone junctures")

with open('Final_Project_Report/build_50page_report.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated build_50page_report.py successfully with all user corrections!')

