from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.core.validators import FileExtensionValidator
from django.db.models import Q, UniqueConstraint


# Create your models here.
class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50, unique=True)
    email_id = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    document = models.FileField(
        upload_to="documents/",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "pdf"]),
        ],
        help_text="Upload a government-issued ID (Driving License, National ID, or Passport). Allowed formats: JPEG, PNG, PDF.",
        null=True,  # remove this
        blank=True,  # remove this
    )
    is_kyc_verified = models.BooleanField(default=False)
    kyc_rejection_reason = models.TextField(blank=True)
    profile_photo = models.ImageField(
        upload_to="profile_photos/", null=True, blank=True
    )

    USERNAME_FIELD = "phone_number"
    # username field cannot be part of required fields
    REQUIRED_FIELDS = ["full_name", "document"]

    objects = CustomUserManager()

    def __str__(self):
        return self.full_name

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["email_id"], name="unique_email_id", condition=~Q(email_id=None)
            )
        ]
