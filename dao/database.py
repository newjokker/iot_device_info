#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

def create_db_engine(db_path):
    """创建数据库引擎"""
    database_url = f"sqlite:///{db_path}"
    return sa_create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_pre_ping=True,
        pool_recycle=3600
    )

def get_session(engine):
    """获取数据库会话"""
    Session = sessionmaker(bind=engine)
    return Session()