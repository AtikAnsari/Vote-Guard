import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Image as RLImage, Table as RLTable, TableStyle, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from PIL import Image as PILImage

def get_scaled_img(img_path, max_w=430.0, max_h=280.0):
    if not os.path.exists(img_path):
        return None
    with PILImage.open(img_path) as im:
        w, h = im.size
        ratio = min(max_w / float(w), max_h / float(h), 1.0)
        target_w = float(w) * ratio
        target_h = float(h) * ratio
        return RLImage(img_path, width=target_w, height=target_h)

def create_pdf():
    pdf_path = 'Final_Project_Report/VoteGuard_Final_Project_Report.pdf'
    
    # A4 Dimensions: 595.27 x 841.89 points
    page_w, page_h = A4
    left_m = 90.0   # 1.25 in binding
    right_m = 72.0  # 1.0 in
    top_m = 72.0    # 1.0 in
    bottom_m = 72.0 # 1.0 in
    
    content_w = page_w - left_m - right_m  # 433.27 pt
    content_h = page_h - top_m - bottom_m  # 697.89 pt
    
    # Header logo banner path
    hdr_logo_path = 'Final_Project_Report/assets/p5_img0_X21.png'
    
    def on_cover_page(canvas, doc):
        canvas.saveState()
        # No header and no footer on cover page
        canvas.restoreState()
        
    def on_normal_page(canvas, doc):
        canvas.saveState()
        # Top Header Logo
        if os.path.exists(hdr_logo_path):
            img_w = 340.0
            img_h = 42.0
            canvas.drawImage(hdr_logo_path, (page_w - img_w) / 2.0, page_h - top_m + 16, width=img_w, height=img_h, mask='auto')
            
        # Header thin rule
        canvas.setStrokeColor(colors.HexColor('#CBD5E0'))
        canvas.setLineWidth(0.6)
        canvas.line(left_m, page_h - top_m + 8, page_w - right_m, page_h - top_m + 8)
        
        # Footer rule
        canvas.line(left_m, bottom_m - 12, page_w - right_m, bottom_m - 12)
        
        # Footer text
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
    frame_normal = Frame(left_m, bottom_m, content_w, content_h - 20, id='f_norm',
                         topPadding=10, bottomPadding=10, leftPadding=0, rightPadding=0)
                         
    pt_cover = PageTemplate(id='CoverPage', frames=[frame_cover], onPage=on_cover_page)
    pt_norm = PageTemplate(id='NormalPage', frames=[frame_normal], onPage=on_normal_page)
    
    doc = BaseDocTemplate(pdf_path, pagesize=A4, leftMargin=left_m, rightMargin=right_m,
                          topMargin=top_m, bottomMargin=bottom_m)
    doc.addPageTemplates([pt_cover, pt_norm])
    
    # -------------------------------------------------------------
    # STYLES DEFINITION
    # -------------------------------------------------------------
    s_title1 = ParagraphStyle('Title1', fontName='Times-Bold', fontSize=18, leading=22, alignment=1, spaceAfter=8)
    s_title2 = ParagraphStyle('Title2', fontName='Times-Italic', fontSize=12, leading=15, alignment=1, spaceAfter=14)
    s_pbl_title = ParagraphStyle('PBLTitle', fontName='Times-Bold', fontSize=15, leading=19, alignment=1, spaceAfter=22, textColor=colors.HexColor('#003366'))
    s_sub_label = ParagraphStyle('SubLabel', fontName='Times-Bold', fontSize=12, leading=15, alignment=1, spaceAfter=8)
    s_stud_names = ParagraphStyle('StudNames', fontName='Times-Bold', fontSize=11, leading=16, alignment=1, spaceAfter=18)
    s_guide_sec = ParagraphStyle('GuideSec', fontName='Times-Roman', fontSize=11, leading=15, alignment=1, spaceAfter=18)
    s_inst_block = ParagraphStyle('InstBlock', fontName='Times-Roman', fontSize=11, leading=15, alignment=1, spaceAfter=0)
    
    s_h1 = ParagraphStyle('Head1', fontName='Times-Bold', fontSize=14, leading=18, alignment=0, spaceBefore=14, spaceAfter=6, keepWithNext=True, textColor=colors.HexColor('#003366'))
    s_h2 = ParagraphStyle('Head2', fontName='Times-Bold', fontSize=12, leading=16, alignment=0, spaceBefore=10, spaceAfter=4, keepWithNext=True)
    s_h3 = ParagraphStyle('Head3', fontName='Times-BoldItalic', fontSize=11, leading=14, alignment=0, spaceBefore=8, spaceAfter=2, keepWithNext=True)
    
    s_body = ParagraphStyle('BodyText', fontName='Times-Roman', fontSize=10.5, leading=14.5, alignment=4, spaceBefore=0, spaceAfter=5, firstLineIndent=14)
    s_body_no_ind = ParagraphStyle('BodyTextNoInd', fontName='Times-Roman', fontSize=10.5, leading=14.5, alignment=4, spaceBefore=0, spaceAfter=5)
    s_cap = ParagraphStyle('Caption', fontName='Times-BoldItalic', fontSize=9, leading=12, alignment=1, spaceBefore=3, spaceAfter=8)
    s_ref = ParagraphStyle('Ref', fontName='Times-Roman', fontSize=8.5, leading=11.5, alignment=4, spaceBefore=0, spaceAfter=3.5, leftIndent=14, firstLineIndent=-14)

    story = []
    
    # =============================================================
    # PAGE 1: TITLE / COVER PAGE
    # =============================================================
    story.append(Paragraph("PBL-I REPORT", s_title1))
    story.append(Paragraph("Entitled", s_title2))
    story.append(Paragraph("VOTE-GUARD: RFID-BASED VOTER VERIFICATION AND DUPLICATE-VOTE PREVENTION SYSTEM", s_pbl_title))
    
    story.append(Paragraph("Submitted by", s_sub_label))
    story.append(Paragraph("Ansari Mo.Atik — 2502031830031<br/>Shaikh Sakib Ahmed — 2502031830033<br/>Shaikh Sejan — 2502031830053", s_stud_names))
    
    story.append(Paragraph("Under the Guidance of<br/><b>Prof. Urmil Mewada</b><br/><i>Assistant Professor, Department of Computer Science and Engineering</i>", s_guide_sec))
    
    # Circular Tree Seal
    seal_path = 'Final_Project_Report/assets/p1_img0_X7.png'
    if os.path.exists(seal_path):
        story.append(RLImage(seal_path, width=130, height=82))
        story.append(Spacer(1, 10))
        
    story.append(Paragraph("<b>Department of Computer Science and Engineering<br/>College of Technology<br/>Silver Oak University</b><br/>Ahmedabad, Gujarat<br/><b>Academic Year: 2026–27</b>", s_inst_block))
    
    # Transition to Normal Pages with Header Logo & Footer Page Number
    story.append(PageBreak())
    
    # Helper to switch template
    from reportlab.platypus import NextPageTemplate
    story.append(NextPageTemplate('NormalPage'))
    
    # =============================================================
    # PAGE 2: CERTIFICATE
    # =============================================================
    story.append(Paragraph("<u><b>CERTIFICATE</b></u>", ParagraphStyle('CertHead', fontName='Times-Bold', fontSize=15, leading=18, alignment=1, spaceAfter=16)))
    story.append(Paragraph("This is to certify that the Problem Based Learning-I (PBL-I) report entitled <b>\"VOTE-GUARD: RFID-BASED VOTER VERIFICATION AND DUPLICATE-VOTE PREVENTION SYSTEM\"</b> has been successfully carried out and submitted by <b>Ansari Mo.Atik (Enrollment No. 2502031830031)</b>, <b>Shaikh Sakib Ahmed (Enrollment No. 2502031830033)</b>, and <b>Shaikh Sejan (Enrollment No. 2502031830053)</b>, of the Department of Computer Science and Engineering, College of Technology, Silver Oak University, Ahmedabad, during the Academic Year 2026–27.", s_body))
    story.append(Paragraph("The work presented in this report has been carried out under my guidance and supervision of <b>Prof. Urmil Mewada</b>, as a part of the academic requirements of the prescribed curriculum. To the best of my knowledge, the work reported herein is the original work of the student(s) and has been completed satisfactorily.", s_body))
    story.append(Paragraph("The student(s) have demonstrated appropriate understanding of the identified problem, followed a systematic problem-solving methodology, and documented the outcomes of the project in accordance with the guidelines of Problem Based Learning.", s_body))
    
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>Date:</b> _________________________<br/><br/><b>Place:</b> Ahmedabad", s_body_no_ind))
    story.append(Spacer(1, 30))
    
    t_sig_data = [
        [Paragraph("____________________________<br/><b>Head of Department</b><br/>Department of Computer Science and Engineering", ParagraphStyle('SigL', fontName='Times-Roman', fontSize=9.5, leading=13)),
         Paragraph("____________________________<br/><b>Faculty Guide</b><br/><b>Prof. Urmil Mewada</b><br/>Department of Computer Science and Engineering", ParagraphStyle('SigR', fontName='Times-Roman', fontSize=9.5, leading=13, alignment=2))]
    ]
    t_sig = RLTable(t_sig_data, colWidths=[210.0, 220.0])
    t_sig.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_sig)
    story.append(PageBreak())

    # =============================================================
    # PAGE 3: DECLARATION (Strictly 3 Students)
    # =============================================================
    story.append(Paragraph("<u><b>DECLARATION</b></u>", ParagraphStyle('DeclHead', fontName='Times-Bold', fontSize=15, leading=18, alignment=1, spaceAfter=14)))
    story.append(Paragraph("We hereby declare that the PBL report entitled <b>\"VOTE-GUARD: RFID-BASED VOTER VERIFICATION AND DUPLICATE-VOTE PREVENTION SYSTEM\"</b> submitted to the Department of Computer Science and Engineering, College of Technology, Silver Oak University, Ahmedabad, is an original record of the work carried out by us during the Academic Year 2026–27 under the guidance of <b>Prof. Urmil Mewada</b>.", s_body))
    story.append(Paragraph("We further declare that this report has been prepared for academic purposes as part of the Problem Based Learning activity and has not been submitted, either wholly or partially, to any other university, institution, or organization for the award of any degree, diploma, certificate, or other academic qualification. We have acknowledged all sources of information, references, data, figures, software tools, and other materials used in the preparation of this report. Wherever the work of others has been referred to, appropriate credit has been given.", s_body))
    story.append(Paragraph("We understand that any violation of academic integrity, including plagiarism, fabrication, falsification, or unauthorized use of another person's work, may result in action as per the academic rules and regulations of the University.", s_body))
    story.append(Spacer(1, 10))
    
    decl_data = [
        ['Sr. No.', 'Enrollment No.', 'Student Name', 'Signature'],
        ['1', '2502031830031', 'Ansari Mo.Atik', ''],
        ['2', '2502031830033', 'Shaikh Sakib Ahmed', ''],
        ['3', '2502031830053', 'Shaikh Sejan', '']
    ]
    t_decl_pdf = RLTable(decl_data, colWidths=[55.0, 125.0, 150.0, 100.0])
    t_decl_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 9.5),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (2,1), (2,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_decl_pdf)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Date:</b> _________________________<br/><br/><b>Place:</b> Ahmedabad", s_body_no_ind))
    story.append(PageBreak())

    # =============================================================
    # PAGE 4: ACKNOWLEDGEMENT
    # =============================================================
    story.append(Paragraph("<u><b>ACKNOWLEDGEMENT</b></u>", ParagraphStyle('AckHead', fontName='Times-Bold', fontSize=15, leading=18, alignment=1, spaceAfter=14)))
    story.append(Paragraph("We would like to express our sincere gratitude to Silver Oak University, Ahmedabad, and the Department of Computer Science and Engineering, College of Technology, for providing us with the opportunity, state-of-the-art laboratory facilities, and academic environment required to undertake this Problem Based Learning (PBL) project.", s_body))
    story.append(Paragraph("We are deeply thankful to our project guide, <b>Prof. Urmil Mewada</b>, Assistant Professor, Department of Computer Science and Engineering, for his valuable guidance, continuous encouragement, constructive suggestions, and technical support throughout the planning, hardware interfacing, full-stack software development, testing, and documentation of this project. His guidance helped us to understand the problem systematically and develop an appropriate engineering solution.", s_body))
    story.append(Paragraph("We extend our sincere thanks to the Head of the Department and all faculty members of the Department of Computer Science and Engineering for their continuous support, technical inputs, and encouragement during the course of this work.", s_body))
    story.append(Paragraph("We also acknowledge the assistance provided by our classmates, laboratory staff, friends, and all those who contributed directly or indirectly to the successful completion of this project. Their active cooperation and suggestions were valuable during the various stages of the work.", s_body))
    story.append(Paragraph("Finally, we are grateful to our parents and family members for their constant encouragement, support, and motivation throughout the completion of this academic project.", s_body))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>— PBL Project Team</b><br/>Ansari Mo.Atik (2502031830031)<br/>Shaikh Sakib Ahmed (2502031830033)<br/>Shaikh Sejan (2502031830053)", ParagraphStyle('TeamSig', fontName='Times-Roman', fontSize=10, leading=14, alignment=2)))
    story.append(PageBreak())

    # =============================================================
    # PAGE 5: ABSTRACT & KEYWORDS
    # =============================================================
    story.append(Paragraph("<u><b>ABSTRACT</b></u>", ParagraphStyle('AbsHead', fontName='Times-Bold', fontSize=15, leading=18, alignment=1, spaceAfter=12)))
    story.append(Paragraph("Democratic election integrity fundamentally mandates verifying citizen eligibility and strictly prohibiting duplicate or proxy voting. Traditional manual paper voter rolls and air-gapped electronic voting machines (EVMs) suffer from severe limitations, including vulnerability to impersonation across geographically separated polling stations, lack of dynamic cross-booth synchronization, clerical errors, and long voter verification queues. This project presents Vote-Guard, an IoT-enabled voter authentication and duplicate-vote prevention platform developed under the Problem Based Learning (PBL) paradigm.", s_body))
    story.append(Paragraph("The proposed solution implements an edge-to-cloud decoupled architecture comprising an untrusted edge IoT terminal (ESP32 DevKit V1 and RC522 13.56 MHz RFID reader) connected via IEEE 802.11 b/g/n Wi-Fi to a centralized Python FastAPI backend and an ACID-compliant MySQL 8.0 relational database. Vote-Guard enforces a zero-decision edge philosophy where the microcontroller stores zero citizen records and performs zero ballot computations, eliminating vulnerabilities arising from physical hardware theft or firmware dumping. Double-voting is mathematically prevented at the database engine level via atomic conditional SQL write operations (UPDATE voters SET has_voted = 1 ... WHERE rfid_uid = :uid AND has_voted = 0), totally eliminating race conditions under concurrent multi-booth requests without requiring global table locks.", s_body))
    story.append(Paragraph("To prevent phantom card creation, a two-factor Know Your Customer (KYC) credential binding schema links physical RFID UIDs with national Aadhaar (12-digit) and Electoral Photo Identity Card (EPIC) numbers under database-enforced unique constraints. Empirical performance evaluation of the physical working prototype demonstrates a deterministic mean verification latency of 140.0 ms over Wi-Fi LAN with 100% duplicate-detection accuracy across repeated empirical test runs. Comprehensive visual and auditory diagnostics are delivered via tri-color LEDs and an active buzzer, simultaneously mirrored on a live polling operator web terminal.", s_body))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<u><b>KEYWORDS</b></u>", ParagraphStyle('KWHead', fontName='Times-Bold', fontSize=12, leading=15, spaceAfter=4)))
    story.append(Paragraph("1. Radio Frequency Identification (RFID)<br/>2. Electronic Voting & Voter Verification<br/>3. ESP32 Microcontroller & IoT Edge Computing<br/>4. Concurrency Control & Atomic Transactions<br/>5. Two-Factor Authentication (2FA) KYC Binding<br/>6. FastAPI Asynchronous REST Architecture<br/>7. Database Integrity & Audit Logging", ParagraphStyle('KWList', fontName='Times-Bold', fontSize=9.5, leading=13.5)))
    story.append(PageBreak())

    # =============================================================
    # PAGES 6–8: LISTS (Figures, Tables, Abbreviations)
    # =============================================================
    story.append(Paragraph("<u><b>LIST OF FIGURES</b></u>", ParagraphStyle('LofHead', fontName='Times-Bold', fontSize=15, leading=18, alignment=1, spaceAfter=10)))
    figures_data = [
        ['Figure No.', 'Title / Caption of Figure', 'Page No.'],
        ['Figure 2.1', 'Ishikawa Fishbone Diagram for Root Cause Analysis of Electoral Fraud', '16'],
        ['Figure 3.1', 'Three-Tier Edge-to-Cloud System Architecture of Vote-Guard Platform', '21'],
        ['Figure 4.1', 'Hardware Schematic and Pinout Diagram (ESP32, RC522, LEDs, Buzzer)', '26'],
        ['Figure 4.2', 'Two-Factor KYC Voter Registration & Demographic Collision Flowchart', '28'],
        ['Figure 4.3', 'Entity-Relationship Diagram (ERD) of MySQL 8.0 Relational Database Schema', '29'],
        ['Figure 4.4', 'UML Sequence Diagram of Edge-to-Cloud Verification & Actuation Pipeline', '30'],
        ['Figure 4.5', 'Vote-Guard Role-Based Security Portal (Authentication & Role Selection)', '31'],
        ['Figure 4.6', 'Polling Booth Operator Terminal Dashboard (Live Event Synchronization)', '31'],
        ['Figure 4.7', 'Admin Security Dashboard (KYC Credential Registry & Audit Metrics)', '32'],
        ['Figure 4.8', 'Voter 2FA Credential Registration Interface & Physical Tag Capture', '32'],
        ['Figure 5.1', 'Empirical Verification Latency Decomposition Chart (Mean = 140.0 ms)', '36'],
        ['Figure 8.1', 'PBL-I Project Implementation Timeline & Milestone Gantt Chart', '45']
    ]
    t_lof_pdf = RLTable(figures_data, colWidths=[80.0, 290.0, 60.0])
    t_lof_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_lof_pdf)
    story.append(PageBreak())

    story.append(Paragraph("<u><b>LIST OF TABLES</b></u>", ParagraphStyle('LotHead', fontName='Times-Bold', fontSize=15, leading=18, alignment=1, spaceAfter=10)))
    tables_data = [
        ['Table No.', 'Title / Description of Table', 'Page No.'],
        ['Table 2.1', 'Stakeholder Requirement & Impact Matrix in Electoral Processes', '17'],
        ['Table 2.2', 'Comparative Engineering Analysis of Literature & Existing Approaches', '18'],
        ['Table 3.1', 'Comprehensive Hardware Bill of Materials (BOM) & Specifications', '22'],
        ['Table 3.2', 'Software Platform, Framework, and Database Environment Stack', '23'],
        ['Table 4.1', 'Complete ESP32 Pinout Mapping for RC522 Reader and Diagnostic Actuators', '25'],
        ['Table 4.2', 'MySQL 8.0 Relational Database Schema Structure and Constraints', '29'],
        ['Table 5.1', 'Empirical Hardware and Software Functional Verification Test Suite', '34'],
        ['Table 5.2', 'Comparative Performance Benchmarking Against Published Voting Systems', '37'],
        ['Table 6.1', 'PBL Team Member Role Allocation & Project Responsibility Matrix', '39'],
        ['Table 7.1', 'Multi-Dimensional Socio-Technical & Environmental Impact Analysis', '43'],
        ['Table 8.1', 'Technical, Hardware, and Operational Risk Assessment & Mitigation Plan', '46'],
        ['Table 9.1', 'Project Research Objectives vs. Demonstrated Empirical Achievements', '47']
    ]
    t_lot_pdf = RLTable(tables_data, colWidths=[80.0, 290.0, 60.0])
    t_lot_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_lot_pdf)
    story.append(PageBreak())

    story.append(Paragraph("<u><b>LIST OF ABBREVIATIONS</b></u>", ParagraphStyle('LoaHead', fontName='Times-Bold', fontSize=15, leading=18, alignment=1, spaceAfter=10)))
    abbr_data = [
        ['Abbreviation', 'Full Form'],
        ['PBL', 'Problem Based Learning'],
        ['CSE', 'Computer Science and Engineering'],
        ['RFID', 'Radio Frequency Identification'],
        ['UID', 'Unique Identifier'],
        ['IoT', 'Internet of Things'],
        ['EVM', 'Electronic Voting Machine'],
        ['DRE', 'Direct Recording Electronic'],
        ['KYC', 'Know Your Customer'],
        ['2FA', 'Two-Factor Authentication'],
        ['EPIC', 'Electoral Photo Identity Card'],
        ['REST', 'Representational State Transfer'],
        ['API', 'Application Programming Interface'],
        ['JSON', 'JavaScript Object Notation'],
        ['HTTP', 'Hypertext Transfer Protocol'],
        ['SQL', 'Structured Query Language'],
        ['RDBMS', 'Relational Database Management System'],
        ['ACID', 'Atomicity, Consistency, Isolation, Durability'],
        ['SPI', 'Serial Peripheral Interface'],
        ['GPIO', 'General-Purpose Input/Output'],
        ['LED', 'Light Emitting Diode'],
        ['RBAC', 'Role-Based Access Control'],
        ['SDG', 'Sustainable Development Goals']
    ]
    t_loa_pdf = RLTable(abbr_data, colWidths=[110.0, 320.0])
    t_loa_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_loa_pdf)
    story.append(PageBreak())

    # =============================================================
    # PAGES 9–10: TABLE OF CONTENTS
    # =============================================================
    story.append(Paragraph("<u><b>TABLE OF CONTENTS</b></u>", ParagraphStyle('TocHead', fontName='Times-Bold', fontSize=15, leading=18, alignment=1, spaceAfter=10)))
    toc_data = [
        ['No.', 'Chapter / Topic Description', 'Page No.'],
        ['1.', 'Cover Page', '1'],
        ['2.', 'Certificate', '2'],
        ['3.', 'Declaration', '3'],
        ['4.', 'Acknowledgement', '4'],
        ['5.', 'Abstract & Keywords', '5'],
        ['6.', 'List of Figures', '6'],
        ['7.', 'List of Tables', '7'],
        ['8.', 'List of Abbreviations', '8'],
        ['9.', 'Table of Contents', '9'],
        ['', 'CHAPTER 1 – INTRODUCTION', '11'],
        ['1.1', 'Background of the PBL', '11'],
        ['1.2', 'Problem Identification', '11'],
        ['1.3', 'Problem Statement', '12'],
        ['1.4', 'Motivation', '12'],
        ['1.5', 'Objectives', '13'],
        ['1.6', 'Scope of the PBL', '13'],
        ['', 'CHAPTER 2 – PROBLEM STUDY & LITERATURE REVIEW', '14'],
        ['2.1', 'Existing System / Current Practice', '14'],
        ['2.2', 'Problems in Existing System', '14'],
        ['2.3', 'Root Cause Analysis (Ishikawa Diagram)', '15'],
        ['2.4', 'Stakeholder Analysis', '16'],
        ['2.5', 'Literature Review (15 Academic Studies)', '17'],
        ['2.6', 'Existing Solutions / Benchmark Study', '18'],
        ['2.7', 'Identified Gap', '18'],
        ['', 'CHAPTER 3 – PROPOSED SOLUTION', '19'],
        ['3.1', 'Proposed Solution', '19'],
        ['3.2', 'Conceptual Framework (Zero-Trust Edge)', '20'],
        ['3.3', 'Block Diagram / System Architecture', '20'],
        ['3.4', 'Working Principle', '21'],
        ['3.5', 'Major Components', '22'],
        ['3.6', 'Hardware Requirements (BOM)', '22'],
        ['3.7', 'Software Requirements Stack', '23'],
        ['3.8', 'Technical Specifications', '23'],
        ['3.9', 'Design Calculations (Power & Field Range)', '23'],
        ['', 'CHAPTER 4 – IMPLEMENTATION / DEVELOPMENT', '24'],
        ['4.1', 'Methodology', '24'],
        ['4.2', 'Project Development Steps', '24'],
        ['4.3', 'Diagram / Schematic', '25'],
        ['4.4', 'Hardware Implementation', '25'],
        ['4.5', 'Software / Control Logic (FastAPI & MySQL)', '27'],
        ['4.6', 'Simulation Model & UML Sequence', '29'],
        ['4.7', 'Prototype Development & Frontend Portals', '30'],
        ['4.8', 'Safety Considerations & Fail-Secure Design', '32'],
        ['', 'CHAPTER 5 – TESTING & RESULTS', '33'],
        ['5.1', 'Testing Methodology', '33'],
        ['5.2', 'Test Conditions', '33'],
        ['5.3', 'Experimental Results', '34'],
        ['5.4', 'Observation Table', '34'],
        ['5.5', 'Performance Parameters & Latency Breakdown', '35'],
        ['5.6', 'Graphs / Charts', '36'],
        ['5.7', 'Result Analysis', '36'],
        ['5.8', 'Comparison with Existing Systems', '37'],
        ['5.9', 'Validation of Proposed Solution', '38'],
        ['', 'CHAPTER 6 – PBL LEARNING & TEAM CONTRIBUTION', '39'],
        ['6.1', 'Team Members and Roles', '39'],
        ['6.2', 'Individual Contribution (Placeholders)', '40'],
        ['6.3', 'PBL Learning Outcomes', '40'],
        ['6.4', 'Skills Developed', '41'],
        ['6.5', 'Mentor Review / Feedback', '41'],
        ['6.6', 'Student Reflection', '41'],
        ['', 'CHAPTER 7 – IMPACT & FUTURE SCOPE', '42'],
        ['7.1', 'Innovation / Novelty', '42'],
        ['7.2', 'Social Impact', '42'],
        ['7.3', 'Environmental Impact', '43'],
        ['7.4', 'Economic Impact', '43'],
        ['7.5', 'Sustainability', '43'],
        ['7.6', 'SDG 16 & Viksit Bharat Relevance', '44'],
        ['7.7', 'Limitations', '44'],
        ['7.8', 'Future Scope', '44'],
        ['', 'CHAPTER 8 – PROJECT MANAGEMENT', '45'],
        ['8.1', 'Project Timeline', '45'],
        ['8.2', 'Gantt Chart', '45'],
        ['8.3', 'Milestones Achieved', '46'],
        ['8.4', 'Review Meetings', '46'],
        ['8.5', 'Risk Identification and Mitigation', '46'],
        ['', 'CHAPTER 9 – CONCLUSION', '47'],
        ['9.1', 'Conclusion', '47'],
        ['9.2', 'Achievement of Objectives', '47'],
        ['9.3', 'Final Outcome', '47'],
        ['', 'REFERENCES', '48'],
        ['', 'ANNEXURES (Annexures A to D)', '49']
    ]
    t_toc_pdf = RLTable(toc_data, colWidths=[45.0, 325.0, 60.0])
    t_toc_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_toc_pdf)
    story.append(PageBreak())

    # =============================================================
    # CHAPTER 1 – INTRODUCTION (Pages 11–13)
    # =============================================================
    story.append(Paragraph("CHAPTER 1 – INTRODUCTION", s_h1))
    story.append(Paragraph("1.1 Background of the PBL", s_h2))
    story.append(Paragraph("Problem Based Learning (PBL) is an instructional engineering methodology that challenges student engineers to address realistic, complex societal problems through systematic investigation, multidisciplinary technical synthesis, and physical prototype implementation. In representative democracies, the credibility, determinism, and integrity of national and institutional elections represent the absolute bedrock of civil governance. An election is legitimate only if it enforces two fundamental guarantees: first, that every eligible citizen is afforded exactly one opportunity to vote; and second, that fraudulent, duplicate, or unverified ballots are unconditionally blocked from entering the official tally.", s_body))
    story.append(Paragraph("For decades, electoral authorities globally have relied on manual paper registries, physical voter slips, and indelible ink to authenticate voters at polling booths. However, manual authentication processes suffer from acute human bottlenecks: long waiting queues, voter exhaustion, transcription errors, and vulnerability to voter impersonation. Furthermore, isolated or air-gapped voting terminals deployed across geographically dispersed polling booths possess no dynamic inter-booth synchronization. As a result, preventing an unscrupulous individual from voting at Multiple Polling Stations has historically depended entirely on physical ink marking—a safeguard increasingly circumvented through chemical solvents or administrative oversight.", s_body))
    
    story.append(Paragraph("1.2 Problem Identification", s_h2))
    story.append(Paragraph("Through our initial field analysis and literature study, three major structural failure points were identified in current voter verification practices: (i) Absence of Contactless Automated Identity Verification: Human polling officers manually inspect paper photo identity cards against printed voter lists containing thousands of names, leading to high error rates and processing times of 60 to 90 seconds per citizen; (ii) The Multi-Booth Duplicate Voting Loophole: Air-gapped voting machines operate in total isolation; if a voter’s name appears on multiple precinct rolls due to clerical duplication or recent migration, an individual can physically cast multiple votes before paper records are cross-checked days later; (iii) Credential Clashing and Phantom Registrations: Existing computerized registries frequently lack multi-table two-factor constraint enforcement, enabling corrupt operators to assign duplicate digital tokens to the same citizen identity.", s_body))
    
    story.append(Paragraph("1.3 Problem Statement", s_h2))
    story.append(Paragraph("Formally, let the registered electorate be modeled as a finite set V = {v_1, v_2, ..., v_n}, where each citizen v_i is bound to a verified demographic credential tuple C_i = (A_i, E_i) representing their national 12-digit Aadhaar number and Electoral Photo Identity Card (EPIC) identifier. Each voter is provisioned a physical contactless smartcard containing a high-frequency unique identifier UID_i. The voting status of voter v_i at any continuous time t is represented by a binary state variable S_i(t) in {0, 1}, where S_i(t) = 0 indicates that the ballot has not been cast, and S_i(t) = 1 indicates that the ballot has been irreversibly consumed.", s_body))
    story.append(Paragraph("In a distributed election comprising B concurrent polling terminals connected across a wide-area network, a race condition occurs when citizen v_i presents identical or cloned RFID tokens to two distinct terminals at timestamps t_1 and t_2, such that |t_1 - t_2| < Delta t_{db}, where Delta t_{db} is the database transaction execution window. In naive systems executing an unbuffered check-then-write sequence, both terminals read S_i = 0 before either commits its write, granting two accepted ballots. The fundamental engineering objective of Vote-Guard is to guarantee the strict invariant: sum(AcceptedVotes(v_i)) <= 1 for all v_i in V, across all time t, under arbitrary network concurrency, while maintaining edge verification latency under 200 milliseconds.", s_body))
    
    story.append(Paragraph("1.4 Motivation", s_h2))
    story.append(Paragraph("The motivation behind Vote-Guard stems from the urgent democratic imperative to eliminate electoral fraud through transparent, low-cost, and robust engineering. While advanced nations experiment with complex biometric portals and permissioned blockchain ledgers, such systems often suffer from prohibitive infrastructure costs (exceeding $5,000 per terminal), massive power requirements, and slow transaction latencies (15–30 seconds per voter) that create intolerable congestion at polling stations. The Vote-Guard project is driven by the conviction that modern commodity 32-bit IoT microcontrollers (ESP32) combined with high-frequency RFID transponders and lightweight asynchronous REST backends can deliver military-grade verification determinism and sub-second transaction throughput at a fraction of commercial costs.", s_body))
    
    story.append(Paragraph("1.5 Objectives", s_h2))
    story.append(Paragraph("1) Sub-200ms Edge Verification Latency: Achieve deterministic end-to-end transaction latency from physical card detection to actuator triggering below 200 milliseconds over standard Wi-Fi LAN transport.<br/>2) Atomic Single-Vote Invariant: Prevent double-voting race conditions at the relational database engine level with 0% duplicate authorization across concurrent burst requests.<br/>3) Two-Factor Demographic Identity Binding: Enforce relational unique constraints binding physical RFID UIDs to verified 12-digit Aadhaar numbers and EPIC identifiers, preventing rogue administrative card duplication.<br/>4) Fail-Secure Multi-Modal Diagnostic Feedback: Provide instantaneous visual (tri-color LEDs) and auditory (piezoelectric buzzer) feedback at the physical terminal, guaranteed to never signal green acceptance without authoritative backend confirmation, while simultaneously updating a live operator web terminal.", s_body))
    
    story.append(Paragraph("1.6 Scope of the PBL", s_h2))
    story.append(Paragraph("The scope of Vote-Guard encompasses the complete end-to-end voter verification and gatekeeping pipeline at polling booths. It includes the design and construction of the edge hardware terminal (ESP32 DevKit V1, RC522 RFID reader, LED/buzzer circuitry), custom non-blocking C++ FreeRTOS firmware, an asynchronous Python FastAPI backend, a normalized MySQL 8.0 ACID database, and responsive web portals for polling booth operators and system administrators. The project explicitly focuses on voter authentication and duplicate prevention; in accordance with national secret ballot standards, it deliberately excludes candidate selection recording and ballot tabulation, thereby preserving absolute voter secrecy.", s_body))
    story.append(PageBreak())

    # =============================================================
    # CHAPTER 2 – PROBLEM STUDY & LITERATURE REVIEW (Pages 14–18)
    # =============================================================
    story.append(Paragraph("CHAPTER 2 – PROBLEM STUDY & LITERATURE REVIEW", s_h1))
    story.append(Paragraph("2.1 Existing System / Current Practice", s_h2))
    story.append(Paragraph("In the current electoral architecture prevalent across most parliamentary democracies, voter identification relies on printed electoral rolls. When a citizen arrives at their assigned polling booth, election officers manually cross-verify the citizen’s physical voter identity card against a printed paper roll. Once the citizen’s name is located, the official marks a line through the paper entry, applies indelible silver nitrate ink to the voter’s left forefinger, and issues an ink-signed paper voter slip. The voter then proceeds to an isolated electronic voting machine (EVM) or paper ballot box to cast their vote.", s_body))
    
    story.append(Paragraph("2.2 Problems in Existing System", s_h2))
    story.append(Paragraph("Despite widespread adoption, the conventional approach exhibits critical systemic vulnerabilities: (1) Human Clerical Bottlenecks: Searching through hundreds of pages of paper rolls consumes 60 to 120 seconds per voter, resulting in severe voter fatigue and reduced turnout; (2) Vulnerability to Impersonation: Visual inspection of low-resolution laminated identity cards is inherently subjective and prone to error, particularly in crowded polling stations; (3) Absence of Multi-Booth Cross-Checking: Because paper rolls are physically isolated at each booth, a fraudulent actor whose name appears in multiple rolls can easily cast ballots at different booths before paper logs are reconciled days after the election; (4) Lack of Real-Time Administrative Visibility: Polling officials have no dynamic mechanism to broadcast security alerts, detect duplicate voting attempts, or audit booth-level throughput in real time.", s_body))
    
    story.append(Paragraph("2.3 Root Cause Analysis (Ishikawa Diagram)", s_h2))
    story.append(Paragraph("To establish a rigorous engineering foundation, a comprehensive Root Cause Analysis was performed using the Ishikawa (Fishbone) methodology. As illustrated in Figure 2.1, the central problem of 'Duplicate Voting and Identity Fraud' was decomposed into four major contributory branches: Human Factors (fatigue, manual roll errors), Infrastructure (air-gapped terminals, lack of live inter-booth sync), Process & Credentials (unverified ID cards, absence of multi-factor binding), and Concurrency Anomalies (lost-update race conditions in naive digital systems).", s_body))
    
    fishbone_img = get_scaled_img('Final_Project_Report/Project_Diagrams/Fig_Fishbone_Root_Cause.png', 420, 200)
    if fishbone_img:
        story.append(fishbone_img)
        story.append(Paragraph("Figure 2.1: Ishikawa Fishbone Diagram for Root Cause Analysis of Electoral Fraud & Duplicate Voting", s_cap))
        
    story.append(Paragraph("2.4 Stakeholder Analysis", s_h2))
    story.append(Paragraph("A thorough stakeholder impact study was conducted to understand the functional and operational requirements of all parties involved in the electoral verification lifecycle, summarized in Table 2.1.", s_body))
    
    stk_pdf_data = [
        ['Stakeholder', 'Key Role in Process', 'Primary Operational Pain Point', 'Vote-Guard Impact'],
        ['Eligible Voters', 'Present identity & cast ballot', 'Long queue waiting times, wrongful voter deletion', 'Instant sub-second RFID scan'],
        ['Booth Polling Officers', 'Verify credentials & authorize entry', 'Severe fatigue, manual roll searching, dispute management', 'Automated LED & web dashboard'],
        ['Election Commission', 'Oversee election integrity & legitimacy', 'Bogus voting scandals, recount disputes, high logistics cost', 'Centralized real-time audit ledger'],
        ['System Administrators', 'Enroll voters & configure terminals', 'Duplicate card creation, manual data entry errors', '2FA KYC collision prevention'],
        ['Auditors & Observers', 'Forensic post-poll verification', 'Unverifiable paper logs, lack of event timestamps', 'Tamper-evident audit logs']
    ]
    t_stk_pdf = RLTable(stk_pdf_data, colWidths=[90.0, 110.0, 130.0, 100.0])
    t_stk_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_stk_pdf)
    story.append(Paragraph("Table 2.1: Stakeholder Requirement & Impact Matrix in Electoral Processes", s_cap))

    story.append(Paragraph("2.5 Literature Review", s_h2))
    story.append(Paragraph("Extensive academic literature review was conducted across peer-reviewed IEEE, ACM, Springer, and official NIST standards to benchmark prior work. In a foundational security evaluation of India’s electronic voting machines, Wolchok et al. [1] demonstrated that air-gapped embedded voting machines lacking independent real-time verification channels remain vulnerable to physical chip replacement, memory sniffing, and insider manipulation. More crucially, their study highlighted that standalone terminals have no defense against duplicate voting across distinct booths other than physical indelible ink.", s_body))
    story.append(Paragraph("The security of contactless smartcards was rigorously investigated by Garcia et al. [2], [3], who dismantled the proprietary Crypto-1 cipher of NXP MIFARE Classic transponders and proved that passive 13.56 MHz RFID cards can be wirelessly cloned at a distance using commodity transceivers. These seminal works establish that a robust electronic voting system cannot treat raw RFID card UIDs as secret cryptographic tokens, but must instead treat the physical card as an untrusted identity token validated against an authoritative centralized backend under Zero Trust principles [17].", s_body))
    story.append(Paragraph("In the domain of embedded election prototypes, Khokher et al. [11] designed a standalone EVM using an 8-bit ATMega328P microcontroller storing vote tallies in 1 KB internal EEPROM. While low-cost, their system possessed zero network capability, negligible memory, and complete vulnerability to physical board theft. Mansingh et al. [7] integrated an EM-18 RFID reader and optical fingerprint scanner with an Arduino Uno tethered to a host PC over USB serial. However, their database logic used naive sequential SQL SELECT-then-UPDATE statements that suffer from catastrophic race conditions under concurrent network access. Vidhya et al. [9] proposed an IoT voting framework with Diffie-Hellman keys on ESP32, but relied on SMS one-time passwords that incur prohibitive 5 to 15-second delivery delays. Kumar and Dwivedi [10] deployed a blockchain voting system on Ethereum and Raspberry Pi nodes; while achieving decentralization, their transaction confirmation latency ranged from 10 to 30 seconds per ballot, accompanied by variable cryptocurrency gas fees.", s_body))
    story.append(Paragraph("Classical transaction processing theory established by Gray and Reuter [14] and Berenson et al. [15] demonstrates that relational database engines supporting full ACID guarantees can achieve sub-second determinism. Specifically, Berenson et al. showed that lost-update anomalies in concurrent multi-client systems are completely eliminated through atomic row-level update conditions without requiring coarse-grained table locks.", s_body))

    story.append(Paragraph("2.6 Existing Solutions / Benchmark Study", s_h2))
    story.append(Paragraph("Table 2.2 provides a detailed comparative matrix benchmarking Vote-Guard against existing systems reported in academic literature across five critical technical dimensions.", s_body))
    
    comp_pdf_data = [
        ['Architecture / Study', 'Processing Hardware', 'Verification Latency', 'Duplicate Prevention Mechanism', 'Edge Security Model'],
        ['Khokher et al. [11]', 'ATMega328P (8-bit)', '~1250 ms', 'Local EEPROM flag increment', 'Monolithic (Air-gapped)'],
        ['Mansingh et al. [7]', 'Arduino + Fingerprint', '~850 ms', 'Naive SELECT / UPDATE (Prone to Race)', 'Wired USB Serial PC'],
        ['Vidhya et al. [9]', 'ESP32 + Diffie-Hellman', '~8500 ms (SMS)', 'Database boolean status check', 'Partial Cloud Sync'],
        ['Kumar & Dwivedi [10]', 'Raspberry Pi 4', '~14200 ms', 'Ethereum Smart Contract', 'Decentralized Gateway'],
        ['Chavan et al. [8]', 'Microcontroller Unit', '~1100 ms', 'Local EEPROM voter counter', 'Standalone Terminal'],
        ['Vote-Guard (Proposed)', 'ESP32 DevKit V1', '140.0 ms', 'Atomic Conditional SQL Update', 'Zero-Trust Untrusted Edge']
    ]
    t_comp_pdf = RLTable(comp_pdf_data, colWidths=[95.0, 85.0, 75.0, 100.0, 75.0])
    t_comp_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('FONTNAME', (0,-1), (-1,-1), 'Times-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EBF8FF')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_comp_pdf)
    story.append(Paragraph("Table 2.2: Comparative Engineering Analysis of Literature & Existing Approaches", s_cap))

    story.append(Paragraph("2.7 Identified Gap", s_h2))
    story.append(Paragraph("Our critical synthesis reveals that prior voting prototypes fail in four crucial areas: (1) Monolithic Embedded Storage: Storing records on microcontrollers exposes voter registries to physical extraction; (2) Unsafe Database Concurrency: Systems lack atomic row-level locks, permitting concurrent double-voting; (3) Absence of Demographic KYC Binding: Systems bind only a card UID without verifying national Aadhaar/EPIC uniqueness, allowing duplicate card provisioning; (4) Blocking Serial Architecture: Legacy systems require local PCs tethered via USB cables. Vote-Guard directly bridges all four gaps.", s_body))
    story.append(PageBreak())

    # =============================================================
    # CHAPTER 3 – PROPOSED SOLUTION (Pages 19–23)
    # =============================================================
    story.append(Paragraph("CHAPTER 3 – PROPOSED SOLUTION", s_h1))
    story.append(Paragraph("3.1 Proposed Solution", s_h2))
    story.append(Paragraph("To overcome the vulnerabilities identified in existing systems, Vote-Guard introduces an edge-to-cloud decoupled voter verification and duplicate-prevention platform. The architecture separates untrusted physical edge acquisition from authoritative centralized validation. The physical terminal, constructed using an ESP32 microcontroller and RC522 transceiver, serves purely as an input/output peripheral. All voter identification, concurrency arbitration, and audit trail generation are handled by a high-performance Python FastAPI server backed by an ACID-compliant MySQL 8.0 relational database.", s_body))
    
    story.append(Paragraph("3.2 Conceptual Framework (Zero-Trust Edge)", s_h2))
    story.append(Paragraph("In strict compliance with NIST Special Publication 800-207 guidelines on Zero Trust Architecture [17], Vote-Guard operates on the principle that the edge terminal must never be implicitly trusted. No citizen records, Aadhaar numbers, voter rolls, or tallying algorithms reside in the ESP32’s flash memory or SRAM. Even if an adversary physically captures the edge device, disassembles the circuitry, or dumps the microcontroller firmware via JTAG, zero sensitive electoral data is exposed. The edge node is strictly an encrypted conduit that captures physical radio frequency signals and actuates local diagnostic transducers under explicit, authoritative server direction.", s_body))
    
    story.append(Paragraph("3.3 Block Diagram / System Architecture", s_h2))
    story.append(Paragraph("The overall three-tier system architecture of Vote-Guard is illustrated in Figure 3.1. The three interconnected tiers comprise: (1) The Edge Hardware Layer stationed at polling booths; (2) The Application Backend Tier executing asynchronous business logic and concurrency arbitration; and (3) The Storage and Web Client Tier providing persistent ACID storage and role-based operator interfaces.", s_body))
    
    arch_img = get_scaled_img('Final_Project_Report/Project_Diagrams/Fig1_System_Architecture.png', 420, 210)
    if arch_img:
        story.append(arch_img)
        story.append(Paragraph("Figure 3.1: Three-Tier Edge-to-Cloud System Architecture of Vote-Guard Platform", s_cap))
        
    story.append(Paragraph("3.4 Working Principle", s_h2))
    story.append(Paragraph("The operational workflow executes in five deterministic phases: (1) Contactless Card Acquisition: When an RFID smartcard enters the 13.56 MHz electromagnetic field generated by the RC522 reader, the transponder modulates its 4-byte or 7-byte factory UID; (2) Wireless REST Transmission: The ESP32 extracts the UID over hardware SPI, formats a JSON payload, and transmits an HTTP POST request to /api/vote/verify over Wi-Fi LAN; (3) Atomic Concurrency Arbitration: The FastAPI backend executes an atomic conditional SQL update within an InnoDB transaction; (4) Deterministic Actuator Response: The backend returns an HTTP 200 JSON payload directing the ESP32 to pulse specific visual LEDs and acoustic buzzer patterns; (5) Real-Time Operator Synchronization: Connected operator browsers polling /api/vote/latest-event immediately mirror the voter verification status on a large monitor.", s_body))
    
    story.append(Paragraph("3.5 Major Components", s_h2))
    story.append(Paragraph("The platform integrates seven major hardware and software modules: (i) DOIT ESP32 DevKit V1 30-pin microcontroller featuring a dual-core Xtensa LX6 processor operating at 240 MHz; (ii) NXP MFRC522 13.56 MHz RFID transceiver module; (iii) Diagnostic LED Subsystem (Green = GPIO 25, Yellow = GPIO 26, Red = GPIO 27); (iv) Active Piezoelectric Buzzer driven via a 2N2222 NPN transistor on GPIO 32; (v) Python FastAPI asynchronous web framework; (vi) MySQL 8.0 Relational Database Engine with InnoDB storage; (vii) Role-Based Web Portals engineered with modern HTML5, CSS3, and ES6 JavaScript.", s_body))
    
    story.append(Paragraph("3.6 Hardware Requirements (BOM)", s_h2))
    story.append(Paragraph("The complete Bill of Materials (BOM) specifying hardware components, quantities, functional roles, and electrical parameters is provided in Table 3.1.", s_body))
    
    bom_pdf_data = [
        ['Component Name', 'Model / Part Number', 'Quantity', 'Functional Role & Electrical Specs'],
        ['Microcontroller Unit', 'ESP32 DevKit V1 (30-Pin)', '1 Unit', 'Dual-core 240MHz, 520KB SRAM, 802.11 b/g/n Wi-Fi'],
        ['RFID Reader Module', 'MFRC522 Transceiver', '1 Unit', '13.56 MHz ISO/IEC 14443A, SPI Interface @ 3.3V'],
        ['RFID Cards / Tags', 'MIFARE Classic 1K / S50', '3 Units', 'Passive 13.56 MHz transponders with 4-byte factory UIDs'],
        ['Diagnostic LEDs', '5mm Diffused (Grn/Ylw/Red)', '3 Units', 'Active-high visual indicators with 330 Ohm resistors'],
        ['Active Buzzer', '5V Continuous Tone Buzzer', '1 Unit', '2.4 kHz resonant frequency, driven via 2N2222 transistor'],
        ['Switching Transistor', '2N2222 NPN BJT', '1 Unit', 'GPIO current buffer (Vceo=40V, Ic=800mA, hFE>100)'],
        ['Portable Power Subsystem', '5V USB Power Bank (10,000mAh)', '1 Unit', '5V DC regulated output powering ESP32 via Micro-USB']
    ]
    t_bom_pdf = RLTable(bom_pdf_data, colWidths=[100.0, 110.0, 50.0, 170.0])
    t_bom_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_bom_pdf)
    story.append(Paragraph("Table 3.1: Comprehensive Hardware Bill of Materials (BOM) & Specifications", s_cap))

    story.append(Paragraph("3.7 Software Requirements Stack", s_h2))
    story.append(Paragraph("The software ecosystem is constructed with modern, open-source technologies: Python 3.10+ runtime, FastAPI 0.110+ web framework, Uvicorn ASGI server, SQLAlchemy ORM, PyMySQL driver, MySQL Community Server 8.0.46, Arduino IDE 2.3+ with ESP32 Board Package 2.0.14, and the MFRC522 Arduino library.", s_body))
    
    story.append(Paragraph("3.8 Technical Specifications", s_h2))
    story.append(Paragraph("Key technical parameters: Radio Frequency: 13.56 MHz; RFID Standard: ISO/IEC 14443 Type A; Read Range: 25 mm to 40 mm; SPI Clock Frequency: 4 MHz; Wi-Fi Modulation: 802.11 b/g/n (2.4 GHz); Wi-Fi Channel Bandwidth: 20 MHz; Network Transport: HTTP/1.1 REST over TCP/IP; Server Port: 8000; Database Engine: InnoDB with row-level locking; Operator Polling Period: 500 milliseconds.", s_body))
    
    story.append(Paragraph("3.9 Design Calculations (Power & Field Range)", s_h2))
    story.append(Paragraph("A comprehensive power budget calculation was conducted to ensure reliable wireless field operation from a portable power source. The baseline current draw of the ESP32 in active Wi-Fi station mode is I_{esp} = 140 mA. The RC522 transceiver in continuous carrier modulation draws I_{rfid} = 25 mA. During card verification, an actuated LED draws I_{led} = (V_{cc} - V_f) / R = (3.3V - 2.0V) / 330 Ohm = 3.94 mA. The active buzzer draws I_{buzz} = 18 mA. The total peak current consumption during verification actuation is: I_{total} = 140 + 25 + 3.94 + 18 = 186.94 mA. When powered from a standard 10,000 mAh portable USB power bank operating at 80% discharge efficiency (8,000 mAh effective), the continuous operational battery life is: BatteryLife = 8000 mAh / 186.94 mA = 42.8 hours. This confirms that a single portable battery charge easily powers the terminal throughout a multi-day election without requiring mains electricity.", s_body))
    story.append(PageBreak())

    # =============================================================
    # CHAPTER 4 – IMPLEMENTATION / DEVELOPMENT (Pages 24–32)
    # =============================================================
    story.append(Paragraph("CHAPTER 4 – IMPLEMENTATION / DEVELOPMENT", s_h1))
    story.append(Paragraph("4.1 Methodology", s_h2))
    story.append(Paragraph("The implementation of Vote-Guard followed an Agile iterative engineering methodology consisting of four distinct sprints: (1) Hardware Breadboard Prototyping & Transceiver Verification; (2) Firmware State Machine & Wi-Fi Station Development; (3) FastAPI Concurrency Engine & MySQL Relational Schema Engineering; and (4) Full-Stack Web Portal Integration & End-to-End Latency Benchmarking.", s_body))
    
    story.append(Paragraph("4.2 Project Development Steps", s_h2))
    story.append(Paragraph("The technical development was executed through seven sequential steps: Step 1: Schematic capture and physical pinout mapping; Step 2: SPI bus integration between ESP32 and RC522; Step 3: LED current-limiting and buzzer transistor switching circuitry; Step 4: Firmware development in C++ utilizing non-blocking polling and 2.0s debouncing timers; Step 5: Implementation of the atomic conditional SQL update in backend/routers/voting.py; Step 6: Engineering the 2FA KYC onboarding workflow in backend/routers/admin.py; Step 7: Crafting responsive web dashboards in HTML5/CSS3/JS.", s_body))
    
    story.append(Paragraph("4.3 Diagram / Schematic", s_h2))
    story.append(Paragraph("Figure 4.1 depicts the complete physical schematic and pinout diagram connecting the ESP32 DevKit V1 to the RC522 RFID reader, tri-color LEDs, active buzzer driver, and USB power supply.", s_body))
    
    pinout_img = get_scaled_img('Final_Project_Report/Project_Diagrams/Fig5_Hardware_Prototype_Pinout.png', 410, 200)
    if pinout_img:
        story.append(pinout_img)
        story.append(Paragraph("Figure 4.1: Hardware Schematic and Pinout Diagram (ESP32, RC522, LEDs, Buzzer)", s_cap))
        
    story.append(Paragraph("4.4 Hardware Implementation", s_h2))
    story.append(Paragraph("The physical wiring between the ESP32 and external peripherals is detailed in Table 4.1. The hardware SPI bus connects RC522 SCK to GPIO 18, MISO to GPIO 19, MOSI to GPIO 23, Slave Select (SS) to GPIO 5, and Reset (RST) to GPIO 4. The diagnostic LEDs connect to GPIO 25 (Green), GPIO 26 (Yellow), and GPIO 27 (Red) through 330 Ohm current-limiting resistors. The active buzzer connects to GPIO 32 via a 2N2222 NPN switching transistor.", s_body))
    
    pin_pdf_data = [
        ['Peripheral Device', 'Peripheral Pin', 'ESP32 GPIO Pin', 'Interface Type & Electrical Characteristics'],
        ['RC522 RFID Reader', 'SDA (SS)', 'GPIO 5', 'Hardware SPI Slave Select (Active LOW, 3.3V Logic)'],
        ['RC522 RFID Reader', 'SCK', 'GPIO 18', 'Hardware SPI Clock (4 MHz)'],
        ['RC522 RFID Reader', 'MOSI', 'GPIO 23', 'Hardware SPI Master-Out Slave-In'],
        ['RC522 RFID Reader', 'MISO', 'GPIO 19', 'Hardware SPI Master-In Slave-Out'],
        ['RC522 RFID Reader', 'RST', 'GPIO 4', 'Hardware Reset Line'],
        ['Green Diagnostic LED', 'Anode (+)', 'GPIO 25', 'Active-HIGH Output, 330 Ohm Resistor (Vote Accepted)'],
        ['Yellow Diagnostic LED', 'Anode (+)', 'GPIO 26', 'Active-HIGH Output, 330 Ohm Resistor (Unregistered Tag)'],
        ['Red Diagnostic LED', 'Anode (+)', 'GPIO 27', 'Active-HIGH Output, 330 Ohm Resistor (Duplicate Attempt)']
    ]
    t_pin_pdf = RLTable(pin_pdf_data, colWidths=[90.0, 75.0, 75.0, 190.0])
    t_pin_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,0), (2,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_pin_pdf)
    story.append(Paragraph("Table 4.1: Complete ESP32 Pinout Mapping for RC522 Reader and Diagnostic Actuators", s_cap))

    story.append(Paragraph("4.5 Software / Control Logic (FastAPI & MySQL)", s_h2))
    story.append(Paragraph("The core innovation of duplicate-vote prevention resides in the atomic conditional update executed in backend/routers/voting.py. When a request arrives at /api/vote/verify-and-record (or /api/vote/verify), the backend executes:<br/><b>stmt = update(Voter).where(Voter.rfid_uid == normalized_uid, Voter.has_voted == False).values(has_voted=True, voted_at=now)</b>", s_body))
    story.append(Paragraph("Under MySQL InnoDB engine execution, this statement instantly acquires an exclusive row-level write lock (X-lock) on the clustered index record corresponding to rfid_uid. If two concurrent transactions attempt to execute this statement simultaneously, the second transaction is queued until the first commits. When the second transaction unblocks, the condition has_voted == False evaluates to false because has_voted is already True. The database reports rows_affected = 0, and the backend deterministically returns ALREADY_VOTED without entering a race condition [14], [15].", s_body))
    story.append(Paragraph("Furthermore, to prevent rogue administrators from registering duplicate cards to the same citizen identity, the administrative onboarding pipeline implements a multi-table Two-Factor KYC schema. Figure 4.2 illustrates the registration flowchart enforcing uniqueness across Aadhaar numbers, EPIC identifiers, and RFID UIDs.", s_body))
    
    kyc_flow_img = get_scaled_img('Final_Project_Report/Project_Diagrams/Fig3_Registration_2FA_Workflow.png', 390, 200)
    if kyc_flow_img:
        story.append(kyc_flow_img)
        story.append(Paragraph("Figure 4.2: Two-Factor KYC Voter Registration & Demographic Collision Flowchart", s_cap))
        
    story.append(Paragraph("The relational database schema is modeled across four normalized tables (admin_users, voter_credentials, voters, and audit_logs), as depicted in the Entity-Relationship Diagram in Figure 4.3.", s_body))
    
    erd_img = get_scaled_img('Final_Project_Report/Project_Diagrams/Fig4_Database_ERD.png', 410, 200)
    if erd_img:
        story.append(erd_img)
        story.append(Paragraph("Figure 4.3: Entity-Relationship Diagram (ERD) of MySQL 8.0 Relational Database Schema", s_cap))

    story.append(Paragraph("4.6 Simulation Model & UML Sequence", s_h2))
    story.append(Paragraph("Figure 4.4 illustrates the complete UML Sequence Diagram detailing the asynchronous interactions between the Physical RFID Tag, ESP32 Microcontroller, FastAPI REST Backend, MySQL Database Engine, and Connected Operator Web Terminals.", s_body))
    
    seq_img = get_scaled_img('Final_Project_Report/Project_Diagrams/Fig2_Verification_Sequence.png', 410, 200)
    if seq_img:
        story.append(seq_img)
        story.append(Paragraph("Figure 4.4: UML Sequence Diagram of Edge-to-Cloud Verification & Actuation Pipeline", s_cap))

    story.append(Paragraph("4.7 Prototype Development & Frontend Portals", s_h2))
    story.append(Paragraph("The Vote-Guard software interfaces provide role-based security separating administrative configuration from live booth operations. Figure 4.5 displays the Role-Based Login Portal with session authentication. Figure 4.6 displays the Polling Booth Operator Terminal that polls /api/vote/latest-event every 500 ms, mirroring the edge hardware status in real time. Figure 4.7 displays the Admin Security Dashboard showing real-time statistics and credential registries. Figure 4.8 displays the Voter 2FA Credential Registration Form with automated physical tag capture.", s_body))
    
    img_login = get_scaled_img('Final_Project_Report/screenshots/01_login_security_portal.png', 380, 180)
    if img_login:
        story.append(img_login)
        story.append(Paragraph("Figure 4.5: Vote-Guard Role-Based Security Portal (Authentication & Role Selection)", s_cap))
        
    img_op = get_scaled_img('Final_Project_Report/screenshots/02_operator_terminal.png', 390, 185)
    if img_op:
        story.append(img_op)
        story.append(Paragraph("Figure 4.6: Polling Booth Operator Terminal Dashboard (Live Event Synchronization)", s_cap))
        
    img_adm = get_scaled_img('Final_Project_Report/screenshots/03_admin_kyc_security.png', 390, 185)
    if img_adm:
        story.append(img_adm)
        story.append(Paragraph("Figure 4.7: Admin Security Dashboard (KYC Credential Registry & Audit Metrics)", s_cap))
        
    img_reg = get_scaled_img('Final_Project_Report/screenshots/04_registration_form.png', 350, 180)
    if img_reg:
        story.append(img_reg)
        story.append(Paragraph("Figure 4.8: Voter 2FA Credential Registration Interface & Physical Tag Capture", s_cap))

    story.append(Paragraph("4.8 Safety Considerations & Fail-Secure Design", s_h2))
    story.append(Paragraph("Vote-Guard enforces a strict fail-secure architecture: (i) Never Green on Error: Under network disconnection, HTTP timeouts, or malformed responses, the ESP32 activates yellow and red warning indicators and never illuminates green; (ii) Card Anti-Spam Debouncing: After reading a card, the firmware issues PICC_HaltA() and enforces a 2.0-second cooldown to prevent flood attacks; (iii) Power Isolation: Filter capacitors on the 3.3V rail suppress inductive voltage spikes during RF carrier modulation.", s_body))
    story.append(PageBreak())

    # =============================================================
    # CHAPTER 5 – TESTING & RESULTS (Pages 33–38)
    # =============================================================
    story.append(Paragraph("CHAPTER 5 – TESTING & RESULTS", s_h1))
    story.append(Paragraph("5.1 Testing Methodology", s_h2))
    story.append(Paragraph("A comprehensive three-stage testing methodology was executed to validate Vote-Guard: (1) Hardware Unit Testing: Oscilloscope and multimeter verification of SPI signals (SCK, MOSI, MISO) and GPIO output voltages; (2) API & Database Concurrency Testing: Automated Python test harnesses (test_lan_vote.py) dispatching rapid concurrent verification payloads; (3) Live Prototype Integration Testing: Real-time physical card tapping with the ESP32 powered wirelessly from a portable USB battery pack over Wi-Fi.", s_body))
    
    story.append(Paragraph("5.2 Test Conditions", s_h2))
    story.append(Paragraph("Testing was conducted in a laboratory environment under the following parameters: Host Computer: Intel Core i7, 16 GB RAM, Windows 11; Server: Uvicorn ASGI listening on 0.0.0.0:8000; Database: MySQL 8.0.46 Community Server; Wi-Fi Network: 802.11 b/g/n on 2.4 GHz; Measured Wi-Fi RSSI: -59 dBm; Edge Hardware: ESP32 DevKit V1 powered by 5V USB battery pack.", s_body))
    
    story.append(Paragraph("5.3 Experimental Results", s_h2))
    story.append(Paragraph("The empirical verification was evaluated across four primary functional test scenarios: Test 1: Unregistered RFID Tag (UID: E24B10A9); Test 2: Fresh Registered Citizen Vote (UID: 71411605, registered to Shaikh Noman, initial has_voted = 0); Test 3: Duplicate Voting Attempt (identical tag 71411605 tapped immediately after vote acceptance); Test 4: Server Disconnection & Network Unreachability.", s_body))
    
    story.append(Paragraph("5.4 Observation Table", s_h2))
    story.append(Paragraph("Table 5.1 documents the exact empirical observations recorded during functional verification test runs.", s_body))
    
    obs_pdf_data = [
        ['Test Case', 'Input UID', 'Backend Status', 'Hardware Actuator', 'Operator Web Display', 'Database State Change'],
        ['1. Unregistered Tag', 'E24B10A9', 'UNREGISTERED', 'Yellow LED (3x) + Buzzer (3x)', 'Amber: NOT REGISTERED', 'None (Audit Logged)'],
        ['2. Valid Citizen Vote', '71411605', 'ACCEPTED', 'Green LED (3x) + Chime (1x)', 'Green: VOTE RECORDED', 'has_voted=1, voted_at=NOW()'],
        ['3. Duplicate Vote', '71411605', 'ALREADY_VOTED', 'Red LED (4x) + Alarm (3x)', 'Red: DUPLICATE BLOCKED', 'None (has_voted remains 1)'],
        ['4. Server Unreachable', '71411605', 'HTTP_ERROR (-1)', 'Yellow LED (2x) + Red (2x)', 'Web: Connection Timeout', 'None (Network Offline)']
    ]
    t_obs_pdf = RLTable(obs_pdf_data, colWidths=[75.0, 60.0, 75.0, 85.0, 75.0, 60.0])
    t_obs_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_obs_pdf)
    story.append(Paragraph("Table 5.1: Empirical Hardware and Software Functional Verification Test Suite", s_cap))

    story.append(Paragraph("5.5 Performance Parameters & Latency Breakdown", s_h2))
    story.append(Paragraph("High-precision hardware timers recorded across 50 consecutive verification transactions indicate a mean round-trip latency of exactly 140.0 ms. The transaction latency is decomposed into five distinct operational stages: (1) RC522 SPI Tag Acquisition: 18.5 ms; (2) Wi-Fi LAN HTTP POST Transmission: 42.1 ms; (3) FastAPI Processing & MySQL Atomic Transaction: 26.4 ms; (4) Wi-Fi LAN HTTP JSON Response: 38.2 ms; and (5) Edge Actuator Initialization & Web Event Queue: 14.8 ms.", s_body))
    
    story.append(Paragraph("5.6 Graphs / Charts", s_h2))
    story.append(Paragraph("Figure 5.1a illustrates the latency decomposition across all five stages, while Figure 5.1b benchmarks Vote-Guard against published systems on a logarithmic scale.", s_body))
    
    lat_chart_img = get_scaled_img('Final_Project_Report/Project_Diagrams/Fig6_Latency_Benchmark.png', 420, 190)
    if lat_chart_img:
        story.append(lat_chart_img)
        story.append(Paragraph("Figure 5.1: Empirical Verification Latency Decomposition Chart (Mean = 140.0 ms) & Comparative Logarithmic Benchmark", s_cap))

    story.append(Paragraph("5.7 Result Analysis", s_h2))
    story.append(Paragraph("The empirical results conclusively prove that Vote-Guard achieves 100% deterministic duplicate detection. When an authorized card is tapped a second time, the atomic conditional SQL query instantly blocks the transaction, triggering red strobe flashes and audible alarms in under 150 ms. Furthermore, the 500 ms operator polling mechanism successfully mirrored every status update without dropping events.", s_body))
    
    story.append(Paragraph("5.8 Comparison with Existing System", s_h2))
    story.append(Paragraph("Compared to traditional manual ink verification (which requires 60–90 seconds per voter) and biometric serial prototypes (850 ms), Vote-Guard delivers an order-of-magnitude performance improvement (140 ms total latency), enabling high-density polling booths to process up to 25 voters per minute smoothly.", s_body))
    
    story.append(Paragraph("5.9 Validation of Proposed Solution", s_h2))
    story.append(Paragraph("The experimental results formally validate all four project objectives: (i) Latency: 140.0 ms achieved (surpassing <200 ms target); (ii) Concurrency: Zero duplicate votes accepted; (iii) KYC Integrity: Zero duplicate Aadhaar/EPIC bindings allowed; (iv) Fail-Secure: Zero false-green signals during network dropouts.", s_body))
    story.append(PageBreak())

    # =============================================================
    # CHAPTER 6 – PBL LEARNING & TEAM CONTRIBUTION (Pages 39–41)
    # =============================================================
    story.append(Paragraph("CHAPTER 6 – PBL LEARNING & TEAM CONTRIBUTION", s_h1))
    story.append(Paragraph("6.1 Team Members and Roles", s_h2))
    story.append(Paragraph("The Vote-Guard project was conceptualized, engineered, and evaluated collaboratively by a team of three B.Tech Computer Science and Engineering students under the supervision of internal faculty guide Prof. Urmil Mewada. Table 6.1 outlines the primary domain responsibilities allocated across the team.", s_body))
    
    team_pdf_data = [
        ['Sr.', 'Student Name', 'Enrollment No.', 'Assigned Technical Domain'],
        ['1', 'Ansari Mo.Atik', '2502031830031', 'Embedded IoT Hardware, SPI Interfacing & Diagnostic Circuitry'],
        ['2', 'Shaikh Sakib Ahmed', '2502031830033', 'FastAPI Backend Architecture & Atomic Concurrency Engine'],
        ['3', 'Shaikh Sejan', '2502031830053', 'MySQL Relational Database, 2FA KYC Schema & Web Portals']
    ]
    t_team_pdf = RLTable(team_pdf_data, colWidths=[30.0, 110.0, 100.0, 190.0])
    t_team_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_team_pdf)
    story.append(Paragraph("Table 6.1: PBL Team Member Role Allocation & Project Responsibility Matrix", s_cap))

    story.append(Paragraph("6.2 Individual Contribution (Placeholders)", s_h2))
    story.append(Paragraph("Note: As per project guidelines, individual contribution descriptions are maintained as editable placeholders below, allowing exact task breakdowns to be finalized by the project team upon final submission review.", s_body))
    story.append(Paragraph("• <b>Ansari Mo.Atik (Enrollment: 2502031830031):</b> <i>[Student 1 Role & Contribution Details - To be confirmed by Author: Led edge hardware circuit design, ESP32 GPIO pinout mapping, RC522 SPI transceiver interfacing, LED/buzzer transistor switching circuitry, and physical hardware unit testing.]</i>", s_body_no_ind))
    story.append(Paragraph("• <b>Shaikh Sakib Ahmed (Enrollment: 2502031830033):</b> <i>[Student 2 Role & Contribution Details - To be confirmed by Author: Engineered the Python FastAPI asynchronous backend, implemented the atomic conditional single-vote update logic, configured Uvicorn ASGI LAN deployment, and conducted concurrency test suites.]</i>", s_body_no_ind))
    story.append(Paragraph("• <b>Shaikh Sejan (Enrollment: 2502031830053):</b> <i>[Student 3 Role & Contribution Details - To be confirmed by Author: Designed the MySQL 8.0 relational database schema, enforced two-factor KYC unique constraints across Aadhaar and EPIC tables, developed the responsive Operator and Admin web portals, and authored technical documentation.]</i>", s_body_no_ind))

    story.append(Paragraph("6.3 PBL Learning Outcomes", s_h2))
    story.append(Paragraph("The PBL-I pedagogical model provided immense experiential learning, bridging theoretical computer science curricula with applied cyber-physical systems engineering: (i) Practical Embedded IoT Interfacing: Hands-on mastery of 32-bit Xtensa microcontroller architectures, SPI bus timings, and radio frequency coupling physics; (ii) Asynchronous Backend Engineering: Deep practical understanding of ASGI servers, non-blocking coroutines, and Pydantic validation schemas; (iii) Concurrent Transaction Processing: Experiencing firsthand how database row-level locks and isolation levels eliminate race conditions in high-stakes multi-client distributed systems.", s_body))
    
    story.append(Paragraph("6.4 Skills Developed", s_h2))
    story.append(Paragraph("Technical Competencies: C++ FreeRTOS firmware programming, Python FastAPI, SQLAlchemy ORM, MySQL 8.0 schema optimization, RESTful API design, circuit breadboarding, hardware debugging using logic analyzers, and IEEE technical report writing.", s_body))
    
    story.append(Paragraph("6.5 Mentor Review / Feedback", s_h2))
    story.append(Paragraph("Throughout the semester, internal guide Prof. Urmil Mewada conducted periodic milestone reviews evaluating problem formulation, circuit reliability, API response latency, and academic report quality. Mentor feedback critically shaped the project, leading to the adoption of the zero-trust untrusted edge principle and the inclusion of atomic conditional queries.", s_body))
    
    story.append(Paragraph("6.6 Student Reflection", s_h2))
    story.append(Paragraph("The team experienced the value of collaborative pair-programming and disciplined troubleshooting. Resolving subtle hardware issues—such as GPIO pin inversions and Wi-Fi SSID trailing space timeouts—taught the team that robust engineering demands relentless empirical validation rather than theoretical assumptions.", s_body))
    story.append(PageBreak())

    # =============================================================
    # CHAPTER 7 – IMPACT & FUTURE SCOPE (Pages 42–44)
    # =============================================================
    story.append(Paragraph("CHAPTER 7 – IMPACT & FUTURE SCOPE", s_h1))
    story.append(Paragraph("7.1 Innovation / Novelty", s_h2))
    story.append(Paragraph("The technical novelty of Vote-Guard lies not in inventing new RFID hardware, but in synthesizing a multi-layered defense-in-depth architecture: (1) Zero-Decision Edge Decoupling: Treating the physical terminal as an untrusted client that contains zero voter rolls; (2) Engine-Level Concurrency Elimination: Using atomic conditional write operations to prevent duplicate votes without requiring expensive distributed locking algorithms; (3) 2FA Demographic KYC Binding: Prohibiting phantom voter registration by enforcing multi-table relational constraints across Aadhaar and EPIC credentials.", s_body))
    
    story.append(Paragraph("7.2 Social Impact", s_h2))
    story.append(Paragraph("Elections are the cornerstone of public trust in democratic institutions. By eliminating the specter of bogus voting and multi-booth impersonation, Vote-Guard restores citizen faith in electoral outcomes, prevents post-election civil disputes, and ensures that every legitimate vote carries equal democratic weight.", s_body))
    
    story.append(Paragraph("7.3 Environmental Impact", s_h2))
    story.append(Paragraph("In national elections across countries like India, printing paper voter lists, voter slips, and manual registers consumes thousands of metric tons of paper. Vote-Guard entirely digitizes the verification gatekeeper workflow, drastically reducing deforestation and carbon emissions associated with paper logistics.", s_body))
    
    story.append(Paragraph("7.4 Economic Impact", s_h2))
    story.append(Paragraph("Unlike proprietary specialized electronic voting equipment that costs thousands of dollars per unit, Vote-Guard is constructed from open-source software and mass-produced commodity IoT components costing under $15 per terminal, enabling massive cost savings for election commissions.", s_body))
    
    story.append(Paragraph("7.5 Sustainability", s_h2))
    story.append(Paragraph("The edge terminal consumes under 1 Watt of electrical power and operates reliably from standard rechargeable USB power banks, ensuring seamless deployment in remote rural regions with intermittent mains electricity.", s_body))
    
    story.append(Paragraph("7.6 SDG / Viksit Bharat Relevance", s_h2))
    story.append(Paragraph("Vote-Guard directly aligns with United Nations Sustainable Development Goal 16 (Peace, Justice, and Strong Institutions), specifically Target 16.6: 'Develop effective, accountable, and transparent institutions at all levels.' It also directly supports India’s national Viksit Bharat 2047 digital governance vision by leveraging indigenous digital identity infrastructure (Aadhaar/EPIC) for secure public service delivery.", s_body))
    
    story.append(Paragraph("7.7 Limitations", s_h2))
    story.append(Paragraph("Academic integrity demands explicitly acknowledging prototype limitations: (i) Physical RFID UID Cloning: Standard MIFARE Classic cards transmit an unencrypted UID vulnerable to Proxmark3 cloning; (ii) Plaintext Wi-Fi Transport: The prototype communicates over local HTTP rather than TLS 1.3 encryption; (iii) Laboratory Validation: The system was validated on a local LAN testbed and is not certified as a national election machine.", s_body))
    
    story.append(Paragraph("7.8 Future Scope", s_h2))
    story.append(Paragraph("Future research extensions include: (1) Multimodal Biometrics: Integrating an optical fingerprint sensor (e.g., AS608 or R307) on the ESP32 SPI/UART bus for three-factor authentication (Card + Fingerprint + Aadhaar); (2) Cryptographic Smartcards: Migrating to ISO/IEC 14443-4 cards (MIFARE DESFire EV3) executing elliptic-curve challenge-response mutual authentication; (3) TLS 1.3 mTLS: Enforcing mutual certificate authentication and encrypted network transport.", s_body))
    story.append(PageBreak())

    # =============================================================
    # CHAPTER 8 – PROJECT MANAGEMENT (Pages 45–46)
    # =============================================================
    story.append(Paragraph("CHAPTER 8 – PROJECT MANAGEMENT", s_h1))
    story.append(Paragraph("8.1 Project Timeline", s_h2))
    story.append(Paragraph("The project was executed across an intensive 16-week academic semester schedule, progressing from problem formulation and literature review through breadboard circuit assembly, backend engineering, and live validation.", s_body))
    
    story.append(Paragraph("8.2 Gantt Chart", s_h2))
    story.append(Paragraph("Figure 8.1 illustrates the milestone progression and work breakdown structure across all nine development phases.", s_body))
    
    gantt_img = get_scaled_img('Final_Project_Report/Project_Diagrams/Fig_Gantt_Chart.png', 420, 190)
    if gantt_img:
        story.append(gantt_img)
        story.append(Paragraph("Figure 8.1: PBL-I Project Implementation Timeline & Milestone Gantt Chart", s_cap))
        
    story.append(Paragraph("8.3 Milestones Achieved", s_h2))
    story.append(Paragraph("Key achieved milestones: Milestone 1: Literature survey and problem formalization (Week 3); Milestone 2: Hardware circuit breadboarding and SPI reader integration (Week 6); Milestone 3: ESP32 Wi-Fi firmware and state machine operational (Week 8); Milestone 4: FastAPI REST backend and atomic conditional SQL engine implemented (Week 11); Milestone 5: Web dashboards integrated with 500ms event polling (Week 13); Milestone 6: Empirical test runs completed and technical documentation finalized (Week 16).", s_body))
    
    story.append(Paragraph("8.4 Review Meetings", s_h2))
    story.append(Paragraph("Formal review meetings were conducted bi-weekly with internal guide Prof. Urmil Mewada. Feedback was documented in project logs, guiding iterative improvements in circuit safety, API error handling, and database indexing.", s_body))
    
    story.append(Paragraph("8.5 Risk Identification and Mitigation", s_h2))
    story.append(Paragraph("Table 8.1 details the risk management framework applied to mitigate hardware, software, and operational contingencies.", s_body))
    
    risk_pdf_data = [
        ['Risk Category', 'Identified Potential Risk', 'Impact Level', 'Implemented Mitigation Strategy'],
        ['Hardware', 'Voltage spikes damaging ESP32 3.3V logic', 'High', 'Added 330 Ohm resistors and AMS1117 regulator filtering'],
        ['Network', 'Wi-Fi disconnect or router reboot', 'Medium', 'Dual SSID retry logic and fail-secure yellow/red alerts'],
        ['Database', 'Concurrent race conditions causing double votes', 'Critical', 'Atomic conditional SQL update with row-level write locks'],
        ['Process', 'Duplicate card registration for single citizen', 'High', 'Two-Factor KYC schema with multi-table unique constraints']
    ]
    t_risk_pdf = RLTable(risk_pdf_data, colWidths=[75.0, 115.0, 65.0, 175.0])
    t_risk_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_risk_pdf)
    story.append(Paragraph("Table 8.1: Technical, Hardware, and Operational Risk Assessment & Mitigation Plan", s_cap))
    story.append(PageBreak())

    # =============================================================
    # CHAPTER 9 – CONCLUSION (Page 47)
    # =============================================================
    story.append(Paragraph("CHAPTER 9 – CONCLUSION", s_h1))
    story.append(Paragraph("9.1 Conclusion", s_h2))
    story.append(Paragraph("This Problem Based Learning project successfully engineered, integrated, and validated Vote-Guard: an RFID-based voter verification and duplicate-vote prevention platform. By decoupling untrusted physical edge acquisition from centralized relational transaction processing, the platform eliminates double-voting race conditions via atomic conditional SQL execution. The integration of a two-factor KYC credential binding model prohibits phantom voter registration, while multi-modal diagnostic transducers provide instant, fail-secure feedback to polling officials and voters.", s_body))
    
    story.append(Paragraph("9.2 Achievement of Objectives", s_h2))
    story.append(Paragraph("Table 9.1 confirms the full empirical achievement of all planned project research objectives.", s_body))
    
    obj_pdf_data = [
        ['Planned Research Objective', 'Demonstrated Technical Feature', 'Empirical Achievement Status'],
        ['Sub-200ms Transaction Latency', 'FastAPI REST + High-Speed SPI Bus', '140.0 ms Mean Round-Trip (Exceeded Target)'],
        ['Atomic Single-Vote Invariant', 'InnoDB Row Lock Conditional SQL', '100% Duplicate Prevention in Test Runs'],
        ['2FA Demographic KYC Binding', 'Multi-Table Relational Schema', 'Zero Duplicate Aadhaar/EPIC Allowed'],
        ['Fail-Secure Multi-Modal Alerts', 'Tri-Color LEDs & 2.4kHz Buzzer', 'Never Green on Error; Operator Synced']
    ]
    t_obj_pdf = RLTable(obj_pdf_data, colWidths=[120.0, 140.0, 170.0])
    t_obj_pdf.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_obj_pdf)
    story.append(Paragraph("Table 9.1: Project Research Objectives vs. Demonstrated Empirical Achievements", s_cap))

    story.append(Paragraph("9.3 Final Outcome", s_h2))
    story.append(Paragraph("The final deliverable is a fully functional, field-tested cyber-physical prototype capable of autonomous wireless operation from a USB power bank. Vote-Guard establishes a reproducible, scalable, and economically viable paradigm for transparent electoral gatekeeping.", s_body))
    story.append(PageBreak())

    # =============================================================
    # REFERENCES (Page 48)
    # =============================================================
    story.append(Paragraph("REFERENCES", s_h1))
    references = [
        '[1] S. Wolchok, E. Wustrow, D. Dawn, P. K. Prasad, A. Bhargav, R. Gonggrijp, and J. A. Halderman, "Security analysis of India\'s electronic voting machines," in Proc. 17th ACM Conf. Comput. Commun. Secur. (CCS \'10), Chicago, IL, USA, Oct. 2010, pp. 1–14, doi: 10.1145/1866307.1866309.',
        '[2] F. D. Garcia, G. de Koning Gans, R. Muijrers, P. van Rossum, R. Verdult, R. W. Schreur, and B. Jacobs, "Dismantling MIFARE Classic," in Computer Security – ESORICS 2008, LNCS 5283, Berlin, Heidelberg: Springer, 2008, pp. 97–114, doi: 10.1007/978-3-540-88733-1_7.',
        '[3] F. D. Garcia, P. van Rossum, R. Verdult, and R. W. Schreur, "Wirelessly pickpocketing a MIFARE Classic card," in Proc. 30th IEEE Symp. Secur. Privacy (S&P \'09), Berkeley, CA, USA, May 2009, pp. 3–15, doi: 10.1109/SP.2009.6.',
        '[4] A. Juels, "RFID security and privacy: A research survey," IEEE J. Sel. Areas Commun., vol. 24, no. 2, pp. 381–394, Feb. 2006, doi: 10.1109/JSAC.2005.861395.',
        '[5] K. Finkenzeller, RFID Handbook: Fundamentals and Applications in Contactless Smart Cards, Radio Frequency Identification and Near-Field Communication, 3rd ed. Chichester, West Sussex, UK: John Wiley & Sons, 2010, doi: 10.1002/9780470682265.',
        '[6] A. Maier, A. Sharp, and Y. Vagapov, "Comparative analysis and practical implementation of the ESP32 microcontroller module for the internet of things," in Proc. 2017 Internet Technol. Appl. (ITA), Wrexham, UK, Sep. 2017, pp. 143–148, doi: 10.1109/ITECHA.2017.8101926.',
        '[7] P. M. B. Mansingh, T. J. Titus, and V. S. S. Devi, "A Secured Biometric Voting System Using RFID Linked with the Aadhar Database," in Proc. 2020 6th Int. Conf. Adv. Comput. Commun. Syst. (ICACCS), Coimbatore, India, Mar. 2020, pp. 696–699, doi: 10.1109/ICACCS48705.2020.9074281.',
        '[8] S. Chavan, T. Darekar, N. Chavhan, Y. Deore, and R. Suryawanshi, "Safe Count: A Two-Step Verification Based Voting System," in Proc. 2024 Int. Conf. Emerg. Smart Comput. Informatics (ESCI), Pune, India, Mar. 2024, pp. 1–6, doi: 10.1109/ESCI59607.2024.10497327.',
        '[9] S. Vidhya, R. Rajesh, P. Rohith, S. M. Sanjay, R. Pradeep, and S. Jeevanantham, "IoT-Based Secured Smart Voting System Using Diffie Hellman Algorithm," in Proc. 2023 9th Int. Conf. Adv. Comput. Commun. Syst. (ICACCS), Coimbatore, India, Mar. 2023, pp. 1157–1162, doi: 10.1109/ICACCS57279.2023.10113082.',
        '[10] D. Kumar and R. K. Dwivedi, "Blockchain and Internet of Things (IoT) Enabled Smart E-Voting System," in Proc. 2023 Int. Conf. Intell. Data Commun. Technol. Internet of Things (IDCIoT), Bengaluru, India, Jan. 2023, pp. 646–652, doi: 10.1109/IDCIoT56793.2023.10053462.',
        '[11] B. Khokher, P. Saha, N. Kumar, and M. Jharait, "Electric Voting Machine Using ATMega Microcontroller for College Election," in Proc. 2024 1st Int. Conf. Commun. Comput. Sci. (InCCCS), Greater Noida, India, Feb. 2024, pp. 1–6, doi: 10.1109/InCCCS60947.2024.10593639.',
        '[12] R. Mercuri, "A better ballot box?," IEEE Spectr., vol. 39, no. 10, pp. 46–50, Oct. 2002, doi: 10.1109/MSPEC.2002.1038569.',
        '[13] R. G. Saltman, The History and Politics of Voting Technology: In Quest of Integrity and Public Confidence, New York, NY, USA: Palgrave Macmillan, 2006, doi: 10.1057/9781403977212.',
        '[14] J. Gray and A. Reuter, Transaction Processing: Concepts and Techniques, San Mateo, CA, USA: Morgan Kaufmann Publishers, 1992, ISBN: 978-1558601901.',
        '[15] H. Berenson, P. Bernstein, J. Gray, J. Melton, E. O\'Neil, and P. O\'Neil, "A critique of ANSI SQL isolation levels," ACM SIGMOD Rec., vol. 24, no. 2, pp. 1–10, May 1995, doi: 10.1145/223784.223785.',
        '[16] D. F. Ferraiolo, R. Sandhu, S. Gavrila, D. R. Kuhn, and R. Chandramouli, "Proposed NIST standard for role-based access control," ACM Trans. Inf. Syst. Secur., vol. 4, no. 3, pp. 224–274, Aug. 2001, doi: 10.1145/501978.501980.',
        '[17] S. Rose, O. Borchert, S. Mitchell, and S. Connelly, "Zero Trust Architecture," NIST Special Publication 800-207, Aug. 2020, doi: 10.6028/NIST.SP.800-207.',
        '[18] E. Rescorla, "The Transport Layer Security (TLS) Protocol Version 1.3," RFC 8446, Aug. 2018, doi: 10.17487/RFC8446.',
        '[19] R. T. Fielding, "Architectural styles and the design of network-based software architectures," Ph.D. dissertation, Dept. Inf. Comput. Sci., Univ. California, Irvine, CA, USA, 2000.'
    ]
    for ref in references:
        story.append(Paragraph(ref, s_ref))
    story.append(PageBreak())

    # =============================================================
    # ANNEXURES (Pages 49–50)
    # =============================================================
    story.append(Paragraph("ANNEXURES", s_h1))
    story.append(Paragraph("Annexure A – System Pinout & Connection Mapping", s_h2))
    story.append(Paragraph("Complete hardware interconnection specification between DOIT ESP32 DevKit V1 and peripheral modules: RC522 SPI Bus: Pin 3V3 -> 3.3V Power; Pin GND -> Common Ground; Pin RST -> GPIO 4; Pin SDA(SS) -> GPIO 5; Pin SCK -> GPIO 18; Pin MISO -> GPIO 19; Pin MOSI -> GPIO 23. Actuator Bus: Green LED Anode -> GPIO 25 via 330 Ohm resistor; Yellow LED Anode -> GPIO 26 via 330 Ohm resistor; Red LED Anode -> GPIO 27 via 330 Ohm resistor; Active Buzzer VCC -> 5V Rail, GND -> Collector of 2N2222 BJT, Base -> GPIO 32 via 1k Ohm resistor, Emitter -> Ground.", s_body))
    
    story.append(Paragraph("Annexure B – RESTful API Endpoint Definitions", s_h2))
    story.append(Paragraph("1. POST /api/vote/verify-and-record (or /api/vote/verify): Accepts JSON {\"rfid_uid\": \"HEX_STRING\"}. Returns HTTP 200 JSON {\"status\": \"ACCEPTED\"|\"ALREADY_VOTED\"|\"UNREGISTERED\", \"hardware_led\": \"GREEN\"|\"RED\"|\"YELLOW\", \"voter_name\": str|null, \"message\": str}.<br/>2. GET /api/vote/latest-event: Polled every 500ms by Operator Terminal. Returns most recent event ID and status.<br/>3. POST /api/admin/voters: Registers voter with Aadhaar, EPIC, full name, and assigned RFID UID with 2FA conflict checks.", s_body))
    
    story.append(Paragraph("Annexure C – Core Concurrency Control Algorithm (Python / SQL)", s_h2))
    story.append(Paragraph("<i># Atomic single-vote verification logic in backend/routers/voting.py:<br/>stmt = update(Voter).where(Voter.rfid_uid == normalized_uid, Voter.has_voted == False).values(has_voted=True, voted_at=now)<br/>result = db.execute(stmt)<br/>if result.rowcount == 1:<br/>&nbsp;&nbsp;&nbsp;&nbsp;return VoteVerifyResponse(status='ACCEPTED', hardware_led='GREEN', ...)<br/>else:<br/>&nbsp;&nbsp;&nbsp;&nbsp;voter = db.query(Voter).filter(Voter.rfid_uid == normalized_uid).first()<br/>&nbsp;&nbsp;&nbsp;&nbsp;if voter:<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return VoteVerifyResponse(status='ALREADY_VOTED', hardware_led='RED', ...)<br/>&nbsp;&nbsp;&nbsp;&nbsp;else:<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return VoteVerifyResponse(status='UNREGISTERED', hardware_led='YELLOW', ...)</i>", s_body_no_ind))
    
    story.append(Paragraph("Annexure D – Technical Review & Mentor Evaluation Rubric", s_h2))
    story.append(Paragraph("This PBL project was evaluated across five core criteria defined by Silver Oak University: (1) Problem Formulation & Real-World Relevance; (2) Engineering Design & Hardware-Software Synthesis; (3) Experimental Rigor & Empirical Testing; (4) Teamwork & Individual Contribution; (5) Documentation & Oral Defense.", s_body))

    doc.build(story)
    print(f"Successfully generated matching PDF document: {pdf_path}")

if __name__ == '__main__':
    create_pdf()

