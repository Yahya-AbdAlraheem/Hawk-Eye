from django.urls import path
from . import views  

urlpatterns = [
    path('', views.WelcomePage, name='WelcomePage'),  
    path('Hawk_Eye/', views.HomePage, name='HomePage'),
    path('Create_Password/', views.CreatePassword, name='CreatePassword'),
    path('About_Us/', views.AboutUs, name='AboutUs'),
    path('Contact/', views.Contact, name='Contact')
]
