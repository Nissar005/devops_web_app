from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify


class CourseCategory(models.TextChoices):
    LINUX = "Linux", "Linux"
    SHELL_SCRIPTS = "Shell Scripting", "Shell Scripting"
    AWS = "AWS", "AWS"
    JENKINS = "Jenkins", "Jenkins"
    GIT_GITHUB = "Git & GitHub", "Git & GitHub"
    DOCKER = "Docker", "Docker"
    KUBERNETES = "Kubernetes", "Kubernetes"
    ANSIBLE = "Ansible", "Ansible"


class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CourseCategory.choices)
    cover_image = models.ImageField(upload_to="course_covers/", blank=True, null=True)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["slug"]),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    order_index = models.PositiveIntegerField()

    class Meta:
        unique_together = [("course", "order_index")]
        ordering = ["order_index"]

    def __str__(self) -> str:
        return f"{self.course.title} - {self.title}"


class CourseLesson(models.Model):
    module = models.ForeignKey(
        CourseModule, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order_index = models.PositiveIntegerField()

    # Store uploads locally for dev; in production point MEDIA_ROOT at S3/NFS.
    video_file = models.FileField(
        upload_to="course_videos/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["mp4", "webm", "ogg"])],
    )

    class Meta:
        unique_together = [("module", "order_index")]
        ordering = ["order_index"]

    def __str__(self) -> str:
        return f"{self.module.course.title} - {self.title}"
