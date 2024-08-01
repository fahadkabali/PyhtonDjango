from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
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
from django.db.models import Q
from .models import AssessmentHistory
from django.core.files.base import ContentFile
from reportlab.lib.utils import ImageReader



User = get_user_model()
###############################################################################################
##################################dashboard view ###############################################
################################################################################################

@login_required
def index(request):
    user = request.user
    user_count = User.objects.count()
    responses = UserResponse.objects.filter(user=request.user)
    total_score = sum(response.total_score() for response in responses)
    normalized_score = request.session.get('assessment_score', 0)



    ############################### Prepare data for charts ############################################
    question_texts = [response.question.text for response in responses]
    scores = [response.total_score() for response in responses]
    question = Question.objects.all()

    return render (request, 'home/index.html', {
        'question':question,
        'user': user,
        'question_texts': question_texts,
        'scores': scores,
        'normalized_score':normalized_score,
        'total_score': total_score,
        'user_count':user_count
    })
###############################################################################################################
##########################################view for taking assessment ##########################################
###############################################################################################################
@login_required

def take_assessment(request):
    if request.method == 'POST':
        # Clear previous responses for this user
        UserResponse.objects.filter(user=request.user).delete()
        
        responses = []
        total_score = 0
        max_possible_score = sum(Question.objects.all().values_list('max_score', flat=True))
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
                        total_score += choice.score
                    except Choice.DoesNotExist:
                        messages.error(request, f"Choice for question {question.id} does not exist.")
                        return redirect('take_assessment')
            elif question.question_type == Question.MULTIPLE_CHOICE:
                choice_ids = request.POST.getlist(f'question_{question.id}')
                if choice_ids:
                    response = UserResponse(user=request.user, question=question)
                    response.save()
                    choices = Choice.objects.filter(id__in=choice_ids)
                    if choices.exists():
                        for choice in choices:
                            response.selected_choices.add(choice)
                            total_score += choice.score
                        responses.append(response)
                    else:
                        messages.error(request, f"One or more choices for question {question.id} do not exist.")
                        return redirect('take_assessment')
        normalized_score = round(min(100, (total_score / max_possible_score) * 100), 1)
        #########################Store the normalized score in the session ##########################################
        request.session['assessment_score'] = normalized_score
        request.session['new_assessment_completed'] = True
        return redirect('assessment_result')
    
    questions = Question.objects.all()
    return render(request, 'assessment/take_assessment.html', {'questions': questions,})

#####################################################################################################################
#####################################Asssessment view################################################################
#####################################################################################################################
@login_required
def assessment_result(request):
    responses = UserResponse.objects.filter(user=request.user).order_by('-submitted_at')
    total_score = sum(response.total_score() for response in responses)
    normalized_score = request.session.get('assessment_score', 0)


    
    if normalized_score > 80:
        result = {'score': total_score, 'text': 'Advanced', 'color': '#32EE32', 'class':'success'}
    elif 60 < normalized_score <= 80:
        result = {'score': total_score, 'text': 'Average', 'color': '#004400', 'class':'primary'}
    elif 40 < normalized_score <= 60:
        result = {'score': total_score, 'text': 'Basic', 'color': '#FFA400', 'class':'warning'}
    else:
        result = {'score': total_score, 'text': 'Weak', 'color': '#FF0000', 'class':'danger'}

    recommendations = []
    if normalized_score < 80:
        recommendations = [
            "Implement stronger password policies",
            "Conduct regular security audits",
            "Enhance staff training on cybersecurity best practices",
            "Implement multi-factor authentication (MFA) where feasible",
            "Deploy endpoint protection solutions on all devices",
            "Establish a formal incident response plan and conduct regular drills",
            "Encrypt sensitive data both in transit and at rest",
            "Implement network segmentation to limit the impact of breaches",
            "Update and patch systems and software regularly",
            "Monitor and log network activity for suspicious behavior",
            "Consider implementing a Security Information and Event Management (SIEM) system",
            "Review and revise access controls periodically to ensure least privilege access",
            "Enhance physical security measures for data centers and critical infrastructure",
            "Emphasize the importance of cyber security awareness and training:",
            "   * This investment prevents greater costs resulting from avoidable data breaches.",
            "   * Educate employees and business owners on effective incident response and risk management.",
            "   * Provide guidance on fraud prevention, phishing awareness, identity theft, and scams.",
            "   * Help employees understand common system vulnerabilities and recognize suspicious activities.",
            "   * Encourage a culture where security considerations are integrated into daily decision-making.",
            "   * Ensure compliance with company security standards, policies, and procedures."
        ]
    if request.session.pop('new_assessment_completed', False):
        AssessmentHistory.objects.create(
            user=request.user,
            score=normalized_score,
            result_text=result['text'],
        )

    ############################### Prepare data for charts##############################################
    responses = UserResponse.objects.filter(user=request.user).order_by('-submitted_at')
    
    question_texts = [response.question.text for response in responses]
    scores = [response.total_score() for response in responses]
    return render(request, 'assessment/assessment_result.html', {
        'result': result,
        'recommendations': recommendations,
        'question_texts': question_texts,
        'total_score': total_score,
        'scores': scores,
        'normalized_score': normalized_score
    })

