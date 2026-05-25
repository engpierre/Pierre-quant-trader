---
name: web_arm
description: Directly open a URL in Google Chrome, bypassing the OpenClaw plugin runtime.
command: powershell.exe -ExecutionPolicy Bypass -File "C:\Users\Pierre\.openclaw\workspace\pierre-quant\skills\web_arm\browse_url.ps1" -url
---

# Web Arm Skill

This skill allows the agent to open a specific URL in the host's Chrome browser.

## Usage
Provide the full URL (e.g., https://www.google.com) you wish to open.

## Example
`https://finance.yahoo.com/quote/PLTR`
