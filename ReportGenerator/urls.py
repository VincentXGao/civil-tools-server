from django.urls import path
from .views import StairCalculateSheetView, DownLoadFileView

urlpatterns = [
    path("down_load_file", DownLoadFileView.as_view(), name="down_load_file"),
]
