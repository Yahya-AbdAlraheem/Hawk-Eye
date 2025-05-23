from django.urls import path
from . import views

urlpatterns = [
    path('', views.dns_lookup, name='dns_lookup'),
    path('download_pdf/<str:domain_name>/', views.download_pdf, name='download_pdf'),  # تعديل هنا
]
