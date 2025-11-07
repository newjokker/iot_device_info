
import sys

sys.path.append("/Volumes/Jokker/Code/iot_device_info")

import uuid
from dao.device_info import DeviceInfo, add_device, DeviceStatus
from datetime import datetime
from dao.device_info import add_device, DeviceStatus, get_all_devices, get_device_by_mac, delete_device, update_device_info
from datetime import datetime

# 增加一个设备
def test_add_device_info(mac):
    add_device(mac, f"Test Device_{str(uuid.uuid1())}", "sensor", "Test Location", "This is a test device.", datetime.now(), DeviceStatus.ACTIVE)

# 查询设备
def test_get_device_info(mac):
    for each in get_all_devices():
        print(each)
        print("-"*100)

# 修改设备状态
def test_update_device_info(mac):
    get_device_by_mac(mac, print=True)
    update_device_info(mac, device_type="新的类型， 这就是新的，哈哈")
    get_device_by_mac(mac, print=True)

# 删除一个设备
def test_delete_device_info(mac):
    delete_device(mac)

# 统计数据的类型
def test():
    
    devices = get_all_devices()
    # print(devices)
    status_count = {
        "active": 0,
        "inactive": 0,
        "maintenance": 0,
        "total": len(devices)
    }
    
    for device in devices:
        status_value = device['status']
        if status_value in status_count:
            status_count[status_value] += 1

    print(status_count)


if __name__ == "__main__":
    
    mac = "00:11:12:33:44:41"
    
    # delete_device(mac)

    test_add_device_info(mac)

    # test_get_device_info(mac)

    # test_update_device_info(mac)

    # test_delete_device_info(mac)

    test()

