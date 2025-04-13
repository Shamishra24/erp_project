from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Department
from erp_core.models import Department
from django.shortcuts import render, redirect

Department.objects.create(name="Computer Science", code="CS")
Department.objects.create(name="Electrical Engineering", code="EE")

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    roll_number = forms.CharField(required=True, max_length=20)
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    admission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                 'password1', 'password2', 'roll_number',
                 'department', 'admission_date', 'phone')
        


class FacultyRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    employee_id = forms.CharField(required=True, max_length=20)
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    designation = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'password1', 'password2', 'employee_id', 
                 'department', 'designation')
        