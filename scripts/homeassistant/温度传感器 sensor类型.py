import json
import paho.mqtt.client as mqtt


def add_temperature_sensor(client, config_topic):
    """
    添加一个温度传感器到 Home Assistant (MQTT Sensor)
    """

    config_payload = {
        "name": "桌面环境温度传感器",
        "unique_id": "sensor_txkj_desktop_temperature",
        "state_topic": "txkj/jokker_desktop/temperature",

        # 关键类型：温度传感器
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "value_template": "{{ value_json.temperature }}",

        "device": {
            "identifiers": ["txkj_jokker_desktop_temperature_device"],
            "name": "TemperatureSensor_DS18B20",
            "manufacturer": "CustomMQTTDevice",
            "model": "DS18B20"
        },

        "availability_topic": "txkj/jokker_desktop/temperature_status",
        "payload_available": "online",
        "payload_not_available": "offline"
    }

    client.publish(config_topic, json.dumps(config_payload), retain=True)


def update_status(client, retain=True):
    """ 上报在线状态 """
    client.publish("txkj/jokker_desktop/temperature_status", "online", retain=retain)


def report_temperature(client, temp_c, retain=True):
    """ 上报温度数据 """
    payload = {
        "temperature": temp_c
    }

    client.publish(
        "txkj/jokker_desktop/temperature",
        json.dumps(payload),
        retain=retain
    )


if __name__ == "__main__":

    broker = "8.153.160.138"
    config_topic = "homeassistant/sensor/txkj_jokker_desktop_temperature/config"

    client = mqtt.Client("txkj_desktop_temperature_sensor")
    client.connect(broker, 1883, 60)

    # 自动发现（只需要发布一次）
    # add_temperature_sensor(client, config_topic)

    # 上报在线状态
    # update_status(client)

    # 上报温度 (示例: 25.6°C)
    report_temperature(client, temp_c=25.6)

    client.disconnect()
