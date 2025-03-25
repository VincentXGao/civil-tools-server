from django.urls import path
from .views import (
    ShearMassRatioExtractor,
    CheckYDBStatus,
    UploadYDB,
    ShearMomentExtractor,
    DriftExtractor,
    DisplacementExtractor,
    TestExtractor,
)

urlpatterns = [
    path("upload_ydb", UploadYDB.as_view()),
    path("check_ydb_status", CheckYDBStatus.as_view()),
    path("shear_mass_ratio_extractor", ShearMassRatioExtractor.as_view()),
    path("shear_moment_extractor", ShearMomentExtractor.as_view()),
    path("drift_extractor", DriftExtractor.as_view()),
    path("displacement_extractor", DisplacementExtractor.as_view()),
    path("test_extract", TestExtractor.as_view()),
]
