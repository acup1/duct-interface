#!/bin/bash
git clean -df
git pull
cd /home/orangepi/duct-interface/interface
py main.py
