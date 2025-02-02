from django.urls import path
from . import views

urlpatterns = [
    path('create-password/', views.check_password_view, name='check_password'),
]