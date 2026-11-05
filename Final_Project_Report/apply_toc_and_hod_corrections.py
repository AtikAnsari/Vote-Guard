import os
import re

print("==================================================================")
print("  APPLYING TOC PAGE NUMBERS & CERTIFICATE HOD CORRECTIONS")
print("==================================================================")

# ==============================================================================
# 1. UPDATE build_50page_report.py
# ==============================================================================
pdf_gen_path = 'Final_Project_Report/build_50page_report.py'
with open(pdf_gen_path, 'r', encoding='utf-8') as f:
    pdf_text = f.read()

# 1.1 Remove ONLY '[Head of Department]' on Certificate Page (Page 2)
# Keep horizontal signature line, and exactly:
# Head of Department
# Department of CSE
# College of Technology
old_hod_block = 'Paragraph("____________________________<br/><b>[Head of Department]</b><br/>Head of Department<br/>Department of CSE<br/>College of Technology", ParagraphStyle(\'SigR\', fontName=\'Times-Roman\', fontSize=9, leading=12.5, alignment=2))'
new_hod_block = 'Paragraph("____________________________<br/>Head of Department<br/>Department of CSE<br/>College of Technology", ParagraphStyle(\'SigR\', fontName=\'Times-Roman\', fontSize=9, leading=12.5, alignment=2))'

if old_hod_block in pdf_text:
    pdf_text = pdf_text.replace(old_hod_block, new_hod_block)
    print("[PDF] 1. Removed '[Head of Department]' while strictly preserving the 3 lines below it.")
else:
    print("[PDF] 1. HOD block already updated.")

# 1.2 Update TOC Part 1 Data in build_50page_report.py
old_toc1_block = """    toc1_data = [
        [Paragraph("No.", s_tbl_hdr), Paragraph("Chapter / Section Topic Description", s_tbl_hdr), Paragraph("Page", s_tbl_hdr)],
        [Paragraph("1.", s_tbl_cell_center), Paragraph("Cover Page / Title Page", s_tbl_cell_bold), Paragraph("1", s_tbl_cell_center)],
        [Paragraph("2.", s_tbl_cell_center), Paragraph("Certificate", s_tbl_cell_bold), Paragraph("2", s_tbl_cell_center)],
        [Paragraph("3.", s_tbl_cell_center), Paragraph("Declaration", s_tbl_cell_bold), Paragraph("3", s_tbl_cell_center)],
        [Paragraph("4.", s_tbl_cell_center), Paragraph("Acknowledgement", s_tbl_cell_bold), Paragraph("4", s_tbl_cell_center)],
        [Paragraph("5.", s_tbl_cell_center), Paragraph("Abstract", s_tbl_cell_bold), Paragraph("5", s_tbl_cell_center)],
        [Paragraph("6.", s_tbl_cell_center), Paragraph("Keywords & Research Scope Summary", s_tbl_cell_bold), Paragraph("6", s_tbl_cell_center)],
        [Paragraph("7.", s_tbl_cell_center), Paragraph("List of Figures", s_tbl_cell_bold), Paragraph("7", s_tbl_cell_center)],
        [Paragraph("8.", s_tbl_cell_center), Paragraph("List of Tables", s_tbl_cell_bold), Paragraph("8", s_tbl_cell_center)],
        [Paragraph("9.", s_tbl_cell_center), Paragraph("List of Abbreviations", s_tbl_cell_bold), Paragraph("9", s_tbl_cell_center)],
        [Paragraph("10.", s_tbl_cell_center), Paragraph("Table of Contents", s_tbl_cell_bold), Paragraph("10", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 1</b>", s_tbl_cell_bold), Paragraph("<b>INTRODUCTION</b>", s_tbl_cell_bold), Paragraph("<b>12</b>", s_tbl_cell_center)],
        [Paragraph("1.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Background of the PBL", s_tbl_cell), Paragraph("12", s_tbl_cell_center)],
        [Paragraph("1.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Problem Identification", s_tbl_cell), Paragraph("12", s_tbl_cell_center)],
        [Paragraph("1.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Problem Statement & Invariant Formulation", s_tbl_cell), Paragraph("13", s_tbl_cell_center)],
        [Paragraph("1.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Motivation", s_tbl_cell), Paragraph("13", s_tbl_cell_center)],
        [Paragraph("1.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Objectives of the Project", s_tbl_cell), Paragraph("14", s_tbl_cell_center)],
        [Paragraph("1.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Scope of the PBL", s_tbl_cell), Paragraph("14", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 2</b>", s_tbl_cell_bold), Paragraph("<b>PROBLEM STUDY & LITERATURE REVIEW</b>", s_tbl_cell_bold), Paragraph("<b>15</b>", s_tbl_cell_center)],
        [Paragraph("2.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Existing System / Current Practice", s_tbl_cell), Paragraph("15", s_tbl_cell_center)],
        [Paragraph("2.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Problems in Existing System", s_tbl_cell), Paragraph("15", s_tbl_cell_center)],
        [Paragraph("2.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Root Cause Analysis (Ishikawa Fishbone Model)", s_tbl_cell), Paragraph("16", s_tbl_cell_center)],
        [Paragraph("2.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Stakeholder Analysis & Requirements Matrix", s_tbl_cell), Paragraph("17", s_tbl_cell_center)],
        [Paragraph("2.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Literature Review (Critical Survey of Prior Work)", s_tbl_cell), Paragraph("18", s_tbl_cell_center)],
        [Paragraph("2.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Existing Solutions / Benchmark Study", s_tbl_cell), Paragraph("20", s_tbl_cell_center)],
        [Paragraph("2.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Identified Gap in Engineering Literature", s_tbl_cell), Paragraph("20", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 3</b>", s_tbl_cell_bold), Paragraph("<b>PROPOSED SOLUTION</b>", s_tbl_cell_bold), Paragraph("<b>21</b>", s_tbl_cell_center)],
        [Paragraph("3.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Proposed Solution & Zero-Trust Paradigm", s_tbl_cell), Paragraph("21", s_tbl_cell_center)],
        [Paragraph("3.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Conceptual Architectural Framework", s_tbl_cell), Paragraph("21", s_tbl_cell_center)],
        [Paragraph("3.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Block Diagram / System Architecture", s_tbl_cell), Paragraph("22", s_tbl_cell_center)],
        [Paragraph("3.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Working Principle & Step-by-Step State Flow", s_tbl_cell), Paragraph("23", s_tbl_cell_center)],
        [Paragraph("3.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Major Components & Subsystem Allocation", s_tbl_cell), Paragraph("24", s_tbl_cell_center)],
        [Paragraph("3.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Hardware Requirements & Bill of Materials (BOM)", s_tbl_cell), Paragraph("24", s_tbl_cell_center)],
        [Paragraph("3.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Software Requirements & Framework Stack", s_tbl_cell), Paragraph("25", s_tbl_cell_center)],
        [Paragraph("3.8", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Technical Specifications", s_tbl_cell), Paragraph("26", s_tbl_cell_center)],
        [Paragraph("3.9", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Design Calculations (Power Budget & Antenna Link)", s_tbl_cell), Paragraph("26", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 4</b>", s_tbl_cell_bold), Paragraph("<b>IMPLEMENTATION / DEVELOPMENT</b>", s_tbl_cell_bold), Paragraph("<b>27</b>", s_tbl_cell_center)],
        [Paragraph("4.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Methodology & Engineering Lifecycle", s_tbl_cell), Paragraph("27", s_tbl_cell_center)],
        [Paragraph("4.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Project Development Steps", s_tbl_cell), Paragraph("27", s_tbl_cell_center)],
        [Paragraph("4.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Diagram / Schematic & Interfacing Circuitry", s_tbl_cell), Paragraph("28", s_tbl_cell_center)],
        [Paragraph("4.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Hardware Implementation & Pinout Mapping", s_tbl_cell), Paragraph("29", s_tbl_cell_center)],
        [Paragraph("4.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Software / Programming / Control Logic", s_tbl_cell), Paragraph("30", s_tbl_cell_center)],
        [Paragraph("4.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2FA KYC Voter Registration Workflow", s_tbl_cell), Paragraph("31", s_tbl_cell_center)],
        [Paragraph("4.8", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Database Schema Design & Normalization", s_tbl_cell), Paragraph("32", s_tbl_cell_center)],
        [Paragraph("4.9", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;System Interaction Flow (UML Sequence)", s_tbl_cell), Paragraph("33", s_tbl_cell_center)],
        [Paragraph("4.10", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Prototype Development & Frontend Web Portals", s_tbl_cell), Paragraph("34", s_tbl_cell_center)],
        [Paragraph("4.11", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Safety, Tamper Resistance & Operational Security", s_tbl_cell), Paragraph("36", s_tbl_cell_center)]
    ]"""

