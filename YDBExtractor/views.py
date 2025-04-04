import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.http import HttpResponse, HttpRequest
from YDBExtractor.models import FileInfo

from django.views import View

from decorators.request_decorators import check_post_data_specific_field

import sys
import os
import uuid

sys.path.append(r"D:\02-Coding\04-YJK_API\yjk-db-load")
sys.path.append(r"D:\000-GITHUB\yjk-db-load")
from CivilTools.YDBLoader import YDBLoader, YDBType
import matplotlib


# YDB文件的临时保存路径
YDB_FILE_TEMP_PATH = r".\temp\ydb"
if not os.path.exists(YDB_FILE_TEMP_PATH):
    os.makedirs(YDB_FILE_TEMP_PATH)


class CheckYDBStatus(APIView):
    @check_post_data_specific_field("hash")
    def post(self, request: HttpRequest, *args, **kwargs):
        data = json.loads(request.body)
        hash_code = data.get("hash")
        specific_records = FileInfo.objects.filter(HashCode=hash_code).filter(
            IsDeleted=False
        )
        if specific_records:
            if os.path.exists(specific_records[0].FilePath):
                return HttpResponse(
                    json.dumps(
                        {
                            "status": "existed",
                            "file_id": specific_records[0].id,
                            "file_uuid": specific_records[0].FilePath,
                        }
                    )
                )
            else:
                specific_records[0].IsDeleted = True
                specific_records[0].save()
        return HttpResponse(
            json.dumps({"status": "not_existed", "file_id": 0, "file_uuid": ""})
        )


class UploadYDB(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request: HttpRequest, *args, **kwargs):
        FILE_NAME = "YDBFile"
        HASH_CODE = "hash"
        if request.FILES.get(FILE_NAME):
            file = request.FILES[FILE_NAME]
            file_path = os.path.join(YDB_FILE_TEMP_PATH, str(uuid.uuid4()) + ".ydb")
            # file_path = f"{YDB_FILE_TEMP_PATH}\{uuid.uuid4()}.ydb"
            hash_code = request.POST.get(HASH_CODE)
            specific_records = FileInfo.objects.filter(HashCode=hash_code)
            if specific_records and os.path.exists(specific_records[0].FilePath):
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


class ShearMomentExtractor(APIView):
    @check_post_data_specific_field("ydb_file_id")
    def post(self, request: HttpRequest):
        data = json.loads(request.body)
        file_id = data.get("ydb_file_id")
        type = data.get("type")
        specific_records = FileInfo.objects.filter(id=file_id)
        if not specific_records:
            return Response(
                {"error": "Invalid file ID, you should upload your file first."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        file_path = specific_records[0].FilePath
        model = YDBLoader(file_path, YDBType.ResultYDB)
        seismic_result = model.get_seismic_result()
        wind_result = model.get_wind_result()
        result = []
        for i in range(len(seismic_result.floor_result)):
            temp_floor_seismic_result = seismic_result.floor_result[::-1][i]
            temp_floor_wind_result = wind_result.floor_result[::-1][i]
            if type == "shear":
                result.append(
                    {
                        "floor": temp_floor_seismic_result.floor_num,
                        "seismic_x": temp_floor_seismic_result.shear.x,
                        "seismic_y": temp_floor_seismic_result.shear.y,
                        "wind_x": temp_floor_wind_result.shear.x,
                        "wind_y": temp_floor_wind_result.shear.y,
                    }
                )
            else:
                result.append(
                    {
                        "floor": round(temp_floor_seismic_result.floor_num, 3),
                        "seismic_x": round(
                            temp_floor_seismic_result.moment.x / 1000, 3
                        ),
                        "seismic_y": round(
                            temp_floor_seismic_result.moment.y / 1000, 3
                        ),
                        "wind_x": round(temp_floor_wind_result.moment.x / 1000, 3),
                        "wind_y": round(temp_floor_wind_result.moment.y / 1000, 3),
                    }
                )
        return Response({"data": result})


class DriftExtractor(APIView):
    @check_post_data_specific_field("ydb_file_id")
    def post(self, request: HttpRequest):
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
        seismic_result = model.get_seismic_result()
        wind_result = model.get_wind_result()
        result = []
        for i in range(len(seismic_result.floor_result)):
            temp_seismic_result = seismic_result.floor_result[::-1][i]
            temp_wind_result = wind_result.floor_result[::-1][i]
            result.append(
                {
                    "floor": temp_seismic_result.floor_num,
                    "seismic_x": temp_seismic_result.drifts[0].drift_x,
                    "seismic_y": temp_seismic_result.drifts[0].drift_y,
                    "wind_x": temp_wind_result.drifts[0].drift_x,
                    "wind_y": temp_wind_result.drifts[0].drift_y,
                }
            )
        return Response({"data": result})


class DisplacementExtractor(APIView):
    @check_post_data_specific_field("ydb_file_id")
    def post(self, request: HttpRequest):
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
        seismic_result = model.get_seismic_result()
        wind_result = model.get_wind_result()
        result = []
        for i in range(len(seismic_result.floor_result)):
            temp_seismic_result = seismic_result.floor_result[::-1][i]
            temp_wind_result = wind_result.floor_result[::-1][i]
            result.append(
                {
                    "floor": temp_seismic_result.floor_num,
                    "seismic_x": temp_seismic_result.drifts[0].max_disp_x,
                    "seismic_y": temp_seismic_result.drifts[0].max_disp_y,
                    "wind_x": temp_wind_result.drifts[0].max_disp_x,
                    "wind_y": temp_wind_result.drifts[0].max_disp_y,
                }
            )
        return Response({"data": result})


class TestExtractor(APIView):
    @check_post_data_specific_field("ydb_file_id")
    def post(self, request: HttpRequest):
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
        seismic_result = model.get_seismic_result()
        result = []
        for temp_result in seismic_result.floor_result:
            result.append(
                {
                    "floor": temp_result.floor_num,
                    "drift_x": temp_result.drifts[0].drift_x,
                    "drift_y": temp_result.drifts[0].drift_y,
                }
            )
        return Response({"data": result})
