from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Project


def get_week_choices():
    # Формируем список из дат начала недели

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['week'].choices = get_week_choices()

    def clean_week(self):
        # Если раньше были сохранены недели
        # которые сегодня уже остались в прошлом - удалим их

        week = self.cleaned_data.get('week')
        cleaned_week = []
        for date_str in week:
            date = datetime.strptime(date_str, '%d-%m-%Y').date()
            if date >= timezone.now().date():
                cleaned_week.append(date_str)
        return cleaned_week

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class WeekSelectForm(forms.Form):
    # Форма для выбора недели который будет предоставлен в приглашении

    week = forms.ChoiceField(choices=[], widget=forms.RadioSelect, label="")

    def __init__(self, weeks, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['week'].choices = [(i, week) for i, week in enumerate(weeks)]


class TimeSelectForm(forms.Form):
    # Форма для выбора недели который будет предоставлен в приглашении

    time = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple, label="")

    def __init__(self, week, times, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time'].choices = [(i, time) for i, time in enumerate(times)]
