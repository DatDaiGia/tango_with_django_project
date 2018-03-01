from django.http import HttpResponse
from django.shortcuts import render

def home(HttpRequest):
  context = {'variable_name': 'Im a newbie with Django'}
  return render(HttpRequest, 'tango_with_django_project/home.html', context)
