from django.template import Template, Context, TemplateSyntaxError
from internships.models.template import Template as TemplateModel
from internships.models.document import Document
from io import BytesIO
from xhtml2pdf import pisa
from django.core.exceptions import ValidationError

def render_template_to_string(template_content: str, context_data: dict) -> str:
    try:
        return Template(template_content).render(Context(context_data))
    except TemplateSyntaxError as e:
        raise ValidationError(f"Template syntax error: {str(e)}")
    except Exception as e:
        raise ValidationError(f"Error rendering template: {str(e)}")

def generate_pdf(html_content: str) -> BytesIO:
    output = BytesIO()
    result = pisa.CreatePDF(html_content, dest=output)
    if result.err:
        raise ValidationError("Failed to generate PDF")
    output.seek(0)
    return output

def create_document_from_template(template: TemplateModel, context_data: dict, internship, uploaded_by) -> Document:
    try:
        rendered = render_template_to_string(template.content, context_data)

        if template.type == "pdf":
            pdf_data = generate_pdf(rendered)
            filename = f"{template.title}_{internship.id}.pdf"

            doc = Document.objects.create(
                internship=internship,
                label=template.title,
                file=None,
                uploaded_by=uploaded_by,
                type="generated",
                status="submitted"
            )
            doc.file.save(filename, pdf_data)
            return doc

        return Document.objects.create(
            internship=internship,
            label=template.title,
            uploaded_by=uploaded_by,
            type="generated",
            status="submitted"
        )
    except Exception as e:
        raise ValidationError(f"Failed to create document: {str(e)}")
