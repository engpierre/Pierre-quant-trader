"""
pierre_quant/tools/swarm_commands.py
Deterministic command execution router for OpenClaw and Hermes.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

# Reconfigure stdout for utf-8 if supported
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

WORKSPACE_ROOT = Path(r"C:\Users\Pierre\.openclaw\workspace")
PYTHON_EXE = WORKSPACE_ROOT / "Julie-Core" / ".venv" / "Scripts" / "python.exe"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)

RUNNERS_DIR = WORKSPACE_ROOT / "pierre-quant" / "pierre_quant" / "runners"
REPORTS_DIR = WORKSPACE_ROOT / "vault" / "Reports"


def run_command(command_name: str, *args) -> str:
    """Executes deterministic quant runners and returns formatted Markdown."""
    cmd_clean = command_name.lstrip("/").lower()

    cmd_map = {
        "status": (RUNNERS_DIR / "run_swarm_status.py", REPORTS_DIR / "System_Status.md"),
        "alpha": (RUNNERS_DIR / "run_confluence_scan.py", REPORTS_DIR / "Daily_Alpha_Matrix.md"),
        "audit": (RUNNERS_DIR / "run_weekly_call_audit.py", REPORTS_DIR / "Weekly_Call_Performance.md"),
        "recon": (RUNNERS_DIR / "run_recon.py", None),
        "ratchet": (RUNNERS_DIR / "run_profit_guard.py", REPORTS_DIR / "Profit_Guard_Matrix.md")
    }

    if cmd_clean not in cmd_map:
        return f"Unknown command: /{command_name}. Available: /status, /alpha, /audit, /recon, /ratchet"

    script_path, report_path = cmd_map[cmd_clean]

    if not script_path.exists():
        return f"Error: Runner script not found at {script_path}"

    try:
        exec_cmd = [str(PYTHON_EXE), str(script_path)]
        if args:
            exec_cmd.extend(args)

        proc = subprocess.run(exec_cmd, capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")

        if report_path and report_path.exists():
            return report_path.read_text(encoding="utf-8")
        
        output = proc.stdout.strip()
        return output if output else f"Command /{cmd_clean} executed successfully."
    except subprocess.CalledProcessError as e:
        return f"Execution Error on /{cmd_clean}:\n{e.stderr or e.stdout}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    sub_args = sys.argv[2:]
    print(run_command(cmd, *sub_args))
