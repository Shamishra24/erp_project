from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Student, Faculty, Course

@staff_member_required
def admin_dashboard(request):
    context = {
        'student_count': Student.objects.count(),
        'faculty_count': Faculty.objects.count(),
        'course_count': Course.objects.count(),
        'recent_students': Student.objects.order_by('-id')[:5],
    }
    return render(request, 'admin/custom_dashboard.html', context)