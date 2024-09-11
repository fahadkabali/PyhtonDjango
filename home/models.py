from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
import os
from CSAT import settings
from django.conf import settings


User = get_user_model()
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
    max_score = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    
    def __str__(self):
        return self.text

class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    # open_ended_response = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def total_score(self):
        return sum([choice.score for choice in self.selected_choices.all()])


def certificate_upload_path(instance, filename):
    return f'certificates/user_{instance.user.id}/{filename}'

class AssessmentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    result_text = models.CharField(max_length=20)
    score_color = models.CharField(max_length=20)
    date_taken = models.DateTimeField(auto_now_add=True)
    certificate = models.FileField(upload_to= certificate_upload_path, null=True, blank=True)


    class Meta:
        ordering = ['-date_taken']

    def __str__(self):
        return f"{self.user.username} - {self.score}% ({self.date_taken})"
    
    # def delete(self, *args, **kwargs):
    #     if self.certificate:
    #         if os.path.isfile(self.certificate.path):
    #             os.remove(self.certificate.path)
    #     super(AssessmentHistory, self).delete(*args, **kwargs)