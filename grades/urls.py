from django.urls import path
from .views import my_journal, grade_create, my_summary

urlpatterns = [
    path("my-journal/", my_journal, name="my_journal"),
    path("grades/add/", grade_create, name="grade_create"),
    path("my-summary/", my_summary, name="my_summary"),
]
