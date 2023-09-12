import os
import uuid

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


def user_image_file_path(instance, filename: str):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.username)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "users", filename)


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(null=True, upload_to=user_image_file_path)
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="follow_users", blank=True)
    followings = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="following_users", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Hashtag(models.Model):
    name = models.CharField(max_length=63)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.name.startswith("#"):
            self.name = f"#{self.name}"

        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self) -> str:
        return self.name


def post_image_file_path(instance, filename: str):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "posts", filename)


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="posts", on_delete=models.CASCADE
    )
    hashtags = models.ManyToManyField(Hashtag, related_name="posts", blank=True)
    image = models.ImageField(null=True, upload_to=post_image_file_path)
    created_at = models.DateTimeField(blank=True, default=timezone.now)

    def __str__(self) -> str:
        return f"{self.title} (author: {self.author.username})"


class ScheduledPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="scheduled_posts", on_delete=models.CASCADE
    )
    hashtags = models.ManyToManyField(Hashtag, related_name="scheduled_posts", blank=True)
    image = models.ImageField(null=True, upload_to=post_image_file_path)
    created_at = models.DateTimeField(blank=True, default=timezone.now)

    def __str__(self) -> str:
        return f"{self.title} (author: {self.author.username})"


class Like(models.Model):
    liker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="likes", on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)