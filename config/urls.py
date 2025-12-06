from django.contrib import admin
from django.urls import path, include
from core_dashboard.views import home, schedule_today, homework_list, homework_create
from core_dashboard.views import home as dashboard_home  # домашня панель
from users.views import profile_view
from grades.views import my_journal, my_summary, grade_create           

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("schedule/today/", schedule_today, name="schedule_today"),
    path("homework/", homework_list, name="homework_list"),
    path("homework/create/", homework_create, name="homework_create"),  # NEW
    path("accounts/", include("django.contrib.auth.urls")),  # <-- критично    
    path("accounts/", include("django.contrib.auth.urls")),  # логін/логаут
    path("profile/", profile_view, name="profile"),
    path("dashboard/", dashboard_home, name="dashboard"),
    path("", include("grades.urls")),
    path("grades/my/", my_journal, name="my_journal"),
    path("grades/summary/", my_summary, name="my_summary"),
    path("grades/new/", grade_create, name="grade_create"),
    path("attendance/", include("attendance.urls")),
]
