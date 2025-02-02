from django.contrib import admin
from django.utils.html import format_html
from .models import FaceEncoding, UnrecognizedFace

@admin.register(FaceEncoding)
class FaceEncodingAdmin(admin.ModelAdmin):
    """
    مدیریت مدل FaceEncoding در پنل ادمین جنگو.
    """
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__national_code')
    readonly_fields = ('created_at', 'encoding_file_preview')
    list_filter = ('created_at',)

    def encoding_file_preview(self, obj):
        """
        نمایش لینک فایل انکودینگ در پنل ادمین.
        """
        if obj.encoding_file:
            file_url = obj.encoding_file.url
            file_name = obj.encoding_file.name.split('/')[-1]

            if file_name.endswith('.pkl'):
                return format_html('<a href="{}" target="_blank">Download {}</a>', file_url, file_name)
            else:
                return format_html('<a href="{}" target="_blank">View {}</a>', file_url, file_name)
        else:
            return 'No File'

    encoding_file_preview.short_description = 'Encoding File'


@admin.register(UnrecognizedFace)
class UnrecognizedFaceAdmin(admin.ModelAdmin):
    """
    مدیریت مدل UnrecognizedFace در پنل ادمین جنگو.
    """
    list_display = ('user', 'created_at', 'image_preview')
    search_fields = ('user__username', 'user__national_code')
    readonly_fields = ('created_at', 'image_preview')
    list_filter = ('created_at',)
    exclude = ('image',)  # حذف فیلد تصویر از فرم ویرایش

    def image_preview(self, obj):
        """
        نمایش پیش‌نمایش تصویر در پنل ادمین.
        """
        if obj.image:
            return format_html('<img src="{}" style="width: 400px; height:auto;" />', obj.image.url)
        else:
            return 'No Image'

    image_preview.short_description = 'Image'