@echo off
title Antigravity Mission Control
:: This line MUST point to where your project files live
cd /d "C:\Users\Pierre\.openclaw\workspace\pierre-quant"

echo Launching local Blackwell kernels...
streamlit run app.py --theme.base="dark"
pause
