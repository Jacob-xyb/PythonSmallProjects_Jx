import copy

CaseResData = {
    "启动标志位": "",
    "消息序号": "",
    "消息标签": "",
    "消息发送方": "",
    "消息接收方": "",
    "IID": "",
    "IOP": "",
    "length": "",
    "payload": "",
    "解析结果": "",
    "断言结果": {},
}


class ParseMsg:
    def __init__(self):
        self.msg_res = copy.deepcopy(CaseResData)

    def parse_msg(self, msg):
        self.msg = msg
        self.parse_payloadHex(self.msg.payload.hex())

        return self.msg_res

    @staticmethod
    def get_IIDIOP(msg):
        payload = msg.payload.hex()
        tmp_payload = payload[10:]
        count = 2
        while count > 0:
            tmp_payload = tmp_payload[tmp_payload.find("00") + 2:]
            count -= 1
        IOP = tmp_payload[2:4] + tmp_payload[0:2]
        IID = tmp_payload[6:8] + tmp_payload[4:6]
        return IID + IOP

    def parse_payloadHex(self, payload):
        payload = payload.strip('\n')  # 删除换行符
        num_head = payload[:2]
        # text_head = "{:04b}".format(int(num_head, 2))
        # res_head = {}
        # for idx, item in enumerate(text_head):
        #     res_head[chr(97 + idx)] = item

        if num_head == "00":
            self.msg_res["启动标志位"] = "0"
        elif num_head == "01":
            self.msg_res["启动标志位"] = "1"
        else:
            self.msg_res["启动标志位"] = num_head

        self.msg_res["消息序号"] = str(int(payload[4:6] + payload[2:4], 16))
        self.msg_res["消息标签"] = str(int(payload[8:10] + payload[6:8], 16))

        tmp_payload = payload[10:]
        index = tmp_payload.find("00")
        self.msg_res["消息发送方"] = translate_ascii_code(tmp_payload[:index])

        tmp_payload = tmp_payload[index + 2:]
        index = tmp_payload.find("00")
        self.msg_res["消息接收方"] = translate_ascii_code(tmp_payload[:index])

        tmp_payload = tmp_payload[index + 2:]
        self.msg_res["IOP"] = tmp_payload[2:4] + tmp_payload[0:2]
        self.msg_res["IID"] = tmp_payload[6:8] + tmp_payload[4:6]

        tmp_payload = tmp_payload[8:]
        num_len = 0
        if len(tmp_payload) > 256 * 2:
            num_len = 4
        else:
            num_len = 2
        length = int(tmp_payload[:num_len], 16)
        self.msg_res["length"] = str(length)
        self.msg_res["payload"] = tmp_payload[num_len:]

        self.parse_pyloadContext()
        # print(self.msg_res)
        return self.msg_res

    def parse_pyloadContext(self):
        IID_IOP = self.msg_res["IID"] + self.msg_res["IOP"]

        func_str = f"self._by_IIDIIP_{IID_IOP.lower()}"
        try:
            eval(func_str)()
            return {"state": 1, "info": "解析成功"}
        except:
            return {"state": 0, "info": "解析失败"}

    def _by_IIDIIP_00060001(self):
        parse_res = ""
        port_list = []

        payload = self.msg_res["payload"]
        num = int(payload[:2], 16)

        cycle_payload = payload[2:]
        cycle_len = 4
        for n in range(num):
            port = int(cycle_payload[cycle_len * n: cycle_len * (n + 1)], 16)
            parse_res += f"\n\tport: {port}"
            port_list.append(str(port))
        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"port": port_list}

    def _by_IIDIIP_00060002(self):
        parse_res = ""
        adr_list = []

        payload = self.msg_res["payload"]
        num = int(payload[:2], 16)

        cycle_payload = payload[2:]
        for n in range(num):
            ip_str = ""
            ip_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            for i in range(ip_len):
                ip_str += str(int(cycle_payload[: 2], 16)) + "."
                cycle_payload = cycle_payload[2:]
            ip_str = ip_str[:-1] + ":"
            ip_str += str(int(cycle_payload[:4], 16))
            cycle_payload = cycle_payload[4:]
            parse_res += f"\n\tadr: {ip_str}"
            adr_list.append(str(ip_str))
        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"py-ip": adr_list}

    def _by_IIDIIP_00060003(self):
        parse_res = ""
        cmd_list = []
        payload = self.msg_res["payload"]
        num = int(payload[:2], 16)
        cycle_payload = payload[2:]

        for n in range(num):
            arr_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            arr_payload = cycle_payload[:arr_len * 2]
            cycle_payload = cycle_payload[arr_len * 2:]
            cmd = ""
            for i in range(arr_len):
                cmd += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
            parse_res += f"\n\tcmd: {cmd}"
            cmd_list.append(cmd)
        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"cmd": cmd_list}

    def _by_IIDIIP_00060004(self):
        parse_res = ""
        ssh_list = []
        payload = self.msg_res["payload"]
        res = ""
        if payload[:2] == "00":
            res = "登录控制台成功"
        elif payload[:2] == "01":
            res = "退出控制台成功"
        elif payload[:2] == "02":
            res = "登录控制台失败"

        parse_res += f"\n\tssh: {res}"
        ssh_list.append(res)

        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"ssh": ssh_list}

    def _by_IIDIIP_00060005(self):
        parse_res = ""
        cmd_list = []
        payload = self.msg_res["payload"]
        res = ""
        if payload[:2] == "00":
            res = "删除命令上报"
        elif payload[:2] == "01":
            res = "重命名命令上报"
        elif payload[:2] == "02":
            res = "复制命令上报"
        elif payload[:2] == "03":
            res = "进程结束命令上报"

        parse_res += f"\n\tcmd: {res}"
        cmd_list.append(res)

        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"cmd": cmd_list}

    def _by_IIDIIP_00060006(self):
        parse_res = ""
        ssh_list = []
        payload = self.msg_res["payload"]
        res = ""
        if payload[:2] == "00":
            res = "打开"
        elif payload[:2] == "01":
            res = "关闭"
        elif payload[:2] == "02":
            res = "服务异常"
        elif payload[:2] == "03":
            res = "服务长时间未关闭"

        parse_res += f"\n\tssh: {res}"
        ssh_list.append(res)

        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"ssh": ssh_list}

    def _by_IIDIIP_00060007(self):
        parse_res = ""
        user_list = []
        payload = self.msg_res["payload"]
        num = int(payload[:2], 16)
        cycle_payload = payload[2:]

        for n in range(num):
            arr_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            arr_payload = cycle_payload[:arr_len * 2]
            cycle_payload = cycle_payload[arr_len * 2:]
            tmp_res = ""
            for i in range(arr_len):
                tmp_res += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
            parse_res += f"\n\tuser: {tmp_res}"
            user_list.append(tmp_res)
        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"user": user_list}

    def _by_IIDIIP_00060008(self):
        parse_res = ""
        serialport_list = []
        payload = self.msg_res["payload"]
        res = ""
        if payload[:2] == "00":
            res = "登录控制台成功"
        elif payload[:2] == "01":
            res = "退出控制台成功"
        elif payload[:2] == "02":
            res = "登录控制台失败"

        parse_res += f"\n\tserialport: {res}"
        serialport_list.append(res)
        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"serialport": serialport_list}

    def _by_IIDIIP_00060009(self):
        parse_res = ""
        res_list = []
        payload = self.msg_res["payload"]
        num = int(payload[:2], 16)
        cycle_payload = payload[2:]

        for n in range(num):  # 代表有几组数据
            tmp_res = {}

            # sship
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += str(int(cycle_payload[:2], 16)) + "."
                cycle_payload = cycle_payload[2:]
            parse_res += f"\n\tsship: {tmp[:-1]}"
            tmp_res["sship"] = tmp[:-1]

            # sshport
            tmp = str(int(cycle_payload[:4], 16))
            cycle_payload = cycle_payload[4:]
            parse_res += f"\n\tsshport: {tmp}"
            # tmp_res["sshport"] = tmp

            # localip
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += str(int(cycle_payload[:2], 16)) + "."
                cycle_payload = cycle_payload[2:]
            parse_res += f"\n\tlocalip: {tmp[:-1]}"
            tmp_res["localip"] = tmp[:-1]

            # localport
            tmp = str(int(cycle_payload[:4], 16))
            cycle_payload = cycle_payload[4:]
            parse_res += f"\n\tlocalport: {tmp}"
            # tmp_res["localport"] = tmp

            # protocol
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            arr_payload = cycle_payload[:tmp_len * 2]
            cycle_payload = cycle_payload[tmp_len * 2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
            parse_res += f"\n\tprotocol: {tmp}"
            tmp_res["protocol"] = tmp

            # process
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            arr_payload = cycle_payload[:tmp_len * 2]
            cycle_payload = cycle_payload[tmp_len * 2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
            parse_res += f"\n\tprocess: {tmp}"
            tmp_res["process"] = tmp

            # type
            tmp = ""
            if cycle_payload[:2] == "00":
                tmp = "未知"
            elif cycle_payload[:2] == "01":
                tmp = "宿主内进程"
            elif cycle_payload[:2] == "02":
                tmp = "容器内进程"
            parse_res += f"\n\ttype: {tmp}"
            tmp_res["type"] = tmp

            res_list.append(tmp_res)

        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"res": res_list}

    def _by_IIDIIP_00060010(self):
        parse_res = ""
        res_list = []
        cycle_payload = self.msg_res["payload"]
        num = int(cycle_payload[:8], 16)
        cycle_payload = cycle_payload[8:]
        tmp_res = {}
        parse_res += f"\n\tMonthlyflowlimit: {num} KB"
        tmp_res["Monthlyflowlimit"] = str(num)
        num = int(cycle_payload[:8], 16)
        cycle_payload = cycle_payload[8:]
        parse_res += f"\n\tBandwidthlimit: {num} KB/s"
        tmp_res["Bandwidthlimit"] = str(num)
        res_list.append(tmp_res)
        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"res": res_list}

    def _by_IIDIIP_00060011(self):
        parse_res = ""
        res_list = []
        cycle_payload = self.msg_res["payload"]
        num = int(cycle_payload[:8], 16)
        cycle_payload = cycle_payload[8:]
        tmp_res = {}
        parse_res += f"\n\tMonthlyflowlimit: {num} KB"
        tmp_res["Monthlyflowlimit"] = str(num)
        num = int(cycle_payload[:8], 16)
        cycle_payload = cycle_payload[8:]
        parse_res += f"\n\tBandwidthlimit: {num} KB/s"
        tmp_res["Bandwidthlimit"] = str(num)
        res_list.append(tmp_res)
        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"res": res_list}

    def _by_IIDIIP_00060012(self):
        parse_res = ""
        res_list = []
        cycle_payload = self.msg_res["payload"]
        num = int(cycle_payload[:2], 16)
        cycle_payload = cycle_payload[2:]
        tmp_res = {}
        tmp = ""
        if cycle_payload[:2] == "01":
            tmp = "SSH服务"
        elif cycle_payload[:2] == "01":
            tmp = "SSH服务"
        cycle_payload = cycle_payload[2:]
        parse_res += f"\n\tconfiguretype: {tmp}"
        tmp_res["configuretype"] = tmp

        num = int(cycle_payload[:8], 16)
        cycle_payload = cycle_payload[8:]
        parse_res += f"\n\tconfiguretime: {num} min"
        tmp_res["configuretime"] = str(num)
        res_list.append(tmp_res)
        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"res": res_list}

    def _by_IIDIIP_0006000a(self):
        parse_res = ""
        res_list = []
        payload = self.msg_res["payload"]
        num = int(payload[:2], 16)
        cycle_payload = payload[2:]

        for n in range(num):  # 代表有几组数据
            tmp_res = {}

            # sship
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += str(int(cycle_payload[:2], 16)) + "."
                cycle_payload = cycle_payload[2:]
            parse_res += f"\n\tsship: {tmp[:-1]}"
            tmp_res["sship"] = tmp[:-1]

            # sshport
            tmp = str(int(cycle_payload[:4], 16))
            cycle_payload = cycle_payload[4:]
            parse_res += f"\n\tsshport: {tmp}"
            # tmp_res["sshport"] = tmp

            # localip
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += str(int(cycle_payload[:2], 16)) + "."
                cycle_payload = cycle_payload[2:]
            parse_res += f"\n\tlocalip: {tmp[:-1]}"
            tmp_res["localip"] = tmp[:-1]

            # localport
            tmp = str(int(cycle_payload[:4], 16))
            cycle_payload = cycle_payload[4:]
            parse_res += f"\n\tlocalport: {tmp}"
            # tmp_res["localport"] = tmp

            # protocol
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            arr_payload = cycle_payload[:tmp_len * 2]
            cycle_payload = cycle_payload[tmp_len * 2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
            parse_res += f"\n\tprotocol: {tmp}"
            tmp_res["protocol"] = tmp

            # process
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            arr_payload = cycle_payload[:tmp_len * 2]
            cycle_payload = cycle_payload[tmp_len * 2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
            parse_res += f"\n\tprocess: {tmp}"
            tmp_res["process"] = tmp

            # Bandwidthlimit
            tmp_num = int(cycle_payload[:8], 16)
            cycle_payload = cycle_payload[8:]
            parse_res += f"\n\tBandwidthlimit: {tmp_num} KB/S"
            tmp_res["Bandwidthlimit"] = str(tmp_num)

            # CurrentSpeed
            tmp_num = int(cycle_payload[:8], 16)
            cycle_payload = cycle_payload[8:]
            parse_res += f"\n\tCurrentSpeed: {tmp_num} KB/S"
            tmp_res["CurrentSpeed"] = str(tmp_num)

            res_list.append(tmp_res)

        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"res": res_list}

    def _by_IIDIIP_0006000b(self):
        parse_res = ""
        res_list = []
        payload = self.msg_res["payload"]
        num = int(payload[:2], 16)
        cycle_payload = payload[2:]

        for n in range(num):  # 代表有几组数据
            tmp_res = {}
            code1 = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            tmp = ""
            if code1 == 1:
                tmp = "进程增加"
            parse_res += f"\n\ttype: {tmp}"
            tmp_res["type"] = tmp

            # 解析时间
            tmp = f"{int(cycle_payload[:4], 16)}-"  # Y
            cycle_payload = cycle_payload[4:]
            tmp += f"{int(cycle_payload[:2], 16)}-"  # M
            cycle_payload = cycle_payload[2:]
            tmp += f"{int(cycle_payload[:2], 16)}"  # D
            cycle_payload = cycle_payload[2:]
            tmp_res["time"] = tmp
            tmp += " "
            tmp += f"{int(cycle_payload[:2], 16)}:"  # h
            cycle_payload = cycle_payload[2:]
            tmp += f"{int(cycle_payload[:2], 16)}:"  # m
            cycle_payload = cycle_payload[2:]
            tmp += f"{int(cycle_payload[:2], 16)}"  # s
            cycle_payload = cycle_payload[2:]
            parse_res += f"\n\ttime: {tmp}"

            # processname
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            arr_payload = cycle_payload[:tmp_len * 2]
            cycle_payload = cycle_payload[tmp_len * 2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
            parse_res += f"\n\tprocessname: {tmp}"
            tmp_res["processname"] = tmp

            # processuser
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            arr_payload = cycle_payload[:tmp_len * 2]
            cycle_payload = cycle_payload[tmp_len * 2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
            parse_res += f"\n\tprocessuser: {tmp}"
            tmp_res["processuser"] = tmp

            # processgroup
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            arr_payload = cycle_payload[:tmp_len * 2]
            cycle_payload = cycle_payload[tmp_len * 2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
            parse_res += f"\n\tprocessgroup: {tmp}"
            tmp_res["processgroup"] = tmp

            # processcmd
            tmp_len = int(cycle_payload[:2], 16)
            cycle_payload = cycle_payload[2:]
            arr_payload = cycle_payload[:tmp_len * 2]
            cycle_payload = cycle_payload[tmp_len * 2:]
            tmp = ""
            for i in range(tmp_len):
                tmp += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
            parse_res += f"\n\tprocesscmd: {tmp}"
            tmp_res["processcmd"] = tmp

            res_list.append(tmp_res)

        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"res": res_list}

    def _by_IIDIIP_0006000c(self):
        parse_res = ""
        res_list = []
        payload = self.msg_res["payload"]
        num = payload[:2]
        cycle_payload = payload[2:]

        tmp_res = {}
        tmp = ""
        if num == "01":
            tmp = "爆破登录"
        parse_res += f"\n\ttype: {tmp}"
        tmp_res["type"] = tmp

        # user
        tmp_len = int(cycle_payload[:2], 16)
        cycle_payload = cycle_payload[2:]
        arr_payload = cycle_payload[:tmp_len * 2]
        cycle_payload = cycle_payload[tmp_len * 2:]
        tmp = ""
        for i in range(tmp_len):
            tmp += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
        parse_res += f"\n\tuser: {tmp}"
        tmp_res["user"] = tmp

        # device
        tmp_len = int(cycle_payload[:2], 16)
        cycle_payload = cycle_payload[2:]
        arr_payload = cycle_payload[:tmp_len * 2]
        cycle_payload = cycle_payload[tmp_len * 2:]
        tmp = ""
        for i in range(tmp_len):
            tmp += chr(int(arr_payload[i * 2:i * 2 + 2], 16))
        parse_res += f"\n\tdevice: {tmp}"
        tmp_res["device"] = tmp

        res_list.append(tmp_res)

        self.msg_res["解析结果"] = parse_res
        self.msg_res["断言结果"] = {"res": res_list}


def translate_ascii_code(context):
    idx = 0
    res = ""
    while idx < len(context):
        res += chr(int(context[idx: idx + 2], 16))
        idx += 2
    return res


# if __name__ == '__main__':
#     msg_16 = "016f0003004d2d7363734d6f6e69746f720042726f61646361737400030006001901172f7573722f6c6f63616c2f657874617070732f74657374"
#
#     print(ParseMsg(msg_16).parse_msg_touch())
