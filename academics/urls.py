from django.urls import path
from . import views

urlpatterns = [
    path("schedule/today/", views.schedule_today, name="schedule_today"),
    path("schedule/week/", views.schedule_week, name="schedule_week"),

    path("homework/", views.homework_list, name="homework_list"),
    path("homework/<int:pk>/", views.homework_detail, name="homework_detail"),
    path("homework/create/", views.homework_create, name="homework_create"),
    path("homework/<int:pk>/toggle-done/", views.homework_toggle_done, name="homework_toggle_done"),
    path("homework/<int:pk>/edit/", views.homework_update, name="homework_update"),
    path("homework/<int:pk>/delete/", views.homework_delete, name="homework_delete"),

    path("subjects/", views.subjects_list, name="subjects_list"),
    
]


