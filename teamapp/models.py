from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.urls import reverse
from django.dispatch import receiver
from .tasks import send_invitation_task


class ProjectManager(User):
    # name = models.CharField(verbose_name='Имя', max_length=20)  ## Дублируют  first_name и last_name
    # surname = models.CharField(verbose_name='Фамилия', max_length=20) ## Дублируют  first_name и last_name
    start_time = models.TimeField(verbose_name='Время начала рабочего дня')
    end_time = models.TimeField(verbose_name='Время конца рабочего дня')
    telegram = models.CharField(verbose_name='Телеграм', max_length=70, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.start_time}-{self.end_time}'

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
    # name = models.CharField(max_length=20, verbose_name='Имя') ## Дублируют  first_name и last_name
    # surname = models.CharField(max_length=20, verbose_name='Фамилия') ## Дублируют  first_name и last_name
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE, verbose_name='Уровень ученика',
                             related_name='student_ranks')
    # mail = models.CharField(max_length=70, verbose_name='Электронная почта') ## Дублируют
    telegram = models.CharField(max_length=70, verbose_name='Телеграм', blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.rank})'

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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class TimeSlot(models.Model):
    # Модель используется для хранения временных интервалов
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.start_time} - {self.end_time}'


class StudentAvailability(models.Model):
    # Модель используется для определения доступности разных периодов для созвонов
    # Хранит периоды которые ученик выбрал возможными для текущего проекта

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'time_slot', 'project')

    def __str__(self):
        return f'{self.student.username} - {self.time_slot}'


class StudentProject(models.Model):
    # Модель используется для отслеживания, в каких проектах участвовал ученик
    # что бы в дальнейшем, не отправлять ему повторного приглашения на тот же проект

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'project',)

    def __str__(self):
        return f'{self.student.username} - {self.project.title}'


class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)
    meeting_time = models.TimeField(verbose_name='Время ежедневных созвонов')
    start_date = models.DateField(verbose_name='День начала проекта')
    project_manager = models.ForeignKey(ProjectManager, on_delete=models.CASCADE, verbose_name='Менеджер',
                                        related_name='team_managers')
    info = models.TextField(verbose_name='Описание проекта', max_length=200)

    def __str__(self):
        return f'{self.project} - {self.project_manager} - {self.start_date} - {self.meeting_time}'

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class Invitation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Проект')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Ученик',
                                related_name='invite_students')
    # is_sent = models.BooleanField(default=False, verbose_name='Отправлено')

    def __str__(self):
        return f'{self.project} {self.student}'

    class Meta:
        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашения'


@receiver(post_save, sender=Invitation)
def trigger_new_invitation(sender, instance, created, **kwargs):
    if created:
        send_invitation_task.delay(instance.id)


'''
class FreeTimeTable(models.Model):
    time = models.TimeField(verbose_name='Слот свободного времени', db_index=True)
    count = models.IntegerField(verbose_name='Количество слотов', default=0)
    week = models.IntegerField(verbose_name='Номер недели')

    def __str__(self):
        if self.count:
            return f'{self.week} неделя. На {self.time} есть {self.count} слот(-а).'
        else:
            return f'{self.week} неделя. На {self.time} нет слотов'

    class Meta:
        ordering = ['week', 'time']
        verbose_name = 'Слот свободного времени'
        verbose_name_plural = 'Слоты свободных времен'



class Account(models.Model):
    login = models.CharField(verbose_name='Логин', max_length=20)
    password = models.CharField(verbose_name='Пароль', max_length=20)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True, verbose_name='Пользователь',
                                   related_name='students')

# '''