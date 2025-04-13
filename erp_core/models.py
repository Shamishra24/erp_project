from django.db import models
from django.contrib.auth.models import User  # सिर्फ यही import रखें

# पहले Department को परिभाषित करें क्योंकि अन्य मॉडल इस पर निर्भर हैं
class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

# फिर Course मॉडल
class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    credits = models.IntegerField()
    
    def __str__(self):
        return self.name

# फिर Student मॉडल
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    admission_date = models.DateField()
    phone = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_number})"

# फिर Faculty मॉडल
class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.designation})"

# अंत में Attendance और Grade मॉडल
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.BooleanField(default=False)  # Present/Absent
    
    class Meta:
        unique_together = ('student', 'course', 'date')

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)
    semester = models.CharField(max_length=20)
    
    class Meta:
        unique_together = ('student', 'course', 'semester')