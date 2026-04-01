"""
taxable_contribute.py
Automated contribution script for taxable brokerage account.
Runs weekly to deploy available cash balance into a diversified ETF portfolio.
Supports both Alpaca and Public.com as broker backends.
Contributes the full available cash balance by default, or an overridden amount.

Algorithm — 3 layers applied in sequence:

    Layer 1 — Minimax Drift Correction
        Allocates contribution across 6 asset buckets (Equities, Metals, Crypto,
        Bonds, REITs, Commodities) to minimize proportional drift from target
        allocations. Funds the most underweight bucket exclusively until it reaches
        parity with the next, then proportionally as more buckets reach parity.
        Overweight buckets receive $0. Minimum $2 per funded bucket enforced via
        haircut from larger allocations.

    Layer 2 — Equity Blended Performance Weighting
        Splits the Equities allocation across 5 sub-buckets (Thematic, Industry,
        Sector, Developed, Emerging) based on a blended score combining a 252-day
        (long term) and 63-day (short term) return, each averaged over the last 5
        trading days. Both scores are normalized as z-scores against SPY as
        benchmark mean and VIX as benchmark SD. The blend weight between long and
        short term is dynamically derived from VVIX — lower VVIX (calmer markets)
        gives more influence to the short term signal. A softmax weighting
        determines the final split, with a dynamic tier system controlling how many
        sub-buckets are funded. Minimum $2 per funded sub-bucket enforced via
        haircut from larger allocations.

    Layer 3 — Fixed ETF Ratios
        Splits each bucket and sub-bucket allocation between its constituent ETFs
        using fixed ratios defined in ETF_SLOT_RATIOS. Minimum $1 per ETF enforced
        via haircut from the other ETFs in the group.

Usage:
    python taxable_contribute.py                        # live execution, Public (default)
    python taxable_contribute.py --broker public        # live execution, Public (explicit)
    python taxable_contribute.py --broker alpaca        # live execution, Alpaca
    python taxable_contribute.py --dry-run              # simulate without placing orders
    python taxable_contribute.py --amount 120           # override contribution amount in USD

Requirements:
    pip install alpaca-py requests yfinance pandas numpy exchange-calendars pytz
"""

import argparse
import importlib
import importlib.util
import os
import subprocess
import sys
import math
import tempfile
import uuid
from datetime import datetime, timedelta

REQUIRED_PACKAGES = {
    "alpaca": "alpaca-py",
    "requests": "requests",
    "yfinance": "yfinance",
    "pandas": "pandas",
    "numpy": "numpy",
    "exchange_calendars": "exchange-calendars",
    "pytz": "pytz",
}
for import_name, pip_name in REQUIRED_PACKAGES.items():
    if importlib.util.find_spec(import_name) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

import requests as req
import numpy as np
import pandas as pd
import yfinance as yf
import exchange_calendars as xcals
import pytz
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

ALPACA_API_KEY    = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
ALPACA_PAPER      = False

PUBLIC_SECRET_KEY = os.environ.get("PUBLIC_SECRET_KEY")
PUBLIC_ACCOUNT_ID = os.environ.get("PUBLIC_ACCOUNT_ID")

MIN_CONTRIBUTION  = 10.00

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

# ── STABLE — core algorithm structure, don't touch ──
BUCKETS            = ["Equities", "Metals", "Crypto", "Bonds", "REITs", "Commodities"]
SUB_BUCKETS        = ["Thematic", "Industry", "Sector", "Developed", "Emerging"]
NON_EQUITY_BUCKETS = ["Metals", "Crypto", "Bonds", "REITs", "Commodities"]

FLOOR_CAT = 2.00
FLOOR_ETF = 1.00

# ── ADJUST IF STRATEGY CHANGES ──────────────────────
LONG_LOOKBACK    = 252
SHORT_LOOKBACK   = 63
AVERAGING_WINDOW = 5

BENCHMARK_MEAN_TICKER       = "SPY"
BENCHMARK_SD_TICKER         = "^VIX"
BENCHMARK_CONFIDENCE_TICKER = "^VVIX"

