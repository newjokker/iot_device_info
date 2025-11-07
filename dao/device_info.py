#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import declarative_base
from config import DEVICE_INFO_DB
from dao.database import create_db_engine, get_session

Base = declarative_base()

class DeviceStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class DeviceInfo(Base):
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

# 创建设备信息数据库引擎和表
engine_device = create_db_engine(DEVICE_INFO_DB)
Base.metadata.create_all(engine_device)

def add_device(mac_address, device_name, device_type, location=None, description=None, install_date=None, status=DeviceStatus.ACTIVE):
    """添加新设备"""
    session = get_session(engine_device)
    try:
        new_device = DeviceInfo(
            mac_address=mac_address,
            device_name=device_name,
            device_type=device_type,
            location=location,
            description=description,
            install_date=install_date,
            status=status
        )
        session.add(new_device)
        session.commit()
        return new_device
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_all_devices():
    """获取所有设备"""
    session = get_session(engine_device)
    try:
        devices = session.query(DeviceInfo).all()
        return [device.to_dict() for device in devices]
    finally:
        session.close()

def get_device_by_mac(mac_address):
    """根据MAC地址获取设备"""
    session = get_session(engine_device)
    try:
        device = session.query(DeviceInfo).filter(DeviceInfo.mac_address == mac_address).first()
        return device.to_dict() if device else None
    finally:
        session.close()

def update_device_status(mac_address, status):
    """更新设备状态"""
    session = get_session(engine_device)
    try:
        device = session.query(DeviceInfo).filter(DeviceInfo.mac_address == mac_address).first()
        if device:
            device.status = status
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()