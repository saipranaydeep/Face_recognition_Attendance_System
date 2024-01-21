from django.contrib import admin
from .models import Student,Faculty,Course,Degree

admin.site.register({Student,Faculty,Degree,Course})