new_toc1_block = """    toc1_data = [
        [Paragraph("No.", s_tbl_hdr), Paragraph("Chapter / Section Topic Description", s_tbl_hdr), Paragraph("Page", s_tbl_hdr)],
        [Paragraph("1.", s_tbl_cell_center), Paragraph("Cover Page / Title Page", s_tbl_cell_bold), Paragraph("", s_tbl_cell_center)],
        [Paragraph("2.", s_tbl_cell_center), Paragraph("Certificate", s_tbl_cell_bold), Paragraph("i", s_tbl_cell_center)],
        [Paragraph("3.", s_tbl_cell_center), Paragraph("Declaration", s_tbl_cell_bold), Paragraph("ii", s_tbl_cell_center)],
        [Paragraph("4.", s_tbl_cell_center), Paragraph("Acknowledgement", s_tbl_cell_bold), Paragraph("iii", s_tbl_cell_center)],
        [Paragraph("5.", s_tbl_cell_center), Paragraph("Abstract", s_tbl_cell_bold), Paragraph("iv", s_tbl_cell_center)],
        [Paragraph("6.", s_tbl_cell_center), Paragraph("Keywords & Research Scope Summary", s_tbl_cell_bold), Paragraph("v", s_tbl_cell_center)],
        [Paragraph("7.", s_tbl_cell_center), Paragraph("List of Figures", s_tbl_cell_bold), Paragraph("1", s_tbl_cell_center)],
        [Paragraph("8.", s_tbl_cell_center), Paragraph("List of Tables", s_tbl_cell_bold), Paragraph("2", s_tbl_cell_center)],
        [Paragraph("9.", s_tbl_cell_center), Paragraph("List of Abbreviations", s_tbl_cell_bold), Paragraph("3", s_tbl_cell_center)],
        [Paragraph("10.", s_tbl_cell_center), Paragraph("Table of Contents", s_tbl_cell_bold), Paragraph("4", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 1</b>", s_tbl_cell_bold), Paragraph("<b>INTRODUCTION</b>", s_tbl_cell_bold), Paragraph("<b>6</b>", s_tbl_cell_center)],
        [Paragraph("1.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Background of the PBL", s_tbl_cell), Paragraph("6", s_tbl_cell_center)],
        [Paragraph("1.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Problem Identification", s_tbl_cell), Paragraph("6", s_tbl_cell_center)],
        [Paragraph("1.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Problem Statement & Invariant Formulation", s_tbl_cell), Paragraph("7", s_tbl_cell_center)],
        [Paragraph("1.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Motivation", s_tbl_cell), Paragraph("7", s_tbl_cell_center)],
        [Paragraph("1.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Objectives of the Project", s_tbl_cell), Paragraph("8", s_tbl_cell_center)],
        [Paragraph("1.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Scope of the PBL", s_tbl_cell), Paragraph("8", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 2</b>", s_tbl_cell_bold), Paragraph("<b>PROBLEM STUDY & LITERATURE REVIEW</b>", s_tbl_cell_bold), Paragraph("<b>9</b>", s_tbl_cell_center)],
        [Paragraph("2.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Existing System / Current Practice", s_tbl_cell), Paragraph("9", s_tbl_cell_center)],
        [Paragraph("2.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Problems in Existing System", s_tbl_cell), Paragraph("9", s_tbl_cell_center)],
        [Paragraph("2.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Root Cause Analysis (Ishikawa Fishbone Model)", s_tbl_cell), Paragraph("10", s_tbl_cell_center)],
        [Paragraph("2.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Stakeholder Analysis & Requirements Matrix", s_tbl_cell), Paragraph("11", s_tbl_cell_center)],
        [Paragraph("2.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Literature Review (Critical Survey of Prior Work)", s_tbl_cell), Paragraph("12", s_tbl_cell_center)],
        [Paragraph("2.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Existing Solutions / Benchmark Study", s_tbl_cell), Paragraph("14", s_tbl_cell_center)],
        [Paragraph("2.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Identified Gap in Engineering Literature", s_tbl_cell), Paragraph("14", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 3</b>", s_tbl_cell_bold), Paragraph("<b>PROPOSED SOLUTION</b>", s_tbl_cell_bold), Paragraph("<b>15</b>", s_tbl_cell_center)],
        [Paragraph("3.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Proposed Solution & Zero-Trust Paradigm", s_tbl_cell), Paragraph("15", s_tbl_cell_center)],
        [Paragraph("3.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Conceptual Architectural Framework", s_tbl_cell), Paragraph("15", s_tbl_cell_center)],
        [Paragraph("3.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Block Diagram / System Architecture", s_tbl_cell), Paragraph("16", s_tbl_cell_center)],
        [Paragraph("3.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Working Principle & Step-by-Step State Flow", s_tbl_cell), Paragraph("17", s_tbl_cell_center)],
        [Paragraph("3.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Major Components & Subsystem Allocation", s_tbl_cell), Paragraph("18", s_tbl_cell_center)],
        [Paragraph("3.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Hardware Requirements & Bill of Materials (BOM)", s_tbl_cell), Paragraph("18", s_tbl_cell_center)],
        [Paragraph("3.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Software Requirements & Framework Stack", s_tbl_cell), Paragraph("19", s_tbl_cell_center)],
        [Paragraph("3.8", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Technical Specifications", s_tbl_cell), Paragraph("20", s_tbl_cell_center)],
        [Paragraph("3.9", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Design Calculations (Power Budget & Antenna Link)", s_tbl_cell), Paragraph("20", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 4</b>", s_tbl_cell_bold), Paragraph("<b>IMPLEMENTATION / DEVELOPMENT</b>", s_tbl_cell_bold), Paragraph("<b>21</b>", s_tbl_cell_center)],
        [Paragraph("4.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Methodology & Engineering Lifecycle", s_tbl_cell), Paragraph("21", s_tbl_cell_center)],
        [Paragraph("4.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Project Development Steps", s_tbl_cell), Paragraph("21", s_tbl_cell_center)],
        [Paragraph("4.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Diagram / Schematic & Interfacing Circuitry", s_tbl_cell), Paragraph("22", s_tbl_cell_center)],
        [Paragraph("4.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Hardware Implementation & Pinout Mapping", s_tbl_cell), Paragraph("23", s_tbl_cell_center)],
        [Paragraph("4.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Software / Programming / Control Logic", s_tbl_cell), Paragraph("24", s_tbl_cell_center)],
        [Paragraph("4.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2FA KYC Voter Registration Workflow", s_tbl_cell), Paragraph("25", s_tbl_cell_center)],
        [Paragraph("4.8", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Database Schema Design & Normalization", s_tbl_cell), Paragraph("26", s_tbl_cell_center)],
        [Paragraph("4.9", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;System Interaction Flow (UML Sequence)", s_tbl_cell), Paragraph("27", s_tbl_cell_center)],
        [Paragraph("4.10", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Prototype Development & Frontend Web Portals", s_tbl_cell), Paragraph("28", s_tbl_cell_center)],
        [Paragraph("4.11", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Safety, Tamper Resistance & Operational Security", s_tbl_cell), Paragraph("30", s_tbl_cell_center)]
    ]"""