TARGET_ALLOC = {
    "Equities":    0.50,
    "Metals":      0.15,
    "Crypto":      0.15,
    "Bonds":       0.05,
    "REITs":       0.10,
    "Commodities": 0.05,
}

ETF_CATS = {
    # Metals
    "IAUM": "Metals",
    "SLV":  "Metals",
    # Crypto
    "IBIT": "Crypto",
    "ETHA": "Crypto",
    # Bonds
    "TLT":  "Bonds",
    "MUB":  "Bonds",
    # REITs
    "USRT": "REITs",
    "IDGT": "REITs",
    # Commodities
    "CMDY": "Commodities",
    "COMT": "Commodities",
    # Equities — Developed
    "EWJ":  "Developed",
    "EWG":  "Developed",
    # Equities — Emerging
    "MCHI": "Emerging",
    "INDA": "Emerging",
    # Equities — Industry
    "ITA":  "Industry",
    "IGV":  "Industry",
    "IHE":  "Industry",
    # Equities — Sector
    "IYK":  "Sector",
    "IYH":  "Sector",
    "IYW":  "Sector",
    "IYE":  "Sector",
    # Equities — Thematic
    "ARTY": "Thematic",
    "ICLN": "Thematic",
}

# ── INPUTS — change these to adjust speculative positions ──
ETF_SLOT_RATIOS = {
    # Metals
    "IAUM": 7,
    "SLV":  2,
    # Crypto
    "IBIT": 7,
    "ETHA": 2,
    # Bonds
    "TLT":  2,
    "MUB":  1,
    # REITs
    "USRT": 2,
    "IDGT": 1,
    # Commodities
    "CMDY": 1,
    "COMT": 1,
    # Equities — Developed
    "EWJ":  1,
    "EWG":  1,
    # Equities — Emerging
    "MCHI": 1,
    "INDA": 1,
    # Equities — Industry
    "ITA":  1,
    "IGV":  1,
    # Equities — Sector
    "IYK":  1,
    "IYH":  1,
    # Equities — Thematic
    "ARTY": 1,
    "ICLN": 1,
}

# ─────────────────────────────────────────────
# SHARED HELPERS
# ─────────────────────────────────────────────

# Exits the script if the market is closed, including holidays and early closures
def check_market_open():
    nyse = xcals.get_calendar("XNYS")
    et = pytz.timezone("America/New_York")
    now = datetime.now(et)

    if not nyse.is_session(now.date()):
        print("Market is closed today (holiday or weekend). Use --dry-run to simulate. Exiting.")
        sys.exit(0)

    market_open  = nyse.session_open(now.date()).astimezone(et)
    market_close = nyse.session_close(now.date()).astimezone(et)

    if not (market_open <= now <= market_close):
        print("Market is currently closed. Use --dry-run to simulate. Exiting.")
        sys.exit(0)

# Aggregates position values into the 6 asset buckets using ETF_CATS
def get_bucket_values(position_values: dict[str, float]) -> dict[str, float]:
    bucket_values = {b: 0.0 for b in BUCKETS}
    for ticker, value in position_values.items():
        cat = ETF_CATS.get(ticker)
        if cat is None:
            print(f"Warning: {ticker} not found in ETF_CATS, skipping.")
            continue
        if cat in SUB_BUCKETS:
            bucket_values["Equities"] += value
        else:
            bucket_values[cat] += value
    return bucket_values

# Downloads adjusted close price history for a list of tickers from yfinance
def get_close_price_history(tickers: list[str]) -> pd.DataFrame:
    end = datetime.today()
    start = end - timedelta(days=int((LONG_LOOKBACK + AVERAGING_WINDOW) * 1.45) + 10)
    prices = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False, threads=True)["Close"]
    return prices

# ─────────────────────────────────────────────
# ALPACA HELPERS
# ─────────────────────────────────────────────

# Creates and returns the Alpaca API client
def get_alpaca_client():
    return TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=ALPACA_PAPER)

# Returns cash and position values from Alpaca account
def get_alpaca_portfolio(client) -> tuple[float, dict[str, float]]:
    account = client.get_account()
    cash = float(account.cash)
    positions = client.get_all_positions()
    position_values = {p.symbol: float(p.market_value) for p in positions}
    return cash, position_values

