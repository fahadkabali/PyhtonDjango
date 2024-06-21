from django import forms
from .models import Question, Choice, Response

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['selected_choices', 'open_ended_response']
        widgets = {
            'selected_choices': forms.CheckboxSelectMultiple,
            'open_ended_response': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        if question.question_type == Question.SINGLE_CHOICE:
            self.fields['selected_choices'].widget = forms.RadioSelect()
            self.fields['selected_choices'].queryset = question.choices.all()
        elif question.question_type == Question.MULTIPLE_CHOICE:
            self.fields['selected_choices'].queryset = question.choices.all()
        else:
            self.fields['selected_choices'].required = False
            self.fields['open_ended_response'].required = True

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.question.question_type in [Question.SINGLE_CHOICE, Question.MULTIPLE_CHOICE]:
            if not cleaned_data.get('selected_choices'):
                raise forms.ValidationError('You must select at least one choice.')
        return cleaned_data
