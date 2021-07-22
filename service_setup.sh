#!/bin/bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo $SRC_DIR

# Disable vision update service
sudo systemctl stop flc_app.service
sudo rm /etc/systemd/system/flc_app.service

# Unit file for Vision update service
echo "[Unit]
Description=FLC APP service
After=network.target
[Service]
Type=simple
ExecStart="$SRC_DIR"/flc.py
User=$USER
[Install]
WantedBy=multi-user.target" | sudo tee -a /etc/systemd/system/flc_app.service

sudo systemctl daemon-reload

# Enable the vision upsate start service on boot
sudo systemctl enable flc_app.service

# Start vision update service now
sudo systemctl start flc_app.service

