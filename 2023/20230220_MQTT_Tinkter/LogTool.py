import os
import time


class PyLog:
    def __init__(self):
        self.filename = ""
        self.configName = "log/log.inf"

    def get_logFileName(self):
        if not os.path.exists(self.configName):
            self.set_logFileName()
        self.filename = open(self.configName, 'r').read()

    @staticmethod
    def init_logDIr():
        if not os.path.exists("log"):
            os.makedirs("log")

    def set_logFileName(self):
        f = open(self.configName, 'w')
        context = time.strftime("%Y%m%d%H%M%S") + ".log"
        f.write(context)
        f.close()

    @staticmethod
    def get_currentTime() -> str:
        return f'[{time.strftime("%Y-%m-%d %H:%M:%S")}]'

    def set_log(self, context):
        self.get_logFileName()
        f = open(f"log/{self.filename}", 'a')
        f.write(f"{self.get_currentTime()}{context}\n")
        f.close()
