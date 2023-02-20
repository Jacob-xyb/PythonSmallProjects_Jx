import copy
from ParseMsg import *
import time
import os
from LogTool import *
from collections import defaultdict
import serial
import serial.tools.list_ports


class PyCase:
    def __init__(self):
        self.case_res = {
            "data": copy.deepcopy(CaseResData),
            "is_Success": False,
            "error_info": "",
            "message": b"",
            "topic": "",
            "time": ""
        }

    def load_ssh_info(self, info):
        self.ssh_info = info

    def get_res(self, case, mqtt_client, ssh_client):
        self.case = case
        self.mqtt_client = mqtt_client
        self.ssh_client = ssh_client

        local_time = time.localtime()
        data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        self.case_res["time"] = data_head

        self.__get_state()
        self.mqtt_client.queue.queue.clear()
        PyLog().set_log("【消息队列已清空】")
        # PyLog().set_log("【Step1】 ==> 状态码:" + self.case.get("状态码"))  # 转移到 get_state 里面
        tmp_return = self.__start_step1()  # 执行获取报文前的操作

        if tmp_return["res"] == 0:
            self.case_res["is_Success"] = False
            self.case_res["erro_info"] = tmp_return["error_info"]
            PyLog().set_log(f'【{self.case.get("用例名称")} 执行结果】: False; erro_info:{tmp_return["error_info"]}')
            return self.case_res

        # 获取报文
        PyLog().set_log(f"【Step2】 ==> 获取mqtt报文, 案例的IID&IOP: {self.case.get('IID&IOP').lower()}")
        tmp_return = self.__get_message_res()  # 执行获取报文前的操作
        if tmp_return["res"] == 0:
            self.case_res["is_Success"] = False
            self.case_res["error_info"] = tmp_return["error_info"]
            PyLog().set_log(f'【{self.case.get("用例名称")} 执行结果】: False; erro_info:{tmp_return["error_info"]}')
            return self.case_res
        else:
            self.case_res["is_Success"] = True
            # 解析报文
            self.case_res["data"] = ParseMsg().parse_msg(self.msg)
            PyLog().set_log(f'【Step3】 ==> 获取报文解析结果:\n{transform_dict(self.case_res["data"])}')
            if self.case_res["data"]["解析结果"] == "":
                self.case_res["is_Success"] = False
                PyLog().set_log(f'【{self.case.get("用例名称")} 执行结果】: False; erro_info:{"报文解析失败"} ')
                return self.case_res
            # 断言结果
            PyLog().set_log(f'【Step4】 ==> 断言:'
                            f'\n断言内容:{str(self.case_res["data"]["断言结果"])}\n用例中result内容:{str(self.case["result"])}')
            tmp_return = self.__assert_result()
            if tmp_return["res"] == 0:
                self.case_res["is_Success"] = False
                self.case_res["error_info"] = tmp_return["error_info"]
                PyLog().set_log(f'【{self.case.get("用例名称")} 执行结果】: False; erro_info:{tmp_return["error_info"]} ')
                return self.case_res
            else:
                PyLog().set_log(f'【{self.case.get("用例名称")} 执行结果】: True ')
                return self.case_res

    def __start_step1(self):
        if self.state["A"] != "0" and self.state["A"] != "":
            PyLog().set_log("【调用serial串口函数】:")
            for i in range(5):
                if self.__connect_serial(int(self.state["A"])):
                    break

        if self.state["B"] == "1":
            self.ssh_client.client.close()
            PyLog().set_log("【调用ssh关闭函数】:" + "ssh_close执行【成功】")
            time.sleep(2)
            # while True:
            #     if self.ssh_client.client.get_transport() is None:
            #         break

        if self.state["C"] == "1":
            if self.state["D"] == "0":
                if not self.__connect_ssh():
                    return {"res": 0, "error_info": "ssh连接失败"}
            elif self.state["D"] == "1":
                hostname = self.case.get("ssh_url").split(':')[0]
                port = int(self.case.get("ssh_url").split(':')[1])
                username = self.case.get("ssh_user")
                password = self.case.get("ssh_pwd")
                context = f'ssh_url={self.case.get("ssh_url")},' \
                          f'ssh_user={username},ssh_pwd={password}'
                if self.ssh_client.connect(hostname, port, username, password):
                    PyLog().set_log("【调用ssh连接函数】:\n\t" + context + "\n\tssh连接【成功】")
                    return {"res": 0, "error_info": "ssh连接异常"}
                else:
                    PyLog().set_log("【调用ssh连接函数】:\n\t" + context + "\n\tssh连接【失败】")
            else:
                hostname = self.case.get("ssh_url").split(':')[0]
                port = int(self.case.get("ssh_url").split(':')[1])
                username = self.case.get("ssh_user")
                password = self.case.get("ssh_pwd")
                context = f'ssh_url={self.case.get("ssh_url")},' \
                          f'ssh_user={username},ssh_pwd={password}'
                PyLog().set_log(
                    "【调用ssh连接函数】:\n\t" + context + f"\n\t爆破登陆次数【{(int(self.state['A']) - 1) * 20}】")
                for i in range((int(self.state["D"]) - 1) * 20):
                    self.ssh_client.connect(hostname, port, username, password)
                    time.sleep(0.5)

        if self.state["E"] == "1":
            self.__execute_ssh_cmd()
        if self.state["F"] == "1":
            self.__execute_mqtt_publish()
            time.sleep(62)
        return {"res": 1}

    def __get_state(self):
        self.state = defaultdict(str)
        keys = ["串口相关操作", "是否断开ssh连接", "是否建立ssh连接", "ssh连接相关参数", "是否通过ssh下发命令",
                "是否下发MQTT报文"]
        key_value_text = ""
        for index, item_key in enumerate(keys):
            cell_value = self.case.get(item_key) or ''
            key_value_text += f"{item_key}:{cell_value}\n"
            if "--" in cell_value:
                self.state[chr(index + 65)] = cell_value.split('--')[1]
        PyLog().set_log("【Step1】 ==> 触发动作执行:\n" + key_value_text.rstrip("\n"))

        # for idx, item in enumerate(self.case.get("状态码")):
        #     self.state[chr(idx + 65)] = item

    def __connect_ssh(self):
        flag = self.ssh_client.connect(
            self.ssh_info["hostname"], self.ssh_info["port"], self.ssh_info["username"], self.ssh_info["password"])
        context = f'ssh_url={self.ssh_info["hostname"]}:{self.ssh_info["port"]},' \
                  f'ssh_user={self.ssh_info["username"]},ssh_pwd={self.ssh_info["password"]}'
        if flag:
            PyLog().set_log("【调用ssh连接函数】:\n\t" + context + "\n\tssh连接【成功】")
        else:
            PyLog().set_log("【调用ssh连接函数】:\n\t" + context + "\n\tssh连接【失败】")
        return flag

    def __connect_serial(self, A=1):
        """
        :param A:
        A = 0: 不执行 __connect_serial 此函数
        A = 1: 不重启ssh
        A = 2: 全执行
        A = 3: 只登陆
        A = 4: 只退出
        备注： 查询ssh状态不成功时，重复执行此函数至多5次
        :return:
        """

        # ports = list(serial.tools.list_ports.comports(include_links=False))
        # for port in ports:
        #     print(port)
        # 创建串口对象,此处port传参serial_port;
        try:
            ser = serial.Serial(port=self.case.get("serial_port"), baudrate=115200, parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                timeout=60, rtscts=False)
        except Exception as e:
            PyLog().set_log("Serial_port串口连接崩溃" + str(e))
            return False
        # 判断串口是否打开
        ser.close()
        ser.open()
        if ser.isOpen():
            PyLog().set_log("Serial_port串口连接成功")
            if A == 3:
                self.__serial_login(ser)
            elif A == 4:
                self.__serial_exit(ser)
            elif A in [1, 2]:
                self.__serial_login(ser)
                self.__serial_cmd(ser)
                if A == 2:
                    self.__serial_restart(ser)
                if not self.__serial_queryStatus(ser):
                    ser.close()
                    return False
                self.__serial_exit(ser)

            # 读取数据，读取的内容也是 bytes 类型
            read_msg = ser.read(1000000)
            PyLog().set_log("read_msg: " + read_msg.decode("utf-8"))

            # 关闭串口
            ser.close()
            return True

        else:
            PyLog().set_log("Serial_port串口连接失败")
            return True

    def __serial_login(self, serialClient: serial.Serial):
        PyLog().set_log("执行serial_login---->")
        # 发送数据，这里只支持 bytes 类型的数据，需要对字符串进行 encode 编码
        serialClient.write(self.case.get("serial_user").encode("utf-8"))  # 此处syssadm传参serial_user
        serialClient.write('\r\n'.encode("utf-8"))
        time.sleep(2)
        PyLog().set_log("rread---->" + str(serialClient.readline().decode("utf-8")))
        serialClient.write(self.case.get("serial_pwd").encode("utf-8"))  # 此处传参serial_pwd
        serialClient.write('\r\n'.encode("utf-8"))
        time.sleep(2)
        PyLog().set_log("rread2---->" + str(serialClient.readline().decode("utf-8")))

    def __serial_cmd(self, serialClient: serial.Serial):
        # PyLog().set_log("执行serial_cmd---->" + self.case.get("serial_cmd"))
        serial_cmd = self.case.get("serial_cmd")
        PyLog().set_log("执行serial_cmd---->" + serial_cmd)
        if serial_cmd != "":
            tmp_cmds = []
            if ";" in serial_cmd:
                tmp_cmds = serial_cmd.split(";")
            else:
                tmp_cmds.append(serial_cmd)
            for cmd in tmp_cmds:
                serialClient.write(cmd.encode("utf-8"))  # 此处传参serial_cmd,若serial_cmd为空，此处不执行
                serialClient.write('\r\n'.encode("utf-8"))
                time.sleep(2)
                PyLog().set_log("serial_cmd执行结果解析:" + str(serialClient.readline().decode("utf-8")))
        else:
            PyLog().set_log("serial_cmd为空")

    def __serial_restart(self, serialClient: serial.Serial):
        PyLog().set_log("执行serial_restart---->")
        serialClient.write('systemctl restart sshd'.encode("utf-8"))
        serialClient.write('\r\n'.encode("utf-8"))
        time.sleep(1)

    def __serial_queryStatus(self, serialClient: serial.Serial):
        PyLog().set_log("执行serial_queryStatus---->")
        serialClient.write('systemctl status sshd | grep Active'.encode("utf-8"))
        serialClient.write('\r\n'.encode("utf-8"))
        b = serialClient.readline()
        if b"running" in b:
            PyLog().set_log("read_all---->" + str(serialClient.read_all()))
            PyLog().set_log("ssh服务恢复正常")
            return True
        else:
            PyLog().set_log("read_all---->" + str(serialClient.read_all()))
            PyLog().set_log("ssh服务恢复失败")
            # 重新执行整个函数，最多再重复执行5次
            return False

    def __serial_exit(self, serialClient: serial.Serial):
        time.sleep(1)
        PyLog().set_log("执行serial_exit---->")
        serialClient.write('exit'.encode("utf-8"))
        serialClient.write('\r\n'.encode("utf-8"))
        PyLog().set_log(str(serialClient.readline().decode("utf-8")))

    def __execute_mqtt_publish(self):
        result = self.mqtt_client.client.publish(self.case.get("publish_topic"),
                                                 bytes.fromhex(self.case.get("publish_mid")))
        context = f'publish_topic={self.case.get("publish_topic")}, publish_mid={self.case.get("publish_mid")}'

        PyLog().set_log("【调用publish函数】:\n\t" + context + "\n\tpublish返回结果：" + str(result))

    def __execute_ssh_cmd(self):
        try:

            command = self.case.get("ssh_cmd")
            command = command.removeprefix(" ")
            PyLog().set_log("【执行cmd函数】:" + command)
            if command and command.startswith('scp'):
                ftp = self.ssh_client.client.open_sftp()
                _, server_file, local_file = tuple(command.split(";"))
                ftp.get(server_file, local_file)
                # ftp.get("/data/app/scsMonitor/log/scsMonitor.log", 'F:\\test\scsMonitor.log')
                PyLog().set_log("【cmd执行结果】:" + "文件下载成功")
                print("文件下载成功")
            else:
                stdin, stdout, stderr = self.ssh_client.client.exec_command(command, timeout=5, get_pty=True)
                time.sleep(2)
                result = stdout.read(100)
                PyLog().set_log("【cmd执行结果】:" + result)
                print(result)
        except Exception as e:
            # errr=stderr.read(100)
            PyLog().set_log("【cmd执行结果】:" + str(e))
            print(e)
            return

    def __get_message_res(self) -> dict:
        msg = None
        t1 = time.time()
        flag = False  # 判断是否获取到对应的报文
        message_idx = 0

        while time.time() - t1 < 10:
            if self.mqtt_client.queue.empty() is False:
                msg = self.mqtt_client.queue.get()
                self.case_res["message"] = msg.payload
                self.case_res["topic"] = msg.topic
                IIDIOP = ParseMsg().get_IIDIOP(msg)
                PyLog().set_log(f"IID&IOP【{message_idx}:02】:{IIDIOP} message:{self.case_res['message'].hex()}")
                # print(f"IID&IOP: {IIDIOP}")
                if IIDIOP.lower() == self.case.get("IID&IOP").lower() and not flag:
                    self.msg = msg
                    flag = True
                    # self.mqtt_client.queue.queue.clear()
            # print(time.time())  # 调试用 判断是否进入无限循环队列
        if not flag:
            return {"res": 0, "error_info": "报文获取超时"}
        else:
            return {"res": 1}

    def __get_url_ip(self):
        ip_list = os.popen("netstat -an").read().split('\n')[4:]
        res = []

        for i in range(len(self.case_res["data"]["断言结果"]["py-ip"])):
            for item in ip_list:
                item = item.split()
                if len(item) < 4:
                    continue
                if item[3] != "ESTABLISHED":
                    continue
                if item[1] == self.case_res["data"]["断言结果"]["py-ip"][i]:
                    res.append(item[2])
                    break
        return res

    def __assert_result(self):
        case_res = {}  # 获取的断言内容
        if self.case["result"] is None:
            return {"res": 0, "error_info": "断言失败:result为空"}
        else:
            try:
                tmp = self.case["result"].replace("：", ":")
                case_res = eval(tmp)
            except:
                return {"res": 0, "error_info": "断言失败:result格式错误"}

        for key, value in case_res.items():
            if key == "py-ip":
                tmp = self.__get_url_ip()
                if not tmp:
                    return {"res": 0, "error_info": "断言失败:获取对应ip失败"}
                elif value != tmp:
                    return {"res": 0, "error_info": "断言失败:获取对应ip不一致"}
                else:
                    continue
            elif key == "CurrentSpeed":
                if self.case_res["data"]["断言结果"][key] >= value:
                    continue
                else:
                    return {"res": 0, "error_info": "断言失败:CurrentSpeed不满足条件"}
            if value != self.case_res["data"]["断言结果"][key]:
                return {"res": 0, "error_info": "断言失败"}

        return {"res": 1}


def transform_dict(d: dict):
    text = ""
    for key, value in d.items():
        if key == "断言结果":
            continue
        text += f"{key}: {value}\n"
    return text


if __name__ == '__main__':
    case = {
        "状态码": "00000",
    }

    # print(PyCase().get_res(case))
