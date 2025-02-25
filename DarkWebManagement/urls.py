from django.urls import path
from . import views

urlpatterns = [
    path('extract-information/', views.DarkWebManagementView.as_view(), name='extract-information'),
]