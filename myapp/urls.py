from django.urls import path
from . import views
from .views import camera_live


urlpatterns = [
    path('', views.Camera.as_view(), name='camera'),
    path('video_feed/', views.camera_live, name='camera_live'),
]