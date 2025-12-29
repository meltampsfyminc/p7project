from django.urls import path
from . import views

app_name = 'kagamitan'

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('<int:pk>/', views.item_detail, name='item_detail'),
    path('upload/', views.item_upload, name='item_upload'),
    path('report/', views.item_report, name='item_report'),
]
