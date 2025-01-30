#!/bin/bash
git clean -df
git pull
cd /home/orangepi/duct-interface/interface
python3 main.py
