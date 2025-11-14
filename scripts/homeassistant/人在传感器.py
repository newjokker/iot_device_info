import json
import time
import os
import paho.mqtt.client as mqtt

def add_presence_sensor(client, config_topic):
    """
    添加一个存在传感器 (presence) 到 Home Assistant
    """

    config_payload = {
        "name": "土星凌德泉人体存在传感器",                 # 在 Home Assistant 中的名称
        "unique_id": "binary_sensor_txkj_desktop_presence",   # 全局唯一 ID
        "state_topic": "txkj/jokker_desktop/presence_state",  # 状态上报主题

        "device_class": "presence",                # <<< 关键：使用 presence 类型
        "payload_on": "present",                  # 有人
        "payload_off": "not_present",             # 无人
        "value_template": "{{ value_json.state }}",

        "device": {
            "identifiers": [
                "txkj_jokker_desktop_presence_sensor_device"
            ],
            "name": "PresenceSensor_LD2401",
            "manufacturer": "CustomMQTTDevice",
            "model": "LD2401"
        },

        "availability_topic": "txkj/jokker_desktop/presence_status",
        "payload_available": "online",
        "payload_not_available": "offline"
    }

    client.publish(config_topic, json.dumps(config_payload), retain=True)

def update_status(client, retain=True):
    """ 上报在线状态 """
    client.publish("txkj/jokker_desktop/presence_status", "online", retain=retain)

def report_presence(client, present=True, retain=True):
    """ 上报 presence 状态 """
    state = "present" if present else "not_present"
    client.publish(
        "txkj/jokker_desktop/presence_state",
        json.dumps({"state": state}),
        retain=retain
    )


if __name__ == "__main__":

    broker = "8.153.160.138"
    config_topic = "homeassistant/binary_sensor/txkj_jokker_desktop_presence/config"

    client = mqtt.Client("txkj_desktop_presence_sensor")
    client.connect(broker, 1883, 60)

    # 发布自动发现配置
    # add_presence_sensor(client, config_topic)

    # 上报在线
    # update_status(client)

    # 上报 presence 存在状态
    report_presence(client, present=True)

    client.disconnect()
