# All Weather Portfolio — Working Summary

*Distilled from full development conversation. Last state: April 25, 2026.*

-----

## 1. Purpose, Philosophy & Strategy

### Purpose

This account acts as a long-duration retirement bucket intended to last a lifetime — drawn from alongside traditional accounts in retirement to provide supplemental income and extra control over taxes.

### Philosophy

The portfolio is modeled on a Ray Dalio-style “All Weather” approach — diversified across asset classes that respond differently to various economic conditions (growth, recession, inflation, deflation). It is made up of 6 different buckets — Equities (further subdivided into Thematic, Industry, Sector, Developed, and Emerging), Metals, Crypto, Bonds, REITs, and Commodities — each built from a curated selection of ETFs, that provide resilience and growth potential across any market regime. This philosophy is a natural fit for an account that needs to compound across decades and survive multiple economic cycles without being derailed.

### Strategy

New money is deployed each week across the six asset buckets according to a drift correction algorithm — always directed toward whatever is most underweight relative to its target allocation. This maintains the All Weather balance and risk exposure over time, ensuring no single category grows to dominate or shrink to irrelevance. Within the Equities bucket, sub-buckets are further allocated by relative performance. This rewards well performing assets, fueling growth. Within each bucket and sub-bucket, the specific ETF selections and their ratios are fixed for the contribution period. This allows room to implement conviction regardless of portfolio status. Existing positions are held indefinitely; selling is reserved for exceptional circumstances only, and when necessary is done from lots held longer than 12 months to qualify for long-term capital gains treatment.

-----

## 2. Account Type & Platform

### Account Type

This is a taxable brokerage account held with Alpaca (transitioning to Public in the future). As a taxable account, selling positions triggers capital gains — not an ideal constraint, but an inherent one that shapes the contribution-only rebalancing approach used throughout this strategy.

### Why Not M1 Finance

This strategy is conceptually similar to M1 Finance’s “Pies” system — automated allocation across a structured set of ETFs. However, M1’s rebalancing applies uniformly across every layer of its nested pie structure. There is no way to tell M1 to rebalance at the category (bucket) level while keeping ETF-pair ratios frozen within each category. That specific behavior — rebalance categories, ignore internal pair drift — requires a custom algorithm.

### Why Alpaca

- Supports every ETF needed for the portfolio
- Full programmatic API access — supports headless, scheduled, set-it-and-forget-it operation
- Fractional/notional dollar orders supported for all target ETFs

**Limitations:**

- No built-in recurring deposit feature — cash must be transferred manually into the account before each contribution run. This is a meaningful gap for a hands-off strategy. A feature request has been submitted; Alpaca was receptive but offered no timeline.

### Why Public

- Full programmatic API access (same headless capability as Alpaca)
- **Built-in recurring deposit** — users can schedule automatic transfers into the account, which is critical for the fully hands-off vision
- Superior consumer app for monitoring balances and holdings

**Limitations:**

- Not all ETFs support notional (dollar-amount) orders. MUB currently fails with error code 125 (`Amount orders are not allowed for symbol MUB`). While all currently active ETFs in the portfolio work correctly, this could be a friction point if ETF selections change in the future. A feature request has been submitted; Public was receptive but offered no timeline.
- The Public UI enforces a $5 minimum per ETF purchase. However this restriction does not apply to API orders — notional purchases at the algorithm’s $1 ETF floor go through without issue. This means the algorithm’s small allocations are only viable headlessly and would not be replicable manually through the app.

### Current Status

Alpaca is the sole active contribution platform. Public holds a minimal balance (~$60) established during initial testing and will remain dormant until ready for the full transition. When the time comes, the full Alpaca balance will be transferred to Public to capture the 1% transfer bonus offered on incoming transfers, at which point Public becomes the primary and only platform due to its built-in recurring deposit feature. In the meantime, contributions are set at an intentionally elevated rate — designed to aggressively build principal during a period of low expenses to maximize the eventual transfer bonus.

-----

## 3. Holdings & Rationale

### Target Allocations

