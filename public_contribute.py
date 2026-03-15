"""
public_contribute.py
Automated contribution script for taxable brokerage account.
Runs weekly to deploy available cash balance into a diversified ETF portfolio.
Contributes the full available cash balance by default, or an overridden amount.

Algorithm — 3 layers applied in sequence:

    Layer 1 — Minimax Drift Correction
        Allocates contribution across 6 asset buckets (Equities, Metals, Crypto,
        Bonds, REITs, Commodities) to minimize proportional drift from target
        allocations. Funds the most underweight bucket exclusively until it reaches
        parity with the next, then proportionally as more buckets reach parity.
        Overweight buckets receive $0. Minimum $2 per funded bucket enforced via
        haircut from larger allocations.

    Layer 2 — Equity Recent Performance Weighting
        Splits the Equities allocation across 4 sub-buckets (Thematic, Country,
        Industry, Sector) based on recent 63-day return averaged over the last 5
        trading days. Scores are normalized against SPY as benchmark mean and
        VIX/2 as benchmark SD. A softmax weighting determines the final split,
        with a tier system controlling how many sub-buckets are funded based on
        the equity allocation size. Minimum $2 per funded sub-bucket enforced via
        haircut from larger allocations.

    Layer 3 — Fixed ETF Ratios
        Splits each bucket and sub-bucket allocation between its constituent ETFs
        using fixed ratios defined in ETF_SLOT_RATIOS. Minimum $1 per ETF enforced
        via haircut from the other ETFs in the group.

Usage:
    python public_contribute.py              # live execution with diagnostics
    python public_contribute.py --dry-run    # simulate orders without placing them
    python public_contribute.py --amount 120 # override contribution amount in USD

Requirements:
    pip install requests yfinance pandas numpy exchange_calendars pytz
"""

import argparse
import importlib
import importlib.util
import os
import subprocess
import sys
import math
import uuid
from datetime import datetime, time, timedelta

REQUIRED_PACKAGES = {
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

import requests
import numpy as np
import pandas as pd
import yfinance as yf
import exchange_calendars as xcals
import pytz

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

PUBLIC_SECRET_KEY = os.environ.get("PUBLIC_SECRET_KEY")
PUBLIC_ACCOUNT_ID = os.environ.get("PUBLIC_ACCOUNT_ID")

MIN_CONTRIBUTION  = 10.00

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

# ── STABLE — core algorithm structure, don't touch ──
BUCKETS            = ["Equities", "Metals", "Crypto", "Bonds", "REITs", "Commodities"]
SUB_BUCKETS        = ["Thematic", "Country", "Industry", "Sector"]
NON_EQUITY_BUCKETS = ["Metals", "Crypto", "Bonds", "REITs", "Commodities"]

FLOOR_CAT = 2.00
FLOOR_ETF = 1.00

# ── ADJUST IF STRATEGY CHANGES ──────────────────────
SCORING_LOOKBACK = 63
AVERAGING_WINDOW = 5

BENCHMARK_MEAN_TICKER = "SPY"
BENCHMARK_SD_TICKER   = "^VIX"

TARGET_ALLOC = {
    "Equities":    0.40,
    "Metals":      0.15,
    "Crypto":      0.15,
    "Bonds":       0.10,
    "REITs":       0.10,
    "Commodities": 0.10,
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
    # Equities — Country
    "EWJ":  "Country",
    "MCHI": "Country",
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
    # Equities — Country
    "EWJ":  1,
    "MCHI": 1,
    # Equities — Industry
    "ITA":  1,
    "IGV":  1,
    # Equities — Sector
    "IYK":  1,
    "IYE":  1,
    # Equities — Thematic
    "ARTY": 1,
    "ICLN": 1,
}
# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

# Exchanges the secret key for a short-lived bearer access token
def get_access_token() -> str:
    response = requests.post(
        "https://api.public.com/userapiauthservice/personal/access-tokens",
        json={"secret": PUBLIC_SECRET_KEY, "validityInMinutes": 15}
    )
    response.raise_for_status()
    return response.json()["accessToken"]

# Fetches portfolio data including cash and positions
def get_portfolio(headers: dict) -> dict:
    response = requests.get(
        f"https://api.public.com/userapigateway/trading/{PUBLIC_ACCOUNT_ID}/portfolio/v2",
        headers=headers
    )
    response.raise_for_status()
    return response.json()

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

# Returns a dictionary of {ticker: market_value} for all current positions
def get_position_values(portfolio: dict) -> dict[str, float]:
    return {
        p["instrument"]["symbol"]: float(p["currentValue"])
        for p in portfolio["positions"]
    }

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
    start = end - timedelta(days=int((SCORING_LOOKBACK + AVERAGING_WINDOW) * 1.45) + 10)
    prices = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False, threads=True)["Close"]
    return prices

