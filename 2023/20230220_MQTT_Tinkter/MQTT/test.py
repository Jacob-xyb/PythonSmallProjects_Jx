import paho.mqtt.client as mqtt
import time
from queue import Queue
from paramiko import SSHClient, AutoAddPolicy


class MqttRoad(object):

    def __init__(self):
        super(MqttRoad, self).__init__()
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_publish = self.on_publish
        client.on_disconnect = self.on_disconnect
        # client.loop_forever()  # 保持连接
        self.rc = 0
        self.client = client
        self.isConnected = False

        self.queue = Queue()

    def loop_forever(self, timeout=1.0, max_packets=1, retry_first_connection=False):
        self.client.loop_forever(timeout, max_packets, retry_first_connection)

    def loop_start(self):
        self.client.loop_start()

    def connect(self, mqtt_host, mqtt_port, mqtt_keepalive):
        try:
            self.client.connect(mqtt_host, mqtt_port, mqtt_keepalive)  # 600为keepalive的时间间隔
            self.isConnected = True
            return True
        except:
            return False

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code: " + str(rc))
        # # 订阅
        # client.subscribe([("M-scsMonitor/Broadcast/0006/0001", 0), ("M-scsMonitor/Broadcast/0006/0002", 0),
        #                   ("M-scsMonitor/Broadcast/0006/0003", 0), ("M-scsMonitor/Broadcast/0006/0004", 0),
        #                   ("M-scsMonitor/Broadcast/0006/0005", 0), ("M-scsMonitor/Broadcast/0006/0006", 0),
        #                   ("M-scsMonitor/Broadcast/0006/0007", 0), ("M-scsMonitor/Broadcast/0006/0008", 0),
        #                   ("M-scsMonitor/Broadcast/0006/0009", 0), ("M-scsMonitor/Broadcast/0006/000A", 0),
        #                   ("M-scsMonitor/Broadcast/0006/000B", 0), ("M-scsMonitor/Broadcast/0006/000C", 0),
        #                   ("M-scsMonitor/Broadcast/0006/0010", 0), ("M-scsMonitor/Broadcast/0006/0011", 0),
        #                   ("M-scsMonitor/Broadcast/0006/0012", 0)])

    def on_message(self, client, userdata, msg):
        # ct = time.time()
        # local_time = time.localtime(ct)
        # data_head = time.strftime("%Y%m%d%H%M%S", local_time)
        # data_secs = (ct - int(ct)) * 1000
        # time_stamp = "%s%03d" % (data_head, data_secs)  # 17位时间戳
        # msg_16 = msg.payload.hex()
        # print("time:" + time_stamp + " " + "on_message topic:" + msg.topic + " message:" + str(msg_16))
        # self.queue.put(msg_16, msg.topic)
        self.queue.put(msg)

    def close_client(self):
        self.client.disconnect()
        self.isConnected = False

    #   订阅回调
    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("On Subscribed: qos = %d" % granted_qos)
        pass

    #   取消订阅回调
    def on_unsubscribe(self, client, userdata, mid):
        # print("取消订阅")
        print("On unSubscribed: qos = %d" % mid)
        pass

    #   发布消息回调
    def on_publish(self, client, userdata, mid):
        # print("发布消息")
        print("On onPublish: qos = %d" % mid)
        pass

    #   断开链接回调
    def on_disconnect(self, client, userdata, rc):
        # print("断开链接")
        print("Unexpected disconnection rc = " + str(rc))
        pass


class SSHRoad:
    def __init__(self):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

    def connect(self, hostname, port, username, password):
        try:
            self.client.connect(hostname, port, username, password)
            return True
        except:
            return False


if __name__ == '__main__':
    MqttRoad()
