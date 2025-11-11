#!/bin/bash 

# Check if escalator_algo_server is running
if systemctl is-active --quiet iot_device_info.service; then
    echo "iot_device_info.service is running. Stopping it..."
    sudo systemctl stop iot_device_info.service
    echo "Service stopped."
fi

echo "Copy server to /etc/systemd/system"
sudo cp ./iot_device_info.service  /etc/systemd/system/iot_device_info.service

# Reload systemd daemon, enable, and start the service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling iot_device_info.service..."
sudo systemctl enable iot_device_info.service

echo "Starting iot_device_info.service..."
sudo systemctl start iot_device_info.service

# Wait for 20 seconds
echo "Wait for start..."
sleep 5

# Check the status of the service
echo "Checking the status of iot_device_info.service..."
sudo systemctl status iot_device_info.service

# 查看实时日志
# journalctl -u iot_device_info.service -f 

# 关闭服务
# sudo systemctl disable iot_device_info; sudo systemctl stop iot_device_info

# 开启服务
# sudo systemctl start iot_device_info; sudo systemctl enable iot_device_info



