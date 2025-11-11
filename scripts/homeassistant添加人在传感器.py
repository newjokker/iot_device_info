import json
import time
import os
import paho.mqtt.client as mqtt

def if_config_topic_exists(config_topic):
    pass
    
def add_sensor(client, config_topic):
    """
    添加传感器到Home Assistant的自动发现功能
    
    Args:
        client: MQTT客户端实例
        config_topic: 配置主题，用于发布传感器配置信息
    """
    
    # 发布 config，让 Home Assistant 自动识别
    config_payload = {
        
        "name": "土星凌德泉座位人在传感器",                        # 传感器在 Home Assistant中显示的名称
        "unique_id": "binary_sensor_txkj_destop_occupancy",     # 传感器的唯一标识符，确保全局唯一
        "state_topic": "txkj/jokker_destop/person_occupancy",            # 传感器状态消息的主题，用于接收实际数据
        "device_class": "occupancy",                            # 设备类型，指定为occupancy（占用传感器）
        "payload_on": "occupied",                               # 表示"开"状态（有人）时接收到的消息内容
        "payload_off": "unoccupied",                            # 表示"关"状态（无人）时接收到的消息内容
        "value_template": "{{ value_json.state }}",             # 从JSON格式的消息中提取 state 字段的值作为传感器状态
        
        # 设备信息，用于在Home Assistant中组织相关实体
        "device": {  
            "identifiers": ["txkj_jokker_destop_occupancy_sensor_device"],     # 设备标识符，用于唯一识别设备
            "name": "OccupancySensor_LD2401​",                     # 设备名称
            "manufacturer": "CustomMQTTDevice",                         # 设备制造商信息
            "model": "LD2401"                                           # 设备型号
        },
        "availability_topic": "txkj/jokker_destop/occupancy_status",  # 设备在线状态主题
        "payload_available": "online",                              # 表示设备在线时发布的消息内容
        "payload_not_available": "offline"                          # 表示设备离线时发布的消息内容
    }

    # 发布配置信息到MQTT，retain=True表示消息会被持久化保存
    client.publish(config_topic, json.dumps(config_payload), retain=True)
    
def update_status(client, retain=True):
    # 上报在线状态
    client.publish("txkj/jokker_destop/occupancy_status", "online", retain=retain)

def has_occupancy(client, occupied=True, retain=True):
    state = "occupied" if occupied else "unoccupied"
    # 保留消息：MQTT broker会保存这条消息，当新的客户端订阅这个主题时，broker会立即将最后一条保留消息发送给新订阅者。
    client.publish("txkj/jokker_destop/person_occupancy", json.dumps({"state": state}), retain=retain)


if __name__ == "__main__":
    
    # -----------------------------------------------------------------------------------
    broker          = "8.153.160.138"  # 替换为你的 MQTT broker IP
    config_topic    = "homeassistant/binary_sensor/txkj_jokker_destop_occupancy/config"
    client          = mqtt.Client("txkj_destop_occupancy_sensor")
    # -----------------------------------------------------------------------------------
    client.connect(broker, 1883, 60)

    # add_sensor(client, config_topic=config_topic)
    
    # update_status(client, retain=True)
    
    has_occupancy(client, occupied=True, retain=True)

    client.disconnect()