# Places fractional market orders via Alpaca
def place_orders_alpaca(client, etf_allocations: dict[str, float], dry_run: bool):
    for etf, amount in etf_allocations.items():
        notional = math.floor(amount * 100) / 100
        if notional < 1.00:
            print(f"Warning: {etf} allocation ${notional:.2f} below minimum, skipping.")
            continue
        if dry_run:
            print(f"DRY RUN — would buy ${notional:.2f} of {etf}")
        else:
            order = MarketOrderRequest(
                symbol=etf,
                notional=notional,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
            )
            client.submit_order(order)
            print(f"Ordered ${notional:.2f} of {etf}")

# ─────────────────────────────────────────────
# PUBLIC HELPERS
# ─────────────────────────────────────────────

# Exchanges the secret key for a short-lived bearer access token
def get_public_access_token() -> str:
    response = req.post(
        "https://api.public.com/userapiauthservice/personal/access-tokens",
        json={"secret": PUBLIC_SECRET_KEY}
    )
    response.raise_for_status()
    return response.json()["accessToken"]

# Returns cash and position values from Public account
def get_public_portfolio(headers: dict) -> tuple[float, dict[str, float]]:
    response = req.get(
        f"https://api.public.com/userapigateway/trading/{PUBLIC_ACCOUNT_ID}/portfolio/v2",
        headers=headers
    )
    response.raise_for_status()
    data = response.json()
    cash = float(data["buyingPower"]["cashOnlyBuyingPower"])
    position_values = {
        p["instrument"]["symbol"]: float(p["currentValue"])
        for p in data["positions"]
    }
    return cash, position_values

# Places fractional market orders via Public
def place_orders_public(headers: dict, etf_allocations: dict[str, float], dry_run: bool):
    for etf, amount in etf_allocations.items():
        notional = math.floor(amount * 100) / 100
        if notional < 1.00:
            print(f"Warning: {etf} allocation ${notional:.2f} below minimum, skipping.")
            continue
        if dry_run:
            print(f"DRY RUN — would buy ${notional:.2f} of {etf}")
        else:
            order = {
                "orderId": str(uuid.uuid4()),
                "instrument": {"symbol": etf, "type": "EQUITY"},
                "orderSide": "BUY",
                "orderType": "MARKET",
                "expiration": {"timeInForce": "DAY"},
                "amount": str(notional)
            }
            response = req.post(
                f"https://api.public.com/userapigateway/trading/{PUBLIC_ACCOUNT_ID}/order",
                headers=headers,
                json=order
            )
            print(f"Ordered ${notional:.2f} of {etf} — {response.json()}")

# ─────────────────────────────────────────────
# CALCULATIONS
# ─────────────────────────────────────────────

# Calculates the return for a single ETF over a given lookback period at a single reference day
def calc_recent_return(series: pd.Series, end_idx: int, lookback: int) -> float:
    start_idx = end_idx - lookback
    if start_idx < -len(series):
        raise ValueError(f"Not enough price history for {series.name}")

    end_price = series.iloc[end_idx]
    if pd.isna(end_price):
        end_price = series.iloc[:end_idx].dropna().iloc[-1]

    start_price = series.iloc[start_idx]
    if pd.isna(start_price):
        start_price = series.iloc[:start_idx].dropna().iloc[-1]

    return (end_price - start_price) / start_price

# Averages the return over the last n completed trading days for a single ETF
def calc_average_recent_return(series: pd.Series, window: int, lookback: int) -> float:
    returns = []
    for i in range(1, window + 1):
        returns.append(calc_recent_return(series, -i, lookback))
    return float(np.mean(returns))

# Normalizes a score against a benchmark mean and standard deviation
def calc_normalize(score: float, mean: float, sd: float) -> float:
    return (score - mean) / sd

# Applies softmax to a dictionary of normalized scores, returns weights summing to 1.0
def calc_softmax(scores: dict[str, float]) -> dict[str, float]:
    keys = list(scores.keys())
    vals = np.array([scores[k] for k in keys])
    vals = vals - np.max(vals)
    exps = np.exp(vals)
    total = exps.sum()
    return {k: float(exps[i] / total) for i, k in enumerate(keys)}

