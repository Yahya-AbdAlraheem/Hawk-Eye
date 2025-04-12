from django.urls import path
from . import views

urlpatterns = [
    path('check-file/', views.Check_File, name='Check_File'),
]
