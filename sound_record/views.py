# views.py
import speech_recognition as sr
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from exam.models import Exam
from .models import AudioRecording
from django.conf import settings
import os
from datetime import datetime
from io import BytesIO
from pydub import AudioSegment

@csrf_exempt
def upload_voice(request):
    try:
        if request.method == 'POST' and request.FILES.get('audio'):
            if not request.user.is_authenticated:
                return JsonResponse({'message': 'User not authenticated'}, status=401)

            audio_file = request.FILES['audio']
            exam_id = request.POST.get('exam_id')

            # print("request.FILES:", request.FILES)
            # print("request.POST:", request.POST)
            print("exam_id:", exam_id)
            print("audio_file:", audio_file)

            # بررسی وجود آزمون
            try:
                exam = Exam.objects.get(id=exam_id)
            except Exam.DoesNotExist:
                return JsonResponse({'message': 'Exam not found'}, status=404)

            # پردازش فایل صوتی
            try:
                # تبدیل فایل صوتی به فرمت قابل پردازش توسط SpeechRecognition با استفاده از pydub
                audio = AudioSegment.from_file(audio_file)
                audio = audio.set_frame_rate(44100).set_sample_width(2)
                audio_data = sr.AudioData(audio.raw_data, sample_rate=audio.frame_rate, sample_width=audio.sample_width)

                # تشخیص متن با استفاده از Google Speech Recognition
                recognizer = sr.Recognizer()
                text = recognizer.recognize_google(audio_data, language='fa-IR')

                # ذخیره‌سازی فایل صوتی و متن
                try:
                    audio_recording = AudioRecording(user=request.user, exam=exam, file=audio_file, text=text)
                    audio_recording.save()
                except Exception as e:
                    print(f"Error saving audio file: {e}")
                    return JsonResponse({'message': 'Error saving audio file'}, status=500)

                return JsonResponse({'message': 'Audio uploaded and processed successfully!',
                                     'file_path': audio_recording.file.url,
                                     'text': text})

            except sr.UnknownValueError:
                return JsonResponse({'message': 'Unable to recognize speech'}, status=400)
            except sr.RequestError as e:
                return JsonResponse({'message': f'Could not request results from Google Speech Recognition service; {e}'}, status=500)
            except Exception as e:
                print(f"Error processing audio: {e}")
                return JsonResponse({'message': 'Error processing audio'}, status=500)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Invalid request'}, status=400)