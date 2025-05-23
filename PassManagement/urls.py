from django.urls import path
from . import views

urlpatterns = [
    path('results/', views.CheckPasswordView.as_view(), name='check_password'),
]