from django.utils.html import format_html
from django.utils.text import slugify
from django.contrib import admin
from .models import Project, ProjectManager, Rank, Student, Invitation
from .forms import ProjectForm


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')
    list_filter = ('week', 'rank', 'project_manager')
    form = ProjectForm

    list_display = ('name', 'description', 'student_count', 'week', 'rank', 'students_not_invited', 'get_iteration_link')

    def get_iteration_link(self, obj):
        url = f"/admin/start-iteration/{slugify(obj.id)}"
        return format_html('<a href="{}">Запустить интерацию</a>', url)
    get_iteration_link.short_description = 'Запустить интерацию'


@admin.register(ProjectManager)
class ProjectManagerAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'start_time', ]


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    pass


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'rank', 'mail', ]
    raw_id_fields = ['rank']


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    raw_id_fields = ['student', 'project']


'''

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    raw_id_fields = ['time', 'project_manager', 'first_student', 'second_student', 'third_student', ]


@admin.register(FreeTimeTable)
class FreeTimeTableAdmin(admin.ModelAdmin):
    search_fields = ['week', ]


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    raw_id_fields = ['rank', ]
    search_fields = ['name', ]
    filter_horizontal = ['project_manager']

# '''
