from django.urls import path
from .views import StairCalculateSheetView

urlpatterns = [
    path("stair_cal_sheet", StairCalculateSheetView.as_view(), name="stair_cal_sheet"),
]
