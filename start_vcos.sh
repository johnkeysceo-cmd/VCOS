#!/bin/bash
# VCOS Linux/macOS Startup Script
# Boots ScreenArc and watches for videos to process

echo "Starting VCOS Boot System..."
cd vcos
python3 scripts/boot_vcos.py
