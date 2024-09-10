from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    otp_key = models.CharField(max_length=32)
    otp_enabled = models.BooleanField(default=False)
    qr_otp = models.ImageField(upload_to="photos/")
