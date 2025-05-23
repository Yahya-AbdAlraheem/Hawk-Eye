from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_view, name='TelegramManagement'),
    path('results/', views.search_view, name='telegram_lookup'),
]