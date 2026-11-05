import pypdf
import docx
import zipfile
import xml.etree.ElementTree as ET

print("==================================================================")
print("  VOTE-GUARD REPORT FINAL FACULTY VALIDATIONS & VERIFICATION")
print("==================================================================")

# ==============================================================================
# 1. PDF VALIDATIONS
# ==============================================================================
pdf_reader = pypdf.PdfReader('Final_Project_Report/VoteGuard_Final_Project_Report.pdf')
total_pages = len(pdf_reader.pages)
print(f"[PDF] Total Page Count: {total_pages} (Target: Exactly 50)")
assert total_pages == 50, f"Error: Page count is {total_pages}, expected exactly 50!"

# 1.1 Page 1 (Title Page): NO header banner, NO footer, NO page number, retains centered logo
p1_text = pdf_reader.pages[0].extract_text()
assert "- 1 -" not in p1_text, "Error: Found page number on Page 1!"
assert "- i -" not in p1_text, "Error: Found roman numeral on Page 1!"
assert "Silver Oak University | Department of Computer Science and Engineering | PBL-I" not in p1_text, "Error: Found footer on Page 1!"
assert "College of Technology" in p1_text, "Error: 'College of Technology' not found on Page 1!"
assert "Silver Oak College of Technology" not in p1_text, "Error: Found 'Silver Oak College of Technology' on Page 1!"
print("[PDF] Requirement 1 (Page 1 Header, Footer, Page Number, Institution): PASSED")

# 1.2 Section 2 (Pages 2 to 6): Roman numerals i, ii, iii, iv, v
roman_expected = {
    1: "- i -",    # Page 2: Certificate
    2: "- ii -",   # Page 3: Declaration
    3: "- iii -",  # Page 4: Acknowledgement
    4: "- iv -",   # Page 5: Abstract
    5: "- v -"     # Page 6: Keywords & Research Scope Summary
}
for p_idx, exp_num in roman_expected.items():
    txt = pdf_reader.pages[p_idx].extract_text()
    assert exp_num in txt, f"Error: Expected {exp_num} on Page {p_idx+1}, not found!"
    print(f"[PDF] Page {p_idx+1} Roman Numbering: {exp_num} -> PASSED")

# 1.3 Section 3 (Pages 7 to 50): Arabic numbering 1, 2, 3... starting with 1 on List of Figures
# Page 7: List of Figures -> "- 1 -"
p7_text = pdf_reader.pages[6].extract_text()
assert "- 1 -" in p7_text, f"Error: Expected '- 1 -' on Page 7 (List of Figures), got: {p7_text[-100:]}"
assert "LIST OF FIGURES" in p7_text, "Error: Page 7 is not LIST OF FIGURES!"
print("[PDF] Page 7 (List of Figures) Arabic Numbering: '- 1 -' -> PASSED")

# Check sample pages in Section 3
arabic_samples = {
    6: "- 1 -",    # Page 7 (List of Figures)
    7: "- 2 -",    # Page 8 (List of Tables)
    8: "- 3 -",    # Page 9 (List of Abbreviations)
    9: "- 4 -",    # Page 10 (Table of Contents p. 1)
    10: "- 5 -",   # Page 11 (Table of Contents p. 2)
    11: "- 6 -",   # Page 12 (Chapter 1 Introduction)
    20: "- 15 -",  # Page 21 (Chapter 3 Proposed Solution)
    49: "- 44 -"   # Page 50 (Annexures)
}
for p_idx, exp_num in arabic_samples.items():
    txt = pdf_reader.pages[p_idx].extract_text()
    assert exp_num in txt, f"Error: Expected {exp_num} on Page {p_idx+1}, not found!"
print("[PDF] Section 3 Arabic Numbering continuity check (all sample pages verified): PASSED")

# 1.4 Certificate Page (Page 2)
p2_text = pdf_reader.pages[1].extract_text()
assert "DATE: ____________________" in p2_text, "Error: Certificate DATE line mismatch!"
assert "PLACE: ____________________" in p2_text, "Error: Certificate PLACE line mismatch!"
assert "Silver Oak College of Technology" not in p2_text, "Error: Found 'Silver Oak College of Technology' on Certificate Page!"
assert "College of Technology" in p2_text, "Error: 'College of Technology' missing on Certificate Page!"
print("[PDF] Certificate Page DATE / PLACE format & 'College of Technology': PASSED")

# 1.5 Declaration Page (Page 3)
p3_text = pdf_reader.pages[2].extract_text()
assert "PLACE: AHMEDABAD" not in p3_text.upper(), "Error: Found PLACE: AHMEDABAD on Declaration Page!"
assert "DATE: [DD/MM" not in p3_text, "Error: Found DATE: [DD/MM/YY] on Declaration Page!"
assert "College of Technology" in p3_text, "Error: 'College of Technology' missing on Declaration Page!"
assert "Ansari Mo.Atik" in p3_text, "Error: Student name missing on Declaration Page!"
assert "Shaikh Sakib Ahmed" in p3_text, "Error: Student name missing on Declaration Page!"
assert "Shaikh Sejan" in p3_text, "Error: Student name missing on Declaration Page!"
print("[PDF] Declaration Page: Date/Place completely removed & 3 student rows preserved: PASSED")

