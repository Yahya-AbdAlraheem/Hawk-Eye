# URLManagement/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('check-url/', views.check_url, name='Check_URL'),
]
