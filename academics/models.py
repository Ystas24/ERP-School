from django.db import models
from django.utils import timezone
from datetime import date
from users.models import ClassRoom, TeacherProfile
from django.conf import settings


class Subject(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="subjects")
    def __str__(self): return self.title

class ScheduleItem(models.Model):
    day = models.DateField(default=date.today)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    classroom_location = models.CharField(max_length=100, blank=True)
    def __str__(self): return f"{self.subject} ({self.start_time}-{self.end_time})"

class Homework(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    deadline = models.DateField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    class Meta: ordering = ["-created"]
    def __str__(self): return f"{self.title} ({self.subject})"




class HomeworkStatus(models.Model):
    """
    Отмечает, что конкретный студент (или просто пользователь) выполнил конкретное ДЗ.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="homework_statuses")
    homework = models.ForeignKey("academics.Homework", on_delete=models.CASCADE, related_name="statuses")
    done = models.BooleanField(default=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "homework")

    def __str__(self):
        return f"{self.user} → {self.homework} ({'done' if self.done else 'not done'})"

