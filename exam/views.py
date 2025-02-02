# views.py
import pytz
from django.db.models import Q
from exam.forms import ExamForm
from django.utils import timezone
from django.contrib import messages
from exam.models import Exam, Answer
from django.utils.timezone import now
from accounts.models import CustomUser
from tab_change.models import TabChange
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from sound_record.models import AudioRecording
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from face_scanner.models import FaceEncoding, UnrecognizedFace


@login_required
def exam_view(request, exam_id):
    """Create the exam page and give it the needed questions if not
    already added.

    Parameters:
        request (HTML request object): HTML request object
        exam_id (int) : The id of the exam you want questions for
    """
    exam = Exam.objects.get(id=exam_id)

    if exam.is_face_scan_needed:
        try:
            face_encoding = FaceEncoding.objects.get(user=request.user)
            if not face_encoding.encoding_file:
                messages.error(request, "Your face encoding file is missing.")
                return redirect('face_data_error_page')
        except FaceEncoding.DoesNotExist:
            messages.error(request, "You first need to scan your face.")
            return redirect('face_data_error_page')

    if Answer.objects.filter(user=request.user, exam=exam).first():
        messages.error(request, "You have already submitted this exam")
        return redirect('exam_error')

    # Check if the questions are already in the session
    if 'questions' not in request.session:
        request.session['questions'] = []
        exam_file = exam.assign_random_questions()
        # If the user's been suspended their questions will be deleted
        if f"exam{exam.id}_time" in request.session:
            del request.session[f'exam{exam.id}_time']

        # Prepare the data to be passed to the form: list of questions as dictionaries
        questions = []
        for i in range(exam.total_questions):
            row = exam_file[i]
            questions.append({
                'id': int(row['id']),
                'question': row['question'],
                'a': int(row['a']),
                'b': int(row['b']),
                'c': int(row['c']),
                'd': int(row['d']),
            })

        request.session['questions'] = questions

    else:
        questions = request.session['questions']

    current_time = timezone.now()
    delta_time = timedelta(hours=exam.exam_time.hour,
                           minutes=exam.exam_time.minute,
                           seconds=exam.exam_time.second)
    if f"exam{exam.id}_time" not in request.session:
        request.session[f'exam{exam.id}_time'] = (
            datetime.isoformat(current_time + delta_time))

    exam_time = datetime.fromisoformat(request.session[f"exam{exam.id}_time"])
    if exam.start > current_time or exam.end < current_time:
        redirect('not-time')

    if exam_time <= current_time:
        # Automatically submit the answers if time is up
        if 'questions' in request.session:
            form = ExamForm(request.POST or None,
                            questions=request.session['questions'])
            if form.is_valid():
                form.save(user=request.user, exam=exam, start_time=exam_time - delta_time)
                del request.session['questions']

        if f"exam{exam.id}_time" in request.session:
            del request.session[f'exam{exam.id}_time']
        return redirect('finish')

    form = ExamForm(request.POST or None, questions=questions)

    if request.method == 'POST' and form.is_valid():
        form.save(user=request.user, exam=exam, start_time=exam_time - delta_time)
        del request.session['questions']
        if f"exam{exam.id}_time" in request.session:
            del request.session[f'exam{exam.id}_time']
        return redirect('finish')  # Redirect to placeholder page after saving answers

    remaining_time = (timedelta(hours=exam_time.hour,
                                minutes=exam_time.minute,
                                seconds=exam_time.second)
                      - timedelta(hours=current_time.hour,
                                  minutes=current_time.minute,
                                  seconds=current_time.second))
    return render(request, 'exam/exam.html', {
        'form': form,
        'exam': exam,
        'remaining_time': int(remaining_time.total_seconds()),
        'check_voice': exam.is_voice_record_needed,
        'face_check': exam.is_face_scan_needed,

    })


@login_required
def finish_view(request):
    """Placeholder to show the successful end of the process """
    return render(request, 'exam/finish.html')


@login_required
def not_time_view(request):
    """Placeholder to show the incorrect time for the process """
    return render(request, 'exam/not-time.html')


@login_required
def get_exam(request):
    # Finding the first active exam
    current_time = now()
    exams = Exam.objects.filter(start__lte=current_time, end__gte=current_time)
    if not exams:
        messages.error(request, "There are no active exams right now")
        return redirect('exam_error')

    return render(request, 'exam/gexam.html', {"exams": exams})


