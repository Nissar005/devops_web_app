from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    # Public pages
    path("", views.course_list, name="course_list"),
    path("courses/<slug:course_slug>/", views.course_detail, name="course_detail"),
    # Admin pages (role-based, not Django admin site)
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/users/", views.admin_user_list, name="admin_user_list"),
    path("admin/users/<int:user_id>/", views.admin_user_edit, name="admin_user_edit"),
    path(
        "admin/users/<int:user_id>/delete/",
        views.admin_user_delete,
        name="admin_user_delete",
    ),
    path("admin/courses/", views.admin_course_list, name="admin_course_list"),
    path("admin/courses/new/", views.admin_course_create, name="admin_course_create"),
    path("admin/courses/<slug:course_slug>/edit/", views.admin_course_edit, name="admin_course_edit"),
    path(
        "admin/courses/<slug:course_slug>/delete/",
        views.admin_course_delete,
        name="admin_course_delete",
    ),
    path(
        "admin/courses/<slug:course_slug>/modules/new/",
        views.admin_module_create,
        name="admin_module_create",
    ),
    path(
        "admin/modules/<int:module_id>/edit/",
        views.admin_module_edit,
        name="admin_module_edit",
    ),
    path(
        "admin/modules/<int:module_id>/delete/",
        views.admin_module_delete,
        name="admin_module_delete",
    ),
    path(
        "admin/modules/<int:module_id>/lessons/new/",
        views.admin_lesson_create,
        name="admin_lesson_create",
    ),
    path(
        "admin/lessons/<int:lesson_id>/edit/",
        views.admin_lesson_edit,
        name="admin_lesson_edit",
    ),
    path(
        "admin/lessons/<int:lesson_id>/delete/",
        views.admin_lesson_delete,
        name="admin_lesson_delete",
    ),
]

