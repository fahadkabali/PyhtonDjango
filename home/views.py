from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, UserResponse
from .forms import ResponseForm




from django.shortcuts import render, redirect
from .models import Question, Choice, UserResponse
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from .models import Question, Choice, UserResponse
from django.contrib.auth.decorators import login_required

# @login_required
def take_assessment(request):
    if request.method == 'POST':
        responses = []
        for question in Question.objects.all():
            if question.question_type == Question.SINGLE_CHOICE:
                choice_id = request.POST.get(f'question_{question.id}')
                choice = Choice.objects.get(id=choice_id)
                response = UserResponse(user=request.user, question=question)
                response.save()
                response.selected_choices.add(choice)
            elif question.question_type == Question.MULTIPLE_CHOICE:
                choice_ids = request.POST.getlist(f'question_{question.id}')
                response = UserResponse(user=request.user, question=question)
                response.save()
                choices = Choice.objects.filter(id__in=choice_ids)
                for choice in choices:
                    response.selected_choices.add(choice)
            responses.append(response)

        return redirect('assessment_result')

    questions = Question.objects.all()
    return render(request, 'assessment/take_assessment.html', {'questions': questions})

# @login_required
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

def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))
