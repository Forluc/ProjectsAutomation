from django.utils.html import format_html
from django.utils.text import slugify
from django.contrib import admin
from .models import (
    Project, ProjectManager, Rank,
    Student, Invitation, Team, StudentVote
    )
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

    
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass
  
  
@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    pass

  
@admin.register(StudentVote)
class StudentVoteAdmin(admin.ModelAdmin):
    raw_id_fields = ['student', 'project']
    list_display = ['project', 'week', 'student', 'time_slot']
    list_filter = ['project', 'student']
