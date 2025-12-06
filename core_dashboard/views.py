from django.shortcuts import render
from django.utils import timezone
from common.decorators import role_required
from academics.models import ScheduleItem, Homework
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

def _teacher_profile(u):
    return getattr(u, "teacher_profile", None) or getattr(u, "teacherprofile", None)

def _student_profile(u):
    return getattr(u, "student_profile", None) or getattr(u, "studentprofile", None)

@role_required()  # любой залогиненный
def home(request):
    return render(request, "core_dashboard/home.html", {})

@role_required("admin", "teacher", "student")
def schedule_today(request):
    today = timezone.localdate()
    qs = ScheduleItem.objects.select_related("classroom","subject","teacher","teacher__user").filter(day=today)
    u = request.user
    if u.is_superuser:
        items = qs.order_by("start_time")
    elif _teacher_profile(u):
        items = qs.filter(teacher=_teacher_profile(u)).order_by("start_time")
    elif _student_profile(u) and getattr(_student_profile(u), "classroom_id", None):
        items = qs.filter(classroom_id=_student_profile(u).classroom_id).order_by("start_time")
    else:
        items = ScheduleItem.objects.none()
    return render(request, "schedule/schedule_today.html", {"today": today, "items": items})

@role_required("admin", "teacher", "student")
def homework_list(request):
    qs = Homework.objects.select_related("subject","teacher","teacher__user","classroom")
    u = request.user
    if u.is_superuser:
        items = qs.order_by("-created")
    elif _teacher_profile(u):
        items = qs.filter(teacher=_teacher_profile(u)).order_by("-created")
    elif _student_profile(u) and getattr(_student_profile(u), "classroom_id", None):
        items = qs.filter(classroom_id=_student_profile(u).classroom_id).order_by("-created")
    else:
        items = qs.none()
    return render(request, "homework/list.html", {"items": items})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from common.decorators import role_required
from academics.models import Homework, Subject, ClassRoom
from django.utils import timezone

@login_required
@role_required("teacher")
def homework_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        text = request.POST.get("text", "").strip()
        subject_id = request.POST.get("subject")
        classroom_id = request.POST.get("classroom")
        deadline = request.POST.get("deadline") or None

        if not (title and text and subject_id and classroom_id):
            messages.error(request, "Заповніть усі обов’язкові поля.")
        else:
            hw = Homework.objects.create(
                title=title,
                text=text,
                subject=Subject.objects.get(pk=subject_id),
                teacher=request.user.teacherprofile,
                classroom=ClassRoom.objects.get(pk=classroom_id),
                deadline=deadline,
                created=timezone.now(),
            )
            messages.success(request, "Домашнє завдання додано.")
            return redirect("homework_list")

    context = {
        "subjects": Subject.objects.all(),
        "classrooms": ClassRoom.objects.all(),
    }
    return render(request, "academics/homework_form.html", context)

# унизу файла поруч з іншими homework-* вьюхами


def _teacher_profile(user):
    return getattr(user, "teacher_profile", None) or getattr(user, "teacherprofile", None)

def _is_teacher_or_admin(user):
    return getattr(user, "is_superuser", False) or _teacher_profile(user) is not None

@role_required("admin", "teacher")
def homework_delete(request, pk: int):
    """Видалення ДЗ (тільки автор-вчитель або адмін)."""
    hw = get_object_or_404(Homework, pk=pk)
    u = request.user
    # дозволяємо, якщо адмін або саме той учитель, що створив
    if not u.is_superuser and _teacher_profile(u) != hw.teacher:
        messages.error(request, "Видаляти може лише автор або адміністратор.")
        return redirect("homework_detail", pk=hw.pk)

    if request.method == "POST":
        title = hw.title
        hw.delete()
        messages.success(request, f"Домашнє завдання «{title}» видалено ✅")
        return redirect("homework_list")

    # підтвердження
    return render(request, "academics/homework_delete_confirm.html", {"hw": hw})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from academics.models import ScheduleItem, Homework
from grades.models import Grade
from events.models import Event
from users.models import StudentProfile, TeacherProfile

@login_required  # или @login_required(login_url="/accounts/login/")
def home(request):
    today = timezone.localdate()
    user = request.user

    # базові queryset-и
    schedule_qs = (ScheduleItem.objects
                   .filter(day=today)
                   .select_related("subject", "teacher", "classroom")
                   .order_by("start_time"))

    homework_qs = Homework.objects.select_related("subject", "teacher", "classroom")
    upcoming_homework = homework_qs.filter(deadline__gte=today).order_by("deadline")[:5]

    grades_qs = (Grade.objects
                 .select_related("student", "subject")
                 .order_by("-created_at")[:5])

    # ⬇️ главное исправление: используем start вместо несуществующего date
    events_qs = (Event.objects
                 .filter(start__date__gte=today)   # ближайшие події, можно убрать фильтр, если нужно всё
                 .order_by("start")[:5])

    # фільтри за роллю
    student = (StudentProfile.objects
               .filter(user=user)
               .select_related("classroom")
               .first())
    teacher = TeacherProfile.objects.filter(user=user).first()

    if student:
        schedule_qs = schedule_qs.filter(classroom=student.classroom)
        upcoming_homework = upcoming_homework.filter(classroom=student.classroom)
        grades_qs = (Grade.objects
                     .filter(student=student)
                     .select_related("subject", "teacher")
                     .order_by("-created_at")[:5])

    if teacher:
        schedule_qs = schedule_qs.filter(teacher=teacher)
        upcoming_homework = upcoming_homework.filter(teacher=teacher)
        grades_qs = (Grade.objects
                     .filter(teacher=teacher)
                     .select_related("subject", "student")
                     .order_by("-created_at")[:5])

    context = {
        "today": today,
        "today_schedule": schedule_qs,
        "upcoming_homework": upcoming_homework,
        "recent_grades": grades_qs,
        "upcoming_events": events_qs,
    }
    return render(request, "core_dashboard/home.html", context)

