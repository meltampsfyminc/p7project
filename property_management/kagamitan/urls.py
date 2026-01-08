from django.urls import path
from . import views

app_name = 'kagamitan'

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('<int:pk>/', views.item_detail, name='item_detail'),
    path('create/', views.item_create, name='item_create'),
    path('<int:pk>/update/', views.item_update, name='item_update'),
    path('<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('upload-csv/', views.kagamitan_csv_upload, name='kagamitan_csv_upload'),
    path('upload/', views.item_upload, name='item_upload'),
    path('category/<str:category>/', views.item_list_by_category, name='item_list_by_category'),
]