if old_toc1_block in pdf_text:
    pdf_text = pdf_text.replace(old_toc1_block, new_toc1_block)
    print("[PDF] 2. Updated Table of Contents Page 1 entries (Empty Cover, Roman i..v, Arabic 1..30).")
else:
    print("[PDF] 2. TOC 1 already updated.")

# 1.3 Update TOC Part 2 Data in build_50page_report.py
old_toc2_block = """    toc2_data = [
        [Paragraph("No.", s_tbl_hdr), Paragraph("Chapter / Section Topic Description", s_tbl_hdr), Paragraph("Page", s_tbl_hdr)],
        [Paragraph("<b>CHAPTER 5</b>", s_tbl_cell_bold), Paragraph("<b>TESTING & RESULTS</b>", s_tbl_cell_bold), Paragraph("<b>37</b>", s_tbl_cell_center)],
        [Paragraph("5.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Testing Methodology & Experimental Setup", s_tbl_cell), Paragraph("37", s_tbl_cell_center)],
        [Paragraph("5.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Test Conditions & Hardware Testbed", s_tbl_cell), Paragraph("37", s_tbl_cell_center)],
        [Paragraph("5.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Experimental Results & Test Execution Cases", s_tbl_cell), Paragraph("38", s_tbl_cell_center)],
        [Paragraph("5.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Comprehensive Observation Table", s_tbl_cell), Paragraph("39", s_tbl_cell_center)],
        [Paragraph("5.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Performance Parameters & Latency Metrics", s_tbl_cell), Paragraph("40", s_tbl_cell_center)],
        [Paragraph("5.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Graphs / Charts & Latency Breakdown", s_tbl_cell), Paragraph("40", s_tbl_cell_center)],
        [Paragraph("5.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Result Analysis & Statistical Validation", s_tbl_cell), Paragraph("41", s_tbl_cell_center)],
        [Paragraph("5.8", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Comparison with Existing Voting Systems", s_tbl_cell), Paragraph("41", s_tbl_cell_center)],
        [Paragraph("5.9", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Validation of Proposed Solution Against Objectives", s_tbl_cell), Paragraph("41", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 6</b>", s_tbl_cell_bold), Paragraph("<b>PBL LEARNING & TEAM CONTRIBUTION</b>", s_tbl_cell_bold), Paragraph("<b>42</b>", s_tbl_cell_center)],
        [Paragraph("6.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Team Members and Roles", s_tbl_cell), Paragraph("42", s_tbl_cell_center)],
        [Paragraph("6.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Individual Contribution (Placeholders)", s_tbl_cell), Paragraph("42", s_tbl_cell_center)],
        [Paragraph("6.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;PBL Learning Outcomes", s_tbl_cell), Paragraph("43", s_tbl_cell_center)],
        [Paragraph("6.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Skills Developed", s_tbl_cell), Paragraph("43", s_tbl_cell_center)],
        [Paragraph("6.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Mentor Review / Formative Feedback", s_tbl_cell), Paragraph("43", s_tbl_cell_center)],
        [Paragraph("6.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Student Reflection & Engineering Insights", s_tbl_cell), Paragraph("43", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 7</b>", s_tbl_cell_bold), Paragraph("<b>IMPACT & FUTURE SCOPE</b>", s_tbl_cell_bold), Paragraph("<b>44</b>", s_tbl_cell_center)],
        [Paragraph("7.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Innovation / Novelty", s_tbl_cell), Paragraph("44", s_tbl_cell_center)],
        [Paragraph("7.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Social Impact, 7.3 Environmental, 7.4 Economic", s_tbl_cell), Paragraph("44", s_tbl_cell_center)],
        [Paragraph("7.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Sustainability & Operational Viability", s_tbl_cell), Paragraph("45", s_tbl_cell_center)],
        [Paragraph("7.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;UN SDG 16 & Viksit Bharat 2047 Relevance", s_tbl_cell), Paragraph("45", s_tbl_cell_center)],
        [Paragraph("7.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Engineering Limitations", s_tbl_cell), Paragraph("45", s_tbl_cell_center)],
        [Paragraph("7.8", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Future Scope & Technology Roadmap", s_tbl_cell), Paragraph("45", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 8</b>", s_tbl_cell_bold), Paragraph("<b>PROJECT MANAGEMENT</b>", s_tbl_cell_bold), Paragraph("<b>46</b>", s_tbl_cell_center)],
        [Paragraph("8.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Project Timeline & Execution Phases", s_tbl_cell), Paragraph("46", s_tbl_cell_center)],
        [Paragraph("8.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Gantt Chart (16-Week Implementation Schedule)", s_tbl_cell), Paragraph("46", s_tbl_cell_center)],
        [Paragraph("8.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Milestones Achieved & Deliverables", s_tbl_cell), Paragraph("46", s_tbl_cell_center)],
        [Paragraph("8.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Review Meetings & Advisory Log", s_tbl_cell), Paragraph("47", s_tbl_cell_center)],
        [Paragraph("8.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Risk Identification and Mitigation Matrix", s_tbl_cell), Paragraph("47", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 9</b>", s_tbl_cell_bold), Paragraph("<b>CONCLUSION</b>", s_tbl_cell_bold), Paragraph("<b>48</b>", s_tbl_cell_center)],
        [Paragraph("9.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Conclusion", s_tbl_cell), Paragraph("48", s_tbl_cell_center)],
        [Paragraph("9.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Achievement of Objectives Conformance", s_tbl_cell), Paragraph("48", s_tbl_cell_center)],
        [Paragraph("9.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Final Outcome & Practical Significance", s_tbl_cell), Paragraph("48", s_tbl_cell_center)],
        [Paragraph("<b>REFERENCES</b>", s_tbl_cell_bold), Paragraph("<b>IEEE Reference Format Bibliography (19 Citations)</b>", s_tbl_cell_bold), Paragraph("<b>49</b>", s_tbl_cell_center)],
        [Paragraph("<b>ANNEXURES</b>", s_tbl_cell_bold), Paragraph("<b>Technical Documentation (Annexures A to D)</b>", s_tbl_cell_bold), Paragraph("<b>50</b>", s_tbl_cell_center)]
    ]"""

