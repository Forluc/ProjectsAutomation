from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta, datetime
from .forms import WeekSelectForm, TimeSelectForm, StudentRegisterForm, LoginForm
from .models import Project, Invitation, Student, StudentVote, Team, StudentProject, StudentAvailability
from .trello import create_workspace, create_board


@login_required(login_url='/login/')
def home(request):
    user = request.user
    today = timezone.now().date()

    # Приглашения на проекты, по которым студент еще не в команде
    invitations = Invitation.objects.filter(student=user).exclude(project__team__students=user)

    # Проекты, по которым студент состоит в команде, но дата начала проекта раньше сегодня, но не более чем на 10 дней
    days_past = today - timedelta(days=10)
    current_projects = Team.objects.filter(students=user, start_date__gt=days_past)

    # Проекты, по которым студент состоит в команде, но дата начала проекта раньше сегодня более чем на 10 дней
    finished_projects = Team.objects.filter(students=user, start_date__lt=days_past)

    context = {
        'invitations': invitations,
        'current_projects': current_projects,
        'finished_projects': finished_projects,
    }

    messages.success(request, 'Вы успешно вошли в систему.')
    return render(request, "main_page.html", context)


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('/login/')


def register(request):
    if request.method == "POST":
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
    else:
        form = StudentRegisterForm()
    return render(request, "registration/register.html", {"form": form})


# Create your views here.
def iteration_starter(request, id):

    project = Project.objects.get(id=id)

    # Получим всех студентов, которые соответствуют рангу проекта
    eligible_students = Student.objects.filter(rank=project.rank)

    # Получим всех студентов, которые уже связаны с этим проектом
    existing_students = Team.objects.filter(project=project).values_list('students__id', flat=True)

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


def get_available_times(project_id, week, interval_minutes=30):
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

    # Преобразовываем week из строки 'DD-MM-YYYY' в объект date
    week_date = project.week[int(week)]
    week_date = datetime.strptime(week_date, "%d-%m-%Y").date()

    # Собираем список всех команд, сформированных каждым менеджером проекта и на данную дату начала проекта
    # И сводим в список все занятые часы для созвонов
    for manager in project_managers:
        teams = Team.objects.filter(project_manager=manager, start_date=week_date)
        booked_times = [team.meeting_time.strftime("%H:%M") for team in teams]

        # Вычитаем собранный список из available_times
        for booked_time in booked_times:
            if booked_time in available_times:
                available_times.remove(booked_time)

    # Избавляемся от дубликатов и сортируем список времен
    available_times = sorted(list(set(available_times)))

    return available_times


def get_free_project_manager(project_id, week, meeting_time):
    project = Project.objects.get(id=project_id)
    # Преобразование строки времени в объект datetime.time
    meeting_time_obj = datetime.strptime(meeting_time, '%H:%M').time()

    # Получаем всех менеджеров проекта
    project_managers = project.project_manager.all()

    # Преобразовываем week из строки 'DD-MM-YYYY' в объект date
    week_date = project.week[int(week)]
    week_date = datetime.strptime(week_date, "%d-%m-%Y").date()

    for manager in project_managers:
        # Проверяем, свободен ли менеджер в это время
        if manager.start_time <= meeting_time_obj <= manager.end_time:
            # Проверяем, запланированы ли у менеджера другие совещания в это время
            other_teams = Team.objects.filter(project_manager=manager, start_date=week_date, meeting_time=meeting_time)
            if not other_teams.exists():
                return manager

    # Если свободный менеджер не найден, возвращаем None
    return None


def time_select_view(request, project_id, week):

    project = get_object_or_404(Project, id=project_id)
    week_date = project.week[int(week)]

    available_times = get_available_times(project_id, week)  # функция, которую нужно реализовать
    if request.method == 'POST':
        form = TimeSelectForm(data=request.POST, times=available_times)
        if form.is_valid():
            time = form.cleaned_data['time']
            return redirect('vote_resolve', project_id=project_id, week=week, vote=time)
    else:
        form = TimeSelectForm(times=available_times)
    return render(request, 'project_time_select.html', {'project': project, 'form': form, 'week': week_date})


def vote_resolver(request, project_id, week, vote):
    import ast
    from collections import Counter

    project = get_object_or_404(Project, id=project_id)
    week_date = project.week[int(week)]
    week_date_str = datetime.strptime(week_date, "%d-%m-%Y").date()
    available_times = get_available_times(project_id, week)
    user = request.user

    # Преобразование строки в список
    vote_list = ast.literal_eval(vote)
    vote_values = [available_times[int(index)] for index in vote_list]

    is_student = False
    try:
        student = user.student
        is_student = True
    except ObjectDoesNotExist:
        messages.error(request, "User is not a student.")

    if is_student:
        # Создание нового объекта StudentVote
        try:
            StudentVote.objects.create(
                student=student,
                project=project,
                time_slot=vote_values,
                week=week_date,
                vote_date=timezone.now().date(),
            )
            messages.success(request, "Выбор был принят")
            print("Выбор был принят")
        except Exception as e:
            messages.error(request, f"Произошла ошибка при обработке выбора: {str(e)}")
            print(f"Произошла ошибка при обработке выбора: {str(e)}")

    # Считаем голоса тех у кого ещё нет группы
    ungrouped_students = project.get_ungrouped_students()
    votes = StudentVote.objects.filter(student__in=ungrouped_students, project=project, week=week_date)
    all_vote_values = [time for vote in votes for time in vote.time_slot]
    counter = Counter(all_vote_values)

    # Получаем самый популярный голос
    most_common_time_slot, most_common_count = counter.most_common()[0]

    if most_common_count >= project.student_count:
        project_manager = get_free_project_manager(project_id, week, most_common_time_slot)
        team = Team.objects.create(
            project=project,
            meeting_time=most_common_time_slot,
            start_date=week_date_str,
            project_manager=project_manager,
            info=''
            )

        # Получим список студентов, которые выбрали самый распространенный временной интервал
        collected_students = [
            vote.student for vote in votes if most_common_time_slot in vote.time_slot
        ]
        # Добавляем этих студентов в команду
        team.students.add(*collected_students)

    return HttpResponseRedirect("/")


def project_view(request, id):
    student = request.user
    project = get_object_or_404(Project, id=id)

    # Проверяем, выбирал ли Студент время в последние 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_availability = StudentVote.objects.filter(
        student=student,
        project_id=id,
        vote_date__gte=thirty_days_ago
        )
    
    # Проверяем, является ли Студент частью команды для этого проекта
    is_part_of_team = Team.objects.filter(project_id=id, students=student).exists()

    if not recent_availability.exists() and not is_part_of_team:
        return redirect('week_select', project_id=id)

    # Если Студент проголосовал, но ещё не набралась команда
    if recent_availability.exists() and not is_part_of_team:
        vote = StudentVote.objects.get(student=student, project_id=id)
        context = {
            'project': project,
            'team': is_part_of_team,
            'vote': vote.time_slot,
            'week': vote.week,
            }
        return render(request, "project_view.html", context)

    # Если Студент в команде
    if is_part_of_team:
        current_team = Team.objects.get(project_id=id, students=student)
        context = {
            'project': project,
            'team': is_part_of_team,
            'current_team': current_team,
            }
        return render(request, "project_view.html", context)
      
    '''
    project = Project.objects.get(id=id)
    context = {
        'project': project,
    }

    # return render(request, 'project_view.html', context=context)
    return week_render
    # '''


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

