from django.urls import path
from .views import ShearMassRatioExtractor, CheckYDBStatus, UploadYDB

urlpatterns = [
    path("upload_ydb", UploadYDB.as_view()),
    path("check_ydb_status", CheckYDBStatus.as_view()),
    path("shear_mass_ratio_extractor", ShearMassRatioExtractor.as_view()),
]
