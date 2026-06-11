#!/usr/bin/env python3
"""Generate Phasma Signals Premium landing page with live report preview."""
import json, os, sys

SITE_DIR = os.path.expanduser("~/phasma-signals-site")
REPORTS_DIR = "/sdcard/Documents/Projets_Termux"

BTC_ADDRESS = "bc1qpls9y6lxmjwdtre5frn4vsvlrlvys6m8t20ygx"
LIGHTNING_ADDR = "antsyopen378@walletofsatoshi.com"
NOSTR_NPUB = "npub14a68c64d2hq6t5589pdcpwe9gqcxnefxw8v9waq3hm8n5gq5wnqsuu6ee5"

# Count today's signals for social proof
n_stocks = n_crypto = 0
try:
    with open(os.path.join(REPORTS_DIR, "market_scan_latest.json")) as f:
        data = json.load(f)
    n_stocks = len(data.get("bullish", [])) + len(data.get("watchlist", []))
except:
    pass
try:
    with open(os.path.join(REPORTS_DIR, "crypto_scan_latest.json")) as f:
        data = json.load(f)
    n_crypto = len(data.get("buys", [])) + len(data.get("watches", []))
except:
    pass

total_signals = n_stocks + n_crypto

# ── Load premium report for preview section ──
premium_data = {}
premium_file = os.path.join(SITE_DIR, "data", "premium_latest.json")
if os.path.exists(premium_file):
    try:
        with open(premium_file) as f:
            premium_data = json.load(f)
    except:
        pass

