from django.urls import path
from .views import ShearMassRatioView, ShearMomentPlotterView, DriftPlotterView

urlpatterns = [
    path("shear_mass_ratio", ShearMassRatioView.as_view(), name="shear_mass_ratio"),
    path("shear_moment", ShearMomentPlotterView.as_view(), name="shear_moment"),
    path("drift", DriftPlotterView.as_view(), name="drift"),
]
