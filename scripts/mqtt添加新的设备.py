import json
import time
import paho.mqtt.client as mqtt

broker = "8.153.160.138"  # 替换为你的 MQTT broker IP
client = mqtt.Client("livingroom_temp_sensor")

client.connect(broker, 1883, 60)

# 发布 config，让 Home Assistant 自动识别
config_topic = "homeassistant/sensor/livingroom_temperature/config"
config_payload = {
    "name": "Living Room Temperature",
    "unique_id": "sensor_livingroom_temperature",
    "state_topic": "home/livingroom/temperature",
    "unit_of_measurement": "°C",
    "device_class": "temperature",
    "value_template": "{{ value_json.value }}",
    "device": {
        "identifiers": ["livingroom_sensor_device"],
        "name": "Living Room Sensor",
        "manufacturer": "CustomMQTTDevice",
        "model": "TempMonitor v1"
    },
    "availability_topic": "home/livingroom/status",
    "payload_available": "online",
    "payload_not_available": "offline"
}
client.publish(config_topic, json.dumps(config_payload), retain=True)

# 上报在线状态
client.publish("home/livingroom/status", "online", retain=True)


client.publish("home/livingroom/temperature", json.dumps({"value": round(16.6, 1)}))
