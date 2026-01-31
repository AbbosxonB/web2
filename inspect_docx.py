import zipfile
import xml.etree.ElementTree as ET
import sys
import os

docx_path = r"c:\Users\Alikhanovich\OneDrive\Ishchi stol\web2\TOSHKENT IJTIMOIY INNOVATSIYA UNIVERSITETI.docx"

if not os.path.exists(docx_path):
    print(f"File not found: {docx_path}")
    sys.exit(1)

try:
    with zipfile.ZipFile(docx_path) as z:
        if 'word/document.xml' not in z.namelist():
            print("word/document.xml not found using standard path.")
            # list all
            # print(z.namelist())
        else:
            with z.open('word/document.xml') as f:
                xml_content = f.read()
                
            root = ET.fromstring(xml_content)
            
            # namespaces
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            # Simple text extraction to see what's in there
            # Flattening paragraphs and tables
            
            print("--- Document Content Preview ---")
            
            # Iterating through body elements
            body = root.find('w:body', ns)
            if body is not None:
                for element in body:
                    tag = element.tag
                    if tag.endswith('p'): # Paragraph
                        texts = [node.text for node in element.findall('.//w:t', ns) if node.text]
                        if texts:
                            print(f"P: {''.join(texts)}")
                    elif tag.endswith('tbl'): # Table
                        print("--- Table Found ---")
                        rows = element.findall('.//w:tr', ns)
                        for i, row in enumerate(rows):
                            cells = row.findall('.//w:tc', ns)
                            row_data = []
                            for cell in cells:
                                cell_texts = [node.text for node in cell.findall('.//w:t', ns) if node.text]
                                row_data.append("".join(cell_texts))
                            print(f"Row {i}: {row_data}")
                        print("--- End Table ---")
                        
except Exception as e:
    print(f"Error: {e}")
