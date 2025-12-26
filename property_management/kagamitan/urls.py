from django.urls import path
from . import views

app_name = 'kagamitan'

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('upload/', views.equipment_upload, name='equipment_upload'),
    path('report/', views.equipment_report, name='equipment_report'),
]
