# Online Exam System

## Overview
This project is an online examination system that ensures secure and fair exams through facial recognition, audio recording, and tab change detection. The system is built using Django, Bootstrap, and JavaScript.

## Features
- **User Registration & Login:** Users must register and log in before accessing exams.
- **Face Scan for Exam Access:** Users must scan their face before starting an exam.
- **Excel-Based Exam Upload:** Exams can be defined by uploading an Excel file in a specific format.
- **Real-Time Face Monitoring:** The system continuously scans the user's face during the exam. If a different person is detected, the system captures an image and stores it.
- **Audio Recording & Speech Recognition:** The system records the user's audio and converts speech to text. Both the audio and text are stored.
- **Tab & Mouse Activity Tracking:** Detects tab switching and mouse movements outside the exam window. Logs the duration of inactivity.
- **Admin Panel:** Admins can access a dedicated panel to monitor all logged activities, including face detection alerts, recorded audio, and tab-switching data.
- **HTTPS Requirement:** The project must be deployed using HTTPS for security purposes.

## Technologies Used
- **Backend:** Django (Python)
- **Frontend:** Bootstrap (HTML, CSS, JavaScript)
- **Database:** PostgreSQL / SQLite
- **Face Recognition:** OpenCV / Deep Learning Models
- **Speech to Text:** SpeechRecognition Library / Google Web Speech API

## Setup Instructions
### Prerequisites
Ensure you have the following installed:
- Python 3.x
- Django
- PostgreSQL / SQLite
- Required Python libraries (listed in `requirements.txt`)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Amirhosseinmoghadam/Protected-Exam.git
   
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # For Linux/macOS
   venv\Scripts\activate      # For Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Deployment Instructions
1. Ensure the project is deployed using HTTPS.
2. Use a production-ready database (PostgreSQL is recommended).
3. Configure proper security settings in Django (`settings.py`).


## License
This project is licensed under [MIT License](LICENSE).
## Contact Us
For questions or feedback, please contact [Amirhosseinbavafa32@gmail.com].
