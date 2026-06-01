#!/usr/bin/env python3
"""Generate Phasma Signals site index.html from scan data.
Enhanced: reads enriched JSON with trading-ops bridge data (VWAP, POC, trade tables, scorecard).
Design unchanged — same dark purple theme, same card layout, richer content inside cards.
"""
import json, os

SITE_DIR = os.path.expanduser("~/phasma-signals-site")
REPORTS_DIR = "/sdcard/Documents/Projets_Termux"
BTC_ADDRESS = "bc1qpls9y6lxmjwdtre5frn4vsvlrlvys6m8t20ygx"
LIGHTNING_ADDR = "antsyopen378@walletofsatoshi.com"

from datetime import datetime, timezone
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# Load bridge data for macro regime
macro_regime = None
macro_dxy = None
macro_10y = None
macro_vix = None
try:
    with open(os.path.join(REPORTS_DIR, "trading_ops_bridge_latest.json")) as f:
        bridge = json.load(f)
    m = bridge.get("macro", {}) or {}
    macro_regime = m.get("regime_quadrant")
    macro_dxy = m.get("dxy")
    macro_10y = m.get("ten_year")
    macro_vix = m.get("vix")
except Exception:
    pass

# Load data
stocks = []
crypto = []
try:
    with open(os.path.join(SITE_DIR, "data", "stocks.json")) as f:
        data = json.load(f)
    # Merge bullish + watchlist, enriched items first
    all_stocks = data.get("bullish", []) + data.get("watchlist", [])
    # ── Validation: remove crypto contamination, zero prices, low scores ──
    import sys, logging; sys.path.insert(0, os.path.expanduser("~"))
    logging.getLogger("phasma_validation").setLevel(logging.ERROR)
    from phasma_validation import validate_scan_data, is_crypto_ticker
    # Filter out crypto tickers that leaked into stock section
    all_stocks = [s for s in all_stocks if not is_crypto_ticker(s.get("ticker", ""))]
    stock_data_v = {"bullish": [s for s in all_stocks if s.get("score", 0) >= 3],
                    "watchlist": [s for s in all_stocks if 1 <= s.get("score", 0) < 3]}
    cleaned, rejected, _ = validate_scan_data(stock_data_v, "stock")
    all_stocks = cleaned.get("bullish", []) + cleaned.get("watchlist", [])
    # Sort: enriched items (have trade_table or scorecard) first
    all_stocks.sort(key=lambda x: bool(x.get("trade_table") or x.get("scorecard_total") or x.get("vwap_levels")), reverse=True)
    stocks = all_stocks[:8]
except Exception:
    pass
try:
    with open(os.path.join(SITE_DIR, "data", "crypto.json")) as f:
        data = json.load(f)
    # Merge buys + watches, enriched items first
    all_crypto = data.get("buys", []) + data.get("watches", []) + data.get("avoids", [])
    # ── Validation: reject zero prices, impossible RSI ──
    crypto_data_v = {"buys": [s for s in all_crypto if s.get("score", 0) >= 3],
                     "watches": [s for s in all_crypto if 1 <= s.get("score", 0) < 3],
                     "avoids": []}
    cleaned, rejected, _ = validate_scan_data(crypto_data_v, "crypto")
    all_crypto = cleaned.get("buys", []) + cleaned.get("watches", [])
    # Sort: enriched items first
    all_crypto.sort(key=lambda x: bool(x.get("trade_table") or x.get("volume_profile") or x.get("vwap_levels")), reverse=True)
    crypto = all_crypto[:8]
except Exception:
    pass

n_stocks = len(stocks)
n_crypto = len(crypto)

def fmt_price(v):
    """Format a price value nicely."""
    try:
        f = float(v)
        if f >= 1000:
            return f"${f:,.0f}"
        elif f >= 1:
            return f"${f:.2f}"
        else:
            return f"${f:.4f}"
    except Exception:
        return str(v)

