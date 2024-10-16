from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
from django.views.generic.base import TemplateView

from django.urls import path


urlpatterns = [
	path('upload/', v.UploadImageViewSet.as_view()),
]