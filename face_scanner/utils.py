import cv2
import dlib
import numpy as np
import pickle
import face_recognition

SHAPE_PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
FACE_REC_MODEL_PATH = "dlib_face_recognition_resnet_model_v1.dat"


def extract_face_encoding(image):
    """
    Extracts face encodings from the given image.
    """
    try:
        # Detect face locations in the image
        face_locations = face_recognition.face_locations(image)
        # Extract face encodings for the detected locations
        encodings = face_recognition.face_encodings(image, face_locations)

        if len(encodings) > 0:
            # Return the first face encoding found
            return encodings[0]
        else:
            # Raise an error if no face is detected
            raise ValueError("No face detected in the image.")
    except Exception as e:
        raise ValueError(f"Error extracting face encoding from image: {e}")


def extract_encoding_from_video(video_path):
    """
    Extracts face encodings from the given video.
    """

    cap = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not cap.isOpened():
        raise ValueError(f"Error opening video file: {video_path}")

    face_detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(SHAPE_PREDICTOR_PATH)
    face_rec_model = dlib.face_recognition_model_v1(FACE_REC_MODEL_PATH)

    face_encodings = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Detect face and extract encoding
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray_img)

        if len(faces) > 0:
            for face in faces:  # Iterate through all detected faces
                shape = shape_predictor(gray_img, face)
                face_encoding = np.array(
                    face_rec_model.compute_face_descriptor(frame, shape)
                )
                face_encodings.append(face_encoding)

        # Process every 5th frame to speed up processing
        for i in range(4):
            ret = cap.grab()
            if not ret:
                break

    cap.release()

    if len(face_encodings) == 0:
        raise ValueError(f"No face detected in the video (processed {frame_count} frames).")

    # Calculate the combined encoding
    combined_encoding = np.mean(face_encodings, axis=0)
    return combined_encoding


def compare_face_with_encoding(image, encoding_file):
    """
    Compares a new face image with stored face encodings.
    """
    try:
        # Load stored face encodings from the file
        with open(encoding_file, "rb") as f:
            stored_encodings = pickle.load(f)

        # Extract face encoding from the new image
        new_encoding = extract_face_encoding(image)  # Use extract_face_encoding for images

        # Get the stored combined encoding
        stored_encoding = stored_encodings["combined"]

        # Calculate the distance between the new encoding and the stored encoding
        distance = np.linalg.norm(new_encoding - stored_encoding)

        # Return True if the distance is below the threshold, indicating a match
        return distance < 0.5, f"Matched with distance: {distance}"

    except ValueError as e:
        return False, str(e)