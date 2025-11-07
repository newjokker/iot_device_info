#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
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
        
    def print_info(self):
        """美观地打印设备信息"""
        info = self.to_dict()
        
        # 定义中文字段名映射
        field_names = {
            'id': '设备ID',
            'mac_address': 'MAC地址',
            'device_name': '设备名称',
            'device_type': '设备类型',
            'location': '安装位置',
            'description': '设备描述',
            'install_date': '安装日期',
            'status': '设备状态',
            'created_at': '创建时间',
            'updated_at': '更新时间'
        }
        
        # 计算最长的字段名长度用于对齐
        max_field_length = max(len(name) for name in field_names.values())
        
        print("=" * 50)
        print("设备详细信息")
        print("=" * 50)
        
        for key, value in info.items():
            chinese_name = field_names.get(key, key)
            # 对齐字段名，并在冒号后添加空格
            field_display = f"{chinese_name}:".ljust(max_field_length + 2)
            
            # 处理可能为None的值
            display_value = value if value is not None else "未设置"
            
            print(f"{field_display} {display_value}")
        
        print("=" * 50)

# 创建设备信息数据库引擎和表
engine_device = create_db_engine(DEVICE_INFO_DB)
Base.metadata.create_all(engine_device)

def _add_device(mac_address, device_name, device_type, location=None, description=None, install_date=None, status=DeviceStatus.ACTIVE):
    """添加新设备
    
    Args:
        mac_address: 设备MAC地址，必须为17个字符且唯一
        device_name: 设备名称，不能为空
        device_type: 设备类型，不能为空
        location: 安装位置，可选
        description: 设备描述，可选
        install_date: 安装日期，可选
        status: 设备状态，默认为ACTIVE
    
    Returns:
        DeviceInfo: 新建设备对象
        
    Raises:
        ValueError: 参数验证失败
        Exception: 数据库操作失败
    """
    # 参数验证
    if not mac_address or len(mac_address) != 17:
        raise ValueError("MAC地址必须为17个字符")
    
    if not device_name or len(device_name.strip()) == 0:
        raise ValueError("设备名称不能为空")
    
    if not device_type or len(device_type.strip()) == 0:
        raise ValueError("设备类型不能为空")
    
    # 验证MAC地址格式（简单验证）
    if not all(c in '0123456789ABCDEFabcdef:' for c in mac_address):
        raise ValueError("MAC地址格式不正确，应包含0-9,A-F,a-f和冒号")
    
    session = get_session(engine_device)
    try:
        # 检查MAC地址是否已存在
        existing_device = session.query(DeviceInfo).filter(
            DeviceInfo.mac_address == mac_address
        ).first()
        
        if existing_device:
            raise ValueError(f"MAC地址 {mac_address} 已存在，设备名称为: {existing_device.device_name}")
        
        # 检查设备名称是否已存在（可选，根据业务需求）
        existing_name = session.query(DeviceInfo).filter(
            DeviceInfo.device_name == device_name
        ).first()
        
        if existing_name:
            raise ValueError(f"设备名称 '{device_name}' 已存在，对应的MAC地址为: {existing_name.mac_address}")
        
        # 创建设备记录
        new_device = DeviceInfo(
            mac_address=mac_address.upper(),  # 统一转为大写
            device_name=device_name.strip(),
            device_type=device_type.strip(),
            location=location.strip() if location else None,
            description=description.strip() if description else None,
            install_date=install_date,
            status=status
        )
        
        session.add(new_device)
        session.commit()
        return new_device
        
    except ValueError:
        # 重新抛出已知的业务逻辑错误
        raise
    except Exception as e:
        session.rollback()
        # 封装数据库错误信息
        if "UNIQUE constraint failed" in str(e) or "Duplicate entry" in str(e):
            raise ValueError(f"设备信息已存在，可能由于重复的MAC地址或设备名称: {mac_address}")
        else:
            raise Exception(f"数据库操作失败: {str(e)}")
    finally:
        session.close()

