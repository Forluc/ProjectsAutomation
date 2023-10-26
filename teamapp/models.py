from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_invitation_task


class ProjectManager(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=20)
    surname = models.CharField(verbose_name='Фамилия', max_length=20)
    start_time = models.TimeField(verbose_name='Время начала рабочего дня')
    end_time = models.TimeField(verbose_name='Время конца рабочего дня')
    telegram = models.CharField(verbose_name='Телеграм', max_length=70, blank=True)

    def __str__(self):
        return f'{self.name} {self.surname} {self.start_time}-{self.end_time}'

    class Meta:
        verbose_name = 'Менеджер'
        verbose_name_plural = 'Менеджеры'


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


class Rank(models.Model):
    name = models.CharField(verbose_name='Уровень ученика', max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Уровень знания'
        verbose_name_plural = 'Уровни знаний'


class Student(models.Model):
    name = models.CharField(max_length=20, verbose_name='Имя')
    surname = models.CharField(max_length=20, verbose_name='Фамилия')
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE, verbose_name='Уровень ученика',
                             related_name='student_ranks')
    mail = models.CharField(max_length=70, verbose_name='Электронная почта')
    telegram = models.CharField(max_length=70, verbose_name='Телеграм', blank=True)
    time = models.ForeignKey(FreeTimeTable, on_delete=models.SET_NULL, verbose_name='Время созванивания в проекте',
                             related_name='times', null=True)

    def __str__(self):
        return f'{self.name} {self.surname} {self.rank} {self.time}'

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'


class Account(models.Model):
    login = models.CharField(verbose_name='Логин', max_length=20)
    password = models.CharField(verbose_name='Пароль', max_length=20)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True, verbose_name='Пользователь',
                                   related_name='students')


class Project(models.Model):
    name = models.CharField(verbose_name='Название проекта', max_length=20)
    description = models.TextField(verbose_name='Описание проекта', max_length=20)
    time = models.TimeField(verbose_name='Время для созванивания')
    week = models.IntegerField(verbose_name='Номер недели')
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE, verbose_name='Уровень ученика',
                             related_name='project_ranks')
    project_manager = models.ManyToManyField(ProjectManager, verbose_name='Менеджер')

    def __str__(self):
        return f'{self.name}. Время проведения {self.time}. Неделя в месяце{self.week}. {self.rank}'

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE, null=True)
    time = models.ForeignKey(FreeTimeTable, on_delete=models.CASCADE, verbose_name='Время созванивания')
    project_manager = models.ForeignKey(ProjectManager, on_delete=models.CASCADE, verbose_name='Менеджер',
                                        related_name='team_managers')
    first_student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Первый ученик',
                                      related_name='first_students')
    second_student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Второй ученик',
                                       related_name='second_students')
    third_student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Третий ученик',
                                      related_name='third_students')
    is_full = models.BooleanField(default=False, verbose_name='Полная команда')

    def __str__(self):
        return f'{self.time} {self.project_manager} {self.is_full}'

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class Invitation(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='Команда', related_name='teams')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Ученик',
                                related_name='invite_students')
    is_sent = models.BooleanField(default=False, verbose_name='Отправлено')

    def __str__(self):
        return f'{self.team} {self.student} {self.is_sent}'

    class Meta:
        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашения'


@receiver(post_save, sender=Invitation)
def trigger_new_invitation(sender, instance, created, **kwargs):
    if created:
        send_invitation_task.delay(instance.id)
