from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model with an explicit role.

    We use this role for application-level authorization (admin vs user) rather than
    relying solely on Django's is_staff/is_superuser.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        USER = "user", _("User")

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    email = models.EmailField(_("email address"), unique=True, blank=True)

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    def save(self, *args, **kwargs):
        # Keep Django's admin site permissions aligned with our app role.
        if self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username
