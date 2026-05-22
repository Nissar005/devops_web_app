from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import User
from catalog.models import Course, CourseLesson
from .models import Enrollment, LessonCompletion


@login_required
def user_dashboard(request):
    enrollments = (
        Enrollment.objects.filter(user=request.user)
        .select_related("course")
        .order_by("-enrolled_at")
    )

    dashboard_rows = []
    for enrollment in enrollments:
        course = enrollment.course
        lessons_qs = CourseLesson.objects.filter(module__course=course)
        total_lessons = lessons_qs.count()
        completed_lessons = LessonCompletion.objects.filter(
            user=request.user, lesson__module__course=course
        ).count()

        percent = 0
        if total_lessons > 0:
            percent = int((completed_lessons / total_lessons) * 100)

        dashboard_rows.append(
            {
                "course": course,
                "completed_lessons": completed_lessons,
                "total_lessons": total_lessons,
                "percent": percent,
            }
        )

    return render(
        request,
        "learning/user_dashboard.html",
        {"dashboard_rows": dashboard_rows},
    )


@login_required
def enroll_course(request, course_slug: str):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    messages.success(request, f"Enrolled in {course.title}.")
    return redirect("catalog:course_detail", course_slug=course.slug)


@login_required
def lesson_play(request, lesson_id: int):
    lesson = get_object_or_404(CourseLesson, pk=lesson_id)
    course = lesson.module.course

    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "Please enroll to access the course content.")
        return redirect("catalog:course_detail", course_slug=course.slug)

    completed = LessonCompletion.objects.filter(user=request.user, lesson=lesson).exists()

    return render(
        request,
        "learning/lesson_play.html",
        {"lesson": lesson, "course": course, "completed": completed},
    )


@login_required
@require_POST
def mark_lesson_completed(request, lesson_id: int):
    lesson = get_object_or_404(CourseLesson, pk=lesson_id)
    course = lesson.module.course

    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "Please enroll to access the course content.")
        return redirect("catalog:course_detail", course_slug=course.slug)

    LessonCompletion.objects.get_or_create(user=request.user, lesson=lesson)
    messages.success(request, "Lesson marked as completed.")
    return redirect("learning:lesson_play", lesson_id=lesson.id)
