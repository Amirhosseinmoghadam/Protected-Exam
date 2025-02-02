import json
import os
import cv2
import time
import pickle
import base64
import datetime
import tempfile
import numpy as np
import mediapipe as mp
import face_recognition
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from accounts.models import CustomUser
from django.shortcuts import redirect, render
from django.core.files.base import ContentFile
from .models import FaceEncoding, UnrecognizedFace
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, HttpResponse
from exam.models import Exam
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from .utils import extract_encoding_from_video, compare_face_with_encoding


# Load Dlib models
SHAPE_PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
FACE_REC_MODEL_PATH = "dlib_face_recognition_resnet_model_v1.dat"

if not all(
        os.path.exists(path) for path in [SHAPE_PREDICTOR_PATH, FACE_REC_MODEL_PATH]
):
    raise FileNotFoundError("Dlib model files are missing.")



@login_required
def face_mesh_view_load(request):
    return render(request, 'face_scanner/face_mesh_load.html')


@csrf_exempt
@login_required
def scan_and_store_face(request):
    if request.method == "POST":
        user = request.user
        try:
            # Get the video data from the request
            video_data = request.FILES.get("video")

            if not video_data:
                return JsonResponse({"error": _("Video file is required.")}, status=400)

            # Create a temporary file and write the video data to it
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in video_data.chunks():
                    temp_file.write(chunk)
                temp_video_path = temp_file.name

            # Extract face encoding from the video using the function from utils.face_analyzer
            try:
                combined_encoding = extract_encoding_from_video(temp_video_path)
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)
            finally:
                # Delete the temporary file
                os.remove(temp_video_path)

            # Save encoding to database
            face_encoding, created = FaceEncoding.objects.get_or_create(
                user=user
            )
            encoding_filename = f"face_encoding_{user.national_code}.pkl"

            if not created and face_encoding.encoding_file:
                if default_storage.exists(face_encoding.encoding_file.name):
                    default_storage.delete(face_encoding.encoding_file.name)

            encoding_file = ContentFile(
                pickle.dumps(
                    {
                        "combined": combined_encoding,  # Only store the combined encoding
                    }
                )
            )
            face_encoding.encoding_file.save(encoding_filename, encoding_file)
            face_encoding.save()

            return JsonResponse({"message": _("Face successfully saved from video.")})

        except Exception as e:
            return JsonResponse(
                {"error": _(f"Error processing video: {str(e)}")}, status=500
            )

    elif request.method == "GET":
        return render(request, "face_scanner/face_mesh_load.html")


@csrf_exempt
@login_required
def face_verification(request):
    if request.method == "POST":
        user = request.user
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Get the exam_id and image data from the request
            data = json.loads(request.body)
            image_data = data.get('imageData')
            exam_id = data.get('exam_id')

            # Get the Exam object
            exam = Exam.objects.get(id=exam_id)

            # Get the FaceEncoding object for the current user
            face_encoding_obj = FaceEncoding.objects.get(user=user)
            if not face_encoding_obj.encoding_file:
                return JsonResponse(
                    {"error": "No face encoding found for this user."}, status=400
                )

            # Get the path to the encoded face data
            encoding_file_path = face_encoding_obj.encoding_file.path

            # Convert base64 to image
            image_bytes = base64.b64decode(image_data.split(',')[1].encode())
            image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

            # Compare faces
            try:
                is_match, message = compare_face_with_encoding(image, encoding_file_path)
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)

            # If the face doesn't match, save the image
            if not is_match:
                print("Saving unrecognized face...")
                save_path = os.path.join(settings.MEDIA_ROOT, 'unrecognized', user.national_code, str(exam.id), 'images')
                os.makedirs(save_path, exist_ok=True)

                image_name = f"{user.username}_unrecognized_{timestamp}.jpg"
                image_path = os.path.join(save_path, image_name)
                print(f"image_path={image_path}")

                with open(os.path.join(settings.MEDIA_ROOT, image_path), "wb") as f:
                    f.write(image_bytes)

                UnrecognizedFace.objects.create(user=user, image=image_path, exam=exam)

            # Return response
            return JsonResponse({"match": str(is_match), "message": message})

        except Exam.DoesNotExist:
            return JsonResponse({"error": "Exam not found."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            print(f"Error in face_verification: {str(e)}")
            return JsonResponse({"error": f"Error processing image: {str(e)}"}, status=500)

    # For GET requests, you can return an error or a different response
    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)