new_toc2_block = """    toc2_data = [
        [Paragraph("No.", s_tbl_hdr), Paragraph("Chapter / Section Topic Description", s_tbl_hdr), Paragraph("Page", s_tbl_hdr)],
        [Paragraph("<b>CHAPTER 5</b>", s_tbl_cell_bold), Paragraph("<b>TESTING & RESULTS</b>", s_tbl_cell_bold), Paragraph("<b>31</b>", s_tbl_cell_center)],
        [Paragraph("5.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Testing Methodology & Experimental Setup", s_tbl_cell), Paragraph("31", s_tbl_cell_center)],
        [Paragraph("5.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Test Conditions & Hardware Testbed", s_tbl_cell), Paragraph("31", s_tbl_cell_center)],
        [Paragraph("5.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Experimental Results & Test Execution Cases", s_tbl_cell), Paragraph("32", s_tbl_cell_center)],
        [Paragraph("5.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Comprehensive Observation Table", s_tbl_cell), Paragraph("33", s_tbl_cell_center)],
        [Paragraph("5.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Performance Parameters & Latency Metrics", s_tbl_cell), Paragraph("34", s_tbl_cell_center)],
        [Paragraph("5.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Graphs / Charts & Latency Breakdown", s_tbl_cell), Paragraph("34", s_tbl_cell_center)],
        [Paragraph("5.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Result Analysis & Statistical Validation", s_tbl_cell), Paragraph("35", s_tbl_cell_center)],
        [Paragraph("5.8", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Comparison with Existing Voting Systems", s_tbl_cell), Paragraph("35", s_tbl_cell_center)],
        [Paragraph("5.9", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Validation of Proposed Solution Against Objectives", s_tbl_cell), Paragraph("35", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 6</b>", s_tbl_cell_bold), Paragraph("<b>PBL LEARNING & TEAM CONTRIBUTION</b>", s_tbl_cell_bold), Paragraph("<b>36</b>", s_tbl_cell_center)],
        [Paragraph("6.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Team Members and Roles", s_tbl_cell), Paragraph("36", s_tbl_cell_center)],
        [Paragraph("6.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Individual Contribution (Placeholders)", s_tbl_cell), Paragraph("36", s_tbl_cell_center)],
        [Paragraph("6.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;PBL Learning Outcomes", s_tbl_cell), Paragraph("37", s_tbl_cell_center)],
        [Paragraph("6.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Skills Developed", s_tbl_cell), Paragraph("37", s_tbl_cell_center)],
        [Paragraph("6.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Mentor Review / Formative Feedback", s_tbl_cell), Paragraph("37", s_tbl_cell_center)],
        [Paragraph("6.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Student Reflection & Engineering Insights", s_tbl_cell), Paragraph("37", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 7</b>", s_tbl_cell_bold), Paragraph("<b>IMPACT & FUTURE SCOPE</b>", s_tbl_cell_bold), Paragraph("<b>38</b>", s_tbl_cell_center)],
        [Paragraph("7.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Innovation / Novelty", s_tbl_cell), Paragraph("38", s_tbl_cell_center)],
        [Paragraph("7.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Social Impact, 7.3 Environmental, 7.4 Economic", s_tbl_cell), Paragraph("38", s_tbl_cell_center)],
        [Paragraph("7.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Sustainability & Operational Viability", s_tbl_cell), Paragraph("39", s_tbl_cell_center)],
        [Paragraph("7.6", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;UN SDG 16 & Viksit Bharat 2047 Relevance", s_tbl_cell), Paragraph("39", s_tbl_cell_center)],
        [Paragraph("7.7", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Engineering Limitations", s_tbl_cell), Paragraph("39", s_tbl_cell_center)],
        [Paragraph("7.8", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Future Scope & Technology Roadmap", s_tbl_cell), Paragraph("39", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 8</b>", s_tbl_cell_bold), Paragraph("<b>PROJECT MANAGEMENT</b>", s_tbl_cell_bold), Paragraph("<b>40</b>", s_tbl_cell_center)],
        [Paragraph("8.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Project Timeline & Execution Phases", s_tbl_cell), Paragraph("40", s_tbl_cell_center)],
        [Paragraph("8.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Gantt Chart (16-Week Implementation Schedule)", s_tbl_cell), Paragraph("40", s_tbl_cell_center)],
        [Paragraph("8.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Milestones Achieved & Deliverables", s_tbl_cell), Paragraph("40", s_tbl_cell_center)],
        [Paragraph("8.4", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Review Meetings & Advisory Log", s_tbl_cell), Paragraph("41", s_tbl_cell_center)],
        [Paragraph("8.5", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Risk Identification and Mitigation Matrix", s_tbl_cell), Paragraph("41", s_tbl_cell_center)],
        [Paragraph("<b>CHAPTER 9</b>", s_tbl_cell_bold), Paragraph("<b>CONCLUSION</b>", s_tbl_cell_bold), Paragraph("<b>42</b>", s_tbl_cell_center)],
        [Paragraph("9.1", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Conclusion", s_tbl_cell), Paragraph("42", s_tbl_cell_center)],
        [Paragraph("9.2", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Achievement of Objectives Conformance", s_tbl_cell), Paragraph("42", s_tbl_cell_center)],
        [Paragraph("9.3", s_tbl_cell_center), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;Final Outcome & Practical Significance", s_tbl_cell), Paragraph("42", s_tbl_cell_center)],
        [Paragraph("<b>REFERENCES</b>", s_tbl_cell_bold), Paragraph("<b>IEEE Reference Format Bibliography (19 Citations)</b>", s_tbl_cell_bold), Paragraph("<b>43</b>", s_tbl_cell_center)],
        [Paragraph("<b>ANNEXURES</b>", s_tbl_cell_bold), Paragraph("<b>Technical Documentation (Annexures A to D)</b>", s_tbl_cell_bold), Paragraph("<b>44</b>", s_tbl_cell_center)]
    ]"""

if old_toc2_block in pdf_text:
    pdf_text = pdf_text.replace(old_toc2_block, new_toc2_block)
    print("[PDF] 3. Updated Table of Contents Page 2 entries (Arabic 31..44 matching visible PDF pages).")
else:
    print("[PDF] 3. TOC 2 already updated.")

# 1.4 Also update List of Figures and List of Tables page references to match visible Arabic pages
old_lof_block = """    lof_data = [
        [Paragraph("Figure No.", s_tbl_hdr), Paragraph("Figure Title / Description", s_tbl_hdr), Paragraph("Page No.", s_tbl_hdr)],
        [Paragraph("Figure 2.1", s_tbl_cell_center), Paragraph("Ishikawa Fishbone Diagram for Root Cause Analysis of Electoral Fraud", s_tbl_cell), Paragraph("16", s_tbl_cell_center)],
        [Paragraph("Figure 3.1", s_tbl_cell_center), Paragraph("Vote-Guard Three-Tier Edge-to-Cloud System Architecture", s_tbl_cell), Paragraph("22", s_tbl_cell_center)],
        [Paragraph("Figure 4.1", s_tbl_cell_center), Paragraph("ESP32 DevKit V1 and RC522 RFID Circuit Wiring Schematic", s_tbl_cell), Paragraph("28", s_tbl_cell_center)],
        [Paragraph("Figure 4.2", s_tbl_cell_center), Paragraph("Two-Factor KYC Voter Registration & Credential Binding Workflow", s_tbl_cell), Paragraph("31", s_tbl_cell_center)],
        [Paragraph("Figure 4.3", s_tbl_cell_center), Paragraph("Normalized Relational Database Entity-Relationship Diagram (ERD)", s_tbl_cell), Paragraph("32", s_tbl_cell_center)],
        [Paragraph("Figure 4.4", s_tbl_cell_center), Paragraph("End-to-End Voter Verification UML Sequence Diagram", s_tbl_cell), Paragraph("33", s_tbl_cell_center)],
        [Paragraph("Figure 4.5", s_tbl_cell_center), Paragraph("Vote-Guard Security Portal (Role-Based Authentication Terminal)", s_tbl_cell), Paragraph("34", s_tbl_cell_center)],
        [Paragraph("Figure 4.6", s_tbl_cell_center), Paragraph("Polling Booth Operator Terminal (Live Hardware Scan Sync)", s_tbl_cell), Paragraph("34", s_tbl_cell_center)],
        [Paragraph("Figure 4.7", s_tbl_cell_center), Paragraph("Admin Security Dashboard (KYC Credential Registry & Metrics)", s_tbl_cell), Paragraph("35", s_tbl_cell_center)],
        [Paragraph("Figure 4.8", s_tbl_cell_center), Paragraph("Voter Registration & 2FA Credential Binding Interface", s_tbl_cell), Paragraph("35", s_tbl_cell_center)],
        [Paragraph("Figure 5.1", s_tbl_cell_center), Paragraph("Empirical Verification Latency Decomposition & Comparison Chart", s_tbl_cell), Paragraph("40", s_tbl_cell_center)],
        [Paragraph("Figure 8.1", s_tbl_cell_center), Paragraph("Vote-Guard PBL-I Project Execution Lifecycle Gantt Chart", s_tbl_cell), Paragraph("46", s_tbl_cell_center)]
    ]"""

