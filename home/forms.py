# from django import forms
# from .models import Question, Choice, UserResponse

# class ResponseForm(forms.ModelForm):
#     class Meta:
#         model = UserResponse
#         fields = ['selected_choices']
#         widgets = {
#             'selected_choices': forms.CheckboxSelectMultiple,
#         }

#     def __init__(self, *args, **kwargs):
#         question = kwargs.pop('question')
#         super().__init__(*args, **kwargs)
#         if question.question_type == Question.SINGLE_CHOICE:
#             self.fields['selected_choices'].widget = forms.RadioSelect()
#             self.fields['selected_choices'].queryset = question.choices.all()
#         else:
#             question.question_type == Question.MULTIPLE_CHOICE
#             self.fields['selected_choices'].queryset = question.choices.all()

#     def clean(self):
#         cleaned_data = super().clean()
#         if self.instance.question.question_type in [Question.SINGLE_CHOICE, Question.MULTIPLE_CHOICE]:
#             if not cleaned_data.get('selected_choices'):
#                 raise forms.ValidationError('You must select at least one choice.')
#         return cleaned_data

# forms.py

from django import forms
from .models import Question, Choice, UserResponse

class ResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for question in Question.objects.prefetch_related('choices'):
            if question.question_type == Question.SINGLE_CHOICE:
                self.fields[f'question_{question.id}'] = forms.ModelChoiceField(
                    queryset=question.choices.all(),
                    widget=forms.RadioSelect,
                    required=True
                )
            else:
                self.fields[f'question_{question.id}'] = forms.ModelMultipleChoiceField(
                    queryset=question.choices.all(),
                    widget=forms.CheckboxSelectMultiple,
                    required=False
                )
    
    def save_response(self, user, question):
        field_name = f'question_{question.id}'
        if field_name in self.cleaned_data:
            choices = self.cleaned_data[field_name]
            if choices:
                response = UserResponse.objects.create(user=user, question=question)
                if isinstance(choices, Choice):  # Single choice
                    response.selected_choices.add(choices)
                else:  # Multiple choices
                    response.selected_choices.add(*choices)
                return response
        return None