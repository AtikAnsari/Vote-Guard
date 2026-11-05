import zipfile
import xml.etree.ElementTree as ET

namespaces = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
}

issues = []

with zipfile.ZipFile('Final_Project_Report/VoteGuard_Final_Project_Report.docx', 'r') as z:
    for name in z.namelist():
        if not name.endswith('.xml') and not name.endswith('.rels'):
            continue
        try:
            raw = z.read(name)
            tree = ET.fromstring(raw)
        except Exception as e:
            issues.append(f'Parse error in {name}: {e}')
            continue
        
        # Check every element in tree
        for elem in tree.iter():
            tag = elem.tag
            if tag.startswith('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'):
                w_tag = tag.split('}')[-1]
                # Check run children
                if w_tag == 'r':
                    for child in elem:
                        c_tag = child.tag.split('}')[-1]
                        allowed_r = {'rPr', 't', 'br', 'cr', 'tab', 'drawing', 'fldChar', 'instrText',
                                     'footnoteReference', 'endnoteReference', 'commentReference',
                                     'annotationRef', 'dayLong', 'dayShort', 'monthLong', 'monthShort',
                                     'yearLong', 'yearShort', 'pgNum', 'noBreakHyphen', 'softHyphen',
                                     'sym', 'ruby', 'separator', 'continuationSeparator'}
                        if c_tag not in allowed_r:
                            issues.append(f'Invalid child <{c_tag}> inside <w:r> in {name}')
                
                # Check table children
                elif w_tag == 'tbl':
                    for child in elem:
                        c_tag = child.tag.split('}')[-1]
                        allowed_tbl = {'tblPr', 'tblGrid', 'tr', 'customXml', 'sdt'}
                        if c_tag not in allowed_tbl:
                            issues.append(f'Invalid child <{c_tag}> inside <w:tbl> in {name}')

                # Check row children
                elif w_tag == 'tr':
                    for child in elem:
                        c_tag = child.tag.split('}')[-1]
                        allowed_tr = {'trPr', 'tc', 'customXml', 'sdt'}
                        if c_tag not in allowed_tr:
                            issues.append(f'Invalid child <{c_tag}> inside <w:tr> in {name}')

                # Check cell children
                elif w_tag == 'tc':
                    for child in elem:
                        c_tag = child.tag.split('}')[-1]
                        allowed_tc = {'tcPr', 'p', 'tbl', 'customXml', 'sdt'}
                        if c_tag not in allowed_tc:
                            issues.append(f'Invalid child <{c_tag}> inside <w:tc> in {name}')
                            
                # Check paragraph children
                elif w_tag == 'p':
                    for child in elem:
                        c_tag = child.tag.split('}')[-1]
                        allowed_p = {'pPr', 'r', 'fldSimple', 'hyperlink', 'subDoc', 'customXml', 'sdt', 'smartTag', 'bookmarkStart', 'bookmarkEnd', 'commentRangeStart', 'commentRangeEnd', 'proofErr'}
                        if c_tag not in allowed_p:
                            issues.append(f'Invalid child <{c_tag}> inside <w:p> in {name}')

print(f"Total schema issues found: {len(issues)}")
for iss in issues:
    print(" - ", iss)

