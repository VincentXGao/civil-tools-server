from django.urls import re_path

from .consumers import StairReportConsumer

websocket_urlpatterns = [
    re_path(r"ws/stair_report_generate", StairReportConsumer.as_asgi()),
]
