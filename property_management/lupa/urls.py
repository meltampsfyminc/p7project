from django.urls import path
from . import views

app_name = 'lupa'

urlpatterns = [
    path('', views.land_list, name='land_list'),
    path('upload/', views.land_upload, name='land_upload'),
    path('create/', views.land_create, name='land_create'),
    path('<int:pk>/', views.land_detail, name='land_detail'),
    path('<int:pk>/update/', views.land_update, name='land_update'),
    path('<int:pk>/delete/', views.land_delete, name='land_delete'),
]
