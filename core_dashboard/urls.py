from django.contrib import admin
from django.urls import path,  include
from .views import home, schedule_today, homework_list
from core_dashboard.views import home, schedule_today
from academics.views import schedule_week, subjects_lis

urlpatterns = [
    path("", home, name="home"),
    path("schedule/today/", schedule_today, name="schedule_today"),
    path("homework/", homework_list, name="homework_list"),
    path("admin/", admin.site.urls),
    path("", include("core_dashboard.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("core_dashboard.urls")),           
    path("", include("academics.urls")),
    path("schedule/week/", schedule_week, name="schedule_week"),     
    #path("subjects/", subjects_list, name="subjects_list"),
    path("grades/", include("grades.urls")),                 

]
