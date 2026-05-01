@echo off
title LeetCode Tracker
cd /d "G:\My Drive\Coding\leetcode-tracker"
call venv\Scripts\activate.bat
start http://127.0.0.1:5000
python app.py
