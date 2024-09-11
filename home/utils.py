# utils.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings
from .models import UserResponse, Question

def generate_certificate_pdf(user, normalized_score, result):
    # Create a BytesIO buffer for the PDF
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO buffer as its "file."
    c = canvas.Canvas(buffer, pagesize=letter)

    # Load the certificate template
    template_path = os.path.join(settings.STATIC_ROOT, 'milima.png')
    c.drawImage(template_path, 0, 0, width=letter[0], height=letter[1])

    # Set font and size for text
    c.setFont("Helvetica-Bold", 24)

    # Add user information
    c.drawString(200, 400, f"Name: {user.get_full_name()}")
    c.drawString(200, 370, f"Email: {user.email}")
    c.drawString(200, 340, f"Organization: {user.organisation_name}")

    # Add score information
    c.drawString(200, 280, f"Score: {normalized_score}%")
    c.drawString(200, 250, f"Result: {result['text']}")

    # Add assessment details
    c.setFont("Helvetica", 12)
    y_position = 200
    questions = Question.objects.all()
    for question in questions:
        response = UserResponse.objects.filter(user=user, question=question).first()
        if response:
            c.drawString(100, y_position, f"Q: {question.text}")
            y_position -= 20
            c.drawString(120, y_position, f"A: {', '.join(choice.text for choice in response.selected_choices.all())}")
            y_position -= 30

    # Save the PDF
    c.showPage()
    c.save()

    # Get the value of the BytesIO buffer and return it
    pdf = buffer.getvalue()
    buffer.close()
    return pdf