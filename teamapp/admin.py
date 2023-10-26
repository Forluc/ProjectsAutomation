from django.contrib import admin
from teamapp.models import Student, ProjectManager, Team, FreeTimeTable, Invitation, Rank, Project


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['name', 'surname', 'rank', 'mail', ]
    raw_id_fields = ['rank', 'time']


@admin.register(ProjectManager)
class ProjectManagerAdmin(admin.ModelAdmin):
    search_fields = ['name', 'surname', 'start_time', ]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    raw_id_fields = ['time', 'project_manager', 'first_student', 'second_student', 'third_student', ]


@admin.register(FreeTimeTable)
class FreeTimeTableAdmin(admin.ModelAdmin):
    search_fields = ['week', ]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    raw_id_fields = ['team', 'student']


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    raw_id_fields = ['rank', ]
    search_fields = ['name', ]
    filter_horizontal = ['project_manager']