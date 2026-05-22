from django.urls import path

from . import views

app_name = "learning"

urlpatterns = [
    path("dashboard/", views.user_dashboard, name="user_dashboard"),
    path("enroll/<slug:course_slug>/", views.enroll_course, name="enroll_course"),
    path("lesson/<int:lesson_id>/", views.lesson_play, name="lesson_play"),
    path(
        "lesson/<int:lesson_id>/complete/",
        views.mark_lesson_completed,
        name="mark_lesson_completed",
    ),
]

