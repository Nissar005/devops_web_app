from django.conf import settings
from django.db import models
from django.utils import timezone


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey("catalog.Course", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("user", "course")]
        indexes = [
            models.Index(fields=["user", "course"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.course}"


class LessonCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey("catalog.CourseLesson", on_delete=models.CASCADE)
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("user", "lesson")]
        indexes = [
            models.Index(fields=["user", "lesson"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} completed {self.lesson}"