# Calculates how far off target a bucket is as a percentage of its target
def calc_pct_off_target(current: float, target: float) -> float:
    if target == 0:
        return 0.0
    return (target - current) / target

# Returns a confidence score (0-1) for the short term signal based on VVIX
# Anchored at: VVIX 60 -> 0.99, VVIX 95 -> 0.50
def calc_variance_confidence(vvix: float) -> float:
    return 1 / (1 + math.exp(0.13129 * (vvix - 95)))

# Returns the short term blend weight derived from VVIX
# Anchored at: VVIX 59.74 (all time low) -> 50%, VVIX -> inf -> 1% floor
def calc_short_term_weight(vvix: float) -> float:
    return max(0.01, 1 / (1 + math.exp(0.032574 * (vvix - 59.74))))

# Calculates the minimax drift correction allocations across all buckets
def calc_minimax(bucket_values: dict[str, float], contribution: float) -> dict[str, float]:
    total = sum(bucket_values.values()) + contribution
    targets = {b: total * TARGET_ALLOC[b] for b in BUCKETS}
    pct_off = {b: calc_pct_off_target(bucket_values[b], targets[b]) for b in BUCKETS}

    underweight = [b for b in BUCKETS if pct_off[b] > 0]
    allocations = {b: 0.0 for b in BUCKETS}
    sorted_buckets = sorted(underweight, key=lambda b: pct_off[b], reverse=True)

    remaining = contribution
    funded = []
    cur_pct_off = {b: pct_off[b] for b in sorted_buckets}

    for i in range(len(sorted_buckets)):
        funded.append(sorted_buckets[i])
        next_pct = pct_off[sorted_buckets[i + 1]] if i + 1 < len(sorted_buckets) else 0.0

        cost = sum(targets[b] * (cur_pct_off[b] - next_pct) for b in funded)

        if cost <= remaining:
            for b in funded:
                allocations[b] += targets[b] * (cur_pct_off[b] - next_pct)
                cur_pct_off[b] = next_pct
            remaining -= cost
        else:
            total_target = sum(targets[b] for b in funded)
            for b in funded:
                allocations[b] += remaining * (targets[b] / total_target)
            remaining = 0.0
            break

    diff = contribution - sum(allocations.values())
    if diff > 0:
        largest = max(allocations, key=lambda b: allocations[b])
        allocations[largest] += diff
    elif diff < 0:
        print(f"Warning: allocations exceeded contribution by ${abs(diff):.4f}, correcting.")
        largest = max(allocations, key=lambda b: allocations[b])
        allocations[largest] += diff

    return allocations

# Raises any allocation below the floor up to the floor, funded by proportional haircut from above
def apply_floor_with_haircut(allocations: dict[str, float], floor: float) -> dict[str, float]:
    result = allocations.copy()

    changed = True
    while changed:
        changed = False
        below = [b for b in result if 0 < result[b] < floor]
        above = [b for b in result if result[b] > floor]

        if not below:
            break

        deficit = sum(floor - result[b] for b in below)
        for b in below:
            result[b] = floor

        total_above = sum(result[b] for b in above)
        for b in above:
            result[b] -= deficit * (result[b] / total_above)

        changed = True

    return result

# ─────────────────────────────────────────────
# SCORING STATS
# ─────────────────────────────────────────────

