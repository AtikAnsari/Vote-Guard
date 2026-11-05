import pypdf
import docx

print("==================================================")
print("  VOTE-GUARD REPORT FINAL VALIDATION TEST SUITE")
print("==================================================")

# --- 1. PDF VALIDATION ---
pdf_reader = pypdf.PdfReader('Final_Project_Report/VoteGuard_Final_Project_Report.pdf')
num_pages = len(pdf_reader.pages)
print(f"[PDF] Total Page Count: {num_pages} (Target: Strictly 50)")
assert num_pages == 50, f"Error: Page count is {num_pages}, expected exactly 50!"

p1_text = pdf_reader.pages[0].extract_text()
print("\n--- [PDF] Page 1 (Title Page) Text Sample ---")
print(p1_text[:350])

assert "Ansari Mo.Atik" in p1_text
assert "Shaikh Sakib Ahmed" in p1_text
assert "Shaikh Sejan" in p1_text
assert "Prof. Urmil Mewada" in p1_text
assert "Department of Computer Engineering" in p1_text
assert "Department of Computer Science and Engineering" in p1_text
assert len([c for c in p1_text if ord(c) > 127]) == 0, "Found non-ASCII character in Page 1!"

# Check preliminary pages 2, 3, 4 (Certificate, Declaration, Acknowledgement)
p2_text = pdf_reader.pages[1].extract_text()
p3_text = pdf_reader.pages[2].extract_text()
p4_text = pdf_reader.pages[3].extract_text()

for p_num, text, name in [(2, p2_text, "Certificate"), (3, p3_text, "Declaration"), (4, p4_text, "Acknowledgement")]:
    assert "SILVER OAK COLLEGE OF TECHNOLOGY\nDEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING" not in text, \
        f"Error: Found redundant institutional header in Page {p_num} ({name})!"
    print(f"[PDF] Page {p_num} ({name}) redundant header check: PASSED (Clean layout)")

# Check Bottom-Right Page Number in PDF
for i in [0, 1, 9, 25, 49]:
    txt = pdf_reader.pages[i].extract_text()
    expected_pnum = f"- {i+1} -"
    assert expected_pnum in txt, f"Error: Page number {expected_pnum} missing on page {i+1}!"
print("[PDF] Page Numbering presence check: PASSED (All sample pages have '- X -')")

# --- 2. DOCX VALIDATION ---
doc = docx.Document('Final_Project_Report/VoteGuard_Final_Project_Report.docx')
sec = doc.sections[0]

page_w = round(sec.page_width.inches, 2)
page_h = round(sec.page_height.inches, 2)
print(f"\n[DOCX] Page Size: {page_w}\" x {page_h}\" (A4: 8.27\" x 11.69\")")
assert page_w == 8.27 and page_h == 11.69, "DOCX Page size not A4!"

lm = round(sec.left_margin.inches, 2)
rm = round(sec.right_margin.inches, 2)
tm = round(sec.top_margin.inches, 2)
bm = round(sec.bottom_margin.inches, 2)
print(f"[DOCX] Margins: Left={lm}\", Right={rm}\", Top={tm}\", Bottom={bm}\"")
assert lm == 1.25 and rm == 1.0 and tm == 1.0 and bm == 1.0, "DOCX Margins mismatch!"

# Check Footer in DOCX
ftr = sec.footer
p_ftr = ftr.paragraphs[0]
ftr_full_txt = p_ftr.text
print(f"[DOCX] Native Footer text: '{ftr_full_txt}'")
assert "Silver Oak University | Department of Computer Science and Engineering | PBL-I" in ftr_full_txt
assert "-" in ftr_full_txt
assert len(p_ftr.paragraph_format.tab_stops) > 0, "Right-aligned tab stop missing in footer!"

# Check Guide department in DOCX
all_docx_text = "\n".join([p.text for p in doc.paragraphs])
for tbl in doc.tables:
    for row in tbl.rows:
        all_docx_text += "\n" + "\t".join([c.text for c in row.cells])

print(f"\n[DOCX] Total characters: {len(all_docx_text)}")
assert "Department of Computer Engineering" in all_docx_text
assert "Prof. Urmil Mewada" in all_docx_text
assert "Assistant Professor, Department of Computer Engineering" in all_docx_text

# Check that the three students are all present
assert "Ansari Mo.Atik" in all_docx_text
assert "Shaikh Sakib Ahmed" in all_docx_text
assert "Shaikh Sejan" in all_docx_text
assert "2502031830031" in all_docx_text
assert "2502031830033" in all_docx_text
assert "2502031830053" in all_docx_text

print("\n==================================================")
print("  ALL VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
print("==================================================")