def face_data_error_page(request):
    return render(request, 'exam/face_data_error.html', {
        'message': "first scan your face then start Quiz"
    })


def exam_error(request):
    return render(request, 'exam/no_exam_available.html')


@login_required
def suspend_exam(request):
    return render(request, 'exam/suspend.html', {'remaining_time': 10})


def restart_exam(request):
    del request.session['questions']
    return redirect('get-exam')


@login_required
def permanent_ban_view(request):
    return render(request, 'exam/ban.html')



#
# @user_passes_test(lambda u: u.is_staff)
# def admin_dashboard(request):
#     exams = Exam.objects.all()
#
#
#     users_data = {}
#
#     for exam in exams:
#         unrecognized_users = CustomUser.objects.filter(
#             Q(unrecognizedface__exam=exam) |
#             Q(tabchange__exam=exam) |
#             Q(audio_recordings__exam=exam)
#         ).distinct()
#
#         users_data[exam.id] = []
#         for user in unrecognized_users:
#             tab_changes = TabChange.objects.filter(user=user, exam=exam)
#             warnings = []
#             total_time_away_mouse = timedelta(0)  # برای نگهداری زمان خروج موس
#             total_time_away_tab = timedelta(0)  # برای نگهداری زمان تعویض تب
#             mouse_leave_count = 0  # شمارنده تعداد دفعات خروج موس
#             tab_change_count = 0  # شمارنده تعداد دفعات تعویض تب
#
#             for tab_change in tab_changes:
#                 if tab_change.tab_changes:
#                     for i in range(len(tab_change.tab_changes)):
#                         change = tab_change.tab_changes[i]
#
#                         if 'action' in change and change['action'] == 'mouse-left':
#                             mouse_leave_count += 1
#                             if 'timestamp' in change:
#                                 try:
#                                     # پیدا کردن زمان  ورود بعدی
#                                     next_entry_time = None
#                                     for j in range(i + 1, len(tab_change.tab_changes)):
#                                         next_change = tab_change.tab_changes[j]
#                                         if 'action' in next_change and next_change['action'] == 'mouse-entered':
#                                             if 'timestamp' in next_change:
#                                                 next_entry_time = datetime.fromisoformat(next_change['timestamp'].replace("Z", "+00:00"))
#                                                 break
#
#                                     # محاسبه اختلاف زمان
#                                     if next_entry_time:
#                                         current_exit_time = datetime.fromisoformat(change['timestamp'].replace("Z", "+00:00"))
#                                         time_away = next_entry_time - current_exit_time
#                                         total_time_away_mouse += time_away
#                                 except ValueError:
#                                     print(f"Error parsing timestamp: {change.get('timestamp')}")
#
#                         elif 'action' in change and change['action'] == 'tab-hidden':
#                             tab_change_count += 1
#                             if 'timestamp' in change:
#                                 try:
#                                     # پیدا کردن زمان ورود بعدی
#                                     next_entry_time = None
#                                     for j in range(i + 1, len(tab_change.tab_changes)):
#                                         next_change = tab_change.tab_changes[j]
#                                         if 'action' in next_change and next_change['action'] == 'tab-visible':
#                                             if 'timestamp' in next_change:
#                                                 next_entry_time = datetime.fromisoformat(next_change['timestamp'].replace("Z", "+00:00"))
#                                                 break
#
#                                     # محاسبه اختلاف زمان
#                                     if next_entry_time:
#                                         current_exit_time = datetime.fromisoformat(change['timestamp'].replace("Z", "+00:00"))
#                                         time_away = next_entry_time - current_exit_time
#                                         total_time_away_tab += time_away
#                                 except ValueError:
#                                     print(f"Error parsing timestamp: {change.get('timestamp')}")
#
#             audio_recordings = AudioRecording.objects.filter(user=user, exam=exam)
#             unrecognized_faces = UnrecognizedFace.objects.filter(user=user, exam=exam)
#
#             users_data[exam.id].append({
#                 'user': user,
#                 'face_status': 'ناموفق' if unrecognized_faces else 'موفق',
#                 'tab_change_warnings': warnings,
#                 'audio_recordings': audio_recordings,
#                 'unrecognized_faces': unrecognized_faces,
#                 'total_time_away_mouse': total_time_away_mouse.total_seconds(),  # اضافه شدن به context
#                 'total_time_away_tab': total_time_away_tab.total_seconds(),  # اضافه شدن به context
#                 'mouse_leave_count': mouse_leave_count,  # تعداد دفعات خروج موس
#                 'tab_change_count': tab_change_count,  # تعداد دفعات تعویض تب
#             })
#
#     context = {
#         'users_data': users_data,
#         'exams': exams,
#     }
#     return render(request, 'exam/admin_dashboard.html', context)


