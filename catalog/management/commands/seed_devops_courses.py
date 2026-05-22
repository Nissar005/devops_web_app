from __future__ import annotations

from django.core.management.base import BaseCommand

from catalog.models import Course, CourseCategory, CourseLesson, CourseModule


class Command(BaseCommand):
    help = "Seed sample DevOps courses (no video files by default)."

    def handle(self, *args, **options):
        courses_data = [
            {
                "slug": "linux-for-devops",
                "title": "Linux for DevOps Engineers",
                "category": CourseCategory.LINUX,
                "description": "A practical course covering Linux fundamentals every DevOps engineer needs: processes, permissions, shells, networking, and troubleshooting.",
                "modules": [
                    {
                        "title": "Linux Essentials",
                        "order_index": 1,
                        "lessons": [
                            {"title": "Filesystem & Permissions", "order_index": 1},
                            {"title": "Processes, Signals & Jobs", "order_index": 2},
                        ],
                    },
                    {
                        "title": "Shell Scripting",
                        "order_index": 2,
                        "lessons": [
                            {"title": "Bash Basics for Automation", "order_index": 1},
                            {"title": "Writing Safe Scripts", "order_index": 2},
                        ],
                    },
                ],
            },
            {
                "slug": "docker-essentials",
                "title": "Docker Essentials for DevOps",
                "category": CourseCategory.DOCKER,
                "description": "Learn how to containerize applications, build efficient images, and run production-ready containers with confidence.",
                "modules": [
                    {
                        "title": "Containers 101",
                        "order_index": 1,
                        "lessons": [
                            {"title": "Images vs Containers", "order_index": 1},
                            {"title": "Working with Dockerfiles", "order_index": 2},
                        ],
                    },
                    {
                        "title": "Production Workflows",
                        "order_index": 2,
                        "lessons": [
                            {"title": "Ports, Volumes & Networking", "order_index": 1},
                            {"title": "Multi-stage Builds", "order_index": 2},
                        ],
                    },
                ],
            },
            {
                "slug": "kubernetes-practice",
                "title": "Kubernetes Hands-on (Practical)",
                "category": CourseCategory.KUBERNETES,
                "description": "A hands-on introduction to Kubernetes concepts and workflows: pods, deployments, services, and operational troubleshooting.",
                "modules": [
                    {
                        "title": "Core Concepts",
                        "order_index": 1,
                        "lessons": [
                            {"title": "Pods, Deployments & ReplicaSets", "order_index": 1},
                            {"title": "Services & Networking Basics", "order_index": 2},
                        ],
                    },
                    {
                        "title": "Operational Skills",
                        "order_index": 2,
                        "lessons": [
                            {"title": "Health Checks & Rolling Updates", "order_index": 1},
                            {"title": "Debugging with kubectl", "order_index": 2},
                        ],
                    },
                ],
            },
        ]

        created_courses = 0
        created_lessons = 0

        for c in courses_data:
            course, course_created = Course.objects.get_or_create(
                slug=c["slug"],
                defaults={
                    "title": c["title"],
                    "description": c["description"],
                    "category": c["category"],
                    "is_published": True,
                },
            )
            if course_created:
                created_courses += 1
                self.stdout.write(self.style.SUCCESS(f"Created course: {course.title}"))

            for m in c["modules"]:
                module, _ = CourseModule.objects.get_or_create(
                    course=course,
                    order_index=m["order_index"],
                    defaults={"title": m["title"]},
                )
                # If a module title changed, update it.
                if module.title != m["title"]:
                    module.title = m["title"]
                    module.save(update_fields=["title"])

                for l in m["lessons"]:
                    lesson, lesson_created = CourseLesson.objects.get_or_create(
                        module=module,
                        order_index=l["order_index"],
                        defaults={"title": l["title"], "description": ""},
                    )
                    if lesson_created:
                        created_lessons += 1
                    elif lesson.title != l["title"]:
                        lesson.title = l["title"]
                        lesson.save(update_fields=["title"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete. Courses created: {created_courses}, lessons created: {created_lessons}."
            )
        )
        self.stdout.write(
            "Note: sample lessons are created without video files. Upload videos from the Admin > Courses UI."
        )

