@echo off
title Antigravity Mission Control
:: This line MUST point to where your project files live
cd /d "C:\Users\crypt\OneDrive\Desktop\Antigravity skill\Trading team"
echo Launching local Blackwell kernels...
streamlit run app_gui.py --theme.base="dark"
pause
