---
name: shell_arm
description: Directly execute OS-level shell commands, bypassing the OpenClaw plugin runtime.
command: powershell.exe -ExecutionPolicy Bypass -File "C:\Users\Pierre\.openclaw\workspace\pierre-quant\skills\shell_arm\run_shell.ps1" -cmd
---

# Shell Arm Skill

This skill allows the agent to execute raw PowerShell commands directly on the host OS.

## Usage
Provide the exact command string you wish to execute.

## Example
`Get-Process | Where-Object {$_.Name -match "python"}`
