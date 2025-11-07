#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PEP 8 compliant
# Author: Jokker

import time
import redis
import json
import config
import requests
import traceback
import copy
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import datetime
import numpy as np
from scipy import signal



app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
# app.include_router(vis_router)

app.mount("/static", StaticFiles(directory="./templates"), name="static")
