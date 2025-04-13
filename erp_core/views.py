from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.sites import site
from django.template.loader import get_template
import datetime

from .models import Student, Faculty, Course, Attendance, Grade
from .forms import StudentRegistrationForm, FacultyRegistrationForm

def home(request):
    """Render the home page"""
    return render(request, 'erp_core/home.html')

def user_login(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            elif hasattr(user, 'faculty'):
                return redirect('faculty_dashboard')
            elif hasattr(user, 'student'):
                return redirect('student_dashboard')
            return redirect('home')
        messages.error(request, 'Invalid username or password')
    return render(request, 'erp_core/login.html')

@login_required
def user_logout(request):
    """Handle user logout"""
    logout(request)
    return redirect('home')

@staff_member_required
def admin_dashboard(request):
    """Admin dashboard view"""
    context = {
        'student_count': Student.objects.count(),
        'faculty_count': Faculty.objects.count(),
        'recent_students': Student.objects.order_by('-id')[:5]
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def faculty_dashboard(request):
    """Faculty dashboard view"""
    if not hasattr(request.user, 'faculty'):
        return redirect('home')
    return render(request, 'faculty/dashboard.html')

@login_required
def student_dashboard(request):
    """Student dashboard view"""
    if not hasattr(request.user, 'student'):
        messages.error(request, "No student profile found")
        return redirect('home')
    
    try:
        student = request.user.student
        context = {
            'student': student,
            'courses': Course.objects.filter(department=student.department),
            'attendance': Attendance.objects.filter(student=student).order_by('-date')[:10],
            'grades': Grade.objects.filter(student=student),
            'attendance_percentage': calculate_attendance_percentage(student),
        }
        return render(request, 'student/dashboard.html', context)
    except Exception as e:
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return redirect('home')

def calculate_attendance_percentage(student):
    """Calculate attendance percentage for a student"""
    total_classes = Attendance.objects.filter(student=student).count()
    if total_classes == 0:
        return 0
    present_classes = Attendance.objects.filter(student=student, status=True).count()
    return round((present_classes / total_classes) * 100, 2)

@login_required
def manage_attendance(request, course_id):
    """Manage attendance for a course"""
    course = get_object_or_404(Course, id=course_id)
    students = Student.objects.filter(department=course.department)
    
    if request.method == 'POST':
        date = request.POST.get('date')
        for student in students:
            status = request.POST.get(f'student_{student.id}') == 'on'
            Attendance.objects.update_or_create(
                student=student,
                course=course,
                date=date,
                defaults={'status': status}
            )
        messages.success(request, 'Attendance saved successfully')
        return redirect('manage_attendance', course_id=course.id)
    
    recent_attendance = Attendance.objects.filter(
        course=course,
        date__gte=datetime.date.today() - datetime.timedelta(days=7)
    ).order_by('-date')
    
    return render(request, 'faculty/attendance.html', {
        'course': course,
        'students': students,
        'recent_attendance': recent_attendance,
        'today': datetime.date.today().isoformat()
    })

@login_required
@require_http_methods(["POST"])
def mark_attendance_ajax(request):
    """Handle AJAX attendance marking"""
    try:
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')
        date = request.POST.get('date')
        status = request.POST.get('status') == 'true'
        
        student = Student.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)
        
        Attendance.objects.update_or_create(
            student=student,
            course=course,
            date=date,
            defaults={'status': status}
        )
        return JsonResponse({'success': True, 'message': 'Attendance updated'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def manage_grades(request, course_id):
    """Manage grades for a course"""
    course = get_object_or_404(Course, id=course_id)
    students = Student.objects.filter(department=course.department)
    semester = "Fall 2023"  # Should be dynamic in production
    
    if request.method == 'POST':
        for student in students:
            grade_value = request.POST.get(f'grade_{student.id}')
            if grade_value:
                Grade.objects.update_or_create(
                    student=student,
                    course=course,
                    semester=semester,
                    defaults={'grade': grade_value}
                )
        messages.success(request, 'Grades saved successfully')
        return redirect('manage_grades', course_id=course.id)
    
    existing_grades = {
        grade.student.id: grade.grade 
        for grade in Grade.objects.filter(course=course, semester=semester)
    }
    
    return render(request, 'faculty/grades.html', {
        'course': course,
        'students': students,
        'semester': semester,
        'existing_grades': existing_grades,
        'grade_choices': ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F']
    })

def register_student(request):
    """Handle student registration"""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Student.objects.create(
                user=user,
                roll_number=form.cleaned_data['roll_number'],
                department=form.cleaned_data['department'],
                admission_date=form.cleaned_data['admission_date'],
                phone=form.cleaned_data['phone']
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'erp_core/register.html', {'form': form})

@staff_member_required
def custom_admin_index(request):
    """Custom admin index view"""
    site.each_context(request)['student_count'] = Student.objects.count()
    site.each_context(request)['faculty_count'] = Faculty.objects.count()
    return TemplateResponse(request, 'admin/index.html', site.each_context(request))

def register_faculty(request):
    """Handle faculty registration"""
    if request.method == 'POST':
        form = FacultyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Faculty.objects.create(
                user=user,
                employee_id=form.cleaned_data['employee_id'],
                department=form.cleaned_data['department'],
                designation=form.cleaned_data['designation']
            )
            messages.success(request, 'Faculty registration successful! Please login.')
            return redirect('login')
    else:
        form = FacultyRegistrationForm()
    return render(request, 'erp_core/register_faculty.html', {'form': form})

def update_student(request, student_id):
    """Update student information"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_dashboard')
    else:
        form = StudentRegistrationForm(instance=student)
    return render(request, 'update_student.html', {'form': form})