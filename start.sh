#!/bin/bash
sleep 5
cd /home/orangepi/duct-interface/
git clean -xdf
git reset --hard
git pull
cd /home/orangepi/duct-interface/interface
python3 main.py
