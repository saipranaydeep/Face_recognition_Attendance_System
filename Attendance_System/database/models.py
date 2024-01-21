from django.db import models
import os

class Student(models.Model):
    roll_no = models.CharField(max_length=9,null=False,blank=False, primary_key=True)
    name = models.CharField(max_length=50)
    Encodings = models.TextField(null=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Faculty(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.username

class Degree(models.Model):
    degree = models.CharField(max_length=10)
    years = models.CharField(max_length=50)
    branches = models.CharField(max_length=50)
    
    def __str__(self):
        return self.degree
    
class Course(models.Model):
    course = models.CharField(max_length=100)
    year = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    degree = models.CharField(max_length=50)
    student = models.ManyToManyField(Student, related_name='courses')
    def __str__(self):
        return self.course
