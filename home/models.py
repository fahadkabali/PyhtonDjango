from django.db import models
from django.contrib.auth.models import User

from CSAT import settings

class Question(models.Model):
    SINGLE_CHOICE = 'SC'
    MULTIPLE_CHOICE = 'MC'
    OPEN_ENDED = 'OE'

    QUESTION_TYPES = [
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (OPEN_ENDED, 'Open Ended'),
    ]

    text = models.TextField()
    question_type = models.CharField(
        max_length=2,
        choices=QUESTION_TYPES,
        default=SINGLE_CHOICE,
    )

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.text} ({self.percentage}%)"

class Response(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    open_ended_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Response to {self.question.text} by {self.user.username}"

    def calculate_score(self):
        if self.question.question_type == Question.SINGLE_CHOICE:
            if self.selected_choices.exists():
                return self.selected_choices.first().percentage or 0
        elif self.question.question_type == Question.MULTIPLE_CHOICE:
            return sum(choice.percentage for choice in self.selected_choices.all())
        return 0

def calculate_total_score(responses):
    total_score = sum(response.calculate_score() for response in responses)
    return total_score

def get_feedback(score):
    if score > 80:
        return "Advanced"
    elif 60 < score <= 80:
        return "Average"
    elif 40 < score <= 60:
        return "Basic"
    else:
        return "Weak"
