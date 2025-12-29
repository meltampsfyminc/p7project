from django.urls import path
from . import views

app_name = 'lupa'

urlpatterns = [
    path('', views.land_list, name='land_list'),
    path('upload/', views.land_upload, name='land_upload'),
]
