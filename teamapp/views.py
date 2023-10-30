from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Project, StudentProject, Invitation, Student, StudentAvailability
from .forms import WeekSelectForm, TimeSelectForm


def home(request):
    return HttpResponse("Site is under construction!")


# Create your views here.
def iteration_starter(request, id):

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


def week_select_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = WeekSelectForm(data=request.POST, weeks=project.week)
        if form.is_valid():
            week = form.cleaned_data['week']
            return redirect('time_select', project_id=project_id, week=week)
    else:
        form = WeekSelectForm(weeks=project.week)
    return render(request, 'project_week_select.html', {'project': project, 'form': form})


def get_available_times(project_id, week, interval_minutes=60):
    project = Project.objects.get(id=project_id)
    project_managers = project.project_manager.all()
    available_times = []

    # Проходим по каждому менеджеру
    for manager in project_managers:
        start_time = datetime.combine(datetime.today(), manager.start_time)
        end_time = datetime.combine(datetime.today(), manager.end_time)

        while start_time < end_time:
            # Добавляем время начала в список доступных времен
            available_times.append(start_time.time().strftime("%H:%M"))

            # Увеличиваем время начала на заданный интервал
            start_time += timedelta(minutes=interval_minutes)

    # Избавляемся от дубликатов и сортируем список времен
    available_times = sorted(list(set(available_times)))

    return available_times


def time_select_view(request, project_id, week):

    project = get_object_or_404(Project, id=project_id)
    week_date = project.week[int(week)]

    available_times = get_available_times(project_id, week)  # функция, которую нужно реализовать
    if request.method == 'POST':
        form = TimeSelectForm(data=request.POST, week=week_date, times=available_times)
        if form.is_valid():
            time = form.cleaned_data['time']
            return redirect('vote_resolve', project_id=project_id, week=week, vote=time)
    else:
        form = TimeSelectForm(week=week_date, times=available_times)
    return render(request, 'project_time_select.html', {'project': project, 'form': form, 'week': week_date})


def vote_resolver(request, project_id, week, vote):
    import ast

    project = get_object_or_404(Project, id=project_id)
    week_date = project.week[int(week)]
    available_times = get_available_times(project_id, week)
    user = request.user

    vote_list = ast.literal_eval(vote)
    vote_values = [available_times[int(index)] for index in vote_list]

    print(request)
    print(user)
    print(project)
    print(week_date)
    print(vote_values)
    return HttpResponseRedirect("/admin/teamapp/project/")


def project_view(request, id):
    student = request.user
    print(student)

    # Проверяем, выбирал ли пользователь время в последние 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_availability = StudentAvailability.objects.filter(
        student=student,
        project_id=id,
        vote_date__gte=thirty_days_ago
    )

    if not recent_availability.exists():
        return redirect('week_select', project_id=id)

    '''
    project = Project.objects.get(id=id)
    context = {
        'project': project,
    }

    # return render(request, 'project_view.html', context=context)
    return week_render
    # '''
