# models.py
from django.db import models
from datetime import datetime
from accounts.models import CustomUser
from exam.models import Exam


def user_face_directory_path(instance, filename):
    return f"faces/{instance.user.national_code}/{instance.user.last_name}_{filename}"


class FaceEncoding(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    encoding_file = models.FileField(upload_to=user_face_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s Face Data"


def unrecognized_face_directory_path(instance, filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"unrecognized/{instance.user.national_code}/images/{instance.user.username}_unrecognized_{timestamp}.jpg"


class UnrecognizedFace(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # User who was being scanned
    image = models.ImageField(upload_to=unrecognized_face_directory_path)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Unrecognized face for {self.user.username} at {self.created_at}"
