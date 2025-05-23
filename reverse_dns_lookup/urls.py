from django.urls import path
from . import views

urlpatterns = [
    path('', views.reverse_dns_lookup, name='reverse_dns_lookup'),
    path('download_pdf/<str:ip_address>/', views.download_pdf, name='download_pdf'),
]
