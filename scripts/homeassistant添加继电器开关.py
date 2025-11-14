import json
import time
import os
import paho.mqtt.client as mqtt

def add_switch(client, config_topic):
    """
    添加继电器开关到 Home Assistant 自动发现
    """

    config_payload = {
        "name": "土星凌德泉桌面继电器",
        "unique_id": "switch_txkj_desktop_relay",
        
        # HA 显示状态的 topic
        "state_topic": "txkj/jokker_desktop/relay/state",

        # 控制继电器开关的 topic
        "command_topic": "txkj/jokker_desktop/relay/command",

        # 设备信息
        "device": {
            "identifiers": ["txkj_jokker_desktop_relay_device"],
            "name": "RelayModule",
            "manufacturer": "CustomMQTTDevice",
            "model": "MQTTRelayV1"
        },

        # 有些开关需要这个
        "payload_on": "ON",
        "payload_off": "OFF",
        "state_on": "ON",
        "state_off": "OFF",

        # 继电器是否有保持状态
        "optimistic": False,

        "availability_topic": "txkj/jokker_desktop/relay/availability",
        "payload_available": "online",
        "payload_not_available": "offline"
    }

    client.publish(config_topic, json.dumps(config_payload), retain=True)


def update_availability(client, retain=True):
    """上报继电器是否在线"""
    client.publish("txkj/jokker_desktop/relay/availability", "online", retain=retain)


def report_state(client, is_on=True, retain=True):
    """
    上报当前继电器状态
    """
    state = "ON" if is_on else "OFF"
    client.publish("txkj/jokker_desktop/relay/state", state, retain=retain)


if __name__ == "__main__":
    
    broker = "8.153.160.138"
    config_topic = "homeassistant/switch/txkj_jokker_desktop_relay/config"
    
    client = mqtt.Client("txkj_desktop_relay")

    client.connect(broker, 1883, 60)

    # 只需执行一次，创建 Home Assistant 自动发现
    # add_switch(client, config_topic)

    # 上报继电器在线
    # update_availability(client)

    # 上报继电器是开还是关
    report_state(client, is_on=True)

    client.disconnect()
