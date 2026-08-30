"""
pierre_quant/runners/run_recon.py
Standardized Sentry Recon Entrypoint routing directly to Target Deep-Dive Dossier.
"""
from __future__ import annotations
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.platform == "win32" and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.orchestration.run_single_dossier import main as run_dossier_main


def main():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        ticker = sys.argv[1]
        sys.argv = [sys.argv[0], "--ticker", ticker]
    run_dossier_main()


if __name__ == "__main__":
    main()
