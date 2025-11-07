#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base
from config import SENSOR_CONFIG_DB
from dao.database import create_db_engine, get_session

Base = declarative_base()

class SensorConfig(Base):
    """设备配置表"""
    __tablename__ = 'sensor_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_mac = Column(String(17), unique=True, nullable=False)
    report_interval = Column(Integer, default=60, comment='上报间隔(秒)')
    alarm_threshold_min = Column(Float, comment='报警阈值下限')
    alarm_threshold_max = Column(Float, comment='报警阈值上限')
    config_data = Column(Text, comment='其他配置信息(JSON格式)')
    updated_by = Column(String(50), comment='最后修改人')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'device_mac': self.device_mac,
            'report_interval': self.report_interval,
            'alarm_threshold_min': self.alarm_threshold_min,
            'alarm_threshold_max': self.alarm_threshold_max,
            'config_data': self.config_data,
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 创建设备配置数据库引擎和表
engine_config = create_db_engine(SENSOR_CONFIG_DB)
Base.metadata.create_all(engine_config)

def add_device_config(device_mac, report_interval=60, alarm_threshold_min=None, 
                     alarm_threshold_max=None, config_data=None, updated_by=None):
    """添加设备配置"""
    session = get_session(engine_config)
    try:
        new_config = SensorConfig(
            device_mac=device_mac,
            report_interval=report_interval,
            alarm_threshold_min=alarm_threshold_min,
            alarm_threshold_max=alarm_threshold_max,
            config_data=config_data,
            updated_by=updated_by
        )
        session.add(new_config)
        session.commit()
        return new_config
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_device_config(device_mac):
    """获取设备配置"""
    session = get_session(engine_config)
    try:
        config = session.query(SensorConfig).filter(SensorConfig.device_mac == device_mac).first()
        return config.to_dict() if config else None
    finally:
        session.close()

def update_device_config(device_mac, **kwargs):
    """更新设备配置"""
    session = get_session(engine_config)
    try:
        config = session.query(SensorConfig).filter(SensorConfig.device_mac == device_mac).first()
        if config:
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()