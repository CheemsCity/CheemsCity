"""remote_control URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from homepage import views

urlpatterns = [
    path('', views.index, name="Homepage"), #lui è il template html della homepge
    path('camera_stream', views.camera_stream, name="camera_stream"), #lui è la vista che gestisce il box di streaming video
    path('camera_calibration',views.camera_calibration, name="camera_calibration"),
    path('CameraCalibration',views.CameraCalibration, name="CameraCalibration"),
]
