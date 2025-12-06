from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Prefetch, Q
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ScheduleItem
from users.models import StudentProfile, TeacherProfile
from django.db.models import Count, Min, Max
from .models import Subject, ScheduleItem


from .models import Homework, HomeworkStatus, ScheduleItem, Subject
from .forms import HomeworkForm  # если уже есть — всё ок

# -------- РОЗКЛАД --------

@login_required
def schedule_today(request):
    today = timezone.localdate()
    qs = (
        ScheduleItem.objects.filter(day=today)
        .select_related("subject", "teacher", "classroom")
        .order_by("start_time")
    )

    # Фільтр по ролі (м'який — якщо профілі є)
    student = getattr(request.user, "studentprofile", None)
    teacher = getattr(request.user, "teacherprofile", None)
    if student and getattr(student, "classroom_id", None):
        qs = qs.filter(classroom=student.classroom)
    if teacher:
        qs = qs.filter(teacher=teacher)

    return render(request, "academics/schedule_today.html", {"items": qs, "today": today})

def _week_bounds(day):
    # понеділок — неділя
    start = day - timedelta(days=day.weekday())
    end = start + timedelta(days=6)
    return start, end

@login_required
def schedule_week(request):
    today = timezone.localdate()
    start, end = _week_bounds(today)

    # GET-параметри: ?classroom=7A&teacher=12&student=33
    classroom_slug = request.GET.get("classroom")
    teacher_id = request.GET.get("teacher")
    student_id = request.GET.get("student")

    qs = ScheduleItem.objects.select_related("subject", "teacher", "classroom") \
                             .filter(day__range=[start, end]) \
                             .order_by("day", "start_time")

    # авто-фільтр за роллю
    student = StudentProfile.objects.filter(user=request.user).select_related("classroom").first()
    teacher = TeacherProfile.objects.filter(user=request.user).first()
    if student:
        qs = qs.filter(classroom=student.classroom)
    if teacher:
        qs = qs.filter(teacher=teacher)

    # ручні фільтри (поверх ролі)
    if classroom_slug:
        qs = qs.filter(classroom__slug=classroom_slug)
    if teacher_id:
        qs = qs.filter(teacher_id=teacher_id)
    if student_id:
        st = StudentProfile.objects.filter(id=student_id).select_related("classroom").first()
        if st:
            qs = qs.filter(classroom=st.classroom)

    # групуємо по днях тижня
    days = {}
    for item in qs:
        days.setdefault(item.day, []).append(item)

    context = {
        "week_start": start, "week_end": end,
        "days": days,  # dict[date] -> list[ScheduleItem]
    }
    return render(request, "academics/schedule_week.html", context)


# -------- ДЗ --------

@login_required
def homework_list(request):
    qs = Homework.objects.select_related("subject", "classroom").order_by("-deadline", "-id")

    student = getattr(request.user, "studentprofile", None)
    teacher = getattr(request.user, "teacherprofile", None)
    if student and getattr(student, "classroom_id", None):
        qs = qs.filter(classroom=student.classroom)
    if teacher:
        qs = qs.filter(teacher=teacher)

    # набор id выполненных ДЗ текущего пользователя
    done_ids = set(
        HomeworkStatus.objects
        .filter(user=request.user, done=True, homework_id__in=qs.values_list("id", flat=True))
        .values_list("homework_id", flat=True)
    )

    return render(
        request,
        "academics/homework_list.html",
        {
            "homework_list": qs,   # <— под твой шаблон
            "done_ids": done_ids,  # для бейджа “виконано”
        },
    )


@login_required
def homework_detail(request, pk):
    hw = get_object_or_404(
        Homework.objects.select_related("subject", "teacher", "classroom"),
        pk=pk
    )
    done_ids = request.session.get("homework_done_ids", [])
    is_done = hw.id in done_ids
    return render(request, "academics/homework_detail.html", {
        "homework": hw,
        "is_done": is_done,
    })


@user_passes_test(lambda u: hasattr(u, "teacherprofile"))  # простая охрана: только учитель
def homework_create(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            hw = form.save(commit=False)
            # страховка: если в форме нет teacher, проставим текущего
            if not getattr(hw, "teacher_id", None) and hasattr(request.user, "teacherprofile"):
                hw.teacher = request.user.teacherprofile
            hw.save()
            form.save_m2m()  # если нужно
            return redirect("homework_list")
    else:
        form = HomeworkForm()
    return render(request, "academics/homework_form.html", {"form": form})


@login_required
def homework_toggle_done(request, pk):
    # простий перемикач “виконано/не виконано” у сесії
    hw = get_object_or_404(Homework, pk=pk)
    if request.method == "POST":
        done_ids = request.session.get("homework_done_ids", [])
        if hw.id in done_ids:
            done_ids = [i for i in done_ids if i != hw.id]
            messages.info(request, "Завдання позначено як НЕ виконано.")
        else:
            done_ids.append(hw.id)
            messages.success(request, "Завдання позначено як виконано.")
        request.session["homework_done_ids"] = done_ids
    return redirect("homework_detail", pk=hw.id)

# -------- ПРЕДМЕТИ --------

@login_required
def subjects_list(request):
    # показуємо всі предмети + базову аналітику з розкладу
    subjects = Subject.objects.all().order_by("title")

    # опціонально — виведемо для кожного предмета скільки разів у розкладі цього тижня
    today = timezone.localdate()
    start, end = _week_bounds(today)
    counts = (ScheduleItem.objects
              .filter(day__range=[start, end])
              .values("subject_id")
              .annotate(cnt=Count("id"),
                        first=Min("day"),
                        last=Max("day")))
    by_id = {c["subject_id"]: c for c in counts}

    enriched = []
    for s in subjects:
        meta = by_id.get(s.id, {})
        enriched.append({
            "obj": s,
            "weekly_count": meta.get("cnt", 0),
            "first_day": meta.get("first"),
            "last_day": meta.get("last"),
        })

    return render(request, "academics/subjects_list.html", {"subjects": enriched})
