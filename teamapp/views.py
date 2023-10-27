from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Project, StudentProject, Invitation, Student


def home(request):
    return HttpResponse("Site is under construction!")


# Create your views here.
def start_iteration(request, id):

    project = Project.objects.get(id=id)

    # Получим всех студентов, которые соответствуют рангу проекта
    eligible_students = Student.objects.filter(rank=project.rank)

    # Получим всех студентов, которые уже связаны с этим проектом
    existing_students = StudentProject.objects.filter(project=project).values_list('student', flat=True)

    # Уберем из списка приглашаемых студентов тех, кто уже связан с проектом
    students_to_invite = eligible_students.exclude(id__in=existing_students)

    # Определим дату, начиная с которой мы хотим рассматривать приглашения
    one_month_ago = timezone.now().date() - timedelta(days=30)

    # Отбросим студентов, которые получали приглашения в течение последнего месяца
    recent_invitations = Invitation.objects.filter(
        student__in=students_to_invite,
        invitation_date__gte=one_month_ago
    ).values_list('student', flat=True)
    students_to_invite = students_to_invite.exclude(id__in=recent_invitations)

    # Создадим приглашение для каждого студента
    for student in students_to_invite:
        Invitation.objects.create(
            project=project,
            student=student,
            invitation_date=timezone.now().date()
        )

    return HttpResponseRedirect("/admin/teamapp/project/")
