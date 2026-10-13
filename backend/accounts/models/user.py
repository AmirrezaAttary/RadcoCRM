from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user model manager where username is the unique identifier
    for authentication.
    """

    def create_user(self, username, phone_number, password=None, **extra_fields):
        if not username:
            raise ValueError(_("The username must be set"))

        if not phone_number:
            raise ValueError(_("The phone number must be set"))

        user = self.model(
            username=username,
            phone_number=phone_number,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, phone_number, password, **extra_fields):
        """
        Create and save a SuperUser with the given username,
        phone number and password.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("type", User.UserType.ADMIN.value)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(
            username=username,
            phone_number=phone_number,
            password=password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):

    class UserType(models.IntegerChoices):
        ADMIN = 1, _("admin")
        EMPLOYEE = 2, _("employee")

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    phone_number = models.CharField(
        _("phone number"),
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message=_(
                    "Phone number must start with 09 and contain exactly 11 digits."
                ),
            ),
        ],
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    type = models.IntegerField(
        choices=UserType.choices,
        default=UserType.EMPLOYEE.value,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone_number"]

    objects = UserManager()

    def __str__(self):
        return self.username