from django.shortcuts import get_object_or_404

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_exam(request):
    exams = Exam.objects.all()
    context = {
        'exams': exams,
    }
    return render(request, 'exam/admin_dashboard_exam.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_user_list(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    # کاربرانی که در این آزمون شرکت کرده‌اند
    participants = CustomUser.objects.filter(answer__exam=exam).distinct()
    context = {
        'exam': exam,
        'participants': participants,
    }
    return render(request, 'exam/admin_dashboard_user_list.html', context)


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_checking(request, exam_id, user_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    user = get_object_or_404(CustomUser, pk=user_id)

    # See if user has submitted an answer to this exam, redirect if not
    if not Answer.objects.filter(exam=exam, user=user).exists():
        return render(request, 'exam/user_not_in_exam.html')

    tab_changes = TabChange.objects.filter(user=user, exam=exam)
    answer = Answer.objects.get(user=user, exam=exam)
    print(answer.submit_time)
    total_time_away_mouse = timedelta(0)
    total_time_away_tab = timedelta(0)
    mouse_leave_count = 0
    tab_change_count = 0

    for tab_change in tab_changes:
        if tab_change.tab_changes:
            for i in range(len(tab_change.tab_changes)):
                change = tab_change.tab_changes[i]

                if 'action' in change and change['action'] == 'mouse-left':
                    mouse_leave_count += 1
                    if 'timestamp' in change:
                        try:
                            next_entry_time = None
                            for j in range(i + 1, len(tab_change.tab_changes)):
                                next_change = tab_change.tab_changes[j]
                                if 'action' in next_change and next_change['action'] == 'mouse-entered':
                                    if 'timestamp' in next_change:
                                        next_entry_time = datetime.fromisoformat(next_change['timestamp'].replace("Z", "+00:00"))
                                        break

                            if next_entry_time:
                                current_exit_time = datetime.fromisoformat(change['timestamp'].replace("Z", "+00:00"))
                                time_away = next_entry_time - current_exit_time
                                total_time_away_mouse += time_away
                        except ValueError:
                            print(f"Error parsing timestamp: {change.get('timestamp')}")

                elif 'action' in change and change['action'] == 'tab-hidden':
                    tab_change_count += 1
                    if 'timestamp' in change:
                        try:
                            next_entry_time = None
                            for j in range(i + 1, len(tab_change.tab_changes)):
                                next_change = tab_change.tab_changes[j]
                                if 'action' in next_change and next_change['action'] == 'tab-visible':
                                    if 'timestamp' in next_change:
                                        next_entry_time = datetime.fromisoformat(next_change['timestamp'].replace("Z", "+00:00"))
                                        break

                            if next_entry_time:
                                current_exit_time = datetime.fromisoformat(change['timestamp'].replace("Z", "+00:00"))
                                time_away = next_entry_time - current_exit_time
                                total_time_away_tab += time_away
                        except ValueError:
                            print(f"Error parsing timestamp: {change.get('timestamp')}")

    audio_recordings = AudioRecording.objects.filter(user=user, exam=exam)
    unrecognized_faces = UnrecognizedFace.objects.filter(user=user, exam=exam)

    context = {
        'exam': exam,
        'user': user,
        'answer': answer,
        # 'face_status': 'ناموفق' if unrecognized_faces else 'موفق',
        'total_time_away_mouse': total_time_away_mouse.total_seconds(),
        'total_time_away_tab': total_time_away_tab.total_seconds(),
        'mouse_leave_count': mouse_leave_count,
        'tab_change_count': tab_change_count,
        'audio_recordings': audio_recordings,
        'unrecognized_faces': unrecognized_faces,
    }
    return render(request, 'exam/admin_dashboard_checking.html', context)