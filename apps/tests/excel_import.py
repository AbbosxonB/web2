import openpyxl
from openpyxl_image_loader import SheetImageLoader
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO
import uuid

def import_questions_from_excel(file):
    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    
    # Initialize image loader
    image_loader = None
    try:
        image_loader = SheetImageLoader(sheet)
    except Exception:
        pass # No images or error loading images
    
    questions = []
    # We scan rows. Cannot use values_only=True because we need coordinates
    for row in sheet.iter_rows(min_row=2):
        # Basic validation: check if first cell has content (text or value)
        # Note: Sometimes cell.value is None but there is an image. 
        # We'll check if at least one of the main cells has something or image.
        if not row:
            continue
            
        # Helper to get content (Text + Image)
        def get_content(cell_idx):
            if cell_idx >= len(row):
                return ""
            
            cell = row[cell_idx]
            text = str(cell.value) if cell.value is not None else ""
            
            # Check for image
            if image_loader and image_loader.image_in(cell.coordinate):
                try:
                    image = image_loader.get(cell.coordinate)
                    
                    # Save to BytesIO
                    img_byte_arr = BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_content = ContentFile(img_byte_arr.getvalue())
                    
                    # Save to storage
                    filename = f"test_questions/{uuid.uuid4().hex}.png"
                    saved_path = default_storage.save(filename, img_content)
                    url = default_storage.url(saved_path)
                    
                    # Append HTML to text
                    # If text exists, add break.
                    img_tag = f'<img src="{url}" class="max-w-full h-auto mt-2 rounded border" style="max-height: 300px;">'
                    if text.strip():
                        text = f"{text}<br>{img_tag}"
                    else:
                        text = img_tag
                        
                except Exception as e:
                    print(f"Error extracting image from {cell.coordinate}: {e}")
            
            return text

        # If question text is empty, skip (unless strict rule? Let's assume question is mandatory)
        q_text = get_content(0)
        if not q_text:
            continue

        question = {
            'question_text': q_text,
            'option_a': get_content(1),
            'option_b': get_content(2),
            'option_c': get_content(3),
            'option_d': get_content(4),
            'correct_answer': str(row[5].value) if len(row) > 5 and row[5].value else 'A',
            'score': 2 # Default score
        }
        questions.append(question)
    
    return questions
