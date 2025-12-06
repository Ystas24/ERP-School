# attendance/urls.py
from django.urls import path
from .views import my_attendance, attendance_mark

urlpatterns = [
    path("my/", my_attendance, name="my_attendance"),
    path("mark/", attendance_mark, name="attendance_mark"),
]
