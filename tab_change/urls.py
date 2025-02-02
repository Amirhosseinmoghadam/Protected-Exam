from django.urls import path
from . import views

urlpatterns = [
    path("track/" , views.track_tab_change , name="tab-change"),

]