new_lof_block = """    lof_data = [
        [Paragraph("Figure No.", s_tbl_hdr), Paragraph("Figure Title / Description", s_tbl_hdr), Paragraph("Page No.", s_tbl_hdr)],
        [Paragraph("Figure 2.1", s_tbl_cell_center), Paragraph("Ishikawa Fishbone Diagram for Root Cause Analysis of Electoral Fraud", s_tbl_cell), Paragraph("10", s_tbl_cell_center)],
        [Paragraph("Figure 3.1", s_tbl_cell_center), Paragraph("Vote-Guard Three-Tier Edge-to-Cloud System Architecture", s_tbl_cell), Paragraph("16", s_tbl_cell_center)],
        [Paragraph("Figure 4.1", s_tbl_cell_center), Paragraph("ESP32 DevKit V1 and RC522 RFID Circuit Wiring Schematic", s_tbl_cell), Paragraph("22", s_tbl_cell_center)],
        [Paragraph("Figure 4.2", s_tbl_cell_center), Paragraph("Two-Factor KYC Voter Registration & Credential Binding Workflow", s_tbl_cell), Paragraph("25", s_tbl_cell_center)],
        [Paragraph("Figure 4.3", s_tbl_cell_center), Paragraph("Normalized Relational Database Entity-Relationship Diagram (ERD)", s_tbl_cell), Paragraph("26", s_tbl_cell_center)],
        [Paragraph("Figure 4.4", s_tbl_cell_center), Paragraph("End-to-End Voter Verification UML Sequence Diagram", s_tbl_cell), Paragraph("27", s_tbl_cell_center)],
        [Paragraph("Figure 4.5", s_tbl_cell_center), Paragraph("Vote-Guard Security Portal (Role-Based Authentication Terminal)", s_tbl_cell), Paragraph("28", s_tbl_cell_center)],
        [Paragraph("Figure 4.6", s_tbl_cell_center), Paragraph("Polling Booth Operator Terminal (Live Hardware Scan Sync)", s_tbl_cell), Paragraph("28", s_tbl_cell_center)],
        [Paragraph("Figure 4.7", s_tbl_cell_center), Paragraph("Admin Security Dashboard (KYC Credential Registry & Metrics)", s_tbl_cell), Paragraph("29", s_tbl_cell_center)],
        [Paragraph("Figure 4.8", s_tbl_cell_center), Paragraph("Voter Registration & 2FA Credential Binding Interface", s_tbl_cell), Paragraph("29", s_tbl_cell_center)],
        [Paragraph("Figure 5.1", s_tbl_cell_center), Paragraph("Empirical Verification Latency Decomposition & Comparison Chart", s_tbl_cell), Paragraph("34", s_tbl_cell_center)],
        [Paragraph("Figure 8.1", s_tbl_cell_center), Paragraph("Vote-Guard PBL-I Project Execution Lifecycle Gantt Chart", s_tbl_cell), Paragraph("40", s_tbl_cell_center)]
    ]"""

if old_lof_block in pdf_text:
    pdf_text = pdf_text.replace(old_lof_block, new_lof_block)
    print("[PDF] 4. Updated List of Figures page references.")
else:
    print("[PDF] 4. LOF already updated.")

old_lot_block = """    lot_data = [
        [Paragraph("Table No.", s_tbl_hdr), Paragraph("Table Title / Description", s_tbl_hdr), Paragraph("Page No.", s_tbl_hdr)],
        [Paragraph("Table 2.1", s_tbl_cell_center), Paragraph("Electoral Stakeholder Requirements and Technical Impact Matrix", s_tbl_cell), Paragraph("17", s_tbl_cell_center)],
        [Paragraph("Table 2.2", s_tbl_cell_center), Paragraph("Systematic Benchmark of Published Electronic & RFID Voting Systems", s_tbl_cell), Paragraph("20", s_tbl_cell_center)],
        [Paragraph("Table 3.1", s_tbl_cell_center), Paragraph("Hardware Bill of Materials (BOM) & Electrical Specifications", s_tbl_cell), Paragraph("24", s_tbl_cell_center)],
        [Paragraph("Table 3.2", s_tbl_cell_center), Paragraph("Complete Software Stack & Deployment Architecture", s_tbl_cell), Paragraph("25", s_tbl_cell_center)],
        [Paragraph("Table 4.1", s_tbl_cell_center), Paragraph("ESP32 DevKit V1 Hardware Pinout & Actuator Mapping Specifications", s_tbl_cell), Paragraph("29", s_tbl_cell_center)],
        [Paragraph("Table 4.2", s_tbl_cell_center), Paragraph("Relational Database Schema & Field Constraint Specifications", s_tbl_cell), Paragraph("32", s_tbl_cell_center)],
        [Paragraph("Table 5.1", s_tbl_cell_center), Paragraph("Comprehensive Empirical Verification & Stress Test Matrix", s_tbl_cell), Paragraph("39", s_tbl_cell_center)],
        [Paragraph("Table 5.2", s_tbl_cell_center), Paragraph("Empirical Verification Latency Component Breakdown", s_tbl_cell), Paragraph("40", s_tbl_cell_center)],
        [Paragraph("Table 5.3", s_tbl_cell_center), Paragraph("Comparative System Benchmark Against Published Paradigms", s_tbl_cell), Paragraph("41", s_tbl_cell_center)],
        [Paragraph("Table 6.1", s_tbl_cell_center), Paragraph("Team Member Roles & Technical Responsibility Matrix", s_tbl_cell), Paragraph("42", s_tbl_cell_center)],
        [Paragraph("Table 8.1", s_tbl_cell_center), Paragraph("Project Milestone Schedule & Phase Deliverables", s_tbl_cell), Paragraph("46", s_tbl_cell_center)],
        [Paragraph("Table 8.2", s_tbl_cell_center), Paragraph("Comprehensive Project Risk Assessment and Mitigation Matrix", s_tbl_cell), Paragraph("47", s_tbl_cell_center)],
        [Paragraph("Table 9.1", s_tbl_cell_center), Paragraph("Conformance Matrix of Experimental Results Against Project Objectives", s_tbl_cell), Paragraph("48", s_tbl_cell_center)]
    ]"""

