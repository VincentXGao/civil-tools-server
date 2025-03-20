from django.urls import path
from .views import ShearMassRatioView

urlpatterns = [
    path("shear_mass_ratio", ShearMassRatioView.as_view(), name="shear_mass_ratio"),
]