The portfolio is structured around fixed target allocations across the six asset buckets. These drive future contributions to constantly attempt to maintain the desired balance. The allocations represent desired long-term exposure for each asset class — ideally unchanging, but open to revision if the thesis behind any category fundamentally changes.

|Bucket     |Target %|
|-----------|--------|
|Equities   |50%     |
|Metals     |15%     |
|Crypto     |15%     |
|Bonds      |5%      |
|REITs      |10%     |
|Commodities|5%      |

The Equities bucket is further subdivided into 5 sub-buckets with no explicit target allocations between them — distribution is determined dynamically each contribution based on a scoring system:

|Sub-Bucket|Focus                             |
|----------|----------------------------------|
|Thematic  |Long-duration structural themes   |
|Industry  |Specific industries within sectors|
|Sector    |Broad GICS sector exposure        |
|Developed |Non-US developed market countries |
|Emerging  |Emerging market countries         |

### Master ETF Registry

A permanent record of every ETF ever held or tracked in this portfolio. ETFs are only ever added, never removed — ensuring existing positions are always correctly categorized regardless of whether contributions are still being made.

|ETF |Category            |
|----|--------------------|
|IAUM|Metals              |
|SLV |Metals              |
|IBIT|Crypto              |
|ETHA|Crypto              |
|TLT |Bonds               |
|MUB |Bonds               |
|USRT|REITs               |
|IDGT|REITs               |
|CMDY|Commodities         |
|COMT|Commodities         |
|EWJ |Developed (Equities)|
|EWG |Developed (Equities)|
|EWY |Developed (Equities)|
|MCHI|Emerging (Equities) |
|INDA|Emerging (Equities) |
|ITA |Industry (Equities) |
|IGV |Industry (Equities) |
|IHE |Industry (Equities) |
|IBB |Industry (Equities) |
|IYK |Sector (Equities)   |
|IYH |Sector (Equities)   |
|IYW |Sector (Equities)   |
|IYE |Sector (Equities)   |
|IYF |Sector (Equities)   |
|IYC |Sector (Equities)   |
|ARTY|Thematic (Equities) |
|ICLN|Thematic (Equities) |

### Current Selection and Rationale

The selections and ratios reflect current conviction, not permanent decisions — both the choice of ETF and the ratio between pairs can change at any time for future contributions. All ETFs are selected from the iShares fund family. What follows captures the reasoning at this point in time.

**Metals — IAUM + SLV (7:2)**
IAUM (Gold) is the primary holding; SLV (Silver) is the secondary speculative position. The 7:2 ratio reflects higher conviction in gold as the primary store of value.

**Crypto — IBIT + ETHA (7:2)**
IBIT (Bitcoin) and ETHA (Ethereum) are the two main iShares crypto ETFs. Bitcoin is the primary holding; Ethereum is the secondary speculative position. 7:2 ratio reflects relative conviction.

**Bonds — TLT + MUB (2:1)**
TLT (long-term Treasuries) is held primarily as a crash hedge — it typically surges when equities collapse, and is the core reason for having a bond allocation in an all-weather portfolio. MUB (municipal bonds) provides tax-free income, low volatility, and stability as a ballast within the bond bucket. TLT is dominant (2:1) because the crash-hedge purpose takes priority; going too heavy on MUB would dilute that function.

**REITs — USRT + IDGT (2:1)**
USRT is a broad US REIT ETF. IDGT covers digital infrastructure and real estate (data centers, towers), providing a more technology-adjacent real estate exposure.

**Commodities — CMDY + COMT (1:1)**
Both are broad commodity ETFs providing diversified exposure across the commodity spectrum. COMT was chosen as the pair to CMDY specifically for its higher energy concentration, providing a meaningful tilt toward energy within the overall commodities allocation. Equal ratio reflects equal conviction across both.

**Developed Markets — EWJ + EWY (1:1)**
Japan selected for its cultural resilience and a meaningful shift in banking philosophy that positions it well in a potential new world order. EWY (South Korea) fills the second slot on the strength of its semiconductor industry — globally significant and currently undervalued due to international uncertainty expected to smooth over time, leaving meaningful upside as conditions normalize. (Note: MSCI, which iShares uses, classifies South Korea as Emerging rather than Developed. However conviction is higher in existing emerging market holdings than in any available developed market alternative, making the classification bend justifiable.) Default equal weight for equity ETFs.