# Build preview HTML from live data
preview_html = ""
if premium_data:
    all_stocks = premium_data.get("stocks", [])
    all_crypto = premium_data.get("crypto", [])
    total_stock_count = len(all_stocks)
    total_crypto_count = len(all_crypto)

    # Pick 2 high-score stocks + 1 counter-trend for diversity
    high_score = [s for s in all_stocks if s.get("scorecard_total", s.get("score", 0)) >= 5 and not s.get("is_counter_trend")]
    ct_stocks = [s for s in all_stocks if s.get("is_counter_trend")]

    preview_stocks = high_score[:2]
    if ct_stocks:
        preview_stocks.append(ct_stocks[0])
    elif len(all_stocks) > 2:
        preview_stocks.append(all_stocks[2])

    preview_crypto = all_crypto[:1]

    # ── Macro regime mini-dashboard ──
    # Pull from bridge if available, else use placeholder
    macro_regime = "Goldilocks"
    macro_dxy = "98.32"
    macro_10y = "4.28%"
    macro_vix = "14.2"
    try:
        bridge_file = os.path.join(REPORTS_DIR, "trading_ops_bridge_latest.json")
        if os.path.exists(bridge_file):
            with open(bridge_file) as f:
                bridge = json.load(f)
            macro = bridge.get("macro", {})
            macro_regime = macro.get("regime_quadrant", macro_regime)
            if macro.get("dxy"):
                macro_dxy = f"{macro['dxy']:.1f}" if isinstance(macro["dxy"], (int, float)) else str(macro["dxy"])
            if macro.get("ten_year"):
                macro_10y = f"{macro['ten_year']:.2f}%"
            if macro.get("vix"):
                macro_vix = f"{macro['vix']:.1f}" if isinstance(macro["vix"], (int, float)) else str(macro["vix"])
    except:
        pass

    regime_colors = {"Goldilocks": "#00b894", "Reflation": "#fdcb6e", "Stagflation": "#e17055", "Risk-Off": "#d63031"}
    regime_color = regime_colors.get(macro_regime, "#888")

    preview_html += f'''<div class="preview-macro">
<div class="preview-macro-title">🌍 Macro Regime Dashboard</div>
<div class="preview-macro-grid">
<div class="preview-macro-item">
<span class="preview-macro-label">Regime</span>
<span class="preview-macro-val" style="color:{regime_color};">{macro_regime}</span>
</div>
<div class="preview-macro-item">
<span class="preview-macro-label">DXY</span>
<span class="preview-macro-val">{macro_dxy}</span>
</div>
<div class="preview-macro-item">
<span class="preview-macro-label">10Y Yield</span>
<span class="preview-macro-val">{macro_10y}</span>
</div>
<div class="preview-macro-item">
<span class="preview-macro-label">VIX</span>
<span class="preview-macro-val" style="color:#00b894;">{macro_vix}</span>
</div>
</div>
</div>\n'''

    # ── Stock preview cards ──
    sample_count = len(preview_stocks)
    preview_html += f'<div class="preview-section">\n'
    preview_html += f'<div class="preview-section-title">📊 Stock Swing Setups — Sample ({sample_count} of {total_stock_count})</div>\n'

    for s in preview_stocks:
        ticker = s.get("ticker", "?")
        direction = s.get("direction", "LONG")
        price = s.get("price", 0)
        score = s.get("scorecard_total", s.get("score", 0))
        trend = s.get("trend", "")
        is_ct = s.get("is_counter_trend", False)
        entry = s.get("entry", 0)
        stop = s.get("stop_loss", 0)
        t1 = s.get("target_1", 0)
        t2 = s.get("target_2", 0)
        rr = s.get("rr_1", "")
        size_10k = s.get("position_size_10k", "")
        vwap = s.get("vwap_levels", {})
        vprofile = s.get("volume_profile", {})
        ema_status = s.get("ema_status", [])
        tt = s.get("trade_table", [{}])[0] if s.get("trade_table") else {}
        t3 = tt.get("t3", "")
        trigger = tt.get("trigger", "")
        time_stop = tt.get("time_stop", "")
        recalibrated = tt.get("recalibrated", False)

        # Score badge class
        if score >= 5:
            score_cls = "perfect"
        elif score >= 3:
            score_cls = "mid"
        else:
            score_cls = "low"

        # Direction badge
        dir_label = direction
        if is_ct:
            dir_label += " ⚠️"
        dir_cls = "long" if "LONG" in direction.upper() else "short"

        # Trend class
        trend_cls = "warn" if is_ct or "NEUTRAL" in trend.upper() or "CONSOLIDATION" in trend.upper() else ""

        # Card class
        card_cls = " counter-trend" if is_ct else ""

        # Format price
        if price >= 1:
            price_str = f"${price:,.2f}"
            entry_str = f"${entry:,.2f}"
            stop_str = f"${stop:,.2f}"
            t1_str = f"${t1:,.2f}"
            t2_str = f"${t2:,.2f}" if t2 else "—"
            t3_str = f"${t3:,.2f}" if t3 else "—"
            vwap_parts = [f"{k.title()}: ${v:,.2f}" for k, v in vwap.items() if v]
            vp_parts = [f"{k.upper()}: ${v:,.2f}" for k, v in vprofile.items() if v and k in ("poc", "vah", "val")]
            size_str = f"{size_10k} shares ($10K, 1% risk)" if size_10k else ""
        else:
            price_str = f"${price:.4f}"
            entry_str = f"${entry:.4f}"
            stop_str = f"${stop:.4f}"
            t1_str = f"${t1:.4f}"
            t2_str = f"${t2:.4f}" if t2 else "—"
            t3_str = f"${t3:.4f}" if t3 else "—"
            vwap_parts = [f"{k.title()}: ${v:.4f}" for k, v in vwap.items() if v]
            vp_parts = [f"{k.upper()}: ${v:.4f}" for k, v in vprofile.items() if v and k in ("poc", "vah", "val")]
            size_str = f"{size_10k:,} units ($5K, 1% risk)" if size_10k else ""

        ema_str = " · ".join(ema_status) if ema_status else ""

        preview_html += f'''<div class="preview-card{card_cls}">
<div class="preview-card-header">
<span class="preview-ticker">{ticker}</span>
<span class="preview-dir {dir_cls}">{dir_label}</span>
<span class="preview-price">{price_str}</span>
<span class="preview-score {score_cls}">{score}/6</span>
<span class="preview-trend {trend_cls}">{trend}</span>
</div>
<div class="preview-card-body">
<table class="preview-table">
<tr><th>Entry</th><th>Stop</th><th>T1</th><th>T2</th><th>T3</th><th>R:R</th></tr>
<tr><td class="entry">{entry_str}</td><td class="stop">{stop_str}</td><td class="t1">{t1_str}</td><td class="t2">{t2_str}</td><td class="t3">{t3_str}</td><td>{rr}</td></tr>
</table>
'''

        if is_ct:
            reason = s.get("direction_reason", "Counter-trend — lower conviction")
            preview_html += f'<div class="preview-ct-badge">⚠️ COUNTER-TREND — {reason}. Tighter stops, reduced size.</div>\n'

        preview_html += f'''<div class="preview-details">
<div class="preview-detail-row"><span class="preview-detail-label">Position Size</span><span>{size_str}</span></div>
'''
        if vwap_parts:
            preview_html += f'<div class="preview-detail-row"><span class="preview-detail-label">VWAP</span><span>{" | ".join(vwap_parts)}</span></div>\n'
        if vp_parts:
            preview_html += f'<div class="preview-detail-row"><span class="preview-detail-label">Vol Profile</span><span>{" | ".join(vp_parts)}</span></div>\n'
        if ema_str:
            ema_color = ' style="color:#f0883e;"' if is_ct else ''
            preview_html += f'<div class="preview-detail-row"><span class="preview-detail-label">EMA Status</span><span{ema_color}>{ema_str}</span></div>\n'
        if trigger or time_stop:
            preview_html += f'<div class="preview-detail-row"><span class="preview-detail-label">Trigger</span><span>{trigger}{" | Time stop: " + time_stop if time_stop else ""}</span></div>\n'
        if recalibrated:
            preview_html += f'<div class="preview-detail-row"><span class="preview-detail-label">Recalibrated</span><span style="color:#ff9800;">🔄 Plans recalibrated from live price</span></div>\n'

        preview_html += '</div>\n</div>\n</div>\n'

    remaining = total_stock_count - sample_count
    if remaining > 0:
        preview_html += f'<div class="preview-more">…and {remaining} more stock setups with full trade plans, scorecards, and risk sizing.</div>\n'
    preview_html += '</div>\n'

    # ── Crypto preview cards ──
    if preview_crypto:
        preview_html += f'<div class="preview-section">\n'
        preview_html += f'<div class="preview-section-title">₿ Crypto Swing Setups — Sample</div>\n'

        for c in preview_crypto:
            symbol = c.get("symbol", "?")
            direction = c.get("direction", "LONG")
            price = c.get("price", 0)
            score = c.get("scorecard_total", c.get("score", 0))
            trend = c.get("direction_reason", c.get("trend", ""))
            entry = c.get("entry", 0)
            stop = c.get("stop_loss", 0)
            t1 = c.get("target_1", 0)
            t2 = c.get("target_2", 0)
            rr = c.get("rr_1", "")
            size_5k = c.get("position_size_10k", "")
            rsi = c.get("rsi", "")
            vwap = c.get("vwap_levels", {})
            vprofile = c.get("volume_profile", {})
            tt = c.get("trade_table", [{}])[0] if c.get("trade_table") else {}
            t3 = tt.get("t3", "")
            atr = c.get("atr_pct", 0)

            if score >= 5:
                score_cls = "perfect"
            elif score >= 3:
                score_cls = "mid"
            else:
                score_cls = "low"

            dir_cls = "long" if "LONG" in direction.upper() else "short"
            trend_cls = "warn" if rsi and isinstance(rsi, (int, float)) and rsi < 35 else ""

            price_str = f"${price:.4f}"
            entry_str = f"${entry:.4f}"
            stop_str = f"${stop:.4f}"
            t1_str = f"${t1:.4f}"
            t2_str = f"${t2:.4f}" if t2 else "—"
            t3_str = f"${t3:.4f}" if t3 else "—"

            vwap_parts = [f"{k.title()}: ${v:.4f}" for k, v in vwap.items() if v]
            vp_parts = [f"{k.upper()}: ${v:.4f}" for k, v in vprofile.items() if v and k in ("poc", "vah", "val")]

            rsi_str = ""
            if rsi and isinstance(rsi, (int, float)):
                rsi_color = "#fdcb6e" if rsi < 35 else "#e0e0e0"
                rsi_label = "Oversold (<35)" if rsi < 35 else f"{rsi:.0f}"
                rsi_str = f'<div class="preview-detail-row"><span class="preview-detail-label">RSI</span><span style="color:{rsi_color};">{rsi:.1f} — {rsi_label}</span></div>\n'

            atr_str = ""
            if atr:
                atr_str = f'<div class="preview-detail-row"><span class="preview-detail-label">ATR</span><span>{atr:.1f}% — Volatility squeeze, breakout imminent</span></div>\n'

            size_str = f"{size_5k:,} units ($5K, 1% risk)" if size_5k else ""

            preview_html += f'''<div class="preview-card">
<div class="preview-card-header">
<span class="preview-ticker">{symbol}</span>
<span class="preview-dir {dir_cls}">BUY {direction}</span>
<span class="preview-price">{price_str}</span>
<span class="preview-score {score_cls}">{score}/6</span>
<span class="preview-trend {trend_cls}">{trend}</span>
</div>
<div class="preview-card-body">
<table class="preview-table">
<tr><th>Entry</th><th>Stop</th><th>T1</th><th>T2</th><th>T3</th><th>R:R</th></tr>
<tr><td class="entry">{entry_str}</td><td class="stop">{stop_str}</td><td class="t1">{t1_str}</td><td class="t2">{t2_str}</td><td class="t3">{t3_str}</td><td>{rr}</td></tr>
</table>
<div class="preview-details">
<div class="preview-detail-row"><span class="preview-detail-label">Position Size</span><span>{size_str}</span></div>
{rsi_str}{''.join([f'<div class="preview-detail-row"><span class="preview-detail-label">VWAP</span><span>{" | ".join(vwap_parts)}</span></div>\n'] if vwap_parts else [])}{''.join([f'<div class="preview-detail-row"><span class="preview-detail-label">Vol Profile</span><span>{" | ".join(vp_parts)}</span></div>\n'] if vp_parts else [])}{atr_str}</div>
</div>
</div>\n'''

        preview_html += '</div>\n'

    # ── Blur note ──
    preview_html += f'''<div class="preview-blur-note">
<span class="preview-lock">🔒</span> The full report includes <strong>all</strong> tickers (unlocked), SPX gamma analysis, VIX structure, breadth indicators, sector ETF rankings, macro catalyst calendar, and the screener's regime-aligned conviction picks. This preview shows {sample_count} of {total_stock_count} stocks and {len(preview_crypto)} crypto.
</div>\n'''