# ─────────────────────────────────────────────
# CALCULATIONS
# ─────────────────────────────────────────────

# Calculates the 63 trading day return for a single ETF at a single reference day
def calc_recent_return(series: pd.Series, end_idx: int) -> float:
    start_idx = end_idx - SCORING_LOOKBACK
    if start_idx < -len(series):
        raise ValueError(f"Not enough price history for {series.name}")

    end_price = series.iloc[end_idx]
    if pd.isna(end_price):
        end_price = series.iloc[:end_idx].dropna().iloc[-1]

    start_price = series.iloc[start_idx]
    if pd.isna(start_price):
        start_price = series.iloc[:start_idx].dropna().iloc[-1]

    return (end_price - start_price) / start_price

# Averages the 63 trading day return over the last n completed trading days for a single ETF
def calc_average_recent_return(series: pd.Series, window: int) -> float:
    returns = []
    for i in range(1, window + 1):
        returns.append(calc_recent_return(series, -i))
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

# Calculates the minimax drift correction allocations across all buckets
def calc_minimax(bucket_values: dict[str, float], contribution: float) -> dict[str, float]:
    total = sum(bucket_values.values()) + contribution
    targets = {b: total * TARGET_ALLOC[b] for b in BUCKETS}
    pct_off = {b: calc_pct_off_target(bucket_values[b], targets[b]) for b in BUCKETS}

    # Overweight buckets get $0
    underweight = [b for b in BUCKETS if pct_off[b] > 0]
    allocations = {b: 0.0 for b in BUCKETS}

    # Sort descending by % off target — most underweight first
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

    # Rounding correction
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
# LAYERS
# ─────────────────────────────────────────────

def layer1(bucket_values: dict[str, float], contribution: float) -> dict[str, float]:
    allocations = calc_minimax(bucket_values, contribution)
    allocations = apply_floor_with_haircut(allocations, FLOOR_CAT)
    return allocations