def fmt_score(s):
    try:
        return str(int(s))
    except Exception:
        return "?"

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_trade_table_card(item):
    """Render enriched trade data inside a card if available."""
    extras = ""
    tt = item.get("trade_table", [])
    if tt:
        # Show first trade plan
        t = tt[0]
        side = t.get("side", "").upper()
        side_color = "var(--green)" if side == "LONG" else "var(--red)" if side == "SHORT" else "var(--text)"
        extras += f'<div class="trade-plan"><span style="color:{side_color};font-weight:bold;">{esc(side)}</span>'
        if t.get("entry"):
            extras += f' Entry {fmt_price(t["entry"])}'
        if t.get("stop"):
            extras += f' · Stop {fmt_price(t["stop"])}'
        if t.get("t1"):
            extras += f' · T1 {fmt_price(t["t1"])}'
        if t.get("t2"):
            extras += f' · T2 {fmt_price(t["t2"])}'
        if t.get("rr"):
            extras += f' · R:R {esc(t["rr"])}'
        extras += '</div>'

    # VWAP levels
    vwap = item.get("vwap_levels", {})
    if vwap:
        parts = []
        for k in ["session", "weekly", "monthly"]:
            if vwap.get(k):
                parts.append(f'{k[:3]} VWAP {fmt_price(vwap[k])}')
        if parts:
            extras += f'<div class="vwap">{esc(" | ".join(parts))}</div>'

    # Volume profile POC
    vp = item.get("volume_profile", {})
    if vp and vp.get("poc"):
        poc_line = f'POC {fmt_price(vp["poc"])}'
        if vp.get("vah"):
            poc_line += f' · VAH {fmt_price(vp["vah"])}'
        if vp.get("val"):
            poc_line += f' · VAL {fmt_price(vp["val"])}'
        extras += f'<div class="vol-profile">{esc(poc_line)}</div>'

    # Scorecard
    sc = item.get("scorecard_total")
    if sc is not None:
        color = "var(--green)" if sc >= 4 else "var(--yellow)" if sc >= 2 else "var(--red)"
        extras += f'<div class="scorecard"><span style="color:{color};font-weight:bold;">Scorecard {sc}/6</span></div>'

    # Max pain
    mp = item.get("max_pain")
    if mp:
        extras += f'<div class="max-pain">Max Pain {fmt_price(mp)}</div>'

    # Regime
    rq = item.get("regime_quadrant") or item.get("macro_regime")
    if rq:
        rq_colors = {"Goldilocks": "var(--green)", "Reflation": "var(--yellow)",
                     "Stagflation": "var(--orange)", "Risk-Off": "var(--red)"}
        color = rq_colors.get(rq, "var(--text)")
        extras += f'<div class="regime-tag"><span style="color:{color};">Regime: {esc(rq)}</span></div>'

    # Funding rate (crypto)
    fr = item.get("funding_rate")
    if fr is not None:
        color = "var(--green)" if fr <= 0.01 else "var(--red)" if fr >= 0.05 else "var(--yellow)"
        extras += f'<div class="funding"><span style="color:{color};">Funding {fr:+.3f}%</span></div>'

    return extras

# ── Stock cards ──
stock_cards = ""
for s in stocks:
    ticker = esc(s.get("ticker", s.get("symbol", "?")))
    score = fmt_score(s.get("score", s.get("rsi_score", "?")))
    entry_raw = s.get("entry", s.get("price", "?"))
    # Format entry with $ if numeric
    try:
        entry = fmt_price(float(entry_raw))
    except (ValueError, TypeError):
        entry = esc(str(entry_raw))
    stop_raw = s.get("stop", "-")
    try:
        stop = fmt_price(float(stop_raw))
    except (ValueError, TypeError):
        stop = "-"
    target_raw = s.get("target", s.get("t1", "-"))
    try:
        target = fmt_price(float(target_raw))
    except (ValueError, TypeError):
        target = "-"
    trend = esc(s.get("trend", s.get("trend_label", "-")))
    # Fill stop/target/trend from bridge trade table if missing
    tt = s.get("trade_table", [])
    if tt and (stop == "-" or target == "-" or trend == "-"):
        t0 = tt[0]
        if stop == "-" and t0.get("stop"):
            stop = fmt_price(t0["stop"])
        if target == "-" and t0.get("t1"):
            target = fmt_price(t0["t1"])
        if trend == "-" and s.get("trend_label"):
            trend = esc(s["trend_label"])
    extras = render_trade_table_card(s)
    stock_cards += f"""
<div class="card">
<span class="ticker">{ticker}</span>
<span class="score">Score {score}</span>
<div class="detail">Entry: {entry} | Stop: {stop} | Target: {target}<br>Trend: {trend}</div>
{extras}
</div>"""

