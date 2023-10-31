from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_invitation_task


class ProjectManager(User):
    start_time = models.TimeField(verbose_name='Время начала рабочего дня')
    end_time = models.TimeField(verbose_name='Время конца рабочего дня')
    telegram = models.CharField(verbose_name='Телеграм', max_length=70, blank=True)

    def __str__(self):
        return f'{self.username} ({self.start_time}-{self.end_time})'

    class Meta:
        verbose_name = 'Менеджер'
        verbose_name_plural = 'Менеджеры'


class Rank(models.Model):
    name = models.CharField(verbose_name='Уровень ученика', max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Уровень знания'
        verbose_name_plural = 'Уровни знаний'


class Student(User):
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE, verbose_name='Уровень ученика',
                             related_name='student_ranks')
    telegram = models.CharField(max_length=70, verbose_name='Телеграм', blank=True)

    def __str__(self):
        return f'{self.username} {self.first_name} {self.last_name} ({self.rank})'

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'


class Project(models.Model):
    name = models.CharField(verbose_name='Название проекта', max_length=20)
    description = models.TextField(verbose_name='Описание проекта', max_length=200)
    student_count = models.IntegerField(verbose_name='Размер группы')
    week = models.JSONField(blank=True, default=list, verbose_name='Недели')
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE, verbose_name='Уровень ученика',
                             related_name='project_ranks')
    project_manager = models.ManyToManyField(ProjectManager, verbose_name='Менеджер')

    def students_not_invited(self):
        one_month_ago = timezone.now() - timedelta(days=30)
        students_not_invited_count = Student.objects.filter(rank=self.rank).exclude(
            invite_students__invitation_date__gt=one_month_ago,
            invite_students__project=self
        ).count()

        return students_not_invited_count
    students_not_invited.short_description = 'Без приглашений'

    def get_ungrouped_students(self):
        grouped_students = Team.objects.filter(project=self).values_list('students', flat=True)
        ungrouped_students = Student.objects.filter(rank=self.rank).exclude(id__in=grouped_students)
        return ungrouped_students

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class StudentVote(models.Model):
    # Модель используется для определения доступности разных периодов для созвонов
    # Хранит периоды которые ученик выбрал возможными для текущего проекта

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    time_slot = models.JSONField(default=list, verbose_name='Подходящее время')
    week = models.CharField(verbose_name='Дата начала', max_length=20)
    vote_date = models.DateField(verbose_name='Дата выбора')

    class Meta:
        unique_together = ('student', 'project')
        verbose_name = 'Выбор Студентов'
        verbose_name_plural = 'Выбор Студентов'

    def __str__(self):
        return f'{self.project} - {self.student.username} - {self.time_slot}'


class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)
    meeting_time = models.TimeField(verbose_name='Время ежедневных созвонов')
    start_date = models.DateField(verbose_name='День начала проекта')
    project_manager = models.ForeignKey(ProjectManager, on_delete=models.CASCADE, verbose_name='Менеджер',
                                        related_name='team_managers')
    info = models.TextField(verbose_name='Командная инфа', max_length=200, blank=True)

    def __str__(self):
        return f'{self.project} - {self.project_manager.username} ({self.start_date} | {self.meeting_time})'

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class Invitation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Проект')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Ученик',
                                related_name='invite_students')
    invitation_date = models.DateField(verbose_name='Дата последнего уведомления')

    def __str__(self):
        return f'{self.project} {self.student}'

    class Meta:
        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашения'


'''
# Для внешней рассылки
@receiver(post_save, sender=Invitation)
def trigger_new_invitation(sender, instance, created, **kwargs):
    if created:
        send_invitation_task.delay(instance.id)

# '''
