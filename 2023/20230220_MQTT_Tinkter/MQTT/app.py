import paho.mqtt.client as mqtt
from test import *
from paramiko import SSHClient, AutoAddPolicy


if __name__ == '__main__':
    mqtt_client = MqttRoad("192.168.1.101", 1883, 600)

    mqtt_client.loop_start()
    ssh_client = SSHClient()
    # 允许连接不在know_hosts文件里的主机
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    # 连接服务器
    ssh_client.connect(hostname='192.168.1.101', port=8888, username='hnxjyb', password='Hnxj$1234')
    time.sleep(1)
    mqtt_client.queue.get()

    # 执行命令
    command = "touch /usr/local/extapps/test"
    stdin, stdout, stderr = ssh_client.exec_command(command)
    # # 获取命令结果
    res, err = stdout.read(), stderr.read()
    result = res if res else err
    # 将字节类型 转换为 字符串类型
    result = str(result, encoding='utf-8')
    print(result)
    print("test 0003")

    while True:
        msg_16 = mqtt_client.queue.get()
        print("----------------------msg_16----------------------")
        print(msg_16)
        a = msg_16
        # todo 解析消息
        if a == 0:
            print("dsfdsf")
            break
    time.sleep(1)

