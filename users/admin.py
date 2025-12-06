# users/admin.py
from django.contrib import admin
from .models import ClassRoom, TeacherProfile, StudentProfile, ParentProfile

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__username", "user__first_name", "user__last_name")

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "classroom")
    list_filter = ("classroom",)
    search_fields = ("user__username", "user__first_name", "user__last_name")

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "student")
    search_fields = ("user__username", "student__user__username")
