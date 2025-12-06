# attendance/admin.py
from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("date", "lesson_number", "student", "subject", "classroom", "status", "teacher")
    list_filter = ("date", "status", "subject", "classroom")
    search_fields = ("student__user__username", "student__user__first_name", "student__user__last_name", "comment")
