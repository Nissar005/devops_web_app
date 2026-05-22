from __future__ import annotations

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from accounts.models import User
from learning.models import Enrollment, LessonCompletion

from .forms import (
    CourseForm,
    CourseLessonForm,
    CourseModuleForm,
    UserRoleForm,
)
from .models import Course, CourseCategory, CourseLesson, CourseModule


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not getattr(request.user, "is_admin", False):
            messages.error(request, "You don't have access to that page.")
            return redirect("catalog:course_list")
        return view_func(request, *args, **kwargs)

    return wrapper


def course_list(request):
    q = (request.GET.get("q") or "").strip()
    category = (request.GET.get("category") or "").strip()

    courses_qs = Course.objects.filter(is_published=True)
    if q:
        courses_qs = courses_qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )
    if category:
        courses_qs = courses_qs.filter(category=category)

    courses_qs = courses_qs.order_by("-created_at")

    paginator = Paginator(courses_qs, 8)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    return render(
        request,
        "catalog/course_list.html",
        {
            "page_obj": page_obj,
            "q": q,
            "category": category,
            "categories": CourseCategory.choices,
        },
    )


def course_detail(request, course_slug: str):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    modules = (
        course.modules.all()
        .prefetch_related("lessons")
        .order_by("order_index")
    )

    is_enrolled = False
    completed_lesson_ids: set[int] = set()

    next_lesson: CourseLesson | None = None
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        lessons_qs = CourseLesson.objects.filter(module__course=course)
        completed_lesson_ids = set(
            LessonCompletion.objects.filter(
                user=request.user, lesson__in=lessons_qs
            ).values_list("lesson_id", flat=True)
        )

        if is_enrolled:
            # Find the next lesson the user hasn't completed yet.
            for lesson in lessons_qs.order_by("module__order_index", "order_index"):
                if lesson.id not in completed_lesson_ids:
                    next_lesson = lesson
                    break

    return render(
        request,
        "catalog/course_detail.html",
        {
            "course": course,
            "modules": modules,
            "is_enrolled": is_enrolled,
            "completed_lesson_ids": completed_lesson_ids,
            "next_lesson": next_lesson,
        },
    )


@admin_required
def admin_dashboard(request):
    context = {
        "user_count": User.objects.count(),
        "course_count": Course.objects.count(),
        "enrollment_count": Enrollment.objects.count(),
        "lesson_completion_count": LessonCompletion.objects.count(),
    }
    return render(request, "catalog/admin_dashboard.html", context)


@admin_required
def admin_user_list(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "catalog/admin_user_list.html", {"users": users})


@admin_required
def admin_user_edit(request, user_id: int):
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated.")
            return redirect("catalog:admin_user_list")
    else:
        form = UserRoleForm(instance=user)

    return render(
        request,
        "catalog/admin_user_form.html",
        {"form": form, "user": user},
    )


@admin_required
def admin_user_delete(request, user_id: int):
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        if user.pk == request.user.pk:
            messages.error(request, "You can't delete your own account.")
            return redirect("catalog:admin_user_list")
        user.delete()
        messages.success(request, "User deleted.")
        return redirect("catalog:admin_user_list")

    return render(request, "catalog/admin_user_confirm_delete.html", {"user": user})


@admin_required
def admin_course_list(request):
    courses = Course.objects.all().order_by("-created_at")
    return render(request, "catalog/admin_course_list.html", {"courses": courses})


@admin_required
@require_http_methods(["GET", "POST"])
def admin_course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            # Ensure we have a slug for the URL.
            if not course.slug:
                course.slug = course.title.lower().replace(" ", "-")
                course.save(update_fields=["slug"])
            messages.success(request, "Course created.")
            return redirect("catalog:admin_course_list")
    else:
        form = CourseForm()

    return render(
        request,
        "catalog/admin_course_form.html",
        {"form": form, "mode": "create"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_course_edit(request, course_slug: str):
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated.")
            return redirect("catalog:admin_course_edit", course_slug=course.slug)
    else:
        form = CourseForm(instance=course)

    modules = course.modules.all().order_by("order_index")
    return render(
        request,
        "catalog/admin_course_form.html",
        {"form": form, "mode": "edit", "course": course, "modules": modules},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_course_delete(request, course_slug: str):
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect("catalog:admin_course_list")

    return render(request, "catalog/admin_course_confirm_delete.html", {"course": course})


@admin_required
@require_http_methods(["GET", "POST"])
def admin_module_create(request, course_slug: str):
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == "POST":
        form = CourseModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, "Module created.")
            return redirect("catalog:admin_course_edit", course_slug=course.slug)
    else:
        form = CourseModuleForm()

    return render(
        request,
        "catalog/admin_module_form.html",
        {"form": form, "course": course, "mode": "create"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_module_edit(request, module_id: int):
    module = get_object_or_404(CourseModule, pk=module_id)
    if request.method == "POST":
        form = CourseModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, "Module updated.")
            return redirect("catalog:admin_course_edit", course_slug=module.course.slug)
    else:
        form = CourseModuleForm(instance=module)

    return render(
        request,
        "catalog/admin_module_form.html",
        {"form": form, "course": module.course, "mode": "edit", "module": module},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_module_delete(request, module_id: int):
    module = get_object_or_404(CourseModule, pk=module_id)
    course = module.course
    if request.method == "POST":
        module.delete()
        messages.success(request, "Module deleted.")
        return redirect("catalog:admin_course_edit", course_slug=course.slug)

    return render(
        request,
        "catalog/admin_module_confirm_delete.html",
        {"course": course, "module": module},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_lesson_create(request, module_id: int):
    module = get_object_or_404(CourseModule, pk=module_id)
    if request.method == "POST":
        form = CourseLessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, "Lesson created.")
            return redirect("catalog:admin_module_edit", module_id=module.id)
    else:
        form = CourseLessonForm()

    return render(
        request,
        "catalog/admin_lesson_form.html",
        {"form": form, "module": module, "mode": "create"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_lesson_edit(request, lesson_id: int):
    lesson = get_object_or_404(CourseLesson, pk=lesson_id)
    module = lesson.module
    if request.method == "POST":
        form = CourseLessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated.")
            return redirect("catalog:admin_module_edit", module_id=module.id)
    else:
        form = CourseLessonForm(instance=lesson)

    return render(
        request,
        "catalog/admin_lesson_form.html",
        {"form": form, "module": module, "mode": "edit", "lesson": lesson},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_lesson_delete(request, lesson_id: int):
    lesson = get_object_or_404(CourseLesson, pk=lesson_id)
    module = lesson.module
    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted.")
        return redirect("catalog:admin_module_edit", module_id=module.id)

    return render(
        request,
        "catalog/admin_lesson_confirm_delete.html",
        {"module": module, "lesson": lesson},
    )
