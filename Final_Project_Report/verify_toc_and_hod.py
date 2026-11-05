import pypdf
import docx

print("==================================================================")
print("  VERIFYING PDF DELIVERABLE: VoteGuard_Final_Project_Report.pdf")
print("==================================================================")
pdf_path = "Final_Project_Report/VoteGuard_Final_Project_Report.pdf"
reader = pypdf.PdfReader(pdf_path)
print("1. Total PDF Pages:", len(reader.pages))
assert len(reader.pages) == 50, f"Error: expected 50 pages, found {len(reader.pages)}"

# Page 1 checks
p1 = reader.pages[0].extract_text()
has_p1_footer = ("Page 1" in p1) or ("Page i" in p1)
print("2. Page 1 Footer Check (Must be None):", "PASS" if not has_p1_footer else "FAIL")

# Page 2 Certificate checks
p2 = reader.pages[1].extract_text()
has_placeholder = "[Head of Department]" in p2
has_hod_text = "Head of Department" in p2
has_dept = "Department of CSE" in p2
has_coll = "College of Technology" in p2
print("3. Certificate Page Checks:")
print("   - [Head of Department] placeholder removed:", not has_placeholder)
print("   - 'Head of Department' text preserved:", has_hod_text)
print("   - 'Department of CSE' text preserved:", has_dept)
print("   - 'College of Technology' text preserved:", has_coll)
assert not has_placeholder and has_hod_text and has_dept and has_coll

# Section 2 Footers (Pages 2-6): Roman numerals i, ii, iii, iv, v
print("4. Preliminary Pages Footer Check (Pages 2-6 -> - i - .. - v -):")
expected_roman = ["- i -", "- ii -", "- iii -", "- iv -", "- v -"]
for idx, exp in enumerate(expected_roman, start=1):
    txt = reader.pages[idx].extract_text()
    matches = [line.strip() for line in txt.splitlines() if exp in line]
    print(f"   - Physical Page {idx+1}: {matches}")
    assert any(exp in line for line in txt.splitlines()), f"Missing {exp} on page {idx+1}"

# Section 3 Footers (Pages 7-50): Arabic numerals 1..44
print("5. Main Report Pages Footer Check (Pages 7-50 -> - 1 - .. - 44 -):")
sample_pages = [(6, "- 1 -"), (7, "- 2 -"), (8, "- 3 -"), (9, "- 4 -"), (11, "- 6 -"), (49, "- 44 -")]
for p_idx, exp in sample_pages:
    txt = reader.pages[p_idx].extract_text()
    matches = [line.strip() for line in txt.splitlines() if exp in line]
    print(f"   - Physical Page {p_idx+1}: {matches}")
    assert any(exp in line for line in txt.splitlines()), f"Missing {exp} on page {p_idx+1}"

# Check Table of Contents on pages 10 and 11
p10 = reader.pages[9].extract_text()
p11 = reader.pages[10].extract_text()
print("6. Table of Contents Heading Check:")
print("   - Page 10 has 'PART 1':", "PART 1" in p10)
print("   - Page 11 has 'PART 2':", "PART 2" in p11)
assert "PART 1" not in p10 and "PART 2" not in p11

print("\n==================================================================")
print("  VERIFYING DOCX DELIVERABLE: VoteGuard_Final_Project_Report.docx")
print("==================================================================")
docx_path = "Final_Project_Report/VoteGuard_Final_Project_Report.docx"
doc = docx.Document(docx_path)
print("1. Total Document Sections:", len(doc.sections))

# Check Certificate HOD block in DOCX
cert_found = False
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            if "Head of Department" in cell.text:
                cert_found = True
                print("2. DOCX Certificate HOD Cell Text:")
                print("   " + "\n   ".join(cell.text.splitlines()))
                assert "[Head of Department]" not in cell.text
                assert "Head of Department" in cell.text
                assert "Department of CSE" in cell.text
                assert "College of Technology" in cell.text

# Check TOC table in DOCX
toc_found = False
for t in doc.tables:
    # check header row
    hdr_texts = [c.text.strip() for c in t.rows[0].cells]
    if "No." in hdr_texts and "Page No." in hdr_texts:
        toc_found = True
        print("3. DOCX TOC Table Rows Sample:")
        for r in t.rows[1:12]:
            vals = [c.text.strip() for c in r.cells]
            print(f"   {vals}")
        # Verify row 1 Cover Page: page column must be empty
        row1_vals = [c.text.strip() for c in t.rows[1].cells]
        assert row1_vals[0] == "1." and "Cover" in row1_vals[1] and row1_vals[2] == "", f"TOC Cover Page check failed: {row1_vals}"
        # Verify row 2 Certificate: page is 'i'
        row2_vals = [c.text.strip() for c in t.rows[2].cells]
        assert row2_vals[2] == "i", f"Certificate page expected 'i', got {row2_vals[2]}"
        # Verify row 7 List of Figures: page is '1'
        row7_vals = [c.text.strip() for c in t.rows[7].cells]
        assert row7_vals[2] == "1", f"LOF page expected '1', got {row7_vals[2]}"
        print("   -> TOC Cover Page is EMPTY, Certificate is 'i', LOF is '1'. All Verified!")
        break

assert toc_found, "Error: DOCX TOC table not found!"

print("\n==================================================================")
print("  ALL VERIFICATIONS PASSED SUCCESSFULLY!")
print("==================================================================")
