from django.urls import path
from . import views

urlpatterns = [
    path('search_in_dark_web/', views.search_darkweb, name='extract-information'),
     path('results/', views.get_results, name='get_results'),
]
