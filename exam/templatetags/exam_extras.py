from django import template
from exam.models import Exam

register = template.Library()

@register.filter
def get_item(queryset, exam_id):
    try:
        return queryset.get(id=exam_id).title
    except Exam.DoesNotExist:
        return ""