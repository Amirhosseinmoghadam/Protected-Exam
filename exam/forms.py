# forms.py
from django.utils.timezone import now

from django import forms
from .models import Answer


class ExamForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.questions = kwargs.pop('questions', [])
        super().__init__(*args, **kwargs)

        # Iterate over the questions and create a ChoiceField (radio buttons) for each
        for question in self.questions:
            choices = [
                ('a', question['a']),
                ('b', question['b']),
                ('c', question['c']),
                ('d', question['d']),
            ]
            choices = [(value, text) for value, text in choices if text]

            choice_field = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question['question'],
                required=False
            )
            self.fields[f'question_{question['id']}'] = choice_field

    def save(self, user, exam, start_time):
        answers = {}
        for field in self.cleaned_data:
            question_idx = int(field.split('_')[1])
            choice_value = self.cleaned_data[field]
            answers[question_idx] = choice_value

        Answer.objects.create(
            exam=exam,
            user=user,
            answer=answers,
            start_time=start_time,
            submit_time=now()
        )


