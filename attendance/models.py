# attendance/models.py
from django.db import models
from django.utils import timezone

from users.models import StudentProfile, TeacherProfile




class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Присутній"
        ABSENT = "absent", "Відсутній"
        LATE = "late", "Запізнився"
        EXCUSED = "excused", "Поважна причина"

    date = models.DateField(default=timezone.localdate)
    lesson_number = models.PositiveSmallIntegerField(null=True, blank=True)

    # ВАЖНО: строковые ссылки на модели из приложения academics
    classroom = models.ForeignKey(
        "users.ClassRoom", on_delete=models.SET_NULL, null=True, blank=True
    )
    subject = models.ForeignKey(
        "academics.Subject", on_delete=models.SET_NULL, null=True, blank=True
    )

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="attendances"
    )
    teacher = models.ForeignKey(
        TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True
    )

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PRESENT
    )
    comment = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["date", "lesson_number", "student", "subject"],
                name="uniq_attendance_per_lesson",
            )
        ]

