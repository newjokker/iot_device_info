#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PEP 8 compliant
# Author: Jokker

import time
import redis
import json
import requests
import traceback
import copy
import os
from fastapi import FastAPI, Request, HTTPException, status, Query, Path
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import numpy as np
from scipy import signal

from dao.device_config import DeviceConfig
from dao.device_info import DeviceInfo, DeviceStatus, add_device, get_all_devices, get_device_by_mac, update_device_status, delete_device, update_device_info, validate_mac_address

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
# app.include_router(vis_router)

app.mount("/static", StaticFiles(directory="./templates"), name="static")

# Pydantic 模型定义
class DeviceCreateRequest(BaseModel):
    """创建设备请求模型"""
    mac_address: str = Field(..., description="设备MAC地址，格式如：AA:BB:CC:DD:EE:FF")
    device_name: str = Field(..., description="设备名称", max_length=50)
    device_type: str = Field(..., description="设备类型", max_length=20)
    location: Optional[str] = Field(None, description="安装位置", max_length=100)
    description: Optional[str] = Field(None, description="设备描述")
    install_date: Optional[datetime.datetime] = Field(None, description="安装日期")
    status: DeviceStatus = Field(DeviceStatus.ACTIVE, description="设备状态")

    @validator('mac_address')
    def validate_mac_address(cls, v):
        normalized_mac = validate_mac_address(v)
        if not normalized_mac:
            raise ValueError('MAC地址格式不正确')
        return normalized_mac

    @validator('device_name')
    def validate_device_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('设备名称不能为空')
        return v.strip()

    @validator('device_type')
    def validate_device_type(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('设备类型不能为空')
        return v.strip()

class DeviceUpdateRequest(BaseModel):
    """更新设备请求模型"""
    device_name: Optional[str] = Field(None, description="设备名称", max_length=50)
    device_type: Optional[str] = Field(None, description="设备类型", max_length=20)
    location: Optional[str] = Field(None, description="安装位置", max_length=100)
    description: Optional[str] = Field(None, description="设备描述")
    status: Optional[DeviceStatus] = Field(None, description="设备状态")

    @validator('device_name')
    def validate_device_name(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('设备名称不能为空')
        return v.strip() if v else v

    @validator('device_type')
    def validate_device_type(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('设备类型不能为空')
        return v.strip() if v else v

class DeviceResponse(BaseModel):
    """设备响应模型"""
    id: int
    mac_address: str
    device_name: str
    device_type: str
    location: Optional[str]
    description: Optional[str]
    install_date: Optional[datetime.datetime]
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

class StatusUpdateRequest(BaseModel):
    """状态更新请求模型"""
    status: DeviceStatus

class SuccessResponse(BaseModel):
    """成功响应模型"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    error: str
    details: Optional[str] = None

# 工具函数
def create_success_response(message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """创建成功响应"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=SuccessResponse(message=message, data=data).dict()
    )

def create_error_response(error: str, details: str = None, status_code: int = status.HTTP_400_BAD_REQUEST) -> JSONResponse:
    """创建错误响应"""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=error, details=details).dict()
    )

# API 路由
@app.get("/")
async def root():
    """根路径"""
    return {"message": "设备管理API服务", "version": "1.0.0"}

@app.get("/api/devices", response_model=List[DeviceResponse])
async def get_devices(
    status: Optional[DeviceStatus] = Query(None, description="按状态筛选设备"),
    device_type: Optional[str] = Query(None, description="按设备类型筛选")
):
    """
    获取所有设备列表
    - 支持按状态和设备类型筛选
    """
    try:
        devices = get_all_devices()
        
        # 筛选逻辑
        filtered_devices = devices
        if status:
            filtered_devices = [d for d in filtered_devices if d['status'] == status.value]
        if device_type:
            filtered_devices = [d for d in filtered_devices if d['device_type'] == device_type]
        
        return filtered_devices
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设备列表失败: {str(e)}"
        )

@app.get("/api/devices/{mac_address}", response_model=DeviceResponse)
async def get_device(mac_address: str = Path(..., description="设备MAC地址")):
    """
    根据MAC地址获取设备详细信息
    """
    try:
        # 验证MAC地址格式
        normalized_mac = validate_mac_address(mac_address)
        if not normalized_mac:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MAC地址格式不正确"
            )
        
        device = get_device_by_mac(normalized_mac)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备 {normalized_mac} 不存在"
            )
        
        return device
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设备信息失败: {str(e)}"
        )

