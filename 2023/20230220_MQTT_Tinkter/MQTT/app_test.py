import time

import paho.mqtt.client as mqtt
import paramiko

from MQTT.test import *


if __name__ == '__main__':
    mqtt_client = MqttRoad()
    mqtt_client.connect("192.168.1.101", 1883, 600)


    ssh_client = SSHRoad()
    # print(ssh_client.connect(hostname='192.168.1.101', port=8888, username='hnxjyb', password='Hnxj$1234'))
    # ssh_client.client.close()
    # paramiko.Transport((self.host, self.port))
    mqtt_client.client.publish("test/M-scsMonitor", bytes.fromhex("0151037D004D2D7075416D72004D2D7363734D6F6E69746F720010000600080000000A00000014"))
    #
    # for i in range(20):
    #     print(ssh_client.connect(hostname='192.168.1.101', port=8888, username='hnxjyb111', password='Hnxj$1234'))
    #     time.sleep(0.5)

    # print("end")
    input()

    print(ssh_client.client.get_transport())
    print(ssh_client.connect(hostname='192.168.1.101', port=8888, username='hnxjyb', password='Hnxj$1234'))
    # print(ssh_client.client.get_transport())

    # ssh_client.client.close()
    # print(ssh_client.client.get_transport())
    ssh_client.client.exec_command("top",tiomeout=5)
    # mqtt_client.queue.get(timeout=1)
    print("等待超时")
    input()

    print(mqtt_client.queue.empty())

    # 订阅
    mqtt_client.client.subscribe([("M-scsMonitor/Broadcast/0006/0001", 0), ("M-scsMonitor/Broadcast/0006/0002", 0),
                      ("M-scsMonitor/Broadcast/0006/0003", 0), ("M-scsMonitor/Broadcast/0006/0004", 0),
                      ("M-scsMonitor/Broadcast/0006/0005", 0), ("M-scsMonitor/Broadcast/0006/0006", 0),
                      ("M-scsMonitor/Broadcast/0006/0007", 0), ("M-scsMonitor/Broadcast/0006/0008", 0),
                      ("M-scsMonitor/Broadcast/0006/0009", 0), ("M-scsMonitor/Broadcast/0006/000A", 0),
                      ("M-scsMonitor/Broadcast/0006/000B", 0), ("M-scsMonitor/Broadcast/0006/000C", 0),
                      ("M-scsMonitor/Broadcast/0006/0010", 0), ("M-scsMonitor/Broadcast/0006/0011", 0),
                      ("M-scsMonitor/Broadcast/0006/0012", 0)])
    # 连接服务器
    print(ssh_client.connect(hostname='192.168.1.101', port=8888, username='hnxjyb', password='Hnxj$1234'))
    input()
    mqtt_client.loop_start()

    time.sleep(1)

    # topic = 'test/M-scsMonitor'
    # payload = b'\x01t\x00\x02\x00M-scsMonitor\x00Broadcast\x00\x02\x00\x06\x00\x08\x01\x04\xc0\xa8\x01\x08\xca\x98'

    # print(payload.hex())
    # qos = 0
    # mqtt_client.client.publish(topic, payload, qos)
    # mqtt_client.client.publish("test/M-scsMonitor" ,"0151037D004D2D7075416D72004D2D7363734D6F6E69746F720010000600080000000A00000014")
    # print(mqtt_client.queue.get())

    print('end.')
    # input()