new_lot_block = """    lot_data = [
        [Paragraph("Table No.", s_tbl_hdr), Paragraph("Table Title / Description", s_tbl_hdr), Paragraph("Page No.", s_tbl_hdr)],
        [Paragraph("Table 2.1", s_tbl_cell_center), Paragraph("Electoral Stakeholder Requirements and Technical Impact Matrix", s_tbl_cell), Paragraph("11", s_tbl_cell_center)],
        [Paragraph("Table 2.2", s_tbl_cell_center), Paragraph("Systematic Benchmark of Published Electronic & RFID Voting Systems", s_tbl_cell), Paragraph("14", s_tbl_cell_center)],
        [Paragraph("Table 3.1", s_tbl_cell_center), Paragraph("Hardware Bill of Materials (BOM) & Electrical Specifications", s_tbl_cell), Paragraph("18", s_tbl_cell_center)],
        [Paragraph("Table 3.2", s_tbl_cell_center), Paragraph("Complete Software Stack & Deployment Architecture", s_tbl_cell), Paragraph("19", s_tbl_cell_center)],
        [Paragraph("Table 4.1", s_tbl_cell_center), Paragraph("ESP32 DevKit V1 Hardware Pinout & Actuator Mapping Specifications", s_tbl_cell), Paragraph("23", s_tbl_cell_center)],
        [Paragraph("Table 4.2", s_tbl_cell_center), Paragraph("Relational Database Schema & Field Constraint Specifications", s_tbl_cell), Paragraph("26", s_tbl_cell_center)],
        [Paragraph("Table 5.1", s_tbl_cell_center), Paragraph("Comprehensive Empirical Verification & Stress Test Matrix", s_tbl_cell), Paragraph("33", s_tbl_cell_center)],
        [Paragraph("Table 5.2", s_tbl_cell_center), Paragraph("Empirical Verification Latency Component Breakdown", s_tbl_cell), Paragraph("34", s_tbl_cell_center)],
        [Paragraph("Table 5.3", s_tbl_cell_center), Paragraph("Comparative System Benchmark Against Published Paradigms", s_tbl_cell), Paragraph("35", s_tbl_cell_center)],
        [Paragraph("Table 6.1", s_tbl_cell_center), Paragraph("Team Member Roles & Technical Responsibility Matrix", s_tbl_cell), Paragraph("36", s_tbl_cell_center)],
        [Paragraph("Table 8.1", s_tbl_cell_center), Paragraph("Project Milestone Schedule & Phase Deliverables", s_tbl_cell), Paragraph("40", s_tbl_cell_center)],
        [Paragraph("Table 8.2", s_tbl_cell_center), Paragraph("Comprehensive Project Risk Assessment and Mitigation Matrix", s_tbl_cell), Paragraph("41", s_tbl_cell_center)],
        [Paragraph("Table 9.1", s_tbl_cell_center), Paragraph("Conformance Matrix of Experimental Results Against Project Objectives", s_tbl_cell), Paragraph("42", s_tbl_cell_center)]
    ]"""

if old_lot_block in pdf_text:
    pdf_text = pdf_text.replace(old_lot_block, new_lot_block)
    print("[PDF] 5. Updated List of Tables page references.")
else:
    print("[PDF] 5. LOT already updated.")
print("[PDF] 4. Updated List of Figures and List of Tables page references to match visible Arabic pages.")

with open(pdf_gen_path, 'w', encoding='utf-8') as f:
    f.write(pdf_text)
print("Successfully saved updated build_50page_report.py\n")


# ==============================================================================
# 2. UPDATE build_final_docx.py
# ==============================================================================
docx_gen_path = 'Final_Project_Report/build_final_docx.py'
with open(docx_gen_path, 'r', encoding='utf-8') as f:
    docx_text = f.read()

# 2.1 Certificate HOD block in build_final_docx.py:
# Strictly:
# ____________________________
# Head of Department
# Department of CSE
# College of Technology
old_docx_hod = """    c0 = t_sig.cell(0, 0)
    c0.width = Inches(3.0)
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r0 = p0.add_run('____________________________\\nHead of Department\\nDepartment of Computer Science and Engineering')
    r0.font.name = 'Times New Roman'
    r0.font.size = Pt(11)
    r0.font.bold = True"""

new_docx_hod = """    c0 = t_sig.cell(0, 0)
    c0.width = Inches(3.0)
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r0 = p0.add_run('____________________________\\nHead of Department\\nDepartment of CSE\\nCollege of Technology')
    r0.font.name = 'Times New Roman'
    r0.font.size = Pt(11)
    r0.font.bold = True"""

if old_docx_hod in docx_text:
    docx_text = docx_text.replace(old_docx_hod, new_docx_hod)
    print("[DOCX] 1. Updated Certificate HOD block: signature line preserved, no placeholder, exact 3 lines.")
else:
    print("[DOCX] 1. DOCX HOD block already updated.")

# 2.2 Update toc_items in build_final_docx.py to match exact final pagination
old_docx_toc_items = """    toc_items = [
        ('1.', 'Cover Page', '1'),
        ('2.', 'Certificate', '2'),
        ('3.', 'Declaration', '3'),
        ('4.', 'Acknowledgement', '4'),
        ('5.', 'Abstract', '5'),
        ('6.', 'Keywords', '5'),
        ('7.', 'List of Figures', '6'),
        ('8.', 'List of Tables', '7'),
        ('9.', 'List of Abbreviations', '8'),
        ('10.', 'Table of Contents', '9'),
        ('', 'CHAPTER 1 - INTRODUCTION', '11'),
        ('1.1', 'Background of the PBL', '11'),
        ('1.2', 'Problem Identification', '11'),
        ('1.3', 'Problem Statement', '12'),
        ('1.4', 'Motivation', '12'),
        ('1.5', 'Objectives', '13'),
        ('1.6', 'Scope of the PBL', '13'),
        ('', 'CHAPTER 2 - PROBLEM STUDY & LITERATURE REVIEW', '14'),
        ('2.1', 'Existing System / Current Practice', '14'),
        ('2.2', 'Problems in Existing System', '14'),
        ('2.3', 'Root Cause Analysis (Ishikawa Diagram)', '15'),
        ('2.4', 'Stakeholder Analysis', '16'),
        ('2.5', 'Literature Review (15 Academic Studies)', '17'),
        ('2.6', 'Existing Solutions / Benchmark Study', '18'),
        ('2.7', 'Identified Gap', '18'),
        ('', 'CHAPTER 3 - PROPOSED SOLUTION', '19'),
        ('3.1', 'Proposed Solution', '19'),
        ('3.2', 'Conceptual Framework (Zero-Trust Edge)', '20'),
        ('3.3', 'Block Diagram / System Architecture', '20'),
        ('3.4', 'Working Principle', '21'),
        ('3.5', 'Major Components', '22'),
        ('3.6', 'Hardware Requirements (BOM)', '22'),
        ('3.7', 'Software Requirements Stack', '23'),
        ('3.8', 'Technical Specifications', '23'),
        ('3.9', 'Design Calculations (Power & Field Range)', '23'),
        ('', 'CHAPTER 4 - IMPLEMENTATION / DEVELOPMENT', '24'),
        ('4.1', 'Methodology', '24'),
        ('4.2', 'Project Development Steps', '24'),
        ('4.3', 'Diagram / Schematic', '25'),
        ('4.4', 'Hardware Implementation', '25'),
        ('4.5', 'Software / Control Logic (FastAPI & MySQL)', '27'),
        ('4.6', 'Simulation Model & UML Sequence', '29'),
        ('4.7', 'Prototype Development & Frontend Portals', '30'),
        ('4.8', 'Safety Considerations & Fail-Secure Design', '32'),
        ('', 'CHAPTER 5 - TESTING & RESULTS', '33'),
        ('5.1', 'Testing Methodology', '33'),
        ('5.2', 'Test Conditions', '33'),
        ('5.3', 'Experimental Results', '34'),
        ('5.4', 'Observation Table', '34'),
        ('5.5', 'Performance Parameters & Latency Breakdown', '35'),
        ('5.6', 'Graphs / Charts', '36'),
        ('5.7', 'Result Analysis', '36'),
        ('5.8', 'Comparison with Existing Systems', '37'),
        ('5.9', 'Validation of Proposed Solution', '38'),
        ('', 'CHAPTER 6 - PBL LEARNING & TEAM CONTRIBUTION', '39'),
        ('6.1', 'Team Members and Roles', '39'),
        ('6.2', 'Individual Contribution (Placeholders)', '40'),
        ('6.3', 'PBL Learning Outcomes', '40'),
        ('6.4', 'Skills Developed', '41'),
        ('6.5', 'Mentor Review / Feedback', '41'),
        ('6.6', 'Student Reflection', '41'),
        ('', 'CHAPTER 7 - IMPACT & FUTURE SCOPE', '42'),
        ('7.1', 'Innovation / Novelty', '42'),
        ('7.2', 'Social Impact', '42'),
        ('7.3', 'Environmental Impact', '43'),
        ('7.4', 'Economic Impact', '43'),
        ('7.5', 'Sustainability', '43'),
        ('7.6', 'SDG 16 & Viksit Bharat Relevance', '44'),
        ('7.7', 'Limitations', '44'),
        ('7.8', 'Future Scope', '44'),
        ('', 'CHAPTER 8 - PROJECT MANAGEMENT', '45'),
        ('8.1', 'Project Timeline', '45'),
        ('8.2', 'Gantt Chart', '45'),
        ('8.3', 'Milestones Achieved', '46'),
        ('8.4', 'Review Meetings', '46'),
        ('8.5', 'Risk Identification and Mitigation', '46'),
        ('', 'CHAPTER 9 - CONCLUSION', '47'),
        ('9.1', 'Conclusion', '47'),
        ('9.2', 'Achievement of Objectives', '47'),
        ('9.3', 'Final Outcome', '47'),
        ('', 'REFERENCES', '48'),
        ('', 'ANNEXURES (Annexures A to D)', '49')
    ]"""

