import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, HttpRequest
from YDBExtractor.models import FileInfo

from decorators.request_decorators import check_post_data_specific_field

import sys
import os
import uuid

sys.path.append(r"D:\02-Coding\04-YJK_API\yjk-db-load")
sys.path.append(r"D:\000-GITHUB\yjk-db-load")
from CivilTools.FigureGenerator.BasicPltPlotter import ShearMassRatioPlotter
from CivilTools.YDBLoader import YDBLoader, YDBType
import matplotlib

matplotlib.use("Agg")
# YDB文件的临时保存路径
YDB_FILE_TEMP_PATH = r".\temp\ydb"
if not os.path.exists(YDB_FILE_TEMP_PATH):
    os.makedirs(YDB_FILE_TEMP_PATH)


class CheckYDBStatus(APIView):
    def post(self, request: HttpRequest, *args, **kwargs):
        data = json.loads(request.body)
        try:
            hash_code = data.get("hash")
            specific_records = FileInfo.objects.filter(HashCode=hash_code)
            if specific_records:
                return HttpResponse(
                    json.dumps(
                        {
                            "status": "existed",
                            "file_id": specific_records[0].id,
                            "file_uuid": specific_records[0].FilePath,
                        }
                    )
                )
            return HttpResponse(
                json.dumps({"status": "not_existed", "file_id": 0, "file_uuid": ""})
            )
        except:
            return Response(
                {"error": 'Missing "hash" field.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UploadYDB(APIView):
    def post(self, request: HttpRequest, *args, **kwargs):
        FILE_NAME = "YDBFile"
        HASH_CODE = "hash"
        if request.FILES.get(FILE_NAME):
            file = request.FILES[FILE_NAME]
            file_path = f"{YDB_FILE_TEMP_PATH}\{uuid.uuid4()}.ydb"
            hash_code = request.data.get(HASH_CODE)
            specific_records = FileInfo.objects.filter(HashCode=hash_code)
            if specific_records:
                # 如果找到了哈希值相同的文件，则不再保存，返回已有文件的路径和id
                return HttpResponse(
                    json.dumps(
                        {
                            "status": "existed",
                            "file_id": specific_records[0].id,
                            "file_uuid": specific_records[0].FilePath,
                        }
                    )
                )
            with open(file_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            file_info = self.save_file_record(hash_code, file_path)
            # 没找到则保存文件至指定目录，并返回路径和id
            return HttpResponse(
                json.dumps(
                    {
                        "status": "saved",
                        "file_id": file_info.id,
                        "file_uuid": file_info.FilePath,
                    }
                )
            )
        return Response(
            {"error": 'Missing file in "YDBFile" field.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def save_file_record(self, hash, path):
        file_info = FileInfo(HashCode=hash, FilePath=path)
        # 保存到数据库
        file_info.save()
        return file_info


class ShearMassRatioExtractor(APIView):
    @check_post_data_specific_field("ydb_file_id")
    def post(self, request: HttpRequest, *args, **kwargs):

        data = json.loads(request.body)
        file_id = data.get("ydb_file_id")
        specific_records = FileInfo.objects.filter(id=file_id)
        if not specific_records:
            return Response(
                {"error": "Invalid file ID, you should upload your file first."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        file_path = specific_records[0].FilePath
        model = YDBLoader(file_path, YDBType.ResultYDB)
        mass = model.get_mass_result()
        force = model.get_seismic_result()
        result = []
        up_mass = 0
        for i in range(len(mass.mass_list)):
            temp_mass = mass.mass_list[::-1][i]
            temp_force = force.floor_result[::-1][i]
            temp_shear_mass_ratio_result = {
                "floor": temp_mass.floor_num,
                "shear_x": temp_force.shear.x,
                "shear_y": temp_force.shear.y,
                "mass": round((temp_mass.total_load) * 10 + up_mass, 4),
            }
            up_mass = temp_shear_mass_ratio_result["mass"]
            result.append(temp_shear_mass_ratio_result)

        return Response({"data": result})