# ── Crypto cards ──
crypto_cards = ""
for c in crypto:
    ticker = esc(c.get("ticker", c.get("symbol", "?")))
    score = fmt_score(c.get("score", c.get("momentum_score", "?")))
    price = esc(c.get("price", c.get("current_price", "?")))
    change = esc(c.get("change_24h", c.get("price_change_24h", c.get("change_1d", "?"))))
    extras = render_trade_table_card(c)
    crypto_cards += f"""
<div class="card">
<span class="ticker">{ticker}</span>
<span class="score">Score {score}</span>
<div class="detail">Price: ${price} | 24h: {change}%</div>
{extras}
</div>"""

# ── Macro banner ──
macro_banner = ""
if macro_regime:
    rq_colors = {"Goldilocks": "#3fb950", "Reflation": "#d29922",
                 "Stagflation": "#f0883e", "Risk-Off": "#f85149"}
    color = rq_colors.get(macro_regime, "#8b949e")
    macro_data = []
    if macro_dxy:
        macro_data.append(f"DXY {macro_dxy:.1f}")
    if macro_10y:
        macro_data.append(f"10Y {macro_10y:.2f}%")
    if macro_vix:
        macro_data.append(f"VIX {macro_vix:.1f}")
    macro_detail = f'({" | ".join(macro_data)})' if macro_data else ""
    macro_banner = f"""
<div class="macro-banner" style="background:linear-gradient(135deg,#1a0030,#0a0a2e);border:1px solid {color};border-radius:12px;padding:1rem;margin-bottom:1.5rem;text-align:center;">
<span style="color:{color};font-weight:bold;font-size:1.2em;">{esc(macro_regime)}</span>
<span style="color:#8b949e;margin-left:1rem;">{esc(macro_detail)}</span>
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
.nav {{ display:flex; justify-content:center; gap:2rem; padding:0.8rem; background:#0a0a0f; border-bottom:1px solid #1a1a2e; }}
.nav a {{ color:#888; text-decoration:none; font-size:0.9rem; }}
.nav a:hover {{ color:#b388ff; }}
.nav a.active {{ color:#e040fb; font-weight:bold; }}
.header {{ background:linear-gradient(135deg,#1a0030,#0a0a2e); padding:2rem 1rem; text-align:center; border-bottom:1px solid #2a1a4a; }}
.header h1 {{ font-size:2rem; color:#b388ff; }}
.header p {{ color:#888; margin-top:0.5rem; }}
.header .btc {{ background:#111; border:1px solid #333; border-radius:8px; padding:0.5rem 1rem; display:inline-block; margin-top:1rem; font-family:monospace; font-size:0.8rem; color:#ffa726; word-break:break-all; }}
.header .zap {{ background:#111; border:1px solid #b388ff; border-radius:8px; padding:0.5rem 1rem; display:inline-block; margin-top:0.5rem; margin-left:0.5rem; font-family:monospace; font-size:0.8rem; color:#b388ff; }}
.container {{ max-width:900px; margin:0 auto; padding:1rem; }}
.section {{ margin:2rem 0; }}
.section h2 {{ color:#b388ff; border-bottom:1px solid #2a1a4a; padding-bottom:0.5rem; margin-bottom:1rem; }}
.card {{ background:#111; border:1px solid #222; border-radius:12px; padding:1rem; margin:0.5rem 0; }}
.card .ticker {{ font-size:1.4rem; font-weight:bold; color:#b388ff; }}
.card .score {{ float:right; background:#2a1a4a; color:#e040fb; padding:0.2rem 0.8rem; border-radius:20px; font-weight:bold; }}
.card .detail {{ color:#888; font-size:0.9rem; margin-top:0.5rem; }}
.card .trade-plan {{ color:#c9d1d9; font-size:0.85rem; margin-top:0.4rem; padding:0.3rem 0.5rem; background:#1a1a2e; border-radius:6px; }}
.card .vwap {{ color:#58a6ff; font-size:0.8rem; margin-top:0.2rem; }}
.card .vol-profile {{ color:#d29922; font-size:0.8rem; margin-top:0.2rem; }}
.card .scorecard {{ font-size:0.8rem; margin-top:0.2rem; }}
.card .max-pain {{ color:#f0883e; font-size:0.8rem; margin-top:0.2rem; }}
.card .regime-tag {{ font-size:0.75rem; margin-top:0.2rem; }}
.card .funding {{ font-size:0.8rem; margin-top:0.2rem; }}
.premium-box {{ background:linear-gradient(135deg,#1a0030,#2a0a3e); border:1px solid #b388ff; border-radius:12px; padding:2rem; text-align:center; margin:2rem 0; }}
.premium-box h3 {{ color:#e040fb; font-size:1.5rem; }}
.premium-box .price {{ color:#b388ff; font-size:1.2rem; margin:1rem 0; }}
.premium-box .steps {{ text-align:left; max-width:400px; margin:1rem auto; color:#ccc; line-height:1.8; }}
.footer {{ text-align:center; padding:2rem; color:#444; font-size:0.8rem; border-top:1px solid #1a1a2e; }}
.tag {{ display:inline-block; background:#1a1a2e; color:#b388ff; padding:0.2rem 0.6rem; border-radius:4px; margin:0.2rem; font-size:0.8rem; }}
</style>
</head>
<body>
<div class="nav">
<a href="/phasma-signals/" class="active">🔮 Signals</a>
<a href="/phasma-signals/premium.html">💎 Premium</a>
</div>
<div class="header">
<h1>&#x1F52E; Phasma Signals</h1>
<p>Daily trading signals &mdash; stocks &amp; crypto</p>
<p style="color:#666;font-size:0.8rem;">Updated: {timestamp}</p>
<div class="btc">&#9749; {BTC_ADDRESS}</div>
<div class="zap">&#9889; {LIGHTNING_ADDR}</div>
</div>
<div class="container">

{macro_banner}

<div class="section">
<h2>&#x1F4CA; Stock Setups ({n_stocks} signals)</h2>
{stock_cards}
{f'<p style="color:#8b949e;padding:10px;">No stock signals today.</p>' if not stocks else ''}
</div>

<div class="section">
<h2>&#x20BF; Crypto Signals ({n_crypto} picks)</h2>
{crypto_cards}
{f'<p style="color:#8b949e;padding:10px;">No crypto signals today.</p>' if not crypto else ''}
</div>

<div class="premium-box">
<h3>&#x1F48E; <a href="/phasma-signals/premium.html" style="color:#e040fb;text-decoration:none;">Premium Access</a></h3>
<p style="color:#ccc;margin:1rem 0;">Deep analysis with entry, stop, target, R:R, position sizing &mdash; delivered via encrypted Nostr DM</p>
<div class="price">&#x1F48E; Monthly &mdash; 50,000 sats (~$50/mo)<br>&#x1F4C4; Single &mdash; 15,000 sats (~$15/report)<br>&#x1F4B0; Quarterly &mdash; 120,000 sats (~$120/3mo)</div>
<div class="steps">
1. Zap to <strong style="color:#b388ff;">antsyopen378@walletofsatoshi.com</strong><br>
2. DM your txid on Nostr<br>
3. Receive premium reports via encrypted DM
</div>
<p style="margin-top:1rem;"><a href="/phasma-signals/premium.html" style="color:#e040fb;font-weight:bold;">→ See full premium details &amp; pricing</a></p>
<p style="margin-top:0.5rem;">
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

print(f"Generated index.html: {n_stocks} stocks, {n_crypto} crypto, regime={macro_regime or 'N/A'}")
