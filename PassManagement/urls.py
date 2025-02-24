from django.urls import path
from . import views

urlpatterns = [
    path('create-password/', views.CheckPasswordView.as_view(), name='check_password'),
]
