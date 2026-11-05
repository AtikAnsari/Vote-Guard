import os
import re

with open('Final_Project_Report/build_50page_report.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update on_normal_page / on_cover_page to a unified on_page that draws header on EVERY page
old_template_setup = '''    def on_cover_page(canvas, doc):
        canvas.saveState()
        canvas.restoreState()
        
    def on_normal_page(canvas, doc):
        canvas.saveState()
        if os.path.exists(hdr_logo_path):
            img_w = 340.0
            img_h = 42.0
            canvas.drawImage(hdr_logo_path, (page_w - img_w) / 2.0, page_h - top_m + 16, width=img_w, height=img_h, mask='auto')
            
        canvas.setStrokeColor(colors.HexColor('#CBD5E0'))
        canvas.setLineWidth(0.6)
        canvas.line(left_m, page_h - top_m + 8, page_w - right_m, page_h - top_m + 8)
        
        canvas.line(left_m, bottom_m - 12, page_w - right_m, bottom_m - 12)
        
        canvas.setFont('Times-Italic', 8)
        canvas.setFillColor(colors.HexColor('#4A5568'))
        canvas.drawString(left_m, bottom_m - 24, 'Silver Oak University | Department of Computer Science and Engineering | PBL-I')
        
        # Page Number
        canvas.setFont('Times-Bold', 9)
        canvas.setFillColor(colors.black)
        page_num = canvas.getPageNumber()
        canvas.drawRightString(page_w - right_m, bottom_m - 24, f'- {page_num} -')
        canvas.restoreState()

    frame_cover = Frame(left_m, bottom_m, content_w, content_h, id='f_cover',
                        topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
    frame_normal = Frame(left_m, bottom_m, content_w, content_h - 22, id='f_norm',
                         topPadding=8, bottomPadding=8, leftPadding=0, rightPadding=0)
                         
    pt_cover = PageTemplate(id='CoverPage', frames=[frame_cover], onPage=on_cover_page)
    pt_norm = PageTemplate(id='NormalPage', frames=[frame_normal], onPage=on_normal_page)
    
    doc = BaseDocTemplate(pdf_path, pagesize=A4, leftMargin=left_m, rightMargin=right_m,
                          topMargin=top_m, bottomMargin=bottom_m)
    doc.addPageTemplates([pt_cover, pt_norm])'''

new_template_setup = '''    def on_page(canvas, doc):
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
        
        # Automatic Page Number: BOTTOM CENTER of every page
        canvas.setFont('Times-Bold', 9)
        canvas.setFillColor(colors.black)
        printable_center_x = (left_m + page_w - right_m) / 2.0
        canvas.drawCentredString(printable_center_x, bottom_m - 24, f'- {page_num} -')
        canvas.restoreState()

    frame_all = Frame(left_m, bottom_m, content_w, content_h - 22, id='f_all',
                      topPadding=8, bottomPadding=8, leftPadding=0, rightPadding=0)
                         
    pt_all = PageTemplate(id='UniversalPage', frames=[frame_all], onPage=on_page)
    
    doc = BaseDocTemplate(pdf_path, pagesize=A4, leftMargin=left_m, rightMargin=right_m,
                          topMargin=top_m, bottomMargin=bottom_m)
    doc.addPageTemplates([pt_all])'''

if old_template_setup in text:
    text = text.replace(old_template_setup, new_template_setup)
    print("Replaced template setup.")
else:
    print("Could not find old_template_setup verbatim, checking...")

# 2. Update styles: all heading colors to black
text = re.sub(r"textColor=colors\.HexColor\('#003366'\)", "textColor=colors.black", text)
text = re.sub(r"textColor=colors\.HexColor\('#1A202C'\)", "textColor=colors.black", text)
text = re.sub(r"color=colors\.HexColor\('#003366'\)", "color=colors.black", text)

# 3. Update table styles:
# Change table header background from #003366 to academic light-gray #F2F2F2
text = re.sub(r"\('BACKGROUND', \(0,0\), \(-1,0\), colors\.HexColor\('#003366'\)\)", "('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F2F2F2'))", text)

# Table header text from white to black
text = text.replace("s_tbl_hdr = ParagraphStyle('TblHdr', fontName='Times-Bold', fontSize=8.5, leading=11, alignment=1, textColor=colors.white)",
                    "s_tbl_hdr = ParagraphStyle('TblHdr', fontName='Times-Bold', fontSize=8.5, leading=11, alignment=1, textColor=colors.black)")

# Remove decorative light blue row backgrounds (#EBF8FF) -> white
text = re.sub(r"\('BACKGROUND', \(\d+,\d+\), \(\S+,\S+\), colors\.HexColor\('#EBF8FF'\)\),?", "", text)

# Table borders to crisp black/dark gray #333333
text = re.sub(r"colors\.HexColor\('#CBD5E0'\)", "colors.HexColor('#333333')", text)

# Ensure captions are black
text = text.replace("s_cap = ParagraphStyle('Caption', fontName='Times-BoldItalic', fontSize=8.5, leading=11.5, alignment=1, spaceBefore=2, spaceAfter=5)",
                    "s_cap = ParagraphStyle('Caption', fontName='Times-BoldItalic', fontSize=8.5, leading=11.5, alignment=1, spaceBefore=2, spaceAfter=5, textColor=colors.black)")

with open('Final_Project_Report/build_50page_report.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Applied black-and-white formatting to build_50page_report.py")

