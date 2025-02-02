from django.urls import path, include
from django.conf.urls.static import static
from .views import *

urlpatterns = [

    # for scanning face
    # path('scan/', scan_and_store_face, name='start_scan'),

    #
    # path('scan_with_video/', recognize_face_with_video, name='scan_with_video'),

    path("scan-face/", scan_and_store_face, name="scan_and_store_face"),

    path('face-mesh_load/', face_mesh_view_load, name='face_mesh_view_load'),

    path("face-match/", face_verification, name="face-match"),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
