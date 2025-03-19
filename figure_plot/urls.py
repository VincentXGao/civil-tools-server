from django.urls import path
from .views import simple_api, shear_mass_ratio

urlpatterns = [
    path("", simple_api, name="simple_api"),
    path("shear_mass_ratio", shear_mass_ratio, name="shear_mass_ratio"),
]
