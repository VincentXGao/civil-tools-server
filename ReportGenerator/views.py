import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.http import FileResponse

from decorators.request_decorators import check_post_data


import sys
import os

# YDB文件的临时保存路径
STAIR_REPORT_FILE_TEMP_PATH = r".\temp\stair_report"
if not os.path.exists(STAIR_REPORT_FILE_TEMP_PATH):
    os.makedirs(STAIR_REPORT_FILE_TEMP_PATH)


from CivilTools.ReportGenerator import StairCalculationReport


class StairCalculateSheetView(APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        file_path = os.path.join(STAIR_REPORT_FILE_TEMP_PATH, "ttt_test__ttt.docx")
        if not os.path.exists(file_path):
            creator = StairCalculationReport()
            creator.set_stair_data()
            creator.set_calculate_info()
            creator.create()
            creator.save_to_file(file_path)
        return FileResponse(open(file_path, "rb"), filename="document.pdf")