################################################################################################
############################### view for generating results#####################################
################################################################################################
@login_required
def generate_certificate(request):
    responses = UserResponse.objects.filter(user=request.user)
    user = request.user
    fullname = user.fullname
    email = user.email
    organisation_name = user.organisation_name
    normalized_score = request.session.get('assessment_score', 0)


    ###############################Determine score text and color######################################
    if normalized_score > 80:
        score_text = "Advanced"
        score_color = "#32EE32" 
        score_class = "success"

    elif 60 < normalized_score <= 80:
        score_text = "Average"
        score_color = "#004400" 
        score_class = "primary"

    elif 40 < normalized_score <= 60:
        score_text = "Basic"
        score_color = "#FFA400" 
        score_class = "warning"
    else:
        score_text = "Weak"
        score_color = "#FF0000"  
        score_class = "danger"

    #########################################Open the certificate template##################################
    template_path = os.path.join(settings.STATIC_ROOT, 'milima.png')
    certificate = Image.open(template_path)
    draw = ImageDraw.Draw(certificate)

    ####################################### Load font############################################################
    font_path = os.path.join(settings.STATIC_ROOT, 'open-sans.bold.ttf')
    font = ImageFont.truetype(font_path, 60)

    ####################################Coordinates for the text##################################################
    coordinates = {
        'fullname': (890, 1520),
        'email': (890, 1590),
        'organisation_name': (890, 1665),
        'total_score': (2164, 2190),
        'score_text': (1500, 2035),
        'score_circle': (688, 2096)
    }
    total_score_with_percentage = f"{normalized_score} %"

    ####################################### Add text to the certificate################################################
    draw.text(coordinates['fullname'], fullname, fill="black", font=font)
    draw.text(coordinates['email'], email, fill="black", font=font)
    draw.text(coordinates['organisation_name'], organisation_name, fill="black", font=font)
    draw.text(coordinates['total_score'], str(total_score_with_percentage), fill=score_color, font=font)
    draw.text(coordinates['score_text'], score_text, fill=score_color, font=font)

    ##################################Draw score circle#########################################################
    circle_center = coordinates['score_circle']
    circle_radius = 135
    draw.ellipse(
        (circle_center[0] - circle_radius, circle_center[1] - circle_radius,
         circle_center[0] + circle_radius, circle_center[1] + circle_radius),
        fill=score_color
    )

    ####################################Save the certificate to a BytesIO object#########################################
    image_buffer = BytesIO()
    certificate.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    #######################################Create a PDF with ReportLab######################################################
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    c.drawImage(ImageReader(image_buffer), 0, 0, width=letter[0], height=letter[1])
    c.showPage()
    c.save()

    ###########################################Get the PDF content##########################################################
    pdf_content = pdf_buffer.getvalue()
    pdf_buffer.close()

    ##################################Save to AssessmentHistory############################################################
    history_entry, created = AssessmentHistory.objects.get_or_create(
        user=request.user,
        score=normalized_score,
        result_text=score_text,
        score_color=score_color,
    )

    ##############################################Save the certificate########################################################
    certificate_filename = f'certificate_{request.user.username}_{history_entry.id}.pdf'
    history_entry.certificate.save(certificate_filename, ContentFile(pdf_content), save=True)

    ######################################Prepare the response###############################################################
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{certificate_filename}"'
    
    return response
#################################################################################################################################
##################################################search button ###############################################################
#################################################################################################################################
def search_view(request):
    query = request.POST.get('q', '')
    query = request.GET.get('q', '')
    words = query.split()
    
    results = []
    if words:
        q_objects = Q()
        for word in words:
            q_objects |= Q(text__icontains=word)
        
        results = Question.objects.filter(q_objects).distinct()

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search/search_results.html', context)

def question_detail_view(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choices.all()

    context = {
        'question': question,
        'choices': choices,
    }
    return render(request, 'search/question_detail.html', context)


########################################################################################################################
################################################# History View ##########################################################
#########################################################################################################################

@login_required
def assessment_history(request):
    history = AssessmentHistory.objects.filter(user=request.user)
    
    context = {
        'history': history,
    }
    return render(request, 'assessment/assessment_history.html', context)