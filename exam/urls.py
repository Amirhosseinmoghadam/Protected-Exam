from django.urls import path
from . import views

urlpatterns = [
    path('exam/<int:exam_id>/', views.exam_view, name='exam_view'),
    path('finsh/', views.finish_view, name='finish'),
    path('not-time/', views.not_time_view, name='not-time'),
    path('get-exam/', views.get_exam, name='get-exam'),

    path('face_data_error/', views.face_data_error_page, name='face_data_error_page'),
    path('error/', views.exam_error, name='exam_error'),
    path('suspend/' , views.suspend_exam , name = 'suspend-page'),
    path('restart-exam/' , views.restart_exam , name = 'restart-exam'),
    path('ban/', views.permanent_ban_view, name='permanent-ban'),

    path('admin-dashboard/', views.admin_dashboard_exam, name='admin_dashboard'),
    path('admin-dashboard/step2/<int:exam_id>/', views.admin_dashboard_user_list, name='admin_dashboard_step2'),
    path('admin-dashboard/step3/<int:exam_id>/<int:user_id>/', views.admin_dashboard_checking, name='admin_dashboard_step3'),

]