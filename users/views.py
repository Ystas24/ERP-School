from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import StudentProfile, TeacherProfile, ParentProfile

@login_required
def profile_view(request):
    user = request.user
    student = StudentProfile.objects.filter(user=user).select_related("classroom").first()
    teacher = TeacherProfile.objects.filter(user=user).first()
    parent = ParentProfile.objects.filter(user=user).first()

    return render(request, "users/profile.html", {
        "student": student,
        "teacher": teacher,
        "parent": parent,
    })
