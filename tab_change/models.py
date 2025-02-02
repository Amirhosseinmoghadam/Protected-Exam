from django.db import models
from django.utils.timezone import now
from datetime import timedelta
import os
from datetime import datetime
from accounts.models import CustomUser
from exam.models import Exam


# Create your models here.
class TabChange(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    tab_changes = models.JSONField(default=list)
    last_warning_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    warning_level = models.IntegerField(default=0)
    is_temporarily_banned = models.BooleanField(default=False)
    is_permanently_banned = models.BooleanField(default=False)
    temporary_ban_start = models.DateTimeField(null=True, blank=True)
    post_ban_changes = models.IntegerField(default=0)  # اضافه کردن فیلد جدید
    questions_version = models.IntegerField(default=1)

    def add_tab_change(self, action, user_agent, ip_address):
        current_changes = self.tab_changes if isinstance(self.tab_changes, list) else []
        
        current_time = now()
        
        # اگر این تغییر بعد از محرومیت موقت است، شمارنده post_ban_changes را افزایش بده
        if (self.temporary_ban_start and 
            not self.is_temporarily_banned and 
            self.warning_level >= 3):
            if action in ['tab-hidden', 'mouse-left']:
                self.post_ban_changes += 1
                self.save()
        
        current_changes.append({
            'action': action,
            'timestamp': current_time.isoformat(),
            'user_agent': user_agent,
            'ip_address': ip_address
        })
        
        self.tab_changes = current_changes
        self.save()

    def count_tab_changes(self):
        if self.warning_level >= 3 and self.temporary_ban_start:
            # بعد از محرومیت موقت، از شمارنده post_ban_changes استفاده کن
            return self.post_ban_changes
        else:
            # قبل از محرومیت موقت، از روش قبلی استفاده کن
            changes = self.tab_changes if isinstance(self.tab_changes, list) else []
            relevant_actions = ['tab-hidden', 'mouse-left']
            relevant_changes = [
                change for change in changes
                if change['action'] in relevant_actions
            ]
            return len(relevant_changes)

    def check_violations(self):
        current_time = now()
        
        # بررسی پایان محرومیت موقت
        if self.is_temporarily_banned:
            if current_time - self.temporary_ban_start >= timedelta(minutes=1):
                self.is_temporarily_banned = False
                self.post_ban_changes = 0  # ریست کردن شمارنده
                self.warning_level = 3  # شروع مرحله دوم
                self.questions_version += 1
                self.save()
                return 'ban_lifted'
            return None

        count = self.count_tab_changes()
        print(f"Current count: {count}, Warning level: {self.warning_level}, Post-ban changes: {self.post_ban_changes}")

        # مرحله اول (قبل از محرومیت موقت)
        if self.warning_level < 3 and not self.is_permanently_banned:
            if count >= 11:
                self.warning_level = 3
                self.is_temporarily_banned = True
                self.temporary_ban_start = current_time
                self.save()
                return 'temporary_ban'
            elif count >= 7 and self.warning_level < 2:
                self.warning_level = 2
                self.save()
                return 'warning_2'
            elif count >= 3 and self.warning_level < 1:
                self.warning_level = 1
                self.save()
                return 'warning_1'
        
        # مرحله دوم (بعد از محرومیت موقت)
        elif self.warning_level >= 3 and not self.is_permanently_banned:
            if count >= 7:
                self.is_permanently_banned = True
                self.save()
                return 'permanent_ban'
            elif count >= 5 and self.warning_level < 5:
                self.warning_level = 5
                self.save()
                return 'warning_final'
            elif count >= 3 and self.warning_level < 4:
                self.warning_level = 4
                self.save()
                return 'warning_post_ban_1'

        return None
