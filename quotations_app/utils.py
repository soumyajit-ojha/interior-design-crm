from io import BytesIO

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from weasyprint import HTML


from .serializers import QuotationDetailSerializer


def generate_quotation_pdf(quotation):
    serializer = QuotationDetailSerializer(quotation)
    html_string = render_to_string(
        "quotation_pdf_template.html",
        context={
            "quotation": serializer.data,
            "rooms": serializer.data.get("rooms", []),
        },
    )

    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    pdf_file.seek(0)
    return pdf_file


def send_quotation_email(quotation):
    if not quotation.client_fk or not quotation.client_fk.email:
        return
    print(f"Sending email to: {quotation.client_fk.email}")
    pdf_file = generate_quotation_pdf(quotation)
    email = EmailMessage(
        subject=f"Quotation #{quotation.quotation_number}",
        body="Please find pdf attached your quotation.",
        to=[quotation.client_fk.email],
    )
    email.attach(
        f"Quotation_{quotation.quotation_number}.pdf",
        pdf_file.read(),
        "application/pdf",
    )
    email.send()
