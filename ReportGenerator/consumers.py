from multiprocessing.managers import BaseManager
import json, io, sys, time
from channels.generic.websocket import WebsocketConsumer
from Utils.SHA256 import str_to_sha256

from CivilTools.ReportGenerator import StairCalculationReport
from CivilTools.YDBLoader.BuildingDefine.StairPart import StairPart, Position
import CivilTools as CT
from ReportGenerator.models import StairSheetGenerateInfo

import uuid
import os

print(CT.__version__, "consumer")
# YDB文件的临时保存路径
STAIR_REPORT_FILE_TEMP_PATH = r".\temp\stair_report"
if not os.path.exists(STAIR_REPORT_FILE_TEMP_PATH):
    os.makedirs(STAIR_REPORT_FILE_TEMP_PATH)


def create_stair_sheet_report(stairs, global_info):
    file_path = os.path.join(STAIR_REPORT_FILE_TEMP_PATH, str(uuid.uuid4()) + ".docx")
    print(file_path)
    creator = StairCalculationReport()
    stair_list = []
    for s in stairs:
        print(s)
        h = s["stairHeight"]
        l1 = s["leftSlabLen"]
        l2 = s["mainSlabLen"]
        l3 = s["rightSlabLen"]
        t1 = s["leftSlabThick"]
        t2 = s["mainSlabThick"]
        t3 = s["rightSlabThick"]
        offset_1 = s["leftBeamOffset"]
        offset_2 = s["rightBeamOffset"]
        sp = StairPart(
            Position(
                0,
                h,
                0,
                l1,
                l1 + l2,
                l1 + l2 + l3,
            ),
            13,
        )
        sp.set_beam_offset(1, offset_1)
        sp.set_beam_offset(2, offset_2)
        sp.set_thickness(t1, t2, t3)
        stair_list.append(sp)
    creator.set_stair_data(stair_list)
    creator.set_calculate_info()
    creator.create()
    creator.save_to_file(file_path)
    return file_path


class StairReportConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({"status": "connected! Let's generate report!"}))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data_hash = str_to_sha256(text_data)
        specific_records = StairSheetGenerateInfo.objects.filter(HashCode=data_hash)
        valid = False
        if specific_records:
            valid, target_file_path = self.has_valid_record(specific_records)
        if valid:
            self.send(
                text_data=json.dumps(
                    {
                        "status": "file existed",
                        "canClose": True,
                        "filePath": target_file_path,
                    }
                )
            )
        else:
            stairs = text_data_json["stairs"]
            global_info = text_data_json["globalInfo"]
            file_path = create_stair_sheet_report(stairs, global_info)
            record = StairSheetGenerateInfo(
                CTVersion=CT.__version__,
                HashCode=data_hash,
                FilePath=file_path,
                IsDeleted=False,
            )
            record.save()
            print("generate done")
            self.send(
                text_data=json.dumps(
                    {
                        "status": "file generated",
                        "canClose": True,
                        "filePath": file_path,
                    }
                )
            )

    def has_valid_record(self, records):
        for record in records:
            if os.path.exists(record.FilePath):
                return (True, record.FilePath)
            record.IsDeleted = True
            record.save()
        return (False, None)
