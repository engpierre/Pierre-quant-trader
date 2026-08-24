"""
pierre_quant/runners/run_vault_query.py
High-Throughput Markdown Vault Search Runner for OpenClaw & Hermes Swarms.
"""
from __future__ import annotations
import argparse
import json
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("VaultQueryRunner")

VAULT_PATH = Path(r"C:\Users\Pierre\.openclaw\workspace\vault")


def search_vault(query: str, limit: int = 5) -> list[dict[str, str]]:
    """Fast regex search across all markdown files in the local vault."""
    if not VAULT_PATH.exists():
        logger.error(f"Vault path not found: {VAULT_PATH}")
        return []

    results = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    for md_file in VAULT_PATH.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            matches = [line.strip() for line in content.splitlines() if pattern.search(line)]
            if matches:
                results.append({
                    "file": md_file.name,
                    "path": str(md_file.relative_to(VAULT_PATH)),
                    "snippets": matches[:3]
                })
                if len(results) >= limit:
                    break
        except Exception as err:
            logger.warning(f"Error reading {md_file}: {err}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query Pierre Quant Obsidian Vault")
    parser.add_argument("query", type=str, help="Search query string")
    parser.add_argument("--limit", type=int, default=5, help="Max files to return")
    args = parser.parse_args()

    findings = search_vault(args.query, args.limit)
    print(json.dumps({"query": args.query, "total_matches": len(findings), "results": findings}, indent=2))
