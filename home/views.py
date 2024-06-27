from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Response, calculate_total_score, get_feedback
from .forms import ResponseForm

# @login_required
def assessment_view(request):
    questions = Question.objects.all()
    if request.method == 'POST':
        responses = []
        for question in questions:
            form = ResponseForm(request.POST, question=question)
            if form.is_valid():
                response = form.save(commit=False)
                response.user = request.user
                response.question = question
                response.save()
                form.save_m2m()
                responses.append(response)
            else:
                return render(request, '/assessment/assessment.html', {'questions': questions, 'form': form})

        total_score = calculate_total_score(responses)
        feedback = get_feedback(total_score)
        
        return render(request, 'assessment/assessment_result.html', {
            'total_score': total_score,
            'feedback': feedback,
        })
    
    form = ResponseForm(question=questions.first())
    return render(request, 'assessment/assessment.html', {
        'questions': questions,
        'form': form,
    })

# @login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/login/")
# def pages(request):
#     context = {}
#     # All resource paths end in .html.
#     # Pick out the html file name from the url. And load that template.
#     try:

#         load_template = request.path.split('/')[-1]

#         if load_template == 'admin':
#             return HttpResponseRedirect(reverse('admin:index'))
#         context['segment'] = load_template

#         html_template = loader.get_template('home/' + load_template)
#         return HttpResponse(html_template.render(context, request))

#     except template.TemplateDoesNotExist:

#         html_template = loader.get_template('home/page-404.html')
#         return HttpResponse(html_template.render(context, request))

#     except:
#         html_template = loader.get_template('home/page-500.html')
#         return HttpResponse(html_template.render(context, request))

def results_view(request):
    return render(request, "home/results.html")