@app.post("/api/devices")
async def create_device(device_data: DeviceCreateRequest):
    """
    创建设备
    - 需要提供完整的设备信息
    - MAC地址和设备名称必须唯一
    """
        
    try:
        status, msg = add_device(
            mac_address=device_data.mac_address,
            device_name=device_data.device_name,
            device_type=device_data.device_type,
            location=device_data.location,
            description=device_data.description,
            install_date=device_data.install_date,
            status=device_data.status
        )
        if status:
            return {"status": "success", "info": msg}
        else:
            return {"status": "failed", "error_info": msg}

    except Exception as e:
        
        error_info = traceback.format_exc()
        print(error_info)
        
        return {"status": "failed", "error_info": f"{error_info}"}

@app.put("/api/devices/{mac_address}", response_model=DeviceResponse)
async def update_device(
    mac_address: str = Path(..., description="设备MAC地址"),
    update_data: DeviceUpdateRequest = ...
):
    """
    更新设备信息
    - 只能修改除ID和MAC地址外的字段
    - 设备名称必须唯一
    """
    try:
        # 验证MAC地址格式
        normalized_mac = validate_mac_address(mac_address)
        if not normalized_mac:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MAC地址格式不正确"
            )
        
        # 检查设备是否存在
        existing_device = get_device_by_mac(normalized_mac)
        if not existing_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备 {normalized_mac} 不存在"
            )
        
        # 构建更新数据
        update_dict = {}
        if update_data.device_name is not None:
            update_dict['device_name'] = update_data.device_name
        if update_data.device_type is not None:
            update_dict['device_type'] = update_data.device_type
        if update_data.location is not None:
            update_dict['location'] = update_data.location
        if update_data.description is not None:
            update_dict['description'] = update_data.description
        if update_data.status is not None:
            update_dict['status'] = update_data.status
        
        if not update_dict:
            return {"status": "success", "info": f"未修改任何内容"}
            
        status, msg = update_device_info(normalized_mac, **update_dict)
        if status:
            return {"status": "failed", "error_info": f"{error_info}"}
        else:
            return {"status": "failed", "error_info": msg}
    except Exception as e:

        error_info = traceback.format_exc()
        print(error_info)        
        return {"status": "failed", "error_info": f"{error_info}"}

@app.patch("/api/devices/{mac_address}/status", response_model=DeviceResponse)
async def update_device_status_api(
    mac_address: str = Path(..., description="设备MAC地址"),
    status_data: StatusUpdateRequest = ...
):
    """
    更新设备状态
    - 只更新设备状态字段
    """
    try:
        # 验证MAC地址格式
        normalized_mac = validate_mac_address(mac_address)
        if not normalized_mac:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MAC地址格式不正确"
            )
        
        # 检查设备是否存在
        existing_device = get_device_by_mac(normalized_mac)
        if not existing_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备 {normalized_mac} 不存在"
            )
        
        success = update_device_status(normalized_mac, status_data.status)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新设备状态失败"
            )
        
        # 返回更新后的设备信息
        updated_device = get_device_by_mac(normalized_mac)
        return updated_device
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新设备状态失败: {str(e)}"
        )

@app.delete("/api/devices/{mac_address}")
async def remove_device(mac_address: str = Path(..., description="设备MAC地址")):
    """
    删除设备
    - 根据MAC地址删除设备
    """
    try:
        # 验证MAC地址格式
        normalized_mac = validate_mac_address(mac_address)
        if not normalized_mac:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MAC地址格式不正确"
            )
        
        # 检查设备是否存在
        existing_device = get_device_by_mac(normalized_mac)
        if not existing_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备 {normalized_mac} 不存在"
            )
        
        success = delete_device(normalized_mac)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除设备失败"
            )
        
        return create_success_response(f"设备 {normalized_mac} 删除成功")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除设备失败: {str(e)}"
        )

@app.get("/api/device-types")
async def get_device_types():
    """
    获取所有设备类型列表
    - 用于前端下拉选择
    """
    try:
        devices = get_all_devices()
        device_types = list(set(device['device_type'] for device in devices))
        return {"device_types": sorted(device_types)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设备类型列表失败: {str(e)}"
        )

@app.get("/api/device-status")
async def get_device_status_count():
    """
    获取设备状态统计
    - 用于前端仪表板显示
    """
    try:
        devices = get_all_devices()
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
        
        return status_count
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设备状态统计失败: {str(e)}"
        )

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error="服务器内部错误", details=str(exc)).dict()
    )

@app.get("/menu")
async def menu():
    html_path = "./templates/device_info.html"
    
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "UI_FILE_NOT_FOUND",
                "message": f"模板文件 {html_path} 不存在",
                "solution": "请检查服务器是否部署了前端资源"
            }
        )
