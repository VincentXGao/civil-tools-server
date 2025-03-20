import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

from decorators.request_decorators import check_post_data

import sys
import os

sys.path.append(r"D:\02-Coding\04-YJK_API\yjk-db-load")
from CivilTools.FigureGenerator.BasicPltPlotter import ShearMassRatioPlotter
import matplotlib

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
