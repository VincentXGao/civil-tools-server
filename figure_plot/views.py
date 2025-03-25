import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

from decorators.request_decorators import check_post_data

import sys
import os

sys.path.append(r"D:\02-Coding\04-YJK_API\yjk-db-load")
sys.path.append(r"D:\000-GITHUB\yjk-db-load")
from CivilTools.FigureGenerator.SeismicReport import (
    ShearMassRatioPlotter,
    ShearMomentPlotter,
)
import matplotlib
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = [
    "WenQuanYi Zen Hei",
    "SimHei",
]  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 14

matplotlib.use("Agg")


class ShearMassRatioView(APIView):
    @check_post_data
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body).get("data")
        shear_x = data.get("shear_x")
        shear_y = data.get("shear_y")
        mass = data.get("mass")
        limitation = data.get("limitation")
        my_plot = ShearMassRatioPlotter(floor_num=len(mass))
        my_plot.set_data(shear_x[::-1], shear_y[::-1], mass[::-1])
        my_plot.set_limit(limitation)
        my_plot.plot()
        buffer = my_plot.save_to_stream()
        return HttpResponse(
            buffer,
            content_type="image/png",
        )


class ShearMomentPlotterView(APIView):
    @check_post_data
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body).get("data")
        wind_x = data.get("wind_x")
        wind_y = data.get("wind_y")
        seismic_x = data.get("seismic_x")
        seismic_y = data.get("seismic_y")
        type = data.get("plot_type")
        my_plot = ShearMomentPlotter(floor_num=len(wind_x), type=type)
        my_plot.set_data(wind_x[::-1], wind_y[::-1], seismic_x[::-1], seismic_y[::-1])
        my_plot.kwargs_y["marker"] = "x"
        my_plot.kwargs_y["ms"] = 5
        my_plot.kwargs_y["color"] = "r"
        my_plot.plot()
        buffer = my_plot.save_to_stream()
        return HttpResponse(
            buffer,
            content_type="image/png",
        )
