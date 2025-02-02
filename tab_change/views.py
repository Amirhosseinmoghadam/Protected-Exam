from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from datetime import timedelta
import os
from django.conf import settings
from exam.models import Exam
from .models import TabChange
# Create your views here.

@csrf_exempt
def track_tab_change(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        exam_id = data.get('exam_id')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = request.META.get('REMOTE_ADDR')
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=403)

        try:
            exam = Exam.objects.get(id=exam_id)
            tab_change, created = TabChange.objects.get_or_create(
                user=user, 
                exam=exam,
                defaults={
                    'tab_changes': [],
                    'post_ban_changes': 0  # مقدار اولیه برای فیلد جدید
                }
            )
        except Exam.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid exam ID'}, status=400)

    
        if tab_change.is_permanently_banned:
            print("User is permanently banned")
            return JsonResponse({
                'status': 'redirect',
                'message': 'شما به دلیل تخلف مکرر از آزمون محروم شده‌اید.',
                'redirect_url': '/exam/ban/',
                'action': 'permanent_ban'
            })

        
        if tab_change.is_temporarily_banned:
            time_remaining = (tab_change.temporary_ban_start + timedelta(minutes=1)) - now()
            if time_remaining.total_seconds() > 0:
                minutes = int(time_remaining.total_seconds() / 60)
                seconds = int(time_remaining.total_seconds() % 60)
                return JsonResponse({
                    'status': 'redirect',
                    'redirect_url': '/exam/suspend/',
                    'message': f'شما به مدت {minutes} دقیقه و {seconds} ثانیه از آزمون محروم هستید.',
                    'action': 'temporary_ban'
                })
        
        if action in ['tab-hidden', 'tab-visible', 'mouse-left', 'mouse-entered']:
            tab_change.add_tab_change(action, user_agent, ip_address)
            violation_status = tab_change.check_violations()
            
            messages = {
                'warning_1': 'اخطار اول: شما ۳ بار از صفحه آزمون خارج شده‌اید.',
                'warning_2': 'اخطار دوم: شما ۷ بار از صفحه آزمون خارج شده‌اید.',
                'temporary_ban': 'شما به دلیل ۱۱ بار خروج از صفحه به مدت ۱ دقیقه از آزمون محروم می‌شوید.',
                'warning_post_ban_1': 'اخطار پس از محرومیت: شما ۳ بار از صفحه آزمون خارج شده‌اید.',
                'warning_final': 'اخطار نهایی: در صورت ۲ بار دیگر خروج از صفحه، به طور دائم محروم خواهید شد.',
                'permanent_ban': 'شما به دلیل تخلف مکرر به طور دائم از آزمون محروم شده‌اید.',
                'ban_lifted': 'محرومیت موقت شما به پایان رسید. لطفاً به سؤالات جدید پاسخ دهید.'
            }

            if violation_status:
                print(f"Violation status: {violation_status}")
                return JsonResponse({
                    'status': 'warning',
                    'message': messages[violation_status],
                    'action': violation_status
                })

            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)