**Emerging Markets — MCHI + INDA (1:1)**
China and India selected as the two largest emerging market economies. Equal weight reflects balanced emerging market exposure. Default equal weight for equity ETFs.

**Industry — IBB + IGV (1:1)**
IGV (Software) is a value play — software stocks were hit hard on fears of AI disruption, a concern expected to prove overblown as the sector adapts and recovers. IBB (Biotechnology) was selected as a complementary holding: after four consecutive years of flat-to-negative returns (2021–2024), biotech had a strong 2025 recovery but still trades at a meaningful valuation discount to the broader market, suggesting the recovery thesis has room to run. Not a high-conviction contrarian thesis — more the best available beaten-down option at time of selection. Default equal weight for equity ETFs.

**Sector — IYF + IYK (1:1)**
IYK (Consumer Staples) provides defensive, recession-resistant exposure as an anchor of the pair. IYF (Financials) introduces cyclicality with deregulation tailwinds and a potential M&A resurgence as longer-term catalysts, and had pulled back meaningfully from its highs at time of selection. Default equal weight for equity ETFs.

**Thematic — ARTY + ICLN (1:1)**
ARTY (AI & Robotics) captures the broad AI and robotics wave — a structural theme with significant hype and momentum behind it. ICLN (Clean Energy) reflects a belief in clean energy as a net good for the world with long-term policy and adoption tailwinds. Default equal weight for equity ETFs.

### Rotated-Out ETFs Still Held

These ETFs were actively contributed to at some point but have since been rotated out. They remain in the master registry permanently so their existing holdings are correctly categorized for drift correction. No new contributions will be made to them.

Developed:

- **EWG** *(active: March 2026, rotated out: April 2026)* — Germany never held a strong conviction slot. Structural headwinds including elevated energy costs, auto sector decline, and political fragility provided additional reason to move on.

Industry:

- **ITA** *(active: March 2026, rotated out: April 2026)* — Aerospace & Defense was added as a geopolitical hedge. The upside thesis played out quickly as Iran-related events drove significant appreciation, so profits were locked in and the slot was redirected toward a new opportunity.

Sector:

- **IYH** *(active: March 2026, rotated out: April 2026)* — Healthcare deemed too defensive for the time being.
- **IYE** *(active: March 2026, rotated out: March 2026)* — Energy rotated out as the Iran conflict drove prices too high for meaningful long term growth, as history often dictates in conflict-driven commodity spikes.

### Sold / Fully Replaced ETFs

These ETFs were sold entirely and are no longer held.

- **IAU** — Sold and replaced with IAUM, which provides identical gold exposure at a lower expense ratio.
- **GSG** — Sold due to a K-1 tax form complication triggered by its partnership structure. Replaced with COMT, which avoids this issue while maintaining broad commodity exposure including meaningful energy weighting.

### Tracking-Only ETFs (never contributed to)

Industry:

- **IHE** — Pharmaceuticals

Sector:

- **IYW** — Technology
- **IYC** — Consumer Discretionary

-----

## 4. Contribution Algorithm

The algorithm deploys all available cash in the account each run — not just the planned contribution amount. Dividends, extra deposits, or any other accumulated cash are swept up automatically. A specific amount can be specified to override this behavior. A minimum of $10 is required for the algorithm to run.

### Layer 1 — Minimax Drift Correction (All Weather Maintenance)

**Purpose:** Distribute the full cash contribution across the 6 asset buckets in a way that maintains the target all-weather exposures over time. Each bucket’s target is defined as a percentage of the total invested value (cash is excluded from target calculations). Overweight buckets receive $0 — new money is never used to add to something already over its target.

**How it works:**

1. Calculate each bucket’s current value as a % of total invested
1. Identify underweight buckets (those below their target %)
1. Find the dollar allocation across underweight buckets that minimizes the *maximum remaining deviation* after funding — the minimax approach
1. Apply floor: any bucket receiving less than $2 gets rounded to $0, and its allocation is redistributed to the next most underweight bucket

This layer is inherently contrarian as a side effect of maintaining target exposures — whatever has underperformed and shrunk in relative weight receives more new money. But the primary purpose is maintaining all-weather diversification, not speculation on mean reversion.

### Layer 2 — Equity Sub-Bucket Weighting (Performance)

**Purpose:** Split the equity allocation from Layer 1 across the 5 equity sub-buckets using a blended performance scoring system. The `--simple` flag bypasses scoring entirely and distributes evenly, useful during volatile periods or when performance data is thin.

**Algorithm (scored mode):**

**Step 1 — Score each sub-bucket at two time horizons:**

- **Long-term score (252 trading days / ~1 year):** Average the 252-day return of each ETF in the sub-bucket, averaged over the last 5 completed trading days. Sub-bucket long score = ratio-weighted mean of its ETFs’ long scores.
- **Short-term score (63 trading days / ~3 months):** Same method using 63-day lookback.

**Step 2 — Determine blend weight using VVIX:**
VVIX (volatility of the VIX) is used as a confidence metric for the short-term signal. High VVIX means the near-term volatility environment is itself unstable — in this regime, the short-term signal is less reliable and the algorithm leans toward the long-term score.

```
short_term_weight = f(VVIX)   # lower VVIX → higher short-term weight
blended_score = (1 - short_term_weight) * long_score + short_term_weight * short_score
```

**Step 3 — Normalize using benchmark:**

```
SD_score = (blended_score - bm_mean) / bm_sd
```

- **Long-term benchmark mean:** SPY’s 252-day return using the same averaging method
- **Short-term benchmark mean:** SPY’s 63-day return using the same averaging method
- **Long-term benchmark SD:** VIX / 100
- **Short-term benchmark SD:** VIX / 2 / 100 (scaled down to 3-month window by ÷√4)

**Step 4 — Apply Softmax:**

```
weight_i = e^(SD_score_i) / sum(e^(SD_score_j) for all j)
```

**Step 5 — Tiered funding:**

- < $2: skip all
- $2–$3.99: top 1 sub-bucket
- $4–$5.99: top 2
- $6–$7.99: top 3
- $8–$9.99: top 4
- $10+: all 5

**Step 6 — Apply floor:** $2 minimum per funded sub-bucket; shortfalls are haircutted proportionally from over-allocated sub-buckets.

### Layer 3 — Fixed ETF Pair Ratios

**Purpose:** Split each bucket/sub-bucket dollar allocation between its two contributing ETFs according to the fixed ratios defined for each pair.

**How it works:**

1. For each bucket (non-equity) and sub-bucket (equity), take the dollar amount from Layer 1 or Layer 2
1. Divide proportionally between the two ETFs using their ratio values
1. Apply floor: each ETF receives a minimum of $1
1. If the total amount is too small to fund both ETFs at the floor, the full amount goes to the primary ETF (higher ratio value)

Within-pair drift is never corrected. The new contribution always uses the fixed ratio regardless of how holdings have drifted.

-----

## 5. Code Architecture

### Entry Points

```bash
python taxable_contribute.py                        # Live run, Public (default)
python taxable_contribute.py --broker alpaca        # Live run, Alpaca
python taxable_contribute.py --broker public        # Live run, Public (explicit)
python taxable_contribute.py --dry-run              # Simulate without placing orders
python taxable_contribute.py --amount 120           # Override contribution amount in USD
python taxable_contribute.py --simple               # Equal sub-bucket split (bypasses Layer 2 scoring)
```

### Environment Variables

```python
ALPACA_API_KEY    = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
ALPACA_PAPER      = False

PUBLIC_SECRET_KEY = os.environ.get("PUBLIC_SECRET_KEY")
PUBLIC_ACCOUNT_ID = os.environ.get("PUBLIC_ACCOUNT_ID")

GMAIL_USERNAME    = os.environ.get("GMAIL_USERNAME")
GMAIL_APP_PASSKEY = os.environ.get("GMAIL_APP_PASSKEY")
PHONE_NUMBER      = os.environ.get("PHONE_NUMBER")
```

### Key Constants

```python
MIN_CONTRIBUTION  = 10.00
FLOOR_CAT         = 2.0       # Minimum $ per bucket/sub-bucket
FLOOR_ETF         = 1.0       # Minimum $ per ETF
AVERAGING_WINDOW  = 5         # Trading days to average scores over
LONG_LOOKBACK     = 252       # Trading days for long-term return (~1 year)
SHORT_LOOKBACK    = 63        # Trading days for short-term return (~3 months)
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

BUCKETS            = ["Equities", "Metals", "Crypto", "Bonds", "REITs", "Commodities"]
SUB_BUCKETS        = ["Thematic", "Industry", "Sector", "Developed", "Emerging"]
NON_EQUITY_BUCKETS = ["Metals", "Crypto", "Bonds", "REITs", "Commodities"]

# Permanent master registry of every ETF ever held or tracked in this portfolio.
# ETFs are only ever added, never removed — ensures all positions can always be categorized.
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
    "EWY":  "Developed",    # Technically Emerging per MSCI but classified here as Developed
    # Equities — Emerging
    "MCHI": "Emerging",
    "INDA": "Emerging",
    # Equities — Industry
    "ITA":  "Industry",
    "IGV":  "Industry",
    "IHE":  "Industry",
    "IBB":  "Industry",
    # Equities — Sector
    "IYK":  "Sector",
    "IYH":  "Sector",
    "IYW":  "Sector",
    "IYE":  "Sector",
    "IYF":  "Sector",
    "IYC":  "Sector",
    # Equities — Thematic
    "ARTY": "Thematic",
    "ICLN": "Thematic",
}

# Current active ETF selections and their contribution ratio weights.
# Reflects current conviction only — both selections and ratios can change at any time.
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
    "EWY":  1,
    # Equities — Emerging
    "MCHI": 1,
    "INDA": 1,
    # Equities — Industry
    "IBB":  1,
    "IGV":  1,
    # Equities — Sector
    "IYF":  1,
    "IYK":  1,
    # Equities — Thematic
    "ARTY": 1,
    "ICLN": 1,
}
```

### Core Functions

```python
# SHARED HELPERS
def is_market_open() -> bool                                        # Returns True if market is open; if closed and not dry run, main switches to dry run
def get_bucket_values(position_values) -> dict[str, float]
def get_close_price_history(tickers) -> pd.DataFrame
def send_text(subject, body)                                        # Sends SMS via Gmail SMTP to carrier gateway

# ALPACA HELPERS
def get_alpaca_client()
def get_alpaca_portfolio(client) -> tuple[float, dict[str, float]]
def place_orders_alpaca(client, etf_allocations, dry_run) -> list[tuple]  # returns (etf, amount, success, msg) per order

# PUBLIC HELPERS
def get_public_access_token() -> str
def get_public_portfolio(headers) -> tuple[float, dict[str, float]]
def place_orders_public(headers, etf_allocations, dry_run) -> list[tuple] # returns (etf, amount, success, msg) per order

# CALCULATIONS
def calc_recent_return(series, end_idx, lookback) -> float
def calc_average_recent_return(series, window, lookback) -> float
def calc_normalize(score, mean, sd) -> float
def calc_softmax(scores) -> dict[str, float]
def calc_pct_off_target(current, target) -> float
def calc_variance_confidence(vvix) -> float        # logistic curve, maps VVIX → 0–1 confidence
def calc_short_term_weight(vvix) -> float          # logistic curve, maps VVIX → short term blend weight
def calc_minimax(bucket_values, contribution) -> dict[str, float]
def apply_floor_with_haircut(allocations, floor) -> dict[str, float]

# SCORING STATS
def get_scoring_stats(prices, vix_data) -> dict    # computes all Layer 2 inputs in one place
                                                   # returns: raw_scores_long, raw_scores_short,
                                                   #          bm_mean_long, bm_sd_long,
                                                   #          bm_mean_short, bm_sd_short,
                                                   #          vvix_value, variance_confidence

# LAYERS
def layer1(bucket_values, contribution) -> dict[str, float]
def layer2(equity_amount, stats) -> dict[str, float]         # scored mode
def layer2_simple(equity_amount, stats) -> dict[str, float]  # even split, uses stats for ranking only
def layer3(allocations) -> dict[str, float]

# DIAGNOSTICS AND NOTIFICATIONS
def print_diagnostics_pre(bucket_values, cash, contribution, l1, l2, stats, l3)
def print_diagnostics_post(new_bucket_values, actual_deployed, cash_remaining, funds_to_balance)
def build_notification(bucket_values, cash, contribution, l1, l2, stats, l3,
                        new_bucket_values, cash_remaining, funds_to_balance,
                        broker, dry_run, simple, order_results) -> tuple[str, str]
def build_insufficient_funds_notification(bucket_values, cash, funds_to_balance,
                                          broker, dry_run) -> tuple[str, str]
```

### Main Flow

```python
def main():
    # Parse --broker, --simple, --dry-run, --amount args

    # Fetch portfolio first (needed for notifications regardless of market state)
    cash, position_values = get_portfolio(broker)
    bucket_values = get_bucket_values(position_values)

    # Check market; switch to dry run if closed
    if not args.dry_run and not is_market_open():
        args.dry_run = True

    # Determine contribution amount
    # If insufficient, print post state, notify, and exit
    contribution = args.amount or cash
    if contribution < MIN_CONTRIBUTION:
        print_diagnostics_post(bucket_values, 0.0, cash, funds_to_balance)
        send_text(*build_insufficient_funds_notification(...))
        sys.exit(0)

    # Fetch market data, compute scoring stats, run layers
    stats = get_scoring_stats(prices, vix_data)
    l1 = layer1(bucket_values, contribution)
    l2 = layer2_simple(...) if args.simple else layer2(...)
    l3 = layer3(combined)

    # Pre-order diagnostics
    print_diagnostics_pre(bucket_values, cash, contribution, l1, l2, stats, l3)

    # Place orders
    order_results = place_orders(broker, l3, dry_run)

    # Post-contribution calculations using actual order results
    # Derives: actual_deployed, cash_remaining, new_bucket_values, funds_to_balance
    ...

    # Post-order diagnostics and notification
    print_diagnostics_post(new_bucket_values, actual_deployed, cash_remaining, funds_to_balance)
    send_text(*build_notification(...))
```

### Public.com API Authentication

```python
response = requests.post(
    "https://api.public.com/userapiauthservice/personal/access-tokens",
    json={"secret": PUBLIC_SECRET_KEY}
    # No validityInMinutes needed — 15 min default is sufficient for a sub-1-minute script
)
access_token = response.json()["accessToken"]
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

-----

## 6. Deployment & Notifications

### GitHub Actions

GitHub Actions was chosen as the free, fully cloud-based scheduling solution. Scripts run in a fresh Ubuntu environment on a cron schedule with no device needing to be powered on. Credentials are stored as GitHub repository secrets.

Two setup challenges worth noting:

- **Cold-start problem:** GitHub Actions is known to skip or delay the first several scheduled runs of a newly created workflow. The workaround is to trigger at least one successful manual run before relying on the schedule.
- **Inactivity disabling:** GitHub automatically disables scheduled workflows in repositories that have had no activity for 60 days. A keepalive workflow was added to prevent this.

```yaml
name: Weekly Contribution

on:
  schedule:
    - cron: '45 13 * * 2'   # Every Tuesday ~9:45am ET (13:45 UTC)
  workflow_dispatch:

jobs:
  contribute:
    runs-on: ubuntu-latest
    steps:
      - name: Scheduler Check
        run: echo "Automated trigger successful at $(date)"

      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install alpaca-py requests yfinance pandas numpy exchange-calendars pytz

      - name: Run contribution script
        env:
          ALPACA_API_KEY: ${{ secrets.ALPACA_API_KEY }}
          ALPACA_SECRET_KEY: ${{ secrets.ALPACA_SECRET_KEY }}
          PUBLIC_SECRET_KEY: ${{ secrets.PUBLIC_SECRET_KEY }}
          PUBLIC_ACCOUNT_ID: ${{ secrets.PUBLIC_ACCOUNT_ID }}
          GMAIL_USERNAME: ${{ secrets.GMAIL_USERNAME }}
          GMAIL_APP_PASSKEY: ${{ secrets.GMAIL_APP_PASSKEY }}
          PHONE_NUMBER: ${{ secrets.PHONE_NUMBER }}
        run: python taxable_contribute.py --broker alpaca --simple
```

### SMS Notifications

The script sends SMS notifications via Gmail SMTP to the Verizon MMS gateway (`@vzwpix.com`). `smtplib` is used directly — no third-party SMS service required. The notification fires on every run regardless of outcome.

**Contribution** — Subject: `All Weather Contribution: $XX.XX [broker]` (prefixed with `DRY RUN --` if applicable). Body contains Layer 1 bucket allocations with before% and target%, Layer 2 mode/benchmark/sub-bucket scores, Layer 3 orders grouped by bucket with ratios, and an after summary showing new bucket dollar values, off%, cash remaining, account total, and funds to balance (the additional deposit needed to bring all buckets to exact target allocation). Failed orders are marked `(FAILED!!!!!)` inline.

**Insufficient funds** — Subject: `All Weather Contribution: Insufficient [broker]`. Body shows current bucket values with target% and off%, account total including cash, and funds to balance.

-----

## 7. Workflow

Each week, approximately $100 is manually deposited into the Alpaca account. The contribution script runs automatically every Tuesday, deploying whatever cash is available across the six asset buckets according to the algorithm. An SMS notification arrives confirming what was deployed, the post-contribution state of each bucket, and the funds needed to fully balance the portfolio. No further action is required until the next week.

Once the transition to Public occurs, even the manual deposit step disappears — automatic recurring contributions will be scheduled directly through the platform, reducing the weekly workflow to simply receiving and reviewing the SMS notification.

-----

## 8. Key Design Decisions & Development History

**March 2026**

|Decision                        |Category                     |Rationale                                                                |Notes                                                                                                                                 |
|--------------------------------|-----------------------------|-------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
|3-layer algorithm architecture  |Algorithm — Global           |Clean separation of concerns                                             |Layer 1 = all-weather maintenance, Layer 2 = performance weighting, Layer 3 = pair ratios                                             |
|Deploy all available cash       |Algorithm — Global           |Sweeps up dividends, variable deposits, and any other cash automatically |Amount override exists for cases where partial deployment is desired                                                                  |
|$10 minimum contribution        |Algorithm — Global           |Minimum required to guarantee the algorithm can function without breaking|A perfectly balanced portfolio needs all 5 non-equity buckets funded at $2 each — below $10 there is literally not enough to fill them|
|Minimax drift correction        |Algorithm — Layer 1          |Optimizes proportional drift, not absolute distance                      |A 5% bucket and 50% bucket are treated proportionally, not equally                                                                    |
|Softmax for sub-bucket weighting|Algorithm — Layer 2          |Always sums to 100%, never produces 0%                                   |Naturally amplifies large score differences while keeping small ones nearly equal                                                     |
|`--simple` flag for Layer 2     |Algorithm — Layer 2 / Feature|Bypasses scoring and splits equity evenly across sub-buckets             |Useful during volatile periods or when performance data is thin                                                                       |
|VIX as benchmark SD             |Algorithm — Layer 2          |VIX represents annualized volatility                                     |Long-term uses VIX/100 directly; short-term uses VIX/2/100 scaled by √4 for quarterly window                                          |
|VVIX as short-term blend weight |Algorithm — Layer 2          |Dynamically adjusts trust in short-term signal                           |High VVIX = lean long-term; low VVIX = trust short-term                                                                               |
|Separate SPY means per horizon  |Algorithm — Layer 2          |Each horizon judged against SPY over same period                         |Prevents a single blended benchmark from misrepresenting either window                                                                |
|GitHub Actions for scheduling   |Deployment                   |Free, cloud-based, no device needed                                      |Keepalive workflow added to prevent 60-day inactivity disabling                                                                       |
|First live run March 16, 2026   |Deployment                   |Proof of concept confirmed                                               |All equity sub-buckets funded, non-equity correctly received $0 as overweight                                                         |
|yfinance timezone cache fix     |Bug Fix                      |Resolved SQLite lock bug                                                 |Isolated each run to a temp directory via `yf.set_tz_cache_location(tempfile.mkdtemp())`                                              |

**April 2026**

|Decision                                         |Category            |Rationale                                                         |Notes                                                                              |
|-------------------------------------------------|--------------------|------------------------------------------------------------------|-----------------------------------------------------------------------------------|
|Post-contribution state uses actual order results|Design              |Correctly reflects failed orders and floor truncation             |Built from `order_results` tuples, not l3 allocations                              |
|Portfolio fetch before market check              |Design              |Balance data needed for all notification paths                    |Moved above market check so all exit paths have full portfolio data                |
|Split diagnostics into pre and post              |Design              |Post state needs actual order results, not theoretical allocations|`print_diagnostics_pre` runs before orders; `print_diagnostics_post` runs after    |
|SMS notifications via Gmail SMTP                 |Feature / Deployment|Free, zero maintenance, no third-party service                    |Uses Verizon MMS gateway (`@vzwpix.com`)                                           |
|`funds_to_balance` metric added                  |Feature             |Shows minimum deposit needed to reach full target allocation      |Derived from most overweight bucket; cash remaining subtracted as already available|
|Market closed switches to dry run                |Feature             |Ensures diagnostics and notifications always fire                 |Previously exited silently; now runs fully in dry run mode                         |
|Insufficient funds path improved                 |Feature             |Gives useful state snapshot even when nothing is deployed         |Now prints post diagnostic and sends full notification rather than exiting silently|

-----

## 9. Open Design Questions & Future Enhancements

1. **Layer 2 performance vs. contrarian:** The equity layer currently rewards recent outperformers while Layer 1 does the opposite. Future consideration: inverting the Layer 2 score for a consistently contrarian algorithm.
1. **Expanded sub-bucket scoring:** Should inactive ETFs in a sub-bucket (e.g., IYW in Sector) be included in the sub-bucket’s performance score? Currently they are not.
1. **Performance diagnostic tool:** A planned separate feature to track overall portfolio performance by bucket — unrealized gains, cost basis, return vs. benchmark — not yet built.
1. **VVIX confidence function tuning:** The exact logistic curve mapping VVIX to short-term blend weight may need empirical tuning over time as more data is gathered.

-----

## 10. Project Files Reference

The following files are uploaded to this project and accessible across all chats:

**`taxable_contribute.py`** — The current, canonical contribution script. Supports both Alpaca and Public via the `--broker` flag. This is the active source of truth.

**`contribute.yml`** — The GitHub Actions workflow file. Defines the weekly Tuesday schedule, Python environment setup, dependency installation, and the command used to run the contribution script with all required secrets.

**`alpaca_contribute.py`** — Legacy Alpaca-specific script, kept for historical reference. Do not treat as current.

**`public_contribute.py`** — Legacy Public-specific script, kept for historical reference. Do not treat as current.

**`taxable_brokerage_working_summary.md`** — A distilled summary of all strategy decisions, algorithm design, code architecture, and open questions. Kept in the project for reference — these instructions were derived from it and should be kept in sync with it.

**`Claude-Taxable_brokerage_account_strategy.md`** — Full exported transcript of the original development conversation (March 4–17, 2026). Contains the reasoning and iteration behind the initial build — algorithm design, platform selection, ETF selection, and deployment setup. Subsequent development is captured in the working summary.

**`contribution_calculator.jsx`** — React-based interactive calculator built as a prototyping tool early in development. No longer part of the active system but kept as a development artifact.

-----

*This document captures the complete working state as of April 25, 2026. Use as the starting context for any continuation conversation.*