new_docx_toc_items = """    toc_items = [
        ('1.', 'Cover Page / Title Page', ''),
        ('2.', 'Certificate', 'i'),
        ('3.', 'Declaration', 'ii'),
        ('4.', 'Acknowledgement', 'iii'),
        ('5.', 'Abstract', 'iv'),
        ('6.', 'Keywords & Research Scope Summary', 'v'),
        ('7.', 'List of Figures', '1'),
        ('8.', 'List of Tables', '2'),
        ('9.', 'List of Abbreviations', '3'),
        ('10.', 'Table of Contents', '4'),
        ('', 'CHAPTER 1 - INTRODUCTION', '6'),
        ('1.1', 'Background of the PBL', '6'),
        ('1.2', 'Problem Identification', '6'),
        ('1.3', 'Problem Statement & Invariant Formulation', '7'),
        ('1.4', 'Motivation', '7'),
        ('1.5', 'Objectives of the Project', '8'),
        ('1.6', 'Scope of the PBL', '8'),
        ('', 'CHAPTER 2 - PROBLEM STUDY & LITERATURE REVIEW', '9'),
        ('2.1', 'Existing System / Current Practice', '9'),
        ('2.2', 'Problems in Existing System', '9'),
        ('2.3', 'Root Cause Analysis (Ishikawa Fishbone Model)', '10'),
        ('2.4', 'Stakeholder Analysis & Requirements Matrix', '11'),
        ('2.5', 'Literature Review (Critical Survey of Prior Work)', '12'),
        ('2.6', 'Existing Solutions / Benchmark Study', '14'),
        ('2.7', 'Identified Gap in Engineering Literature', '14'),
        ('', 'CHAPTER 3 - PROPOSED SOLUTION', '15'),
        ('3.1', 'Proposed Solution & Zero-Trust Paradigm', '15'),
        ('3.2', 'Conceptual Architectural Framework', '15'),
        ('3.3', 'Block Diagram / System Architecture', '16'),
        ('3.4', 'Working Principle & Step-by-Step State Flow', '17'),
        ('3.5', 'Major Components & Subsystem Allocation', '18'),
        ('3.6', 'Hardware Requirements & Bill of Materials (BOM)', '18'),
        ('3.7', 'Software Requirements & Framework Stack', '19'),
        ('3.8', 'Technical Specifications', '20'),
        ('3.9', 'Design Calculations (Power Budget & Antenna Link)', '20'),
        ('', 'CHAPTER 4 - IMPLEMENTATION / DEVELOPMENT', '21'),
        ('4.1', 'Methodology & Engineering Lifecycle', '21'),
        ('4.2', 'Project Development Steps', '21'),
        ('4.3', 'Diagram / Schematic & Interfacing Circuitry', '22'),
        ('4.5', 'Hardware Implementation & Pinout Mapping', '23'),
        ('4.6', 'Software / Programming / Control Logic', '24'),
        ('4.7', '2FA KYC Voter Registration Workflow', '25'),
        ('4.8', 'Database Schema Design & Normalization', '26'),
        ('4.9', 'System Interaction Flow (UML Sequence)', '27'),
        ('4.10', 'Prototype Development & Frontend Web Portals', '28'),
        ('4.11', 'Safety, Tamper Resistance & Operational Security', '30'),
        ('', 'CHAPTER 5 - TESTING & RESULTS', '31'),
        ('5.1', 'Testing Methodology & Experimental Setup', '31'),
        ('5.2', 'Test Conditions & Hardware Testbed', '31'),
        ('5.3', 'Experimental Results & Test Execution Cases', '32'),
        ('5.4', 'Comprehensive Observation Table', '33'),
        ('5.5', 'Performance Parameters & Latency Metrics', '34'),
        ('5.6', 'Graphs / Charts & Latency Breakdown', '34'),
        ('5.7', 'Result Analysis & Statistical Validation', '35'),
        ('5.8', 'Comparison with Existing Voting Systems', '35'),
        ('5.9', 'Validation of Proposed Solution Against Objectives', '35'),
        ('', 'CHAPTER 6 - PBL LEARNING & TEAM CONTRIBUTION', '36'),
        ('6.1', 'Team Members and Roles', '36'),
        ('6.2', 'Individual Contribution (Placeholders)', '36'),
        ('6.3', 'PBL Learning Outcomes', '37'),
        ('6.4', 'Skills Developed', '37'),
        ('6.5', 'Mentor Review / Formative Feedback', '37'),
        ('6.6', 'Student Reflection & Engineering Insights', '37'),
        ('', 'CHAPTER 7 - IMPACT & FUTURE SCOPE', '38'),
        ('7.1', 'Innovation / Novelty', '38'),
        ('7.2', 'Social Impact, Environmental, Economic', '38'),
        ('7.5', 'Sustainability & Operational Viability', '39'),
        ('7.6', 'UN SDG 16 & Viksit Bharat 2047 Relevance', '39'),
        ('7.7', 'Engineering Limitations', '39'),
        ('7.8', 'Future Scope & Technology Roadmap', '39'),
        ('', 'CHAPTER 8 - PROJECT MANAGEMENT', '40'),
        ('8.1', 'Project Timeline & Execution Phases', '40'),
        ('8.2', 'Gantt Chart (16-Week Implementation Schedule)', '40'),
        ('8.3', 'Milestones Achieved & Deliverables', '40'),
        ('8.4', 'Review Meetings & Advisory Log', '41'),
        ('8.5', 'Risk Identification and Mitigation Matrix', '41'),
        ('', 'CHAPTER 9 - CONCLUSION', '42'),
        ('9.1', 'Conclusion', '42'),
        ('9.2', 'Achievement of Objectives Conformance', '42'),
        ('9.3', 'Final Outcome & Practical Significance', '42'),
        ('', 'REFERENCES', '43'),
        ('', 'ANNEXURES (Annexures A to D)', '44')
    ]"""