# Computes all scoring data needed by layer2 and diagnostics
def get_scoring_stats(prices: pd.DataFrame, vix_data: pd.DataFrame) -> dict:
    vix_value  = float(vix_data[BENCHMARK_SD_TICKER].dropna().tail(AVERAGING_WINDOW).mean())
    vvix_value = float(vix_data[BENCHMARK_CONFIDENCE_TICKER].dropna().tail(AVERAGING_WINDOW).mean())

    bm_mean_long  = calc_average_recent_return(prices[BENCHMARK_MEAN_TICKER], AVERAGING_WINDOW, LONG_LOOKBACK)
    bm_mean_short = calc_average_recent_return(prices[BENCHMARK_MEAN_TICKER], AVERAGING_WINDOW, SHORT_LOOKBACK)
    bm_sd_long    = vix_value / 100
    bm_sd_short   = vix_value / 2 / 100

    raw_scores_long  = {}
    raw_scores_short = {}
    for sub in SUB_BUCKETS:
        etfs = [ticker for ticker in ETF_SLOT_RATIOS.keys() if ETF_CATS.get(ticker) == sub]
        ratios = [ETF_SLOT_RATIOS[etf] for etf in etfs]
        total_ratio = sum(ratios)

        long_returns  = [calc_average_recent_return(prices[etf], AVERAGING_WINDOW, LONG_LOOKBACK)  for etf in etfs]
        short_returns = [calc_average_recent_return(prices[etf], AVERAGING_WINDOW, SHORT_LOOKBACK) for etf in etfs]

        raw_scores_long[sub]  = float(sum(s * r / total_ratio for s, r in zip(long_returns,  ratios)))
        raw_scores_short[sub] = float(sum(s * r / total_ratio for s, r in zip(short_returns, ratios)))

    return {
        "raw_scores_long":      raw_scores_long,
        "raw_scores_short":     raw_scores_short,
        "bm_mean_long":         bm_mean_long,
        "bm_sd_long":           bm_sd_long,
        "bm_mean_short":        bm_mean_short,
        "bm_sd_short":          bm_sd_short,
        "vvix_value":           vvix_value,
        "variance_confidence":  calc_variance_confidence(vvix_value),
    }

# ─────────────────────────────────────────────
# LAYERS
# ─────────────────────────────────────────────

def layer1(bucket_values: dict[str, float], contribution: float) -> dict[str, float]:
    allocations = calc_minimax(bucket_values, contribution)
    allocations = apply_floor_with_haircut(allocations, FLOOR_CAT)
    return allocations


def layer2(equity_amount: float, stats: dict) -> dict[str, float]:

    # Skip if equity amount is below floor
    if equity_amount < FLOOR_CAT:
        return {s: 0.0 for s in SUB_BUCKETS}

    # Derive short term weight from VVIX
    short_weight = calc_short_term_weight(stats["vvix_value"])
    long_weight  = 1 - short_weight

    # Normalize both sets of scores against their respective benchmarks
    normalized_long  = {s: calc_normalize(stats["raw_scores_long"][s],  stats["bm_mean_long"],  stats["bm_sd_long"])  for s in SUB_BUCKETS}
    normalized_short = {s: calc_normalize(stats["raw_scores_short"][s], stats["bm_mean_short"], stats["bm_sd_short"]) for s in SUB_BUCKETS}

    # Blend the two normalized scores using VVIX-derived short term weight
    blended = {s: long_weight * normalized_long[s] + short_weight * normalized_short[s] for s in SUB_BUCKETS}

    # Rank and select top n funded sub-buckets dynamically based on equity amount
    ranked = sorted(blended.items(), key=lambda x: x[1], reverse=True)
    funded_scores = {}
    for n in range(len(SUB_BUCKETS), 0, -1):
        if equity_amount >= n * FLOOR_CAT:
            funded_scores = dict(ranked[:n])
            break

    # Softmax on funded sub-buckets only
    weights = calc_softmax(funded_scores)

    # Raw dollar allocations
    allocations = {s: 0.0 for s in SUB_BUCKETS}
    for s in funded_scores:
        allocations[s] = weights[s] * equity_amount

    # Apply floor with haircut
    allocations = apply_floor_with_haircut(allocations, FLOOR_CAT)

    return allocations


def layer2_simple(equity_amount: float, stats: dict) -> dict[str, float]:

    # Skip if equity amount is below floor
    if equity_amount < FLOOR_CAT:
        return {s: 0.0 for s in SUB_BUCKETS}

    # Rank by short term if confidence is high, long term if low
    rank_scores = stats["raw_scores_short"] if stats["variance_confidence"] >= 0.50 else stats["raw_scores_long"]
    ranked = sorted(rank_scores.items(), key=lambda x: x[1], reverse=True)

    # Fund as many sub-buckets as the equity amount supports
    funded = {}
    for n in range(len(SUB_BUCKETS), 0, -1):
        if equity_amount >= n * FLOOR_CAT:
            funded = dict(ranked[:n])
            break

    # Even split across funded sub-buckets
    allocations = {s: 0.0 for s in SUB_BUCKETS}
    even_amount = equity_amount / len(funded)
    for s in funded:
        allocations[s] = even_amount

    allocations = apply_floor_with_haircut(allocations, FLOOR_CAT)
    return allocations


