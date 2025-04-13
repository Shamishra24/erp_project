from django.contrib import admin
from .models import Department, Course, Student, Faculty, Attendance, Grade

admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Attendance)
admin.site.register(Grade)