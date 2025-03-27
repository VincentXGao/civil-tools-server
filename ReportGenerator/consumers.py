import json, io, sys, time
from channels.generic.websocket import WebsocketConsumer
from Utils.SHA256 import str_to_sha256

from CivilTools.ReportGenerator import StairCalculationReport
import CivilTools as CT

print(CT.__version__)


class ReportConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({"status": "connected!Let's generate report!"}))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(str_to_sha256(text_data + CT.__version__))
        message = text_data_json["message"]
        time.sleep(3)
        print("Done")
        self.send(
            text_data=json.dumps(
                {"status": "???", "message???": message, "canClose": True}
            )
        )
        print("反正信息我发了，你收没收到再说")
