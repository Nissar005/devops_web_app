from django import forms
from django.contrib.auth import get_user_model

from .models import Course, CourseLesson, CourseModule

User = get_user_model()


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "category", "cover_image", "is_published"]


class CourseModuleForm(forms.ModelForm):
    class Meta:
        model = CourseModule
        fields = ["title", "order_index"]


class CourseLessonForm(forms.ModelForm):
    class Meta:
        model = CourseLesson
        fields = ["title", "description", "order_index", "video_file"]


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["role"]

