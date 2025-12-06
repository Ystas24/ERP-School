from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import Grade
from .forms import GradeForm
from users.models import StudentProfile, TeacherProfile  # вже є в твоєму проєкті
from common.decorators import role_required  # якщо робили; інакше перевіряй вручну ролі


@login_required
def my_journal(request):
    """
    Учень бачить свої оцінки.
    Учитель тут нічого особливого не бачить (можна розширити пізніше).
    """
    user = request.user
    student = StudentProfile.objects.filter(user=user).first()

    grades = Grade.objects.none()
    if student:
        grades = (
            Grade.objects.filter(student=student)
            .select_related("subject")
            .order_by("-created_at")
        )

    # прості фільтри за датою (опційно ?from=YYYY-MM-DD&to=YYYY-MM-DD)
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")
    if date_from:
        grades = grades.filter(created_at__date__gte=date_from)
    if date_to:
        grades = grades.filter(created_at__date__lte=date_to)

    context = {
        "grades": grades,
        "date_from": date_from or "",
        "date_to": date_to or "",
    }
    return render(request, "grades/journal_list.html", context)


@role_required("teacher")
def grade_create(request):
    """
    Вчитель створює оцінку.
    """
    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("my_journal")  # або зробимо окрему сторінку списку для вчителя пізніше
    else:
        form = GradeForm()

    return render(request, "grades/grade_form.html", {"form": form})


@login_required
def my_summary(request):
    """
    Середні бали учня по предметах + фільтр за періодом.
    """
    user = request.user
    student = StudentProfile.objects.filter(user=user).first()
    summary = []

    if student:
        qs = Grade.objects.filter(student=student).select_related("subject")

        date_from = request.GET.get("from")
        date_to = request.GET.get("to")
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        # середній бал по кожному предмету
        summary = (
            qs.values("subject__title")
            .annotate(avg=Avg("value"))
            .order_by("subject__title")
        )
    else:
        date_from = date_to = None

    return render(
        request,
        "grades/summary.html",
        {"summary": summary, "date_from": request.GET.get("from", ""), "date_to": request.GET.get("to", "")},
    )