if old_docx_toc_items in docx_text:
    docx_text = docx_text.replace(old_docx_toc_items, new_docx_toc_items)
    print("[DOCX] 2. Updated Table of Contents items.")
else:
    print("[DOCX] 2. DOCX TOC items already updated.")

# 2.3 Also update figures_list in build_final_docx.py
old_docx_lof = """    figures_list = [
        ('Figure 2.1', 'Ishikawa Fishbone Diagram for Root Cause Analysis of Electoral Fraud', '16'),
        ('Figure 3.1', 'Three-Tier Edge-to-Cloud System Architecture of Vote-Guard Platform', '21'),
        ('Figure 4.1', 'Hardware Schematic and Pinout Diagram (ESP32, RC522, LEDs, Buzzer)', '26'),
        ('Figure 4.2', 'Two-Factor KYC Voter Registration & Demographic Collision Flowchart', '28'),
        ('Figure 4.3', 'Entity-Relationship Diagram (ERD) of MySQL 8.0 Relational Database Schema', '29'),
        ('Figure 4.4', 'UML Sequence Diagram of Edge-to-Cloud Verification & Actuation Pipeline', '30'),
        ('Figure 4.5', 'Vote-Guard Role-Based Security Portal (Authentication & Role Selection)', '31'),
        ('Figure 4.6', 'Polling Booth Operator Terminal Dashboard (Live Event Synchronization)', '31'),
        ('Figure 4.7', 'Admin Security Dashboard (KYC Credential Registry & Audit Metrics)', '32'),
        ('Figure 4.8', 'Voter 2FA Credential Registration Interface & Physical Tag Capture', '32'),
        ('Figure 5.1', 'Empirical Verification Latency Decomposition Chart (Mean = 140.0 ms)', '36'),
        ('Figure 8.1', 'PBL-I Project Implementation Timeline & Milestone Gantt Chart', '45')
    ]"""

new_docx_lof = """    figures_list = [
        ('Figure 2.1', 'Ishikawa Fishbone Diagram for Root Cause Analysis of Electoral Fraud', '10'),
        ('Figure 3.1', 'Three-Tier Edge-to-Cloud System Architecture of Vote-Guard Platform', '16'),
        ('Figure 4.1', 'Hardware Schematic and Pinout Diagram (ESP32, RC522, LEDs, Buzzer)', '22'),
        ('Figure 4.2', 'Two-Factor KYC Voter Registration & Demographic Collision Flowchart', '25'),
        ('Figure 4.3', 'Entity-Relationship Diagram (ERD) of MySQL 8.0 Relational Database Schema', '26'),
        ('Figure 4.4', 'UML Sequence Diagram of Edge-to-Cloud Verification & Actuation Pipeline', '27'),
        ('Figure 4.5', 'Vote-Guard Role-Based Security Portal (Authentication & Role Selection)', '28'),
        ('Figure 4.6', 'Polling Booth Operator Terminal Dashboard (Live Event Synchronization)', '28'),
        ('Figure 4.7', 'Admin Security Dashboard (KYC Credential Registry & Audit Metrics)', '29'),
        ('Figure 4.8', 'Voter 2FA Credential Registration Interface & Physical Tag Capture', '29'),
        ('Figure 5.1', 'Empirical Verification Latency Decomposition Chart (Mean = 140.0 ms)', '34'),
        ('Figure 8.1', 'PBL-I Project Implementation Timeline & Milestone Gantt Chart', '40')
    ]"""

if old_docx_lof in docx_text:
    docx_text = docx_text.replace(old_docx_lof, new_docx_lof)
    print("[DOCX] 3. Updated List of Figures items.")
else:
    print("[DOCX] 3. DOCX LOF already updated.")

# 2.4 Also update tables_list in build_final_docx.py
old_docx_lot = """    tables_list = [
        ('Table 2.1', 'Stakeholder Requirement & Impact Matrix in Electoral Processes', '17'),
        ('Table 2.2', 'Comparative Engineering Analysis of Literature & Existing Approaches', '18'),
        ('Table 3.1', 'Comprehensive Hardware Bill of Materials (BOM) & Specifications', '22'),
        ('Table 3.2', 'Software Platform, Framework, and Database Environment Stack', '23'),
        ('Table 4.1', 'Complete ESP32 Pinout Mapping for RC522 Reader and Diagnostic Actuators', '25'),
        ('Table 4.2', 'MySQL 8.0 Relational Database Schema Structure and Constraints', '29'),
        ('Table 5.1', 'Empirical Hardware and Software Functional Verification Test Suite', '34'),
        ('Table 5.2', 'Comparative Performance Benchmarking Against Published Voting Systems', '37'),
        ('Table 6.1', 'PBL Team Member Role Allocation & Project Responsibility Matrix', '39'),
        ('Table 7.1', 'Multi-Dimensional Socio-Technical & Environmental Impact Analysis', '43'),
        ('Table 8.1', 'Technical, Hardware, and Operational Risk Assessment & Mitigation Plan', '46'),
        ('Table 9.1', 'Project Research Objectives vs. Demonstrated Empirical Achievements', '47')
    ]"""

new_docx_lot = """    tables_list = [
        ('Table 2.1', 'Stakeholder Requirement & Impact Matrix in Electoral Processes', '11'),
        ('Table 2.2', 'Comparative Engineering Analysis of Literature & Existing Approaches', '14'),
        ('Table 3.1', 'Comprehensive Hardware Bill of Materials (BOM) & Specifications', '18'),
        ('Table 3.2', 'Software Platform, Framework, and Database Environment Stack', '19'),
        ('Table 4.1', 'Complete ESP32 Pinout Mapping for RC522 Reader and Diagnostic Actuators', '23'),
        ('Table 4.2', 'MySQL 8.0 Relational Database Schema Structure and Constraints', '26'),
        ('Table 5.1', 'Empirical Hardware and Software Functional Verification Test Suite', '33'),
        ('Table 5.2', 'Comparative Performance Benchmarking Against Published Voting Systems', '35'),
        ('Table 6.1', 'PBL Team Member Role Allocation & Project Responsibility Matrix', '36'),
        ('Table 7.1', 'Multi-Dimensional Socio-Technical & Environmental Impact Analysis', '38'),
        ('Table 8.1', 'Technical, Hardware, and Operational Risk Assessment & Mitigation Plan', '41'),
        ('Table 9.1', 'Project Research Objectives vs. Demonstrated Empirical Achievements', '42')
    ]"""

if old_docx_lot in docx_text:
    docx_text = docx_text.replace(old_docx_lot, new_docx_lot)
    print("[DOCX] 4. Updated List of Tables items.")
else:
    print("[DOCX] 4. DOCX LOT already updated.")
print("[DOCX] 2. Updated Table of Contents, List of Figures, and List of Tables page references.")

with open(docx_gen_path, 'w', encoding='utf-8') as f:
    f.write(docx_text)
print("Successfully saved updated build_final_docx.py\n")

print("==================================================================")
print("  TOC & HOD CORRECTIONS SUCCESSFULLY APPLIED TO BOTH GENERATORS!")
print("==================================================================")
