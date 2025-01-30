#!/bin/bash
sleep 5
git clean -xdf
git reset --hard
git pull
cd /home/orangepi/duct-interface/interface
python3 main.py
