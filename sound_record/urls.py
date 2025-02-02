from django.urls import path
from . import views

urlpatterns = [
    path('upload-voice/', views.upload_voice, name='upload-voice'),
]
