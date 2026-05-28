#!/usr/bin/env python3
"""Generate Phasma Signals site index.html from scan data."""
import json, os

SITE_DIR = os.path.expanduser("~/phasma-signals-site")
REPORTS_DIR = "/sdcard/Documents/Projets_Termux"
BTC_ADDRESS = "bc1qpls9y6lxmjwdtre5frn4vsvlrlvys6m8t20ygx"

from datetime import datetime, timezone
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# Load data
stocks = []
crypto = []
try:
    with open(os.path.join(SITE_DIR, "data", "stocks.json")) as f:
        data = json.load(f)
        stocks = data.get("bullish", data.get("watchlist", []))[:5]
except Exception:
    pass
try:
    with open(os.path.join(SITE_DIR, "data", "crypto.json")) as f:
        data = json.load(f)
        crypto = data.get("buys", data.get("top_picks", []))[:5]
except Exception:
    pass

n_stocks = len(stocks)
n_crypto = len(crypto)

def fmt_score(s):
    try:
        return str(int(s))
    except Exception:
        return "?"

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

stock_cards = ""
for s in stocks:
    ticker = esc(s.get("ticker", s.get("symbol", "?")))
    score = fmt_score(s.get("score", s.get("rsi_score", "?")))
    entry = esc(s.get("entry", s.get("price", "?")))
    stop = esc(s.get("stop", "-"))
    target = esc(s.get("target", s.get("t1", "-")))
    trend = esc(s.get("trend", s.get("trend_label", "-")))
    stock_cards += f"""
<div class="card">
<span class="ticker">{ticker}</span>
<span class="score">Score {score}</span>
<div class="detail">Entry: ${entry} | Stop: ${stop} | Target: ${target}<br>Trend: {trend}</div>
</div>"""

crypto_cards = ""
for c in crypto:
    ticker = esc(c.get("ticker", c.get("symbol", "?")))
    score = fmt_score(c.get("score", c.get("momentum_score", "?")))
    price = esc(c.get("price", c.get("current_price", "?")))
    change = esc(c.get("change_24h", c.get("price_change_24h", "?")))
    crypto_cards += f"""
<div class="card">
<span class="ticker">{ticker}</span>
<span class="score">Score {score}</span>
<div class="detail">Price: ${price} | 24h: {change}%</div>
</div>"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Phasma Signals</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0a0a0f; color:#e0e0e0; font-family:'Segoe UI',system-ui,sans-serif; min-height:100vh; }}
.header {{ background:linear-gradient(135deg,#1a0030,#0a0a2e); padding:2rem 1rem; text-align:center; border-bottom:1px solid #2a1a4a; }}
.header h1 {{ font-size:2rem; color:#b388ff; }}
.header p {{ color:#888; margin-top:0.5rem; }}
.header .btc {{ background:#111; border:1px solid #333; border-radius:8px; padding:0.5rem 1rem; display:inline-block; margin-top:1rem; font-family:monospace; font-size:0.8rem; color:#ffa726; word-break:break-all; }}
.container {{ max-width:900px; margin:0 auto; padding:1rem; }}
.section {{ margin:2rem 0; }}
.section h2 {{ color:#b388ff; border-bottom:1px solid #2a1a4a; padding-bottom:0.5rem; margin-bottom:1rem; }}
.card {{ background:#111; border:1px solid #222; border-radius:12px; padding:1rem; margin:0.5rem 0; }}
.card .ticker {{ font-size:1.4rem; font-weight:bold; color:#b388ff; }}
.card .score {{ float:right; background:#2a1a4a; color:#e040fb; padding:0.2rem 0.8rem; border-radius:20px; font-weight:bold; }}
.card .detail {{ color:#888; font-size:0.9rem; margin-top:0.5rem; }}
.premium-box {{ background:linear-gradient(135deg,#1a0030,#2a0a3e); border:1px solid #b388ff; border-radius:12px; padding:2rem; text-align:center; margin:2rem 0; }}
.premium-box h3 {{ color:#e040fb; font-size:1.5rem; }}
.premium-box .price {{ color:#b388ff; font-size:1.2rem; margin:1rem 0; }}
.premium-box .steps {{ text-align:left; max-width:400px; margin:1rem auto; color:#ccc; line-height:1.8; }}
.footer {{ text-align:center; padding:2rem; color:#444; font-size:0.8rem; border-top:1px solid #1a1a2e; }}
.tag {{ display:inline-block; background:#1a1a2e; color:#b388ff; padding:0.2rem 0.6rem; border-radius:4px; margin:0.2rem; font-size:0.8rem; }}
</style>
</head>
<body>
<div class="header">
<h1>&#x1F52E; Phasma Signals</h1>
<p>Daily trading signals &mdash; stocks &amp; crypto</p>
<p style="color:#666;font-size:0.8rem;">Updated: {timestamp}</p>
<div class="btc">&#9749; {BTC_ADDRESS}</div>
</div>
<div class="container">

<div class="section">
<h2>&#x1F4CA; Stock Setups ({n_stocks} signals)</h2>
{stock_cards}
</div>

<div class="section">
<h2>&#x20BF; Crypto Signals ({n_crypto} picks)</h2>
{crypto_cards}
</div>

<div class="premium-box">
<h3>&#x1F52E; Premium Access</h3>
<p style="color:#ccc;margin:1rem 0;">Deep analysis with entry, stop, target, R:R, position sizing &mdash; delivered via encrypted Nostr DM</p>
<div class="price">&#x1F48E; Monthly &mdash; 50,000 sats (~$50/mo)<br>&#x1F4C4; Single &mdash; 15,000 sats (~$15/report)</div>
<div class="steps">
1. Send sats to the tip address above<br>
2. DM us your txid on Nostr<br>
3. Receive premium reports via encrypted DM
</div>
<p style="margin-top:1rem;">
<span class="tag">#phasma</span>
<span class="tag">#signals</span>
<span class="tag">#premium</span>
<span class="tag">#nostr</span>
</p>
</div>

</div>
<div class="footer">
Phasma Signals &mdash; Independent trading research<br>
&#9888;&#65039; Not financial advice. Do your own research.
</div>
</body>
</html>"""

with open(os.path.join(SITE_DIR, "index.html"), "w") as f:
    f.write(html)

print(f"Generated index.html: {n_stocks} stocks, {n_crypto} crypto")
