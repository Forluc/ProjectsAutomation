from django import forms
from datetime import datetime, timedelta
from .models import Project


def get_week_choices():
    choices = []
    for i in range(1, 7):  # Следующие шесть недель
        start_date = datetime.now() + timedelta(weeks=i)
        # week_number = start_date.isocalendar()[1]
        # choices.append((week_number, start_date.strftime('%Y-%m-%d')))
        start_date_str = start_date.strftime('%d-%m-%Y')
        choices.append((start_date_str, start_date_str))
    return choices


class ProjectForm(forms.ModelForm):
    week = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'size': 6}),
        choices=get_week_choices,
        label="Недели"
    )

    class Meta:
        model = Project
        fields = ('name', 'description', 'student_count', 'week', 'rank', 'project_manager')

    def clean_weeks(self):
        week = self.cleaned_data.get('week')
        return week

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