# 1.6 Table of Contents Heading (Pages 10 and 11)
p10_text = pdf_reader.pages[9].extract_text()
p11_text = pdf_reader.pages[10].extract_text()
assert "TABLE OF CONTENTS (PART 1)" not in p10_text, "Error: Found 'PART 1' on Page 10!"
assert "TABLE OF CONTENTS (PART 2)" not in p11_text, "Error: Found 'PART 2' on Page 11!"
assert "TABLE OF CONTENTS" in p10_text, "Error: 'TABLE OF CONTENTS' missing on Page 10!"
assert "TABLE OF CONTENTS" in p11_text, "Error: 'TABLE OF CONTENTS' missing on Page 11!"
print("[PDF] Table of Contents headings (no PART 1 / PART 2, both titled TABLE OF CONTENTS): PASSED")


# ==============================================================================
# 2. DOCX VALIDATIONS
# ==============================================================================
doc = docx.Document('Final_Project_Report/VoteGuard_Final_Project_Report.docx')
print(f"\n[DOCX] Number of Sections: {len(doc.sections)} (Target: Exactly 3)")
assert len(doc.sections) == 3, f"Error: Expected 3 sections in DOCX, found {len(doc.sections)}!"

# 2.1 Section 1: Title Page (No header, no footer, no page number)
sec1 = doc.sections[0]
sec1_hdr_text = sec1.header.paragraphs[0].text.strip()
sec1_ftr_text = sec1.footer.paragraphs[0].text.strip()
assert sec1_hdr_text == "", f"Error: Section 1 header has text: '{sec1_hdr_text}'"
assert sec1_ftr_text == "", f"Error: Section 1 footer has text: '{sec1_ftr_text}'"
print("[DOCX] Section 1 (Title Page): Empty Header & Footer verified -> PASSED")

# 2.2 Section 2: Certificate to Keywords (lowerRoman, starts at 1)
sec2 = doc.sections[1]
sec2_ftr_text = sec2.footer.paragraphs[0].text
assert "Silver Oak University | Department of Computer Science and Engineering | PBL-I" in sec2_ftr_text
pgNumType2 = sec2._sectPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pgNumType')
assert pgNumType2 is not None, "Error: pgNumType missing on Section 2!"
assert pgNumType2.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fmt') == 'lowerRoman', "Error: Section 2 fmt is not lowerRoman!"
assert pgNumType2.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}start') == '1', "Error: Section 2 start is not 1!"
print("[DOCX] Section 2: Page numbering fmt='lowerRoman', start='1' -> PASSED")

# 2.3 Section 3: List of Figures to Final Page (decimal, starts at 1)
sec3 = doc.sections[2]
sec3_ftr_text = sec3.footer.paragraphs[0].text
assert "Silver Oak University | Department of Computer Science and Engineering | PBL-I" in sec3_ftr_text
pgNumType3 = sec3._sectPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pgNumType')
assert pgNumType3 is not None, "Error: pgNumType missing on Section 3!"
assert pgNumType3.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fmt') == 'decimal', "Error: Section 3 fmt is not decimal!"
assert pgNumType3.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}start') == '1', "Error: Section 3 start is not 1!"
print("[DOCX] Section 3: Page numbering fmt='decimal', start='1' -> PASSED")

# 2.4 Check Certificate & Declaration in DOCX text
all_docx_text = "\n".join([p.text for p in doc.paragraphs])
for tbl in doc.tables:
    for row in tbl.rows:
        all_docx_text += "\n" + "\t".join([c.text for c in row.cells])

assert "DATE: ____________________" in all_docx_text, "Error: Certificate DATE field missing in DOCX!"
assert "PLACE: ____________________" in all_docx_text, "Error: Certificate PLACE field missing in DOCX!"
assert "Place: Ahmedabad" not in all_docx_text, "Error: Found Place: Ahmedabad in Declaration or Certificate in DOCX!"
assert "College of Technology" in all_docx_text, "Error: 'College of Technology' missing in DOCX!"
assert "TABLE OF CONTENTS" in all_docx_text, "Error: 'TABLE OF CONTENTS' missing in DOCX!"
assert "TABLE OF CONTENTS (PART 1)" not in all_docx_text, "Error: Found PART 1 in DOCX!"
assert "TABLE OF CONTENTS (PART 2)" not in all_docx_text, "Error: Found PART 2 in DOCX!"
print("[DOCX] Certificate, Declaration, and TOC text validation -> PASSED")

print("\n==================================================================")
print("  ALL 9 FACULTY REQUIREMENTS VERIFIED WITH 100% SUCCESS!")
print("==================================================================")