def validate_mac_address(mac_address):
    """
    验证并规范化 MAC 地址格式
    支持常见格式: AA:BB:CC:DD:EE:FF 或 AA-BB-CC-DD-EE-FF
    返回值：
        如果合法 -> 返回规范化后的 MAC（大写、冒号分隔）
        如果非法 -> 返回 None
    """
    if not mac_address or not isinstance(mac_address, str):
        return None

    # 去除首尾空格
    mac_address = mac_address.strip()

    # 匹配格式: 允许 : 或 - 分隔
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    if re.match(pattern, mac_address):
        # 统一成冒号分隔 + 大写形式
        normalized = mac_address.replace('-', ':').upper()
        return normalized

    # 尝试匹配无分隔符形式，例如 AABBCCDDEEFF
    pattern_no_sep = r'^[0-9A-Fa-f]{12}$'
    if re.match(pattern_no_sep, mac_address):
        normalized = ':'.join(mac_address[i:i+2] for i in range(0, 12, 2)).upper()
        return normalized

    return None

def _is_device_name_exists(device_name, exclude_mac=None):
    """检查设备名称是否已存在（排除指定MAC地址）"""
    session = get_session(engine_device)
    try:
        query = session.query(DeviceInfo).filter(DeviceInfo.device_name == device_name)
        if exclude_mac:
            query = query.filter(DeviceInfo.mac_address != exclude_mac)
        return query.first() is not None
    finally:
        session.close()

def _is_mac_address_exists(mac_address, exclude_name=None):
    """检查MAC地址是否已存在（排除指定设备名称）"""
    session = get_session(engine_device)
    try:
        query = session.query(DeviceInfo).filter(DeviceInfo.mac_address == mac_address)
        if exclude_name:
            query = query.filter(DeviceInfo.device_name != exclude_name)
        return query.first() is not None
    finally:
        session.close()

def add_device(mac_address, device_name, device_type, location=None, description=None, install_date=None, status=DeviceStatus.ACTIVE):
    """增强版的添加设备函数，包含更严格的验证"""
    
    # 标准化MAC地址
    if not validate_mac_address(mac_address):
        raise ValueError("MAC地址格式不正确")
        
    # 参数验证
    if not device_name or len(device_name.strip()) == 0:
        raise ValueError("设备名称不能为空")
    
    if len(device_name.strip()) > 50:
        raise ValueError("设备名称长度不能超过50个字符")
    
    if not device_type or len(device_type.strip()) == 0:
        raise ValueError("设备类型不能为空")
    
    if len(device_type.strip()) > 20:
        raise ValueError("设备类型长度不能超过20个字符")
    
    # 检查唯一性
    if _is_mac_address_exists(mac_address):
        raise ValueError(f"MAC地址 {mac_address} 已存在")
    
    if _is_device_name_exists(device_name):
        raise ValueError(f"设备名称 '{device_name}' 已存在")
    
    return _add_device(mac_address, device_name, device_type, location, description, install_date, status)

def get_all_devices():
    """获取所有设备"""
    session = get_session(engine_device)
    try:
        devices = session.query(DeviceInfo).all()
        return [device.to_dict() for device in devices]
    finally:
        session.close()

def get_device_by_mac(mac_address, print=False):
    """根据MAC地址获取设备"""
    session = get_session(engine_device)
    try:
        device = session.query(DeviceInfo).filter(DeviceInfo.mac_address == mac_address).first()
        if print:
            device.print_info()
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
        
def delete_device(mac_address):
    """根据设备的MAC地址删除设备"""
    session = get_session(engine_device)
    try:
        # 查找设备
        device = session.query(DeviceInfo).filter(DeviceInfo.mac_address == mac_address).first()
        
        if not device:
            raise ValueError(f"设备 {mac_address} 不存在")
        
        # 删除设备
        session.delete(device)
        session.commit()
        print(f"设备 {mac_address} 删除成功")
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
  
def update_device_info(mac_address, device_name=None, device_type=None, location=None, description=None, status=None):
    """修改设备信息（只能修改除了ID和MAC地址的字段）"""
    session = get_session(engine_device)
    try:
        # 查找设备
        device = session.query(DeviceInfo).filter(DeviceInfo.mac_address == mac_address).first()
        
        if not device:
            raise ValueError(f"设备 {mac_address} 不存在")
        
        # 只能修改非ID和非MAC地址的字段
        if device_name:
            device.device_name = device_name.strip()
            if _is_device_name_exists(device_name):
                raise ValueError(f"设备名称 '{device_name}' 已存在")
        if device_type:
            device.device_type = device_type.strip()
        if location:
            device.location = location.strip()
        if description:
            device.description = description.strip()
        if status:
            device.status = status
        
        session.commit()
        print(f"设备 {mac_address} 信息更新成功")
        return device.to_dict()  # 返回更新后的设备信息
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
