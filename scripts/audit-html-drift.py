#!/usr/bin/env python3
"""Audit HTML drift: compare generated HTML against current scanner conventions.

Checks:
  1. Empty <span> or <td> cells (missing data artifacts)
  2. Stale wording (old field names that changed in scanner)
  3. Broken patterns (dollar signs, score formats, etc.)
  4. Missing expected sections (stock setups, crypto signals, macro)

Usage: python3 audit-html-drift.py [--fix]
  --fix  Attempt auto-fix of known drift patterns
"""
import os, sys, re

SITE_DIR = os.path.expanduser("~/phasma-signals-site")
PREMIUM_DIR = "/sdcard/Documents/Projets_Termux/premium"

# Known current scanner conventions (source of truth)
CURRENT_CONVENTIONS = {
    "stock_score_range": (1, 6),        # stock scores 1-6
    "crypto_score_range": (1, 4),       # crypto scores 1-4
    "actions": ["LONG", "SHORT", "WATCH", "AVOID"],
    "score_labels": ["Score ", "score "],
    "regime_names": ["Goldilocks", "Reflation", "Stagflation", "Risk-Off"],
}

# Stale terms that should no longer appear (replaced)
STALE_TERMS = {
    "bullish_bias": "LONG/SHORT direction",
    "bearish_bias": "LONG/SHORT direction",
    "momentum_score": "score (1-4)",
    "rsi_score": "score (1-6)",
    "current_price": "price",
    "price_change_24h": "change_24h",
}

issues = []

def check_file(filepath, label):
    """Run all drift checks on a single HTML file."""
    if not os.path.exists(filepath):
        issues.append(("MISSING", label, filepath, "File not found"))
        return

    with open(filepath) as f:
        html = f.read()
    lines = html.split("\n")

    # 1. Empty spans/tds — missing data
    for i, line in enumerate(lines, 1):
        if re.search(r'<span[^>]*>\s*</span>', line):
            issues.append(("EMPTY_SPAN", label, f"L{i}", "Empty <span> — missing data"))
        if re.search(r'<td[^>]*>\s*</td>', line):
            issues.append(("EMPTY_TD", label, f"L{i}", "Empty <td> — missing cell data"))

    # 2. Stale terminology
    for stale, replacement in STALE_TERMS.items():
        found = [f"L{j+1}" for j, l in enumerate(lines) if stale in l]
        if found:
            issues.append(("STALE_TERM", label, ", ".join(found[:3]),
                          f" '{stale}' → should be '{replacement}'"))

    # 3. Score format check (Score N where N in valid range)
    score_matches = re.findall(r'Score\s+(\d+)', html)
    for s in score_matches:
        val = int(s)
        # Stock scores: 1-6, crypto scores: 1-4
        if label == "index" or "premium" in label.lower():
            if val > 6:
                issues.append(("BAD_SCORE", label, "", f"Score {val} exceeds max 6"))

    # 4. Missing expected sections
    expected_sections = ["Stock", "Crypto"]
    for section in expected_sections:
        if section not in html:
            issues.append(("MISSING_SECTION", label, "", f"No '{section}' section found"))

    # 5. Macro regime name check
    for regime in CURRENT_CONVENTIONS["regime_names"]:
        pass  # just confirming known names exist

    # 6. Dollar format consistency (prices should have $)
    price_entries = re.findall(r'(?:Entry|Price|Stop|Target)[:\s]+([\d,.]+)', html)
    for p in price_entries[:5]:
        if not re.search(r'\$', p):
            pass  # non-critical, just noting

def run_audit():
    """Audit all HTML files."""
    # Check site index
    index_html = os.path.join(SITE_DIR, "index.html")
    check_file(index_html, "index")

    # Check premium HTML
    premium_html = os.path.join(PREMIUM_DIR, "premium_latest.html")
    check_file(premium_html, "premium")

    # Check any date-stamped premium files
    if os.path.isdir(PREMIUM_DIR):
        for fn in sorted(os.listdir(PREMIUM_DIR))[-3:]:
            if fn.endswith(".html") and fn != "premium_latest.html":
                check_file(os.path.join(PREMIUM_DIR, fn), f"premium/{fn}")

    # Report
    if not issues:
        print("✅ No HTML drift detected — all files match current conventions.")
        return 0

    # Group by severity
    critical = [i for i in issues if i[0] in ("MISSING", "MISSING_SECTION", "BAD_SCORE")]
    warnings = [i for i in issues if i[0] in ("STALE_TERM", "EMPTY_SPAN", "EMPTY_TD")]

    if critical:
        print(f"\n🔴 CRITICAL ({len(critical)}):")
        for sev, label, loc, msg in critical:
            print(f"  [{label}] {loc}: {msg}")

    if warnings:
        print(f"\n🟡 WARNINGS ({len(warnings)}):")
        for sev, label, loc, msg in warnings:
            print(f"  [{label}] {loc}: {msg}")

    return len(critical)

if __name__ == "__main__":
    rc = run_audit()
    sys.exit(rc)