def layer3(allocations: dict[str, float]) -> dict[str, float]:
    etf_allocations = {}

    for cat in NON_EQUITY_BUCKETS + SUB_BUCKETS:
        amount = allocations[cat]
        etfs = [ticker for ticker in ETF_SLOT_RATIOS.keys() if ETF_CATS.get(ticker) == cat]
        total_ratio = sum(ETF_SLOT_RATIOS[etf] for etf in etfs)
        etf_group = {etf: amount * (ETF_SLOT_RATIOS[etf] / total_ratio) for etf in etfs}
        etf_group = apply_floor_with_haircut(etf_group, FLOOR_ETF)
        etf_allocations.update(etf_group)

    return etf_allocations

# ─────────────────────────────────────────────
# DIAGNOSTICS
# ─────────────────────────────────────────────

# Prints a full diagnostic summary of the contribution run
def print_diagnostics(bucket_values, cash, l1, l2, stats, l3):
    invested = sum(bucket_values.values())
    total_after = invested + cash
    targets_before = {b: invested * TARGET_ALLOC[b] for b in BUCKETS}
    targets_after  = {b: total_after * TARGET_ALLOC[b] for b in BUCKETS}

    print(f"\n{'='*60}")
    print(f"  CONTRIBUTION DIAGNOSTIC — {datetime.today().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"  Cash to deploy:           ${cash:.2f}")
    print(f"  Current invested:         ${invested:.2f}")
    print(f"  Total after contribution: ${total_after:.2f}")

    # ── CURRENT STATE ──
    print(f"\n{'─'*60}")
    print(f"  CURRENT BUCKET STATE")
    print(f"{'─'*60}")
    print(f"  {'BUCKET':<14} {'VALUE':>8} {'CURR%':>7} {'OFF%':>8}")
    print(f"  {'-'*40}")
    for b in BUCKETS:
        curr_pct = (bucket_values[b] / invested) * 100 if invested > 0 else 0
        pct_off  = calc_pct_off_target(bucket_values[b], targets_before[b]) * 100
        print(f"  {b:<14} ${bucket_values[b]:>7.2f} {curr_pct:>6.1f}% {pct_off:>+7.2f}%")

    # ── LAYER 1 ──
    print(f"\n{'─'*60}")
    print(f"  LAYER 1 — Bucket Allocations")
    print(f"{'─'*60}")
    print(f"  {'BUCKET':<14} {'ALLOC':>8}")
    print(f"  {'-'*24}")
    for b in BUCKETS:
        print(f"  {b:<14} ${l1[b]:>7.2f}")

    # ── LAYER 2 ──
    print(f"\n{'─'*60}")
    print(f"  LAYER 2 — Equity Sub-Bucket Allocations")
    print(f"  Benchmark mean (L): {stats['bm_mean_long']*100:.2f}%   SD: {stats['bm_sd_long']*100:.2f}%")
    print(f"  Benchmark mean (S): {stats['bm_mean_short']*100:.2f}%   SD: {stats['bm_sd_short']*100:.2f}%")
    print(f"  Short Term Confidence: {stats['variance_confidence']:.2f}")
    print(f"{'─'*60}")
    print(f"  {'SUB-BUCKET':<14} {'LONG%':>7} {'SHORT%':>7} {'ALLOC':>8}")
    print(f"  {'-'*38}")
    for s in SUB_BUCKETS:
        long_score  = stats['raw_scores_long'][s] * 100
        short_score = stats['raw_scores_short'][s] * 100
        print(f"  {s:<14} {long_score:>6.2f}% {short_score:>6.2f}% ${l2[s]:>7.2f}")

    # ── LAYER 3 ──
    print(f"\n{'─'*60}")
    print(f"  LAYER 3 — Final ETF Allocations")
    print(f"{'─'*60}")
    print(f"  {'ETF':<8} {'ALLOC':>8}")
    print(f"  {'-'*18}")
    for etf, amount in l3.items():
        print(f"  {etf:<8} ${amount:>7.2f}")
    print(f"  {'TOTAL':<8} ${sum(l3.values()):>7.2f}")

    # ── POST-CONTRIBUTION ──
    new_bucket_values = bucket_values.copy()
    for etf, amount in l3.items():
        cat = ETF_CATS.get(etf)
        if cat in SUB_BUCKETS:
            new_bucket_values["Equities"] += amount
        elif cat:
            new_bucket_values[cat] += amount

    print(f"\n{'─'*60}")
    print(f"  POST-CONTRIBUTION BUCKET STATE")
    print(f"{'─'*60}")
    print(f"  {'BUCKET':<14} {'NEW VAL':>8} {'NEW%':>7} {'OFF%':>8}")
    print(f"  {'-'*40}")
    for b in BUCKETS:
        new_val = new_bucket_values[b]
        new_pct = (new_val / total_after) * 100
        new_off = calc_pct_off_target(new_val, targets_after[b]) * 100
        print(f"  {b:<14} ${new_val:>7.2f} {new_pct:>6.1f}% {new_off:>+7.2f}%")

    print(f"\n{'='*60}\n")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    # ── ARGUMENTS ──
    parser = argparse.ArgumentParser(description="Taxable brokerage weekly contribution script")
    parser.add_argument("--broker", type=str, default="public", choices=["public", "alpaca"], help="Broker to use (default: public)")
    parser.add_argument("--simple", action="store_true", help="Split equity evenly across sub-buckets instead of using blended scoring")
    parser.add_argument("--dry-run", action="store_true", help="Simulate orders without placing them")
    parser.add_argument("--amount", type=float, default=None, help="Override contribution amount in USD")
    args, _ = parser.parse_known_args()

    # ── INITIALIZE ──
    if not args.dry_run:
        check_market_open()

    if args.broker == "alpaca":
        client = get_alpaca_client()
        cash, position_values = get_alpaca_portfolio(client)
    else:
        access_token = get_public_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        cash, position_values = get_public_portfolio(headers)

    bucket_values = get_bucket_values(position_values)

    # ── CONTRIBUTION AMOUNT ──
    if args.amount is not None:
        if args.amount > cash:
            print(f"Warning: override amount ${args.amount:.2f} exceeds available cash ${cash:.2f}. Using cash balance instead.")
            contribution = cash
        else:
            contribution = args.amount
    else:
        contribution = cash

    if contribution < MIN_CONTRIBUTION:
        print(f"Insufficient cash ${contribution:.2f} — minimum is ${MIN_CONTRIBUTION:.2f}. Exiting.")
        sys.exit(0)

    # ── MARKET DATA ──
    yf.set_tz_cache_location(tempfile.mkdtemp())
    equity_tickers = [ticker for ticker in ETF_SLOT_RATIOS.keys() if ETF_CATS.get(ticker) in SUB_BUCKETS] + [BENCHMARK_MEAN_TICKER]
    prices = get_close_price_history(equity_tickers)

    vix_data = yf.download(
        [BENCHMARK_SD_TICKER, BENCHMARK_CONFIDENCE_TICKER],
        period="10d",
        auto_adjust=False,
        progress=False
    )["Close"]

    # ── SCORING STATS ──
    stats = get_scoring_stats(prices, vix_data)

    # ── LAYERS ──
    l1 = layer1(bucket_values, contribution)
    l2 = layer2_simple(l1["Equities"], stats) if args.simple else layer2(l1["Equities"], stats)
    combined = {**{b: l1[b] for b in NON_EQUITY_BUCKETS}, **l2}
    l3 = layer3(combined)

    # ── DIAGNOSTICS ──
    print_diagnostics(bucket_values, contribution, l1, l2, stats, l3)

    # ── EXECUTE ──
    if args.broker == "alpaca":
        place_orders_alpaca(client, l3, dry_run=args.dry_run)
    else:
        place_orders_public(headers, l3, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
