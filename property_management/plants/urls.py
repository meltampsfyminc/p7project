from django.urls import path
from . import views

app_name = 'plants'

urlpatterns = [
    path('', views.plant_list, name='plant_list'),
    path('upload/', views.plant_upload, name='plant_upload'),
]
