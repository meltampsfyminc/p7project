from django.urls import path
from . import views

app_name = 'gusali'

urlpatterns = [
    path('', views.building_list, name='building_list'),
    path('<int:pk>/', views.building_detail, name='building_detail'),
    path('upload/', views.building_upload, name='building_upload'),
    path('report/', views.building_report, name='building_report'),
]
