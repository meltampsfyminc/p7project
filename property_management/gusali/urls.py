from django.urls import path
from . import views

app_name = 'gusali'

urlpatterns = [
    path('', views.building_list, name='building_list'),
    path('<int:pk>/', views.building_detail, name='building_detail'),
    path('upload/', views.building_upload, name='building_upload'),
    path('report/', views.building_report, name='building_report'),
    path('create/', views.building_create, name='building_create'),
    path('<int:pk>/update/', views.building_update, name='building_update'),
    path('<int:pk>/delete/', views.building_delete, name='building_delete'),
    path('<int:building_pk>/yearly-record/create/', views.yearly_record_create, name='yearly_record_create'),
    path('yearly-record/<int:pk>/update/', views.yearly_record_update, name='yearly_record_update'),
    path('yearly-record/<int:pk>/delete/', views.yearly_record_delete, name='yearly_record_delete'),
    path('upload-csv/', views.gusali_csv_upload, name='gusali_csv_upload'),
    path("ajax/load-locals/", views.load_locals, name="ajax_load_locals"),

]