def layer2(equity_amount: float, prices: pd.DataFrame, bm_mean: float, bm_sd: float) -> tuple[dict[str, float], dict[str, float]]:
    # Score each sub-bucket using only ETFs in ETF_SLOT_RATIOS, weighted by ratio
    raw_scores = {}
    for sub in SUB_BUCKETS:
        etfs = [ticker for ticker in ETF_SLOT_RATIOS.keys() if ETF_CATS.get(ticker) == sub]
        ratios = [ETF_SLOT_RATIOS[etf] for etf in etfs]
        scores = [calc_average_recent_return(prices[etf], AVERAGING_WINDOW) for etf in etfs]
        total_ratio = sum(ratios)
        raw_scores[sub] = float(sum(s * r / total_ratio for s, r in zip(scores, ratios)))

    # Skip remainder if equity amount is below floor
    if equity_amount < FLOOR_CAT:
        return {s: 0.0 for s in SUB_BUCKETS}, raw_scores

    # Normalize scores against benchmark mean and SD
    normalized = {s: calc_normalize(raw_scores[s], bm_mean, bm_sd) for s in SUB_BUCKETS}

    # Rank and select top n funded sub-buckets by normalized score
    ranked = sorted(normalized.items(), key=lambda x: x[1], reverse=True)
    if equity_amount < 4:
        funded_scores = dict(ranked[:1])
    elif equity_amount < 6:
        funded_scores = dict(ranked[:2])
    elif equity_amount < 8:
        funded_scores = dict(ranked[:3])
    else:
        funded_scores = dict(ranked[:4])

    # Softmax on funded sub-buckets only
    weights = calc_softmax(funded_scores)

    # Raw dollar allocations
    allocations = {s: 0.0 for s in SUB_BUCKETS}
    for s in funded_scores:
        allocations[s] = weights[s] * equity_amount

    # Apply floor with haircut
    allocations = apply_floor_with_haircut(allocations, FLOOR_CAT)

    return allocations, raw_scores


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
def print_diagnostics(bucket_values, cash, l1, l2, raw_scores, bm_mean, bm_sd, l3):
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
    print(f"  Benchmark mean: {bm_mean*100:.2f}%   Benchmark SD: {bm_sd*100:.2f}%")
    print(f"{'─'*60}")
    print(f"  {'SUB-BUCKET':<14} {'SCORE':>8} {'ALLOC':>8}")
    print(f"  {'-'*32}")
    for s in SUB_BUCKETS:
        score = raw_scores.get(s, 0) * 100
        print(f"  {s:<14} {score:>7.2f}% ${l2[s]:>7.2f}")

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
# EXECUTION
# ─────────────────────────────────────────────

# Places fractional market orders for all non-zero ETF allocations
def place_orders(headers: dict, etf_allocations: dict[str, float], dry_run: bool = True):
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
            response = requests.post(
                f"https://api.public.com/userapigateway/trading/{PUBLIC_ACCOUNT_ID}/order",
                headers=headers,
                json=order
            )
            print(f"Ordered ${notional:.2f} of {etf} — {response.json()}")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    # ── ARGUMENTS ──
    parser = argparse.ArgumentParser(description="Public.com weekly contribution script")
    parser.add_argument("--dry-run", action="store_true", help="Simulate orders without placing them")
    parser.add_argument("--amount", type=float, default=None, help="Override contribution amount in USD")
    args, _ = parser.parse_known_args()

    # ── INITIALIZE ──
    if not args.dry_run:
        check_market_open()

    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # ── ACCOUNT DATA ──
    portfolio = get_portfolio(headers)
    cash = float(portfolio["buyingPower"]["cashOnlyBuyingPower"])
    position_values = get_position_values(portfolio)
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
    equity_tickers = [ticker for ticker in ETF_SLOT_RATIOS.keys() if ETF_CATS.get(ticker) in SUB_BUCKETS] + [BENCHMARK_MEAN_TICKER]
    prices = get_close_price_history(equity_tickers)

    bm_mean = calc_average_recent_return(prices[BENCHMARK_MEAN_TICKER], AVERAGING_WINDOW)
    vix = yf.download(BENCHMARK_SD_TICKER, period="10d", auto_adjust=False, progress=False)["Close"]
    bm_sd = float(vix.dropna().tail(AVERAGING_WINDOW).mean().iloc[0]) / 2 / 100

    # ── LAYERS ──
    l1 = layer1(bucket_values, contribution)
    l2, raw_scores = layer2(l1["Equities"], prices, bm_mean, bm_sd)
    combined = {**{b: l1[b] for b in NON_EQUITY_BUCKETS}, **l2}
    l3 = layer3(combined)

    # ── DIAGNOSTICS ──
    print_diagnostics(bucket_values, contribution, l1, l2, raw_scores, bm_mean, bm_sd, l3)

    # ── EXECUTE ──
    place_orders(headers, l3, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
