from django.contrib import admin
from .models import Exam, Answer

# Register your models here.


class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    search_fields = ('title', 'question_file')
    # inlines = [AnswerInline]  # To display related answers in the Exam form

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('exam', 'user', 'score', 'start_time')
    search_fields = ('exam__title', 'user__username', 'score')

# Register the models with the admin site
admin.site.register(Exam, ExamAdmin)
admin.site.register(Answer, AnswerAdmin)
