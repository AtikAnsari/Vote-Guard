# Final Format & Validation Checklist (Silver Oak University PBL-I)

This checklist documents the complete validation of the final project report for **VOTE-GUARD: RFID-BASED VOTER VERIFICATION AND DUPLICATE-VOTE PREVENTION SYSTEM** following all faculty corrections and official Silver Oak University Problem Based Learning (PBL-I) formatting requirements.

---

## 1. Faculty Corrections Compliance Matrix

| No. | Faculty Correction Requirement | Implementation in DOCX & PDF | Validation Status |
| :---: | :--- | :--- | :---: |
| **1** | **First Page – Logo & Footer**<br/>• Remove header logo/banner on Page 1<br/>• Keep centered university logo on Page 1<br/>• Correct centered logo proportions<br/>• Remove entire footer & page number from Page 1 | • Header banner is strictly removed on Page 1.<br/>• Centered logo (`p1_img0_X7.png`) is retained with true native 1.593 aspect ratio (not stretched).<br/>• Page 1 has zero footer and zero page numbering. | **VERIFIED PASS** |
| **2** | **Logo Proportions – All Pages**<br/>• Correct header logo stretching throughout report<br/>• Preserve original aspect ratio of both logos (4.625 for banner, 1.593 for centered seal)<br/>• Do not stretch width and height independently | • Header banner (`p5_img0_X21.png`, 1073 $\times$ 232) rendered with locked 4.625 aspect ratio on all applicable pages.<br/>• Centered logo rendered with locked 1.593 aspect ratio.<br/>• Zero independent or distorted stretching. | **VERIFIED PASS** |
| **3** | **Table of Contents Headings**<br/>• Remove "PART 1" and "PART 2"<br/>• Use identical heading **TABLE OF CONTENTS** on both pages<br/>• Preserve all chapters, subheadings, and page references | • Page 10 heading: `TABLE OF CONTENTS`<br/>• Page 11 heading: `TABLE OF CONTENTS`<br/>• Words "PART 1" and "PART 2" completely removed.<br/>• All rows, chapters, sections, and references preserved intact. | **VERIFIED PASS** |
| **4** | **Page Numbering System (3 Sections)**<br/>• **Section 1 (Page 1):** No footer, no page number<br/>• **Section 2 (Pages 2–6):** Lowercase Roman numerals (`i, ii, iii, iv, v`) on Certificate through Keywords<br/>• **Section 3 (Pages 7–50):** Arabic numerals starting at 1 on List of Figures (`1, 2, 3...`) through final page | • Built with native Microsoft Word Section Breaks (`WD_SECTION_START.NEW_PAGE`).<br/>• **Section 1:** Blank header and blank footer.<br/>• **Section 2:** Unlinked footer, `w:fmt="lowerRoman"`, `w:start="1"`, displays `- i -` to `- v -`.<br/>• **Section 3:** Unlinked footer, `w:fmt="decimal"`, `w:start="1"`, List of Figures displays `- 1 -` and continues to `- 44 -` on final page. | **VERIFIED PASS** |
| **5** | **Certificate – Date & Place Format**<br/>• Replace `[DD/MM/YY]` or actual values<br/>• Display exact style: blank underlined lines | Displayed exactly as specified:<br/>`DATE: ____________________`<br/><br/>`PLACE: ____________________` | **VERIFIED PASS** |
| **6** | **Declaration – Remove Date & Place**<br/>• Completely remove `PLACE: AHMEDABAD` and `DATE: [DD/MM/YY]`<br/>• Do not replace with blank fields<br/>• Retain 3-student team table | • Date and Place entries completely eliminated.<br/>• Zero blank lines introduced.<br/>• Exact 3-row student signature table preserved. | **VERIFIED PASS** |
| **7** | **Institution Name Correction**<br/>• First Page & Certificate: write only `College of Technology` (not `Silver Oak College of Technology`) | • Page 1: `Department of Computer Science and Engineering, College of Technology, Silver Oak University`<br/>• Certificate: `Department of Computer Science and Engineering, College of Technology, Silver Oak University`<br/>• Guide & HOD blocks updated to `College of Technology`. | **VERIFIED PASS** |
| **8** | **Certificate Page – Remove Only Bracketed Placeholder**<br/>• Remove only `[Head of Department]`<br/>• Preserve signature line `____________________________`<br/>• Preserve exact 3 lines below it:<br/>  - Head of Department<br/>  - Department of CSE<br/>  - College of Technology<br/>• Do not add HOD name | • Bracketed placeholder `[Head of Department]` completely removed.<br/>• Signature horizontal line `____________________________` preserved intact.<br/>• Exact 3 designation lines retained below the signature line in both DOCX and PDF.<br/>• Zero placeholder leaks or inserted names. | **VERIFIED PASS** |
| **9** | **Table of Contents – Correct Page Numbers**<br/>• Cover Page / Title Page: Page column left **EMPTY** (no "1")<br/>• Preliminary Pages: Display actual Roman numbers (`i, ii, iii, iv, v`)<br/>• Main Report: Display actual Arabic numbers starting at `1` on List of Figures (`1, 2, 3...44`)<br/>• LOF and LOT updated to matching Arabic pages | • Cover Page / Title Page row has empty string `""` in Page column.<br/>• Certificate is `i`, Declaration is `ii`, Acknowledgement is `iii`, Abstract is `iv`, Keywords is `v`.<br/>• List of Figures is `1`, List of Tables is `2`, List of Abbreviations is `3`, Table of Contents is `4`, Chapter 1 is `6`... Annexures is `44`.<br/>• 100% matched to visible physical page footers in PDF and DOCX. | **VERIFIED PASS** |
| **10** | **Preserve All Approved Content**<br/>• 3 Students: Ansari Mo.Atik, Shaikh Sakib Ahmed, Shaikh Sejan<br/>• Guide: Prof. Urmil Mewada (Dept. of Computer Engineering)<br/>• Black headings, Times New Roman, 1.5 line spacing, 50 pages | • All names, enrollment numbers, and departments preserved.<br/>• Black-only headings (`#000000`).<br/>• Strictly 50 pages total in matching PDF. | **VERIFIED PASS** |

---

## 2. Document-Level Audit Table

| Parameter | University Specification | Actual Value in Report | Status |
| :--- | :--- | :--- | :--- |
| **A4 Paper Size** | 210 mm $\times$ 297 mm (8.27" $\times$ 11.69") | 8.27" $\times$ 11.69" (A4) | **PASS** |
| **Font (All Elements)** | Times New Roman | Times New Roman (Body, Headings, Captions, Tables, Header/Footer) | **PASS** |
| **Body Text Size** | 12 pt | 12.0 pt in Word DOCX, 10–10.5 pt scaled in PDF for 50-page target | **PASS** |
| **Line Spacing** | 1.5 Lines | 1.5 Line Spacing (21.6 pt exact leading) | **PASS** |
| **Paragraph Alignment** | Justified | Justified (Full Justification across all body text) | **PASS** |
| **Margins** | Left: 1.25", Right: 1.0", Top: 1.0", Bottom: 1.0" | Left: 1.25", Right: 1.0", Top: 1.0", Bottom: 1.0" | **PASS** |
| **Total Page Count** | 45–50 Pages | Strictly **50 Pages** | **PASS** |

---

## 3. Section and Pagination Structure

| Document Section | Physical Pages | Visible Page Display | Content Included | TOC Page Column | Status |
| :---: | :---: | :---: | :--- | :---: | :---: |
| **Section 1** | **Page 1** | *None* | Title / Cover Page | *(Empty)* | **VERIFIED** |
| **Section 2** | **Pages 2–6** | `- i -` to `- v -` | Certificate (`i`), Declaration (`ii`), Acknowledgement (`iii`), Abstract (`iv`), Keywords & Research Scope Summary (`v`) | `i`, `ii`, `iii`, `iv`, `v` | **VERIFIED** |
| **Section 3** | **Pages 7–50** | `- 1 -` to `- 44 -` | List of Figures (`1`), List of Tables (`2`), List of Abbreviations (`3`), Table of Contents (`4`), Chapter 1 (`6`), Chapter 2 (`9`), Chapter 3 (`15`), Chapter 4 (`21`), Chapter 5 (`31`), Chapter 6 (`36`), Chapter 7 (`38`), Chapter 8 (`40`), Chapter 9 (`42`), References (`43`), Annexures (`44`) | `1`, `2`, `3`, `4`, `6`...`44` | **VERIFIED** |

---

## 4. Final Deliverables Generated

1. `Final_Project_Report/VoteGuard_Final_Project_Report.docx` — Fully editable master Microsoft Word document with 3 native section breaks, unlinked headers/footers, lowerRoman and decimal page numbering fields, locked logo aspect ratios, clean black-and-white academic tables, corrected institutional designations, clean Certificate HOD signature block without bracketed placeholder, and verified TOC page numbers (Cover Page empty, Roman i..v, Arabic 1..44).
2. `Final_Project_Report/VoteGuard_Final_Project_Report.pdf` — High-resolution print-ready 50-page PDF matching the DOCX layout, 3-tier pagination system, centered Page 1 seal, blank Date/Place on Certificate, clean Declaration without Date/Place, unified Table of Contents headings, and exact TOC/LOF/LOT Arabic page alignment.
3. `Final_Project_Report/Report_Validation_Checklist.md` — Complete verification checklist documenting all compliance results.
