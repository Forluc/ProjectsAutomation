import os
from dotenv import load_dotenv
from .models import Project, ProjectManager, Rank, Student, Invitation, Team
import requests
import json


load_dotenv()
trello_token = os.environ["TRELLO_TOKEN"]
trello_key = os.environ["TRELLO_API_KEY"]


def create_workspace(name, desc):
    header = {'key': trello_key, 'token': trello_token, 'displayName': name, 'desc':desc}
    response = requests.post('https://api.trello.com/1/organizations', header)
    response.raise_for_status()
    return response


def create_board(name, desc, id_organization):
    header = {'key': trello_key, 'token': trello_token, 'name': name, 'desc':desc, "idOrganization":id_organization}
    response = requests.post('https://api.trello.com/1/boards', header)
    response.raise_for_status()
    #print(response.text)
    return response


def delete_workspace(id):
    url = f"https://api.trello.com/1/organizations/{id}"
    query = {'key': trello_key,
            'token': trello_token
            }
    response = requests.request("DELETE", url, params=query)
    response.raise_for_status()


'''
projects = Project.objects.all()
for project in projects:
    id_workspace = create_workspace(f"Проект {project.name} {project.week}", project.description).json()["id"]
    create_board(f"11:30-11:50 Вася, Петя", "123", id_workspace)

# '''
