# models.py
from django.db import models
import os
from django.conf import settings
# Create your models here.
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    national_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

