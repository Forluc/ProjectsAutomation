"""
URL configuration for ProjectsAutomation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from teamapp.views import (
    home,
    iteration_starter, vote_resolver,
    project_view, week_select_view, time_select_view
)

urlpatterns = [
    path('project/<int:project_id>/week_select/', week_select_view, name='week_select'),
    path('project/<int:project_id>/time_select/<int:week>/', time_select_view, name='time_select'),
    path('project/<int:project_id>/vote_resolve/<int:week>/<str:vote>/', vote_resolver, name='vote_resolve'),
    path('project/<int:id>', project_view, name='project-view'),
    path('admin/start-iteration/<int:id>', iteration_starter, name='start-iteration'),
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]
