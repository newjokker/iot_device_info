import json
import time
import os
import paho.mqtt.client as mqtt

def if_config_topic_exists(config_topic):
    pass
    
def add_sensor(client, config_topic):

    # 发布 config，让 Home Assistant 自动识别
    
    config_payload = {
        "name": "Living Room Occupancy",
        "unique_id": "binary_sensor_txkj_destop_occupancy",
        "state_topic": "home/txkj_destop/occupancy",
        "device_class": "occupancy",  # 设备类型改为 occupancy
        "payload_on": "occupied",     # 有人时的状态
        "payload_off": "unoccupied",  # 无人时的状态
        "value_template": "{{ value_json.state }}",  # 从JSON中提取state字段
        "device": {
            "identifiers": ["txkj_destop_occupancy_sensor_device"],
            "name": "Living Room Occupancy Sensor",
            "manufacturer": "CustomMQTTDevice",
            "model": "Occupancy Monitor v1"
        },
        "availability_topic": "home/txkj_destop/occupancy_status",
        "payload_available": "online",
        "payload_not_available": "offline"
    }

    client.publish(config_topic, json.dumps(config_payload), retain=True)

def update_status(client, retain=True):
    # 上报在线状态
    client.publish("home/txkj_destop/occupancy_status", "online", retain=retain)

def has_occupancy(client, occupied=True, retain=True):
    state = "occupied" if occupied else "unoccupied"
    # 保留消息：MQTT broker会保存这条消息，当新的客户端订阅这个主题时，broker会立即将最后一条保留消息发送给新订阅者。
    client.publish("home/txkj_destop/occupancy", json.dumps({"state": state}), retain=retain)


if __name__ == "__main__":
    
    # -----------------------------------------------------------------------------------
    broker          = "8.153.160.138"  # 替换为你的 MQTT broker IP
    config_topic    = "homeassistant/binary_sensor/txkj_destop_occupancy/config"
    client          = mqtt.Client("txkj_destop_occupancy_sensor")
    # -----------------------------------------------------------------------------------
    client.connect(broker, 1883, 60)

    if not if_config_topic_exists(config_topic):
        add_sensor(client)
        
    has_occupancy(client, occupied=True)

    client.disconnect()