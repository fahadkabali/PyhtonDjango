from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ResponseForm
from .models import Question, Choice, UserResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .utils import generate_certificate
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import os
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

# @login_required
def take_assessment(request):
    if request.method == 'POST':
        responses = []
        for question in Question.objects.all():
            if question.question_type == Question.SINGLE_CHOICE:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    try:
                        choice = Choice.objects.get(id=choice_id)
                        response = UserResponse(user=request.user, question=question)
                        response.save()
                        response.selected_choices.add(choice)
                        responses.append(response)
                    except Choice.DoesNotExist:
                        messages.error(request, f"Choice for question {question.id} does not exist.")
                        return redirect('take_assessment')  # Redirect back to the assessment page
            elif question.question_type == Question.MULTIPLE_CHOICE:
                choice_ids = request.POST.getlist(f'question_{question.id}')
                if choice_ids:
                    response = UserResponse(user=request.user, question=question)
                    response.save()
                    choices = Choice.objects.filter(id__in=choice_ids)
                    if choices.exists():
                        for choice in choices:
                            response.selected_choices.add(choice)
                        responses.append(response)
                    else:
                        messages.error(request, f"One or more choices for question {question.id} do not exist.")
                        return redirect('take_assessment')  # Redirect back to the assessment page

        return redirect('assessment_result')

    questions = Question.objects.all()
    return render(request, 'assessment/take_assessment.html', {'questions': questions})

def assessment_result(request):
    responses = UserResponse.objects.filter(user=request.user)
    total_score = sum(response.total_score() for response in responses)
    
    if total_score > 80:
        result = {'score': total_score, 'text': 'Advanced', 'color': 'green'}
    elif 60 < total_score <= 80:
        result = {'score': total_score, 'text': 'Average', 'color': 'darkgreen'}
    elif 40 < total_score <= 60:
        result = {'score': total_score, 'text': 'Basic', 'color': 'orange'}
    else:
        result = {'score': total_score, 'text': 'Weak', 'color': 'red'}

    recommendations = []
    if total_score < 80:
        recommendations = [
            "Implement stronger password policies",
            "Conduct regular security audits",
            "Enhance staff training on cybersecurity best practices"
        ]

    # Prepare data for charts
    question_texts = [response.question.text for response in responses]
    scores = [response.total_score() for response in responses]

    return render(request, 'assessment/assessment_result.html', {
        'result': result,
        'recommendations': recommendations,
        'question_texts': question_texts,
        'scores': scores,
        'total_score': total_score
    })



def generate_certificate(request):
    responses = UserResponse.objects.filter(user=request.user)
    user = request.user
    fullname = user.fullname
    email = user.email
    organisation_name = user.organisation_name
    total_score = sum(response.total_score() for response in responses)
    score_text = ""
    score_color = ""

    # Determine score text and color
    if total_score > 80:
        score_text = "Advanced"
        score_color = "green"
    elif 60 <= total_score <= 80:
        score_text = "Average"
        score_color = "darkgreen"
    elif 40 <= total_score < 60:
        score_text = "Basic"
        score_color = "orange"
    else:
        score_text = "Weak"
        score_color = "red"

    # Open the certificate template
    template_path = os.path.join(settings.STATIC_ROOT, 'milima.png')
    certificate = Image.open(template_path)
    draw = ImageDraw.Draw(certificate)

    # Load font
    font_path = os.path.join(settings.STATIC_ROOT, 'arial.ttf')
    font = ImageFont.truetype(font_path, 40)

    # Coordinates for the text
    coordinates = {
        'fullname': (500, 200),
        'email': (500, 300),
        'organisation_name': (500, 400),
        'total_score': (500, 500),
        'score_text': (500, 600),
    }

    # Add text to the certificate
    draw.text(coordinates['fullname'], fullname, fill="black", font=font)
    draw.text(coordinates['email'], email, fill="black", font=font)
    draw.text(coordinates['organisation_name'], organisation_name, fill="black", font=font)
    draw.text(coordinates['total_score'], str(total_score), fill="black", font=font)
    draw.text(coordinates['score_text'], score_text, fill=score_color, font=font)

    # Save the certificate to a BytesIO object
    image_buffer = BytesIO()
    certificate.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    # Create a PDF with ReportLab
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    image_file_path = os.path.join(settings.MEDIA_ROOT, f'certificate_{user.username}.png')
    image_file = open(image_file_path, 'wb')
    image_file.write(image_buffer.read())
    image_file.close()
    c.drawImage(image_file_path, 0, 0, width=letter[0], height=letter[1])
    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    # Return the PDF as a downloadable file
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=certificate_{user.username}.pdf'
    return response