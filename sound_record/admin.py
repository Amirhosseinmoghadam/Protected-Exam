# from django.contrib import admin
# from .models import AudioRecording
# # Register your models here.
#
# @admin.register(AudioRecording)
# class AudioRecordingAdmin(admin.ModelAdmin):
#     list_display = ('user', 'file_name', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('user__phone_number',)
#     def file_name(self, obj):
#         return obj.file.name.split('/')[-1]
#     file_name.short_description = 'File Name'




# sound_record/admin.py

from django.contrib import admin
from .models import AudioRecording

class AudioRecordingAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'created_at', 'text_preview')  # فیلدهای قابل نمایش در لیست
    list_filter = ('user', 'exam')  # فیلترها
    search_fields = ('user__username', 'exam__title', 'text')  # فیلدهای قابل جستجو
    readonly_fields = ('created_at',)  # فیلدهای فقط خواندنی

    def text_preview(self, obj):
        return obj.text[:500] + '...' if obj.text else ''  # نمایش خلاصه‌ای از متن

    text_preview.short_description = 'Text Preview'  # عنوان ستون

admin.site.register(AudioRecording, AudioRecordingAdmin)