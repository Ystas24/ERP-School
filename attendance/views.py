# attendance/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db import transaction

from users.models import StudentProfile, TeacherProfile
from django.apps import apps
from .models import Attendance


def _is_teacher(user):
    return user.is_authenticated and (hasattr(user, "teacherprofile") or hasattr(user, "teacher_profile"))

@login_required
def my_attendance(request):
    """Журнал відвідуваності для учня."""
    student = StudentProfile.objects.filter(user=request.user).select_related("classroom").first()
    records = Attendance.objects.none()
    if student:
        records = (
            Attendance.objects.filter(student=student)
            .select_related("subject", "classroom", "teacher")
            .order_by("-date", "-lesson_number")
        )

        # прості фільтри
        month = request.GET.get("month")  # YYYY-MM
        if month:
            y, m = month.split("-")
            records = records.filter(date__year=int(y), date__month=int(m))

    return render(request, "attendance/my_attendance.html", {"records": records})


@login_required
def attendance_mark(request):
    """Вчитель відмічає відвідуваність для всього класу за один урок."""
    if not _is_teacher(request.user):
        return redirect("home")

    teacher = TeacherProfile.objects.filter(user=request.user).first()

    # Початкові значення
    date = request.GET.get("date") or timezone.localdate().isoformat()
    classroom_id = request.GET.get("classroom")
    subject_id = request.GET.get("subject")
    lesson_number = request.GET.get("lesson") or ""

    Subject = apps.get_model("academics", "Subject")
    Classroom = apps.get_model("academics", "Classroom")

    students = []
    if classroom_id:
        students = StudentProfile.objects.filter(classroom_id=classroom_id).select_related("user").order_by("user__last_name", "user__first_name")

    if request.method == "POST":
        date = request.POST.get("date")
        classroom_id = request.POST.get("classroom")
        subject_id = request.POST.get("subject")
        lesson_number = request.POST.get("lesson") or None

        students = StudentProfile.objects.filter(classroom_id=classroom_id).select_related("user")

        with transaction.atomic():
            for s in students:
                status = request.POST.get(f"status_{s.id}", "present")
                comment = request.POST.get(f"comment_{s.id}", "")
                Attendance.objects.update_or_create(
                    date=date,
                    lesson_number=lesson_number,
                    student=s,
                    subject_id=subject_id or None,
                    defaults={
                        "classroom_id": classroom_id or None,
                        "teacher": teacher,
                        "status": status,
                        "comment": comment[:255],
                    },
                )
        return redirect("attendance_mark")  # повертаємося на цю ж сторінку

    return render(
        request,
        "attendance/attendance_mark.html",
        {
            "date": date,
            "classrooms": Classroom,
            "subjects": Subject,
            "selected_classroom": int(classroom_id) if classroom_id else None,
            "selected_subject": int(subject_id) if subject_id else None,
            "lesson_number": lesson_number,
            "students": students,
        },
    )
