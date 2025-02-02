# models.py
from django.db import models
import os
from datetime import datetime
from accounts.models import CustomUser
from exam.models import Exam


def audio_file_path(instance, filename):
    """Generate file path for new audio file in unrecognized folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = filename.split('.')[-1]
    filename = f"{instance.user.username}_{timestamp}.{ext}"
    # استفاده از exam_id برای نامگذاری پوشه
    return os.path.join('unrecognized', instance.user.national_code, str(instance.exam.id), 'audio', filename)


class AudioRecording(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='audio_recordings')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    file = models.FileField(upload_to=audio_file_path)
    text = models.TextField(blank=True, null=True)  # اضافه شدن فیلد متن
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recording by {self.user.username} at {self.created_at}"