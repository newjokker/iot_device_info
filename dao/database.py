# dao/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean, BigInteger, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from datetime import datetime
import enum
import os
from typing import Optional

Base = declarative_base()

class DeviceStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"     # 维护中

class Device(Base):
    """设备基本信息表"""
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mac_address = Column(String(17), unique=True, nullable=False, comment='设备MAC地址')
    device_name = Column(String(50), nullable=False, comment='设备名称')
    device_type = Column(String(20), nullable=False, comment='设备类型')
    location = Column(String(100), comment='安装位置')
    description = Column(Text, comment='设备描述')
    install_date = Column(DateTime, comment='安装日期')
    status = Column(Enum(DeviceStatus), default=DeviceStatus.ACTIVE, comment='设备状态')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'mac_address': self.mac_address,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'location': self.location,
            'description': self.description,
            'install_date': self.install_date.isoformat() if self.install_date else None,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class DeviceConfig(Base):
    """设备配置表"""
    __tablename__ = 'device_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_mac = Column(String(17), unique=True, nullable=False)
    report_interval = Column(Integer, default=60, comment='上报间隔(秒)')
    alarm_threshold_min = Column(Float, comment='报警阈值下限')
    alarm_threshold_max = Column(Float, comment='报警阈值上限')
    config_data = Column(Text, comment='其他配置信息(JSON格式)')
    updated_by = Column(String(50), comment='最后修改人')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

