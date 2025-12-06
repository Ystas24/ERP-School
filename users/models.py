from django.db import models
from django.contrib.auth.models import User

class ClassRoom(models.Model):
    name = models.CharField(max_length=50)  # напр. "10-А"
    def __str__(self): return self.name

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacherprofile")
    def __str__(self): return f"Teacher: {self.user.get_full_name() or self.user.username}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="studentprofile")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self): return f"Student: {self.user.get_full_name() or self.user.username}"

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parentprofile")
    student = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self): return f"Parent: {self.user.get_full_name() or self.user.username}"
