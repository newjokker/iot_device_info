
import sys

sys.path.append("/Volumes/Jokker/Code/iot_device_info")

from dao.device_info import DeviceInfo, add_device, DeviceStatus
from datetime import datetime

def test_add_device_info():

    result = add_device("00:11:22:33:44:55", "Test Device", "sensor", "Test Location", "This is a test device.", datetime.now(), DeviceStatus.ACTIVE)
    assert result.id is not None
    assert result.mac_address == "00:11:22:33:44:55"

test_add_device_info()
