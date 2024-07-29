from django.db import models
from django.contrib.auth.models import User

from CSAT import settings
from django.conf import settings



class Question(models.Model):
    SINGLE_CHOICE = 'SC'
    MULTIPLE_CHOICE = 'MC'
    # OPEN_ENDED = 'OE'

    QUESTION_TYPES = [
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        # (OPEN_ENDED, 'Open Ended'),
    ]

    text = models.TextField()
    question_type = models.CharField(
        max_length=2,
        choices=QUESTION_TYPES,
        default=SINGLE_CHOICE,
    )
    max_score = models.IntegerField()

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    score = models.IntegerField()
    
    def __str__(self):
        return self.text

class UserResponse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    # open_ended_response = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def total_score(self):
        return sum([choice.score for choice in self.selected_choices.all()])

class AssessmentHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.FloatField()
    result_text = models.CharField(max_length=20)
    date_taken = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_taken']

    def __str__(self):
        return f"{self.user.username} - {self.score} - {self.date_taken}"