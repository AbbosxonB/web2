from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from .models import TestResult
from apps.tests.models import Test
from docxtpl import DocxTemplate
import os
from django.contrib.auth.decorators import login_required

@login_required
def export_results_docx(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    
    # Filter results by test
    results = TestResult.objects.filter(test=test).select_related('student', 'student__group').order_by('-score')
    
    # Check if any results exist
    if not results.exists():
        # You might want to handle this gracefully, e.g., redirect with a message
        pass 

    # Prepare data for template
    # Assuming all students in the result set might help determine faculty/course if consistent
    # Or just taking the first one for header info
    first_result = results.first()
    group_name = "N/A"
    faculty_name = "N/A" # Default
    course_name = "N/A"
    
    if first_result and first_result.student.group:
        group_name = first_result.student.group.name
        # Assuming group has faculty/course info, or student does. 
        # Adjust based on actual models. inspecting Student/Group models might be needed if these fields exist.
        # For now, simplistic approach or hardcoded if specific fields are missing in models
        
    
    template_path = os.path.join(settings.BASE_DIR, 'apps/results/templates/results/docx/vedmost_template.docx')
    if not os.path.exists(template_path):
         return HttpResponse("Template not found", status=404)

    doc = DocxTemplate(template_path)

    results_list = []
    for index, result in enumerate(results, start=1):
        results_list.append({
            'number': index,
            'full_name': result.student.full_name,
            'score': result.score,
            'signature': '' # Placeholder
        })

    context = {
        'university_name': "TOSHKENT IJTIMOIY INNOVATSIYA UNIVERSITETI",
        'Guruh': group_name,
        'Fakultet': faculty_name,
        'Kursi': course_name,
        'Test_nomi': test.title,
        'Sana': timezone.now().strftime("%d.%m.%Y"),
        'results_table': results_list, # We need to map this to the table rows in the template. 
                                       # docxtpl requires specific tags in the table row to iterate. 
                                       # I might need to inspect the xml again to see what tags I should use or if I need to edit the template to add jinja2 tags.
    }
    
    # NOTE: The template likely doesn't have jinja2 tags yet ({% for ... %}). 
    # The user provided a raw docx. I need to know IF I can Edit the docx programmatically to insert tags OR 
    # if I should ask the user to add tags?
    # Usually, with docxtpl, you need to put {{ variable }} in the docx.
    # The inspecting script showed "VEDMOST ({Guruh})", so {Guruh} style might be there, but loop for table?
    # The table row showed: ['1', 'Full_name', 'Result ', 'Null'] in the inspection. 
    # I should probably assume I need to map context keys to what's visually in the docx, 
    # OR better, since I can't easily see exact placeholder syntax without opening it, 
    # I will assume standard jinja2 {{ val }} is needed. 
    # BUT, the file provided is likely just a static text file. 
    # Strategy: I will render it using keys I saw in inspection like {Guruh} -> {{ Guruh }} logic? 
    # No, docxtpl expects `{{ var }}`. CONSTANT text `{Guruh}` won't work unless I define custom delimiters or replace text.
    # HOWEVER, checking the user request: "VEDMOST ({Guruh})". 
    # I will try to use the `doc.render(context)` and hopefully if I use the same keys it might just work if they used `{}` which matches some format, 
    # but docxtpl default is `{{}}`.
    # I will update the template file to have proper tags if possible, OR just try to render.
    # Actually, I'll write the view first, but I suspect I need to MODIFY the template to have `{{ }}` tags.
    # Since I cannot open the word processor to edit, I might rely on text replacement or just assume the user will accept a best-effort 
    # or I might need to instruct the user to put `{{ }}`.
    # 
    # Let's inspect the `Student` and `Group` models first to get accurate data.
    
    doc.render(context)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    filename = f"Vedmost_{test.id}_{timezone.now().strftime('%Y%m%d')}.docx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    doc.save(response)
    
    return response

# Placeholder for now, will write to actual file after checking models
