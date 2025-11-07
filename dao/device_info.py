# dao/device_dao.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .database import Database, Device, SensorData, DeviceConfig, DeviceStatus

class BaseDAO:
    """基础DAO类"""
    
    def __init__(self):
        self.session = None
    
    def __enter__(self):
        self.session = Database.get_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
        self.session = None

class DeviceDAO(BaseDAO):
    """设备数据访问对象"""
    
    def add_device(self, device_data: Dict[str, Any]) -> Optional[Device]:
        """添加新设备"""
        try:
            # 检查设备是否已存在
            existing_device = self.session.query(Device).filter(
                Device.mac_address == device_data['mac_address']
            ).first()
            
            if existing_device:
                return None  # 设备已存在
            
            # 创建新设备
            device = Device(
                # 必须要的参数
                mac_address=device_data['mac_address'],
                device_name=device_data['device_name'],
                device_type=device_data['device_type'],
                # 可以不要的参数
                location=device_data.get('location'),
                description=device_data.get('description'),
                install_date=device_data.get('install_date'),
                status=DeviceStatus(device_data.get('status', 'active'))
            )
            
            self.session.add(device)
            self.session.commit()
            return device
            
        except Exception as e:
            self.session.rollback()
            print(f"添加设备失败: {e}")
            return None
    
    def get_device_by_mac(self, mac_address: str) -> Optional[Device]:
        """根据MAC地址查询设备"""
        try:
            return self.session.query(Device).filter(
                Device.mac_address == mac_address
            ).first()
        except Exception as e:
            print(f"查询设备失败: {e}")
            return None
    
    def update_device(self, mac_address: str, update_data: Dict[str, Any]) -> bool:
        """更新设备信息"""
        try:
            device = self.get_device_by_mac(mac_address)
            if not device:
                return False
            
            for key, value in update_data.items():
                if hasattr(device, key):
                    if key == 'status' and value:
                        setattr(device, key, DeviceStatus(value))
                    else:
                        setattr(device, key, value)
            
            device.updated_at = datetime.now()
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"更新设备失败: {e}")
            return False
    
    def get_all_devices(self, status: str = None) -> List[Device]:
        """获取所有设备列表"""
        try:
            query = self.session.query(Device)
            if status:
                query = query.filter(Device.status == DeviceStatus(status))
            
            return query.order_by(desc(Device.created_at)).all()
        except Exception as e:
            print(f"查询设备列表失败: {e}")
            return []
    
    def delete_device(self, mac_address: str) -> bool:
        """删除设备"""
        try:
            device = self.get_device_by_mac(mac_address)
            if device:
                self.session.delete(device)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            print(f"删除设备失败: {e}")
            return False

