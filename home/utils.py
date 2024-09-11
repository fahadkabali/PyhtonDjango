from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os

def calculate_normalized_score(total_score, max_possible_score):
    return round(min(100, (total_score / max_possible_score) * 100), 1)

def get_result_data(normalized_score):
    if normalized_score > 80:
        return {'text': 'Advanced', 'color': '#32EE32', 'class': 'success'}
    elif 60 < normalized_score <= 80:
        return {'text': 'Average', 'color': '#004400', 'class': 'primary'}
    elif 40 < normalized_score <= 60:
        return {'text': 'Basic', 'color': '#FFA400', 'class': 'warning'}
    else:
        return {'text': 'Weak', 'color': '#FF0000', 'class': 'danger'}

def generate_certificate_pdf(user, normalized_score, result):
    template_path = os.path.join(settings.STATIC_ROOT, 'milima.png')
    certificate = Image.open(template_path)
    draw = ImageDraw.Draw(certificate)

    font_path = os.path.join(settings.STATIC_ROOT, 'open-sans.bold.ttf')
    font = ImageFont.truetype(font_path, 60)

    coordinates = {
        'fullname': (890, 1520),
        'email': (890, 1590),
        'organisation_name': (890, 1665),
        'total_score': (2164, 2190),
        'score_text': (1500, 2035),
        'score_circle': (688, 2096)
    }

    draw.text(coordinates['fullname'], user.fullname, fill="black", font=font)
    draw.text(coordinates['email'], user.email, fill="black", font=font)
    draw.text(coordinates['organisation_name'], user.organisation_name, fill="black", font=font)
    draw.text(coordinates['total_score'], f"{normalized_score} %", fill=result['color'], font=font)
    draw.text(coordinates['score_text'], result['text'], fill=result['color'], font=font)

    circle_center = coordinates['score_circle']
    circle_radius = 135
    draw.ellipse(
        (circle_center[0] - circle_radius, circle_center[1] - circle_radius,
         circle_center[0] + circle_radius, circle_center[1] + circle_radius),
        fill=result['color']
    )

    image_buffer = BytesIO()
    certificate.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    c.drawImage(ImageReader(image_buffer), 0, 0, width=letter[0], height=letter[1])
    c.showPage()
    c.save()

    return pdf_buffer.getvalue()