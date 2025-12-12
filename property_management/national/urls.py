from django.urls import path
from . import views

app_name = "national"

urlpatterns = [
    path("", views.district_list, name="district_list"),
    path("district/<str:dcode>/locals/", views.local_list, name="local_list"),
    path("district/<str:dcode>/summary/", views.district_summary, name="district_summary"),
    path("local/<int:local_id>/reports/", views.report_list, name="report_list"),
    path("report/<int:report_id>/", views.report_detail, name="report_detail"),
    path("upload/", views.upload_file, name="upload"),
]