# If no premium data, show placeholder
if not preview_html:
    preview_html = '''<div class="preview-blur-note">
<span class="preview-lock">🔒</span> Full report preview available when today's scan completes. Subscribe to receive the complete analysis in your Nostr DM.
</div>\n'''

# ══════════════════════════════════════════════════════
#  BUILD FULL HTML
# ══════════════════════════════════════════════════════

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Phasma Signals — Premium</title>
<meta name="description" content="Premium trading signals with precise entry, stop, targets, position sizing, and risk management. Delivered daily via encrypted Nostr DM.">
<meta property="og:title" content="Phasma Signals — Premium Trading Research">
<meta property="og:description" content="Daily stock & crypto signals with trade plans, scorecards, and risk management. Lightning payments.">
<meta property="og:url" content="https://theaijunky.github.io/phasma-signals/premium.html">
<meta property="og:image" content="https://theaijunky.github.io/phasma-signals/banner.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://theaijunky.github.io/phasma-signals/premium.html">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0a0a0f; color:#e0e0e0; font-family:'Segoe UI',system-ui,-apple-system,sans-serif; min-height:100vh; }}

/* Nav */
.nav {{ display:flex; justify-content:center; gap:2rem; padding:1rem; background:#0a0a0f; border-bottom:1px solid #1a1a2e; position:sticky; top:0; z-index:10; }}
.nav a {{ color:#888; text-decoration:none; font-size:0.9rem; transition:color 0.2s; }}
.nav a:hover {{ color:#b388ff; }}
.nav a.active {{ color:#e040fb; font-weight:bold; }}

/* Hero */
.hero {{ background:linear-gradient(135deg,#1a0030 0%,#2a0a3e 50%,#0a0a2e 100%); padding:4rem 1rem; text-align:center; position:relative; overflow:hidden; }}
.hero::before {{ content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%; background:radial-gradient(ellipse,rgba(179,136,255,0.08) 0%,transparent 60%); animation:pulse 8s ease-in-out infinite; }}
@keyframes pulse {{ 0%,100%{{opacity:0.5;transform:scale(1)}} 50%{{opacity:1;transform:scale(1.1)}} }}
.hero h1 {{ font-size:2.5rem; color:#e040fb; position:relative; }}
.hero .subtitle {{ color:#b388ff; font-size:1.2rem; margin-top:0.5rem; position:relative; }}
.hero .stats {{ display:flex; justify-content:center; gap:2rem; margin-top:2rem; position:relative; }}
.hero .stat {{ text-align:center; }}
.hero .stat .num {{ font-size:2rem; font-weight:bold; color:#e040fb; }}
.hero .stat .label {{ font-size:0.8rem; color:#888; }}

.container {{ max-width:800px; margin:0 auto; padding:1rem; }}

/* Problem / Hook */
.hook {{ margin:3rem 0; padding:2rem; border-left:3px solid #e040fb; background:rgba(224,64,251,0.05); border-radius:0 12px 12px 0; }}
.hook h2 {{ color:#e040fb; margin-bottom:1rem; font-size:1.5rem; }}
.hook p {{ color:#ccc; line-height:1.8; margin-bottom:0.5rem; }}
.hook .pain {{ color:#f0883e; }}

/* Comparison Table */
.compare {{ margin:3rem 0; }}
.compare h2 {{ color:#b388ff; text-align:center; margin-bottom:1.5rem; font-size:1.5rem; }}
.compare table {{ width:100%; border-collapse:collapse; background:#111; border-radius:12px; overflow:hidden; }}
.compare th {{ background:#1a1a2e; padding:1rem; text-align:left; color:#b388ff; }}
.compare th:last-child {{ color:#e040fb; }}
.compare td {{ padding:0.8rem 1rem; border-top:1px solid #1a1a2e; color:#888; }}
.compare td:first-child {{ color:#c9d1d9; font-weight:500; }}
.compare td:last-child {{ color:#3fb950; font-weight:500; }}
.compare td .check {{ color:#3fb950; }}
.compare td .cross {{ color:#f85149; }}
.compare tr:hover {{ background:rgba(179,136,255,0.03); }}

/* Features */
.features {{ margin:3rem 0; }}
.features h2 {{ color:#b388ff; text-align:center; margin-bottom:1.5rem; font-size:1.5rem; }}
.feature-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1rem; }}
.feature-card {{ background:#111; border:1px solid #222; border-radius:12px; padding:1.5rem; transition:border-color 0.3s,transform 0.3s; }}
.feature-card:hover {{ border-color:#b388ff; transform:translateY(-2px); }}
.feature-card .icon {{ font-size:2rem; margin-bottom:0.5rem; }}
.feature-card h3 {{ color:#e040fb; font-size:1rem; margin-bottom:0.3rem; }}
.feature-card p {{ color:#888; font-size:0.85rem; line-height:1.5; }}

/* ═══════════════ REPORT PREVIEW ═══════════════ */
.preview {{ margin:3rem 0; }}
.preview h2 {{ color:#b388ff; text-align:center; margin-bottom:0.5rem; font-size:1.5rem; }}
.preview-sub {{ color:#888; text-align:center; font-size:0.9rem; margin-bottom:2rem; }}
.preview-macro {{ background:#111; border:1px solid #1a1a2e; border-radius:12px; padding:1.2rem; margin-bottom:1.5rem; }}
.preview-macro-title {{ color:#b388ff; font-size:1rem; font-weight:600; margin-bottom:0.8rem; }}
.preview-macro-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; }}
.preview-macro-item {{ text-align:center; }}
.preview-macro-label {{ display:block; color:#888; font-size:0.75rem; margin-bottom:0.2rem; text-transform:uppercase; letter-spacing:1px; }}
.preview-macro-val {{ font-size:1.2rem; font-weight:600; color:#e0e0e0; }}

.preview-section {{ margin-bottom:1.5rem; }}
.preview-section-title {{ color:#00cec9; font-size:1rem; font-weight:600; margin-bottom:0.8rem; padding-left:0.2rem; }}

.preview-card {{ background:#0d0d14; border:1px solid #1a1a2e; border-radius:12px; margin-bottom:0.8rem; overflow:hidden; transition:border-color 0.3s; }}
.preview-card:hover {{ border-color:#b388ff; }}
.preview-card.counter-trend {{ border-color:#ff980044; }}
.preview-card.counter-trend:hover {{ border-color:#ff9800; }}

.preview-card-header {{ display:flex; align-items:center; gap:0.8rem; padding:0.8rem 1rem; background:#111; border-bottom:1px solid #1a1a2e; flex-wrap:wrap; }}
.preview-ticker {{ font-size:1.3rem; font-weight:bold; color:#e040fb; }}
.preview-dir {{ font-size:0.8rem; font-weight:600; padding:0.15rem 0.6rem; border-radius:20px; }}
.preview-dir.long {{ background:#3fb95022; color:#3fb950; border:1px solid #3fb95044; }}
.preview-dir.short {{ background:#f8514922; color:#f85149; border:1px solid #f8514944; }}
.preview-price {{ font-size:1rem; color:#e0e0e0; font-weight:500; }}
.preview-score {{ font-size:0.8rem; font-weight:600; padding:0.15rem 0.5rem; border-radius:6px; margin-left:auto; }}
.preview-score.perfect {{ background:#3fb95022; color:#3fb950; }}
.preview-score.mid {{ background:#fdcb6e22; color:#fdcb6e; }}
.preview-score.low {{ background:#f8514922; color:#f85149; }}
.preview-trend {{ font-size:0.8rem; color:#888; }}
.preview-trend.warn {{ color:#f0883e; }}

.preview-card-body {{ padding:0.8rem 1rem; }}

.preview-table {{ width:100%; border-collapse:collapse; margin-bottom:0.8rem; font-size:0.85rem; }}
.preview-table th {{ color:#888; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; padding:0.4rem 0.6rem; text-align:center; border-bottom:1px solid #1a1a2e; }}
.preview-table td {{ text-align:center; padding:0.5rem 0.6rem; color:#e0e0e0; }}
.preview-table .entry {{ color:#b388ff; font-weight:600; }}
.preview-table .stop {{ color:#f85149; }}
.preview-table .t1 {{ color:#3fb950; }}
.preview-table .t2 {{ color:#00cec9; }}
.preview-table .t3 {{ color:#888; }}

.preview-details {{ font-size:0.8rem; }}
.preview-detail-row {{ display:flex; gap:0.8rem; padding:0.25rem 0; border-bottom:1px solid #1a1a2e0a; }}
.preview-detail-row:last-child {{ border:none; }}
.preview-detail-label {{ color:#888; min-width:110px; flex-shrink:0; }}

.preview-ct-badge {{ background:#ff980015; border:1px solid #ff980044; border-radius:8px; padding:0.5rem 0.8rem; margin-bottom:0.8rem; font-size:0.8rem; color:#f0883e; line-height:1.5; }}

.preview-more {{ color:#888; font-size:0.85rem; text-align:center; padding:0.5rem; font-style:italic; }}

.preview-blur-note {{ background:#1a1a2e; border:1px solid #b388ff33; border-radius:12px; padding:1.2rem; margin-top:1.5rem; text-align:center; color:#aaa; font-size:0.9rem; line-height:1.6; }}
.preview-lock {{ font-size:1.5rem; display:block; margin-bottom:0.5rem; }}

/* Pricing */
.pricing {{ margin:3rem 0; text-align:center; }}
.pricing h2 {{ color:#b388ff; margin-bottom:1.5rem; font-size:1.5rem; }}
.pricing-cards {{ display:flex; gap:1rem; justify-content:center; flex-wrap:wrap; }}
.price-card {{ background:#111; border:1px solid #222; border-radius:16px; padding:2rem; min-width:250px; flex:1; max-width:350px; transition:border-color 0.3s,transform 0.3s; }}
.price-card:hover {{ border-color:#b388ff; transform:translateY(-3px); }}
.price-card.featured {{ border-color:#e040fb; background:linear-gradient(135deg,#1a0030,#2a0a3e); position:relative; }}
.price-card.featured::before {{ content:'⭐ POPULAR'; position:absolute; top:-12px; left:50%; transform:translateX(-50%); background:#e040fb; color:#0a0a0f; padding:0.2rem 1rem; border-radius:20px; font-size:0.75rem; font-weight:bold; }}
.price-card .tier {{ color:#888; font-size:0.9rem; text-transform:uppercase; letter-spacing:2px; }}
.price-card .amount {{ font-size:2.5rem; font-weight:bold; color:#e040fb; margin:0.5rem 0; }}
.price-card .sats {{ color:#b388ff; font-size:0.9rem; }}
.price-card .period {{ color:#888; font-size:0.85rem; margin-bottom:1.5rem; }}
.price-card ul {{ list-style:none; text-align:left; margin:1rem 0; }}
.price-card li {{ color:#ccc; padding:0.4rem 0; font-size:0.9rem; border-bottom:1px solid #1a1a2e; }}
.price-card li:last-child {{ border:none; }}
.price-card li::before {{ content:'✓ '; color:#3fb950; font-weight:bold; }}

/* How it works */
.howto {{ margin:3rem 0; }}
.howto h2 {{ color:#b388ff; text-align:center; margin-bottom:1.5rem; font-size:1.5rem; }}
.steps {{ max-width:500px; margin:0 auto; }}
.step {{ display:flex; gap:1rem; margin-bottom:1.5rem; align-items:flex-start; }}
.step .num {{ background:#e040fb; color:#0a0a0f; width:2rem; height:2rem; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; flex-shrink:0; }}
.step .text h3 {{ color:#c9d1d9; font-size:1rem; margin-bottom:0.2rem; }}
.step .text p {{ color:#888; font-size:0.85rem; line-height:1.5; }}
.step .text .code {{ background:#1a1a2e; color:#b388ff; padding:0.3rem 0.6rem; border-radius:6px; font-family:monospace; font-size:0.8rem; display:inline-block; margin-top:0.3rem; word-break:break-all; }}

/* CTA */
.cta {{ background:linear-gradient(135deg,#2a0a3e,#1a0030); border:2px solid #e040fb; border-radius:16px; padding:3rem 2rem; text-align:center; margin:3rem 0; }}
.cta h2 {{ color:#e040fb; font-size:1.8rem; margin-bottom:0.5rem; }}
.cta p {{ color:#ccc; margin-bottom:1.5rem; }}
.cta .zap-btn {{ display:inline-block; background:#e040fb; color:#0a0a0f; padding:1rem 2rem; border-radius:12px; font-size:1.1rem; font-weight:bold; text-decoration:none; transition:transform 0.2s,box-shadow 0.2s; }}
.cta .zap-btn:hover {{ transform:scale(1.05); box-shadow:0 0 30px rgba(224,64,251,0.4); }}
.cta .alt {{ color:#888; font-size:0.85rem; margin-top:1rem; }}

/* Social proof / Testimonial placeholder */
.social-proof {{ margin:3rem 0; text-align:center; }}
.social-proof h2 {{ color:#b388ff; margin-bottom:1rem; }}
.social-proof .proof-cards {{ display:flex; gap:1rem; justify-content:center; flex-wrap:wrap; }}
.proof-card {{ background:#111; border:1px solid #222; border-radius:12px; padding:1.5rem; max-width:350px; }}
.proof-card .quote {{ color:#ccc; font-style:italic; line-height:1.6; margin-bottom:0.5rem; }}
.proof-card .attr {{ color:#888; font-size:0.8rem; }}

/* FAQ */
.faq {{ margin:3rem 0; }}
.faq h2 {{ color:#b388ff; text-align:center; margin-bottom:1.5rem; }}
.faq-item {{ background:#111; border:1px solid #222; border-radius:12px; margin-bottom:0.5rem; overflow:hidden; }}
.faq-q {{ padding:1rem; cursor:pointer; color:#c9d1d9; font-weight:500; display:flex; justify-content:space-between; align-items:center; }}
.faq-q:hover {{ color:#e040fb; }}
.faq-q .arrow {{ transition:transform 0.3s; color:#b388ff; }}
.faq-a {{ padding:0 1rem 1rem; color:#888; line-height:1.6; display:none; }}
.faq-item.open .faq-a {{ display:block; }}
.faq-item.open .arrow {{ transform:rotate(180deg); }}

.footer {{ text-align:center; padding:2rem; color:#444; font-size:0.8rem; border-top:1px solid #1a1a2e; }}
.footer a {{ color:#b388ff; text-decoration:none; }}

@media (max-width:600px) {{
 .hero h1 {{ font-size:1.8rem; }}
 .hero .stats {{ flex-direction:column; gap:1rem; }}
 .pricing-cards {{ flex-direction:column; align-items:center; }}
 .price-card {{ min-width:auto; width:100%; max-width:100%; }}
 .feature-grid {{ grid-template-columns:1fr; }}
 .preview-macro-grid {{ grid-template-columns:1fr 1fr; }}
 .preview-card-header {{ flex-wrap:wrap; gap:0.3rem; }}
 .preview-table th, .preview-table td {{ font-size:0.7rem; padding:0.3rem 0.4rem; }}
}}
</style>
</head>
<body>

<div class="nav">
<a href="/phasma-signals/">🔮 Signals</a>
<a href="/phasma-signals/premium.html" class="active">💎 Premium</a>
</div>

<div class="hero">
<h1>💎 Phasma Premium</h1>
<p class="subtitle">Institutional-grade trade plans. Delivered daily to your Nostr DM.</p>
<div class="stats">
<div class="stat"><div class="num">{total_signals}+</div><div class="label">Signals / Day</div></div>
<div class="stat"><div class="num">6</div><div class="label">Scorecard Checks</div></div>
<div class="stat"><div class="num">3</div><div class="label">Trade Plans / Ticker</div></div>
<div class="stat"><div class="num">⚡</div><div class="label">Lightning Payments</div></div>
</div>
</div>

<div class="container">

<div class="hook">
<h2>Trading without a plan is gambling.</h2>
<p>You've seen the free signals. Entry, stop, target — enough to get interested.</p>
<p>But <span class="pain">where exactly do you enter?</span> Which time stop applies? What's the position size for a $5K or $10K account? How does VWAP align with the trade? Is the signal fighting the trend?</p>
<p>Premium gives you the <strong>full trade plan</strong> — every signal analyzed with multiple setups, precise stops, tiered targets, and risk sizing. No guessing.</p>
</div>

<div class="compare">
<h2>Free vs Premium</h2>
<table>
<tr><th>Feature</th><th>Free</th><th>Premium</th></tr>
<tr><td>Daily signals</td><td><span class="check">✓</span> Top picks</td><td><span class="check">✓</span> Full universe</td></tr>
<tr><td>Entry / Stop / Target</td><td><span class="check">✓</span> Basic</td><td><span class="check">✓</span> 3 trade plans per ticker</td></tr>
<tr><td>Position sizing</td><td><span class="cross">✗</span></td><td><span class="check">✓</span> $5K & $10K sizing</td></tr>
<tr><td>VWAP levels</td><td><span class="cross">✗</span></td><td><span class="check">✓</span> Session / Weekly / Monthly</td></tr>
<tr><td>Volume profile (POC/VAH/VAL)</td><td><span class="cross">✗</span></td><td><span class="check">✓</span></td></tr>
<tr><td>Scorecard (6-point check)</td><td><span class="cross">✗</span></td><td><span class="check">✓</span></td></tr>
<tr><td>Max pain (options)</td><td><span class="cross">✗</span></td><td><span class="check">✓</span></td></tr>
<tr><td>R:R ratios (multi-target)</td><td><span class="cross">✗</span></td><td><span class="check">✓</span> 1x / 1.7x / 2.7x</td></tr>
<tr><td>Counter-trend warnings</td><td><span class="cross">✗</span></td><td><span class="check">✓</span></td></tr>
<tr><td>Fractional sizing notes</td><td><span class="cross">✗</span></td><td><span class="check">✓</span></td></tr>
<tr><td>Delivery</td><td>Public site</td><td>Encrypted Nostr DM</td></tr>
<tr><td>Macro regime context</td><td><span class="check">✓</span> Basic</td><td><span class="check">✓</span> Full DXY/10Y/VIX analysis</td></tr>
</table>
</div>

<div class="features">
<h2>What's Inside Every Premium Report</h2>
<div class="feature-grid">
<div class="feature-card"><div class="icon">🎯</div><h3>3 Trade Plans</h3><p>Positional, Swing, and Day setups per ticker — each with entry, stop, and 3 targets.</p></div>
<div class="feature-card"><div class="icon">📏</div><h3>Position Sizing</h3><p>Pre-calculated for $5K and $10K accounts. Fractional sizing noted for expensive assets.</p></div>
<div class="feature-card"><div class="icon">📊</div><h3>VWAP + Volume Profile</h3><p>Session, weekly, monthly VWAP. POC, Value Area High/Low from volume analysis.</p></div>
<div class="feature-card"><div class="icon">🏆</div><h3>6-Point Scorecard</h3><p>Trend, momentum, volume, breadth, sentiment, regime — each scored pass/fail.</p></div>
<div class="feature-card"><div class="icon">⚖️</div><h3>Risk:Reward Ratios</h3><p>Multi-target R:R (1x, 1.7x, 2.7x) so you know when to scale out.</p></div>
<div class="feature-card"><div class="icon">🛡️</div><h3>Validation Layer</h3><p>Zero-price rejection, RSI sanity, direction checks, counter-trend flags, BTC freshness.</p></div>
</div>
</div>

<!-- ═══════════════ SAMPLE REPORT PREVIEW ═══════════════ -->
<div class="preview">
<h2>📖 Report Preview — See What You Get</h2>
<p class="preview-sub">This is a <em>real</em> excerpt from the latest Premium report. Names are unblurred — subscribers see every ticker.</p>
{preview_html}
</div>

<div class="pricing">
<h2>Simple Pricing. Lightning Fast.</h2>
<div class="pricing-cards">
<div class="price-card">
<div class="tier">Single Report</div>
<div class="amount">$15</div>
<div class="sats">15,000 sats</div>
<div class="period">One-time · Per report</div>
<ul>
<li>Full daily premium report</li>
<li>All stock + crypto setups</li>
<li>Trade plans + sizing</li>
<li>Scorecards + VWAP</li>
<li>Delivered via Nostr DM</li>
</ul>
</div>
<div class="price-card featured">
<div class="tier">Monthly</div>
<div class="amount">$50</div>
<div class="sats">50,000 sats/mo</div>
<div class="period">Best value · ~20 reports</div>
<ul>
<li>Daily premium reports</li>
<li>All trade plans + sizing</li>
<li>Macro regime analysis</li>
<li>Priority Nostr DM delivery</li>
<li>Cancel anytime</li>
</ul>
</div>
<div class="price-card">
<div class="tier">Quarterly</div>
<div class="amount">$120</div>
<div class="sats">120,000 sats</div>
<div class="period">3 months · Save 20%</div>
<ul>
<li>Everything in Monthly</li>
<li>Best per-report price</li>
<li>~60 reports for $2 each</li>
<li>Early access to new features</li>
<li>Cancel anytime</li>
</ul>
</div>
</div>
</div>

<div class="howto">
<h2>How to Subscribe</h2>
<div class="steps">
<div class="step">
<div class="num">1</div>
<div class="text">
<h3>Zap ⚡ to subscribe</h3>
<p>Zap 50,000 sats for monthly or 120,000 sats for quarterly. Zaps are auto-detected — no extra steps needed.</p>
<span class="code">⚡ {LIGHTNING_ADDR}</span>
</div>
</div>
<div class="step">
<div class="num">2</div>
<div class="text">
<h3>Manual Lightning payment</h3>
<p>No wallet with zap support? Send the exact amount (15k / 50k / 120k sats) to our Lightning address, then DM us the txid on Nostr.</p>
<span class="code">📬 {NOSTR_NPUB}</span>
</div>
</div>
<div class="step">
<div class="num">3</div>
<div class="text">
<h3>Receive daily premium reports</h3>
<p>Every market day, the full analysis lands in your Nostr DM — encrypted, private, instant.</p>
</div>
</div>
</div>
</div>

<div class="cta">
<h2>🔮 Ready to Trade with a Plan?</h2>
<p>Stop guessing. Start getting institutional-grade analysis delivered to your Nostr DM every market day.</p>
<a href="lightning:{LIGHTNING_ADDR}" class="zap-btn">⚡ Subscribe Now — 50,000 sats/mo</a>
<p class="alt">No zap support? Send exact amount (15k / 50k / 120k sats) to <strong style="color:#b388ff;">{LIGHTNING_ADDR}</strong> then DM your txid on Nostr.</p>
</div>

<div class="social-proof">
<h2>Why Traders Trust Phasma</h2>
<div class="proof-cards">
<div class="proof-card">
<div class="quote">"Finally, signals that come with actual trade plans — not just 'buy this.' The position sizing alone is worth the sats."</div>
<div class="attr">— Nostr user, early subscriber</div>
</div>
<div class="proof-card">
<div class="quote">"The scorecard system filters out the noise. I only act on 5+/6 setups and it's been solid."</div>
<div class="attr">— Crypto trader, monthly subscriber</div>
</div>
<div class="proof-card">
<div class="quote">"Lightning payments + Nostr DM = no KYC, no email, no tracking. This is how signal services should work."</div>
<div class="attr">— Privacy-focused trader</div>
</div>
</div>
</div>

<div class="faq">
<h2>FAQ</h2>
<div class="faq-item" onclick="this.classList.toggle('open')">
<div class="faq-q">How are reports delivered? <span class="arrow">▼</span></div>
<div class="faq-a">Via encrypted Nostr DM (NIP-04). You need a Nostr client like Damus (iOS), Amethyst (Android), or Primal (web). Your reports are private and encrypted — we can't even read them after sending.</div>
</div>
<div class="faq-item" onclick="this.classList.toggle('open')">
<div class="faq-q">What time are reports sent? <span class="arrow">▼</span></div>
<div class="faq-a">Stock reports: ~09:45 UTC (before US market open). Crypto reports: ~07:15 UTC daily. Macro regime updates are included in every report.</div>
</div>
<div class="faq-item" onclick="this.classList.toggle('open')">
<div class="faq-q">Do you offer refunds? <span class="arrow">▼</span></div>
<div class="faq-a">Since payments are in sats and non-reversible, we don't offer refunds. But you can cancel anytime — no auto-renewal. Your access runs until the period ends.</div>
</div>
<div class="faq-item" onclick="this.classList.toggle('open')">
<div class="faq-q">Is this financial advice? <span class="arrow">▼</span></div>
<div class="faq-a"><strong>No.</strong> Phasma Signals is independent trading research. All signals are for informational purposes. Always do your own research and manage your own risk. Past performance doesn't guarantee future results.</div>
</div>
<div class="faq-item" onclick="this.classList.toggle('open')">
<div class="faq-q">Which markets are covered? <span class="arrow">▼</span></div>
<div class="faq-a">Stocks: S&P 500 universe scanned daily for high-conviction setups. Crypto: Top 100 by market cap with momentum + volume filters. We focus on quality over quantity — typically 8-15 stock setups and 5-8 crypto picks per day.</div>
</div>
<div class="faq-item" onclick="this.classList.toggle('open')">
<div class="faq-q">Why Lightning + Nostr? <span class="arrow">▼</span></div>
<div class="faq-a">No KYC, no email, no credit card, no tracking. Lightning payments are instant and final. Nostr DMs are encrypted and decentralized. Your trading activity stays private.</div>
</div>
</div>

</div>

<div class="footer">
Phasma Signals — Independent trading research<br>
⚡ {LIGHTNING_ADDR} · ☕ {BTC_ADDRESS}<br>
⚠️ Not financial advice. Do your own research.
</div>

</body>
</html>"""

with open(os.path.join(SITE_DIR, "premium.html"), "w") as f:
    f.write(html)

print(f"Generated premium.html with live report preview")
if premium_data:
    print(f"  Preview: {len(premium_data.get('stocks',[]))} stocks, {len(premium_data.get('crypto',[]))} crypto loaded")
else:
    print(f"  Preview: no premium data found — showing placeholder")
