#!/bin/bash

# service redis-server start

uvicorn server:app --host 0.0.0.0 --port 52021 --workers 1

