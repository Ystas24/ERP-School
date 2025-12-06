from django.db import models
from users.models import StudentProfile
from django.db import models

class Grade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey("academics.Subject", on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.student} – {self.subject}: {self.value}"
