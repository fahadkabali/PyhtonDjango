from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q, Sum
from django.core.files.base import ContentFile
from .models import Question, Choice, UserResponse, AssessmentHistory
from .utils import generate_certificate_pdf, calculate_normalized_score, get_result_data
from django.contrib.auth import get_user_model

User = get_user_model()
@login_required
def index(request):
    user = request.user
    user_count = User.objects.count()
    responses = UserResponse.objects.filter(user=request.user)
    
    # Calculate total score
    total_score = sum(
        sum(choice.score for choice in response.selected_choices.all())
        for response in responses
    )
    
    normalized_score = request.session.get('assessment_score', 0)

    # Prepare data for charts
    question_texts = [response.question.text for response in responses]
    scores = [
        sum(choice.score for choice in response.selected_choices.all())
        for response in responses
    ]
    
    questions = Question.objects.all()

    context = {
        'questions': questions,
        'user': user,
        'question_texts': question_texts,
        'scores': scores,
        'normalized_score': normalized_score,
        'total_score': total_score,
        'user_count': user_count
    }

    return render(request, 'home/index.html', context)
@login_required
def take_assessment(request):
    if request.method == 'POST':
        # Clear previous responses for this user
        UserResponse.objects.filter(user=request.user).delete()
        
        total_score = 0
        max_possible_score = sum(Question.objects.all().values_list('max_score', flat=True))
        
        for question in Question.objects.all():
            response = UserResponse(user=request.user, question=question)
            response.save()  # Save the response object first
            
            if question.question_type == Question.SINGLE_CHOICE:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    try:
                        choice = Choice.objects.get(id=choice_id)
                        response.selected_choices.add(choice)
                        total_score += choice.score
                    except Choice.DoesNotExist:
                        messages.error(request, f"Choice for question {question.id} does not exist.")
                        return redirect('take_assessment')
            
            elif question.question_type == Question.MULTIPLE_CHOICE:
                choice_ids = request.POST.getlist(f'question_{question.id}')
                if choice_ids:
                    choices = Choice.objects.filter(id__in=choice_ids)
                    if choices.exists():
                        response.selected_choices.add(*choices)
                        total_score += sum(choice.score for choice in choices)
                    else:
                        messages.error(request, f"One or more choices for question {question.id} do not exist.")
                        return redirect('take_assessment')
            
            if not response.selected_choices.exists():
                response.delete()  # Remove responses without selected choices
        
        normalized_score = round(min(100, (total_score / max_possible_score) * 100), 1)
        request.session['assessment_score'] = normalized_score
        request.session['new_assessment_completed'] = True
        return redirect('assessment_result')
    
    questions = Question.objects.all()
    return render(request, 'assessment/take_assessment.html', {'questions': questions})
    if request.method == 'POST':
        UserResponse.objects.filter(user=request.user).delete()
        
        total_score = 0
        max_possible_score = Question.objects.aggregate(Sum('max_score'))['max_score__sum'] or 0

        for question in Question.objects.all():
            response = UserResponse(user=request.user, question=question)
            
            if question.question_type == Question.SINGLE_CHOICE:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    choice = get_object_or_404(Choice, id=choice_id)
                    response.selected_choices.add(choice)
                    total_score += choice.score
            elif question.question_type == Question.MULTIPLE_CHOICE:
                choice_ids = request.POST.getlist(f'question_{question.id}')
                choices = Choice.objects.filter(id__in=choice_ids)
                response.selected_choices.set(choices)
                total_score += sum(choice.score for choice in choices)

            response.score = response.total_score()
            response.save()

        normalized_score = calculate_normalized_score(total_score, max_possible_score)
        request.session['assessment_score'] = normalized_score
        request.session['new_assessment_completed'] = True
        return redirect('assessment_result')
    
    questions = Question.objects.all()
    return render(request, 'assessment/take_assessment.html', {'questions': questions})

@login_required
def assessment_result(request):
    responses = UserResponse.objects.filter(user=request.user).order_by('-submitted_at')
    
    # Calculate total score
    total_score = sum(
        sum(choice.score for choice in response.selected_choices.all())
        for response in responses
    )
    
    # Get the normalized score from the session
    normalized_score = request.session.get('assessment_score', 0)

    # Determine result based on normalized score
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
            # ... (other recommendations)
        ]

    if request.session.pop('new_assessment_completed', False):
        AssessmentHistory.objects.create(
            user=request.user,
            score=normalized_score,
            result_text=result['text'],
        )

    # Prepare data for charts
    question_texts = [response.question.text for response in responses]
    scores = [
        sum(choice.score for choice in response.selected_choices.all())
        for response in responses
    ]

    context = {
        'result': result,
        'recommendations': recommendations,
        'question_texts': question_texts,
        'total_score': total_score,
        'scores': scores,
        'normalized_score': normalized_score
    }
    
    return render(request, 'assessment/assessment_result.html', context)
@login_required
def generate_certificate(request):
    user = request.user
    normalized_score = request.session.get('assessment_score', 0)
    result = get_result_data(normalized_score)

    pdf_content = generate_certificate_pdf(user, normalized_score, result)

    history_entry, _ = AssessmentHistory.objects.get_or_create(
        user=user,
        score=normalized_score,
        result_text=result['text'],
        score_color=result['color'],
    )

    certificate_filename = f'certificate_{user.username}_{history_entry.id}.pdf'
    history_entry.certificate.save(certificate_filename, ContentFile(pdf_content), save=True)

    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{certificate_filename}"'
    return response

def search_view(request):
    query = request.GET.get('q', '')
    words = query.split()
    
    results = Question.objects.filter(
        Q(text__icontains=query) | 
        Q(choices__text__icontains=query)
    ).distinct() if words else []

    context = {'query': query, 'results': results}
    return render(request, 'search/search_results.html', context)

def question_detail_view(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question, 'choices': question.choices.all()}
    return render(request, 'search/question_detail.html', context)

@login_required
def assessment_history(request):
    history = AssessmentHistory.objects.filter(user=request.user)
    return render(request, 'assessment/assessment_history.html', {'history': history})