# Fidelity CMA Strategy — Conversation Narrative

*A chronological account of how the strategy was developed: the decisions made, unmade, and evolved. Last conversation state: April 11, 2026.*

-----

## Chapter 1: The Starting Point — A Single World Blue Chip Fund

The conversation began with a clear, simple goal: invest in the best companies in the world. The framing was “world market blue chip stocks” — large and mid-cap companies from US, developed, and emerging markets combined, agnostic to country or market classification, roughly 2,500–3,000 stocks. The ideal instrument would be a single, low-cost fund that simply owned the top global companies regardless of domicile.

**The single-fund problem:** The closest available option was iShares ACWI, which holds approximately 2,300–2,500 securities across global markets with a balanced US and international split. But its expense ratio was judged too high to justify when cheaper alternatives existed. No low-cost single-fund global equity equivalent was available.

**The two-fund compromise:** With no ideal single fund available, VOO + VEU emerged as the best approximation chosen purely for their low expense ratios — not because they were ideal. The problems each creates individually:

- **VOO** covers approximately 500 US companies — too *concentrated*. The US section of ACWI alone contains more than 500 companies, so VOO doesn’t even fully capture the domestic portion of the target.
- **VEU** covers approximately 4,000 international companies across developed and emerging markets — too *broad*. The international section of ACWI is far more selective.

But beyond the individual fund issues, there is a structural cost to using two funds at all: the US/international ratio has to be chosen and approximated, it will drift over time as the two funds perform differently, and any rebalancing is an imperfect manual correction of something a single fund would handle automatically and exactly. A true single-fund ACWI equivalent maintains its internal balance by construction — no ratio to decide, no drift to manage.

**Contributions:** $20/week to begin — $13 to VOO and $7 to VEU. This was later increased to $30/week and then again to $40/week, the latter increase driven by a period of low expenses that allowed more focus on building investment principal. The starting split was also later restructured as the strategy evolved.

**The ACWI watch item:** A permanent watch item was established: if a low-cost single-fund ACWI equivalent ever emerged (expense ratio being the only barrier), it would replace VOO + VEU entirely and simplify the account to a single holding.

-----

## Chapter 2: The Idea of Opportunistic DCA — The SPAXX Pool

A new dimension was introduced: rather than a passive DCA into a fixed allocation, the account could be made more dynamic. The observation was that all other accounts (401k, Roth IRA, HSA) either maxed contributions at the start of the year or DCA’d rigidly, with no sensitivity to market conditions. The CMA, as a flexible taxable account with a liquid SPAXX component, was the natural home for a more tactical approach.

**The core idea:** The weekly contribution to the account is unconditional — it goes in no matter what. But rather than all of it going to investments, some portion could be redirected to build a SPAXX pool over time. The pool would then be deployed opportunistically when markets fall, allowing a genuine buy-the-dip mechanism layered on top of the baseline DCA. The SPAXX pool is not built from some separate source of funds — it is funded by redirecting a portion of those same weekly contributions.

**Tom Nash:** Tom Nash (a YouTube investor) and his DCA double-down method were cited as an inspiration among others. His approach was to double contributions when a stock fell 10% below its 52-week high. The account-level adaptation of this idea was identified as a more systematic and emotionally disciplined version — using a rules-based system rather than judgment calls on individual positions.

**Two levers identified:** The discussion surfaced two independent levers: (1) how to split the weekly contribution between investments and SPAXX, and (2) when and how to move existing holdings between investments and SPAXX. Profit-taking and SPAXX deployment were recognized as two sides of the same mechanism — bidirectional transfers between VOO and SPAXX, not separate decisions. A potential lever over the VOO/VEU ratio was also discussed and then subsumed as a sub-decision within lever one.

-----

## Chapter 3: Building the Signal Framework — What Should Drive the Decisions?

The timing idea required signals to drive when contributions lean toward SPAXX vs. investments. The design constraint throughout was simplicity — periodic nudges, not active weekly management.

**Signals explored:**

**Tom Nash’s 52-week high method:** His trigger of 10% below the 52-week high was noted as a candidate but identified as price-based (technical) rather than valuation-based, better as a secondary signal than a primary one. It was filed for later.

**CAPE (Shiller P/E):** The Cyclically Adjusted Price-to-Earnings ratio was introduced as the primary valuation signal. It measures price relative to 10 years of smoothed, inflation-adjusted earnings, producing a slow-moving indicator of whether markets are cheap or expensive historically. Key properties: strong predictive power over 10+ year horizons; essentially useless for short-term timing; reading at the time (~37–38) was near all-time highs. Supporting literature cited included Research Affiliates work and academic studies on CAPE-based allocation.

**CAPE API:** A free GitHub-hosted Shiller data wrapper was initially identified. This was later found to have stale data and was replaced by scraping multpl.com directly for current CAPE.

**PEG / Buffett Indicator detour:** A question arose about whether CAPE was intellectually complete — it measures valuation against earnings history but ignores growth. At the individual stock level, PEG (P/E divided by growth rate) corrects for this. The Buffett Indicator (total market cap / GDP) was identified as the closest market-level analog. Investigation found that the Buffett Indicator is actually more like a Price/Sales ratio at the market level — it captures economic scale but doesn’t incorporate earnings efficiency. It was rejected as largely redundant with CAPE — both ask the same underlying question about market expensiveness — and adding complexity without independent information.

**Research Affiliates AAI — the growth question:** Because CAPE ignores growth and it felt intellectually dishonest to pretend growth doesn’t matter for long-term expected returns, a substantial deep dive was made into the Research Affiliates Asset Allocation Interactive tool (AAI). Key findings:

- The valuation-dependent model in AAI is mathematically derived from 1/CAPE — the same signal, just expressed as an expected annual return percentage.
- The yield-and-growth model adds dividend yield (1.2%) and real EPS growth (2.9%) on top.
- At CAPE ~38, the valuation-dependent model shows ~0.7% real / 3.1% nominal expected return for US Large — effectively expected to underperform cash over 10 years.
- The yield-and-growth model shows ~4.1% real / 6.5% nominal — the difference being the 2.9% EPS growth assumption, which is elevated vs. the long-run historical norm of ~1.5%, driven by the exceptional earnings growth of the tech-heavy 2010s.
- Attempts to find a historical archive of the tool’s outputs found only scattered data points, not a usable series for calibrating thresholds.

**The key insight that unlocked CAPE as the sole signal:** Three observations together allowed setting the growth concern aside and settling on CAPE alone:

1. **Growth estimates are structurally stable.** Long-term market EPS growth assumptions don’t shift meaningfully from month to month. Including them in the signal wouldn’t change the output at the frequency this system checks. This alone is the primary reason to set the growth component aside.
1. **US earnings growth advantage is a real factor** — and one that would normally argue for a growth-adjusted metric, since accepting above-average US earnings growth without accounting for it could look like double-counting.
1. **International dividend yields are higher** — which would similarly argue for adjustment, since ignoring the yield advantage of international stocks understates their return potential.

However, points 2 and 3 together are what resolves the tension: US has something going for it (earnings growth), international has something different going for it (dividend yield), and the two broadly offset each other in the blended portfolio context. What remains after that cancellation is price — and price movement over time is exactly what CAPE captures. Nothing meaningful is lost by using CAPE alone.

**Moving average (50/200 day):** The MA spread on the investment holdings was introduced as a second, complementary signal. It measures momentum and trend rather than valuation. The pairing was recognized as powerful precisely because they measure different things: CAPE answers “do I want to buy?”, the MA spread answers “is now a reasonable moment to act on that?”. Three zones were adopted: bearish (well below), neutral (near the crossover), bullish (well above).

**International CAPE — the unresolved problem:** The original plan was to use a blended CAPE signal weighted in proportion to the contribution ratio between VOO and VEU. Investigation found that international CAPE (MSCI EAFE) is not cleanly available via any free API: paywalled at Siblis Research, no retail API from MSCI, trailing P/E on EFA via yfinance is a different metric (not cyclically adjusted), and Star Capital’s historical data is inconsistently available. The structural difference also mattered — EAFE CAPE historically averages 14–17 vs. US average of ~17, with a narrower historical range, making the same zone thresholds inappropriate for both. This problem was marked as unresolved.

-----

## Chapter 4: The VEU Problem and Account Architecture Pivot

The international CAPE problem was the catalyst for a much larger restructuring.

**How the VEU problem evolved:** The original design was one coherent strategy — a blended CAPE signal driving the blended investment allocation (VOO + VEU as a single bucket). When the blended CAPE proved unworkable, the idea of separating VEU as a passive, fixed-contribution component was raised — essentially running VEU on autopilot while managing VOO + SPAXX actively. This seemed workable mechanically, but once articulated, a deeper strategic dissonance was felt: the CMA was now running two fundamentally different strategies in one account for one purpose. A passive international DCA and an active US market timing system share no common logic and don’t belong together.

**The options considered:**

1. **Keep as-is** — passive VEU alongside active VOO/SPAXX in the same account for the same big-purchase purpose. Technically functional but strategically incoherent.
1. **Open a second account for VEU with the same big-purchase purpose** — physically separates the two strategies but since both accounts would serve the same goal, the purpose duplication remains. Cleaner mechanically but not conceptually.
1. **Open a second account for VEU with a brand-new purpose** — would cleanly separate strategies, but no compelling new purpose could be identified.
1. **Carve out a new account that takes one of the two existing goals from Brokerage 1** — the taxable brokerage account was serving two retirement goals simultaneously (tax flexibility bucket and early retirement income bridge). Splitting these into two dedicated accounts would be architecturally cleaner and would give VEU a natural home in the second account.

**Account inventory — triggered by exploring option 4:** Pursuing option 4 required auditing what accounts existed and what goals needed to be served. An empty Fidelity Individual brokerage account was identified as available for repurposing. The taxable all-weather brokerage served two retirement goals. A different account *type* (CMA vs. brokerage vs. other Fidelity offerings) was explored but found to be a dead end — a second taxable brokerage was the only sensible structure.

**3 goals, 2 accounts → 3 goals, 3 accounts:** With the second brokerage available, the architecture question became how three goals (perpetual retirement supplement, temporary income bridge, big purchases) map to three accounts with three strategies (all-weather, buy-and-hold global, S&P timing).

After working through the pros and cons of every possible mapping across accounts, goals, and strategies (including explicitly ruling out all-weather for the CMA), the following architecture was locked in:

|Account    |Goal                                                               |Strategy                     |
|-----------|-------------------------------------------------------------------|-----------------------------|
|Brokerage 1|Perpetual retirement supplement — never depleted                   |All Weather drift correction |
|Brokerage 2|Temporary income replacement — fully depleted by 59½               |Buy-and-hold diversified     |
|CMA        |Big purchases / flexible capital — cyclically deployed and refilled|S&P 500 market timing + SPAXX|

**VEU’s resolution:** With Brokerage 2 established as a dedicated buy-and-hold account, VEU found its natural home there. And with a clear long-term purpose and dedicated account, the strategy was expanded from a single-fund concept into a three-fund portfolio: QQQM (growth), SCHD (dividend income), and VEU (international exposure) — equal thirds at $100/month each, no rebalancing.

**CMA now fully defined:** With VEU moved out, the CMA became purely VOO + SPAXX. The full weekly contribution is managed between the two. No VEU position, not even a dormant one.

**Notes on Brokerage 2 and the Rule of 55:** The income bridge account has a sharp cliff: if retirement happens at exactly 55, the Rule of 55 allows immediate penalty-free 401k access and Brokerage 2 is barely needed. But if retirement happens before 55, the account must cover the gap to 55 and then the further gap to 59½, potentially requiring hundreds of thousands of dollars. This creates a significant discontinuity in how much the account needs to grow.

-----

## Chapter 5: The VOO/SPAXX System — Cash Pool Design and the First Decision Matrix

With the CMA cleanly a two-asset account, the conversation returned fully to building the timing mechanism. The two signals selected were CAPE (as a valuation signal determining the target cash pool size) and the 50/200 MA spread on VOO (as a directional momentum signal).

**The invisible SPAXX floor:** A permanent $50 floor was established in SPAXX as a convenience buffer for the account’s cash management function (debit card use). This $50 is invisible to all strategy calculations:

- Deployable SPAXX = total SPAXX − $50
- Active portfolio = VOO value + deployable SPAXX

**CAPE as the target-setter:** Rather than using CAPE directly as a contribution signal, CAPE was given a structural role: it determines how large the SPAXX pool should be as a percentage of the active portfolio. This is a cleaner framing — CAPE doesn’t tell you what to do this month, it tells you what equilibrium state you’re trying to maintain. The monthly decision is then about how to get to or maintain that equilibrium.

**CAPE zone table:**

|CAPE    |Zone     |Target Pool|Acceptable Range|
|--------|---------|-----------|----------------|
|Below 20|Steal    |0%         |0%              |
|20–24   |Cheap    |0%         |0–5%            |
|25–29   |Fair     |10%        |5–15%           |
|30–34   |Elevated |20%        |15–25%          |
|35–39   |Expensive|30%        |25–35%          |
|40+     |Extreme  |40%        |35–45%          |

The 5% tolerance band on each side smooths zone transitions and means crossing a CAPE boundary doesn’t force an immediate hard rebalance.

**Funding state:** The comparison of current pool vs. zone target produces three states: underfunded (below zone floor), funded (within acceptable range), overfunded (above zone ceiling).

**The MA spread as the second signal:** The 50-day / 200-day MA spread on VOO was confirmed as the second dimension. Three zones: bearish (spread < −5%), neutral (between −5% and +2%), bullish (spread > +2%). The asymmetric thresholds reflect a deliberate design choice: a lower bar to call bullish (+2%) because the system wants to deploy on recoveries promptly, and a higher bar to call bearish (−5%) to avoid reacting to short-term noise.

**The 2D decision matrix (first complete version):** Before the 52-week signal was introduced, the first complete decision matrix used funding state and MA trend. A key structural property emerged in its diagonal shape: cells along the same diagonal from top-left to bottom-right share the same action, creating five distinct aggressiveness bands — very aggressive, somewhat aggressive, neutral, somewhat defensive, and very defensive. The most extreme actions — deploying SPAXX into VOO, or selling VOO into SPAXX — are reserved for the corner cells where both signals agree maximally. The bulk of scenarios produce contribution-only adjustments, leaving the existing balance untouched.

|               |Bearish            |Neutral           |Bullish                    |
|---------------|-------------------|------------------|---------------------------|
|**Underfunded**|All to SPAXX + sell|All to SPAXX      |Maintain split             |
|**Funded**     |All to SPAXX       |Maintain split    |All to investments         |
|**Overfunded** |Maintain split     |All to investments|All to investments + deploy|

**“Maintain split” defined dynamically:** Not a fixed ratio. X% to SPAXX and (100−X)% to VOO, where X equals the current CAPE zone’s target percentage. Self-calibrates automatically as CAPE moves across zones.

**Balance action amounts:** For corner cells requiring a balance trade, 5% of the total active portfolio value per month was established as the default — meaning 5% of VOO + deployable SPAXX combined, not 5% of whichever holding is being moved. A “deploy a lot” level of 10% of active portfolio was later added for the most aggressive scenarios. The sizing was intentional: the acceptable band is 10% wide (5% on each side of the target), so a 10% move can never push you from one edge of the acceptable range past the other in a single action. Importantly, the 5% or 10% move is not designed to fully close a large funding gap in one step — if the gap remains after the move, the next monthly check will call for another action. The system accepts incremental progress.

-----

## Chapter 6: The Third Signal — 52-Week High/Low

Tom Nash’s 52-week method had been mentioned early in the conversation as an inspiration. Now it was incorporated as a third signal, added on top of the 2D matrix.

**The critical reframe — distance, not proximity:** The signal was carefully redefined: it is not a proximity signal (“you are near the bottom”). It is a distance signal (“you are far enough from the top that buying makes sense”). The buy flag fires when price has fallen meaningfully from its peak. The sell flag fires when price has risen meaningfully from its trough.

- **Buy flag:** price is more than 10% below the 52-week high
- **Sell flag:** price is more than 25% above the 52-week low

The 10% vs. 25% asymmetry is intentional: a lower bar for the buy signal because the system is structurally more eager to deploy than to exit.

**Two binary checks, not one:** The signal was refined into two independent checks. All four combinations are possible and each has distinct meaning:

- Buy flag only: fallen meaningfully from peak, not far above trough — clearest buy signal
- Sell flag only: well above trough, still near peak — clearest caution/sell signal
- Neither flag: price near the high and not far above the low — no strong signal
- Both flags: large 52-week range, price somewhere in the middle — the market had a big run but pulled back somewhat; ambiguous

For scoring, both and neither map to neutral (0), collapsing to three effective states: buy modifier (+1), neutral (0), sell modifier (−1).

**Expanding to 27 scenarios:** With three signals (funding state × MA trend × 52-week flag, each with three states), the full decision space is 3 × 3 × 3 = 27 scenarios. These 27 scenarios need to be mapped to actions. The question of how to do that mapping systematically and consistently was the major design challenge of the chapters that follow.

-----

## Chapter 7: Design Criteria and First Attempts

### Design Criteria — The North Star and Desired Properties

Before building any framework, principles were established to evaluate candidate systems against.

**The North Star:** As signals get more favorable, actions should get more aggressive. As signals get less favorable, actions should become more defensive. Any framework that violated this — however elegant — was considered flawed.

**Formal properties established:**

**1. Monotonicity of aggregate aggressiveness.** The 27 scenarios sit on the vertices of a 3D cube in signal space. There are 27 axis-parallel lines through this cube (9 per axis, labeled F1–F9 for the funding axis, T1–T9 for the trend axis, and W1–W9 for the 52-week axis). Along any such line — holding two signals constant while varying the third — the aggregate aggressiveness of the combined action should always strictly increase as the signal moves in the positive direction.

Two separate standards were applied: one for the aggregate score, and a softer one for individual dials.

**Aggregate score standard (primary):**

- Strictly increases at every step: full pass
- Stays flat at a step: partial failure — not catastrophic but noted as a flaw
- Goes down at a step: critical failure

**Individual dial standard (secondary, aspirational):**
It is desirable that neither dial ever reverses direction, but a dial decreasing is acceptable as long as the aggregate still strictly increases. The distinction between a dial staying flat vs. reversing is meaningful but not disqualifying on its own — what matters is whether the aggregate is preserved.

**What can be determined by inspection alone** (before any coordinate weighting is applied):

Scenarios that are *guaranteed to pass both standards*, regardless of weighting:

- Both dials increase at every step
- One dial increases at every step while the other stays flat (never decreases)
- One dial jumps at one step while the other jumps at a different step, with neither dial decreasing at any step

Scenarios that are *guaranteed to fail*, regardless of weighting:

- Both dials stay flat at a step → partial aggregate failure (aggregate stays flat, not strictly increasing)
- One dial decreases at a step while the other dial doesn’t increase → critical aggregate failure (aggregate goes down), and fails the dial standard too

Scenarios that are *ambiguous* — outcome depends on how the dials are scored and weighted:

- One dial increases while the other decreases at the same step: fails the dial standard (one dial reversed), but the aggregate may still strictly increase depending on the relative weights assigned to each dial action. Cannot be evaluated by inspection alone.

**2. Non-contradicting dials.** The two action dials (contributions and balance) should never point in opposite directions in the same cell — e.g., directing 100% of contributions to SPAXX while simultaneously deploying SPAXX into VOO would be self-defeating.

**3. CAPE primacy.** The funding state (derived from CAPE) should be the most important signal. Two non-CAPE signals should not be able to fully override the CAPE signal and call for a balance trade that CAPE says shouldn’t happen.

**4. Matching intuition.** The generated actions should feel instinctively correct when examined scenario by scenario. A full intuition exercise — working through all 27 scenarios independently to record instinctive actions — would be carried out later in the conversation, after the first frameworks were built, and used as a benchmark for comparison.

-----

### Framework 1: The Double 3×3

**The proposal:** Rather than one 27-cell matrix, use two independent 3×3 matrices — one per non-CAPE signal — each anchored by funding state. One signal controls the contributions dial; the other controls the balance dial.

**Assignment of signals to dials:** Trend → contributions was chosen. The logic: trend is a continuous ongoing signal that maps naturally to the continuous ongoing action of weekly contributions; the 52-week flag is an event-like signal (price crossed a threshold) that maps naturally to the event-like action of a one-time balance trade.

**Structure of each grid:** Each grid was deliberately designed to mirror the geometric structure of the 2D decision matrix from Chapter 5 — with the most extreme actions in the corners and the neutral state in the middle, producing the same five diagonal aggressiveness bands: very aggressive, somewhat aggressive, neutral, somewhat defensive, and very defensive. Because each grid uses only *one* dial to express its full range of aggressiveness, that single dial needs five distinct actions to cover all five bands. This forced the introduction of finer gradations that wouldn’t naturally emerge from intuition — in the contributions grid, a “50/50 split” to fill the intermediate level between maintain split and 100% SPAXX, and a “half-SPAXX split” (half the CAPE target percentage to SPAXX, the rest to VOO) to fill the intermediate level between maintain split and 100% VOO; in the balance grid, a smaller “2% VOO→SPAXX” action between doing nothing and the full 5% sell, and a larger “10% SPAXX→VOO” action above the 5% deploy.

**The two grids:**

Contributions (Funding × MA Trend):

|               |Bearish       |Neutral         |Bullish         |
|---------------|--------------|----------------|----------------|
|**Underfunded**|100% SPAXX    |50/50           |Maintain split  |
|**Funded**     |50/50         |Maintain split  |Half-SPAXX split|
|**Overfunded** |Maintain split|Half-SPAXX split|100% VOO        |

Balance (Funding × 52-Week Flag):

|               |Sell        |Neutral     |Buy          |
|---------------|------------|------------|-------------|
|**Underfunded**|5% VOO→SPAXX|2% VOO→SPAXX|Do nothing   |
|**Funded**     |2% VOO→SPAXX|Do nothing  |5% SPAXX→VOO |
|**Overfunded** |Do nothing  |5% SPAXX→VOO|10% SPAXX→VOO|

Note that both grids share the funding state dimension, so knowing your funding state constrains the cells in both grids simultaneously. The 27 outcomes are uniquely determined.

**All 27 combined actions:**

|# |Scenario                   |Contributions   |Balance      |
|--|---------------------------|----------------|-------------|
|1 |Underfunded/Bearish/Sell   |100% SPAXX      |5% VOO→SPAXX |
|2 |Underfunded/Bearish/Neutral|100% SPAXX      |2% VOO→SPAXX |
|3 |Underfunded/Bearish/Buy    |100% SPAXX      |Do nothing   |
|4 |Underfunded/Neutral/Sell   |50/50           |5% VOO→SPAXX |
|5 |Underfunded/Neutral/Neutral|50/50           |2% VOO→SPAXX |
|6 |Underfunded/Neutral/Buy    |50/50           |Do nothing   |
|7 |Underfunded/Bullish/Sell   |Maintain split  |5% VOO→SPAXX |
|8 |Underfunded/Bullish/Neutral|Maintain split  |2% VOO→SPAXX |
|9 |Underfunded/Bullish/Buy    |Maintain split  |Do nothing   |
|10|Funded/Bearish/Sell        |50/50           |2% VOO→SPAXX |
|11|Funded/Bearish/Neutral     |50/50           |Do nothing   |
|12|Funded/Bearish/Buy         |50/50           |5% SPAXX→VOO |
|13|Funded/Neutral/Sell        |Maintain split  |2% VOO→SPAXX |
|14|Funded/Neutral/Neutral     |Maintain split  |Do nothing   |
|15|Funded/Neutral/Buy         |Maintain split  |5% SPAXX→VOO |
|16|Funded/Bullish/Sell        |Half-SPAXX split|2% VOO→SPAXX |
|17|Funded/Bullish/Neutral     |Half-SPAXX split|Do nothing   |
|18|Funded/Bullish/Buy         |Half-SPAXX split|5% SPAXX→VOO |
|19|Overfunded/Bearish/Sell    |Maintain split  |Do nothing   |
|20|Overfunded/Bearish/Neutral |Maintain split  |5% SPAXX→VOO |
|21|Overfunded/Bearish/Buy     |Maintain split  |10% SPAXX→VOO|
|22|Overfunded/Neutral/Sell    |Half-SPAXX split|Do nothing   |
|23|Overfunded/Neutral/Neutral |Half-SPAXX split|5% SPAXX→VOO |
|24|Overfunded/Neutral/Buy     |Half-SPAXX split|10% SPAXX→VOO|
|25|Overfunded/Bullish/Sell    |100% VOO        |Do nothing   |
|26|Overfunded/Bullish/Neutral |100% VOO        |5% SPAXX→VOO |
|27|Overfunded/Bullish/Buy     |100% VOO        |10% SPAXX→VOO|

**Assessment of the double 3×3:**

- **CAPE primacy:** Preserved by design — funding state anchors both grids, making it co-present in every decision.
- **Dial monotonicity:** Each grid is monotonic along each axis by construction.
- **Aggregate monotonicity:** Passes all 27 axis-parallel lines — W and T lines are clean by grid construction; F lines pass because both dials move monotonically together.
- **Non-contradicting dials:** **Fails.** Since the two grids are fully independent, combinations like “100% SPAXX contributions + deploy 5% SPAXX into VOO” or “100% VOO contributions + sell VOO into SPAXX” are possible and appear in the table.
- **Matching intuition:** Partially — has 18 distinct combined actions across 27 scenarios, which feels excessive. The inflated count is partly a consequence of the framework’s structure: actions like half-SPAXX split were introduced to fill the five-band requirement of each grid, but they don’t appear in intuition at all and feel like artifacts of the framework rather than naturally correct choices.

-----

### Framework 2: The First Cube

**The proposal:** Assign each signal a score of −1, 0, or +1. Sum the three scores to get an aggregate from −3 to +3 (7 levels). Map each aggregate level to one combined action.

- Underfunded = −1, Funded = 0, Overfunded = +1
- Bearish = −1, Neutral = 0, Bullish = +1
- Sell = −1, Neutral = 0, Buy = +1

**The geometric elegance:** The 27 scenarios are points in a 3D cube, hung by its diagonal — oriented so the main diagonal runs vertically, with the (−1,−1,−1) corner at the bottom and the (+1,+1,+1) corner at the top. The 7 distinct aggregate score levels then correspond to 7 horizontal planes slicing through the cube at each score level, the most defensive plane at the bottom and the most aggressive at the top. This is the natural 3D expansion of the 5 diagonal lines from the 2D matrix in Chapter 5 — the same geometric principle extended to an additional dimension, producing 7 planes where the 2D version had 5 diagonal bands. The North Star property is satisfied by construction: the scoring rule guarantees aggregate monotonicity on all 27 axis-parallel lines. The distribution is also elegant — 1 scenario at each extreme, 3 at ±2, 6 at ±1, and 7 at neutral 0.

**The action table for the first cube:** The action pattern was designed around a key principle: a balance trade (moving a percentage of the full portfolio between VOO and SPAXX) was assumed to carry more weight than a contribution adjustment (redirecting weekly inflows). With that assumption, the ±2 level was designed to activate the heavier dial (balance trade) while dialing back the lighter dial (contributions) to maintain split — a form of internal offset. The system ramps up its more impactful action at ±2 while moderating its ongoing behavior. At the most extreme ±3, both dials are combined for maximum impact in the same direction.

|Score|Contributions |Balance            |
|-----|--------------|-------------------|
|+3   |100% VOO      |Deploy 5% SPAXX→VOO|
|+2   |Maintain split|Deploy 5% SPAXX→VOO|
|+1   |100% VOO      |Do nothing         |
|0    |Maintain split|Do nothing         |
|−1   |100% SPAXX    |Do nothing         |
|−2   |Maintain split|Sell 5% VOO→SPAXX  |
|−3   |100% SPAXX    |Sell 5% VOO→SPAXX  |

**All 27 combined actions (first cube):**

|# |Scenario                   |Score|Contributions |Balance            |
|--|---------------------------|-----|--------------|-------------------|
|1 |Underfunded/Bearish/Sell   |−3   |100% SPAXX    |Sell 5% VOO→SPAXX  |
|2 |Underfunded/Bearish/Neutral|−2   |Maintain split|Sell 5% VOO→SPAXX  |
|3 |Underfunded/Bearish/Buy    |−1   |100% SPAXX    |Do nothing         |
|4 |Underfunded/Neutral/Sell   |−2   |Maintain split|Sell 5% VOO→SPAXX  |
|5 |Underfunded/Neutral/Neutral|−1   |100% SPAXX    |Do nothing         |
|6 |Underfunded/Neutral/Buy    |0    |Maintain split|Do nothing         |
|7 |Underfunded/Bullish/Sell   |−1   |100% SPAXX    |Do nothing         |
|8 |Underfunded/Bullish/Neutral|0    |Maintain split|Do nothing         |
|9 |Underfunded/Bullish/Buy    |+1   |100% VOO      |Do nothing         |
|10|Funded/Bearish/Sell        |−2   |Maintain split|Sell 5% VOO→SPAXX  |
|11|Funded/Bearish/Neutral     |−1   |100% SPAXX    |Do nothing         |
|12|Funded/Bearish/Buy         |0    |Maintain split|Do nothing         |
|13|Funded/Neutral/Sell        |−1   |100% SPAXX    |Do nothing         |
|14|Funded/Neutral/Neutral     |0    |Maintain split|Do nothing         |
|15|Funded/Neutral/Buy         |+1   |100% VOO      |Do nothing         |
|16|Funded/Bullish/Sell        |0    |Maintain split|Do nothing         |
|17|Funded/Bullish/Neutral     |+1   |100% VOO      |Do nothing         |
|18|Funded/Bullish/Buy         |+2   |Maintain split|Deploy 5% SPAXX→VOO|
|19|Overfunded/Bearish/Sell    |−1   |100% SPAXX    |Do nothing         |
|20|Overfunded/Bearish/Neutral |0    |Maintain split|Do nothing         |
|21|Overfunded/Bearish/Buy     |+1   |100% VOO      |Do nothing         |
|22|Overfunded/Neutral/Sell    |0    |Maintain split|Do nothing         |
|23|Overfunded/Neutral/Neutral |+1   |100% VOO      |Do nothing         |
|24|Overfunded/Neutral/Buy     |+2   |Maintain split|Deploy 5% SPAXX→VOO|
|25|Overfunded/Bullish/Sell    |+1   |100% VOO      |Do nothing         |
|26|Overfunded/Bullish/Neutral |+2   |Maintain split|Deploy 5% SPAXX→VOO|
|27|Overfunded/Bullish/Buy     |+3   |100% VOO      |Deploy 5% SPAXX→VOO|

**Assessment of the first cube:**

- **CAPE primacy:** **Fails.** All three signals are equally weighted. Underfunded (−1) + Bullish (+1) + Buy (+1) = +1, which calls for 100% VOO contributions — directing new money fully into investments even though CAPE says the pool is short.
- **Non-contradicting dials:** **Passes** by design — no cell combines contributions and balance in opposite directions.
- **Aggregate monotonicity:** **Passes** on all 27 lines by construction of the scoring rule.
- **Individual dial monotonicity:** **Fails on some W lines** — because the action swaps between dials at intermediate levels, some individual dials are non-monotonic on certain lines (though the aggregate never decreases).
- **Matching intuition:** Partially aligned on contributions; less so on balance actions.

These two frameworks were both initial attempts, and neither was a strict upgrade over the other. The double 3×3 preserved CAPE primacy and achieved dial monotonicity by construction, but suffered from contradicting dials and an inflated action vocabulary full of framework artifacts. The first cube achieved geometric elegance and eliminated contradicting dials, but only had aggregate monotonicity without dial monotonicity, and introduced the CAPE primacy failure the double 3×3 avoided. Neither framework fully satisfied the design criteria, and both were carried forward as reference points for the next phase.

-----

## Chapter 8: Intuition and Advanced Attempts

### The Intuition Exercise

After generating both the double 3×3 and the first cube, all 27 scenarios were worked through independently — without consulting any framework — to record the instinctive action for each. The purpose was not to commit to anything but to create a reference point for evaluating where the models diverged from instinct, and to surface what action vocabulary naturally emerged.

|# |Scenario                   |Contributions |Balance    |
|--|---------------------------|--------------|-----------|
|1 |Underfunded/Bearish/Sell   |100% SPAXX    |Max sell   |
|2 |Underfunded/Bearish/Neutral|100% SPAXX    |Do nothing |
|3 |Underfunded/Bearish/Buy    |Maintain split|Do nothing |
|4 |Underfunded/Neutral/Sell   |100% SPAXX    |Sell little|
|5 |Underfunded/Neutral/Neutral|50/50         |Do nothing |
|6 |Underfunded/Neutral/Buy    |Maintain split|Do nothing |
|7 |Underfunded/Bullish/Sell   |Maintain split|Sell little|
|8 |Underfunded/Bullish/Neutral|Maintain split|Do nothing |
|9 |Underfunded/Bullish/Buy    |100% VOO      |Do nothing |
|10|Funded/Bearish/Sell        |50/50         |Sell little|
|11|Funded/Bearish/Neutral     |50/50         |Do nothing |
|12|Funded/Bearish/Buy         |Maintain split|Do nothing |
|13|Funded/Neutral/Sell        |50/50         |Do nothing |
|14|Funded/Neutral/Neutral     |Maintain split|Do nothing |
|15|Funded/Neutral/Buy         |100% VOO      |Do nothing |
|16|Funded/Bullish/Sell        |Maintain split|Do nothing |
|17|Funded/Bullish/Neutral     |100% VOO      |Do nothing |
|18|Funded/Bullish/Buy         |100% VOO      |Buy little |
|19|Overfunded/Bearish/Sell    |Maintain split|Do nothing |
|20|Overfunded/Bearish/Neutral |100% VOO      |Do nothing |
|21|Overfunded/Bearish/Buy     |100% VOO      |Buy little |
|22|Overfunded/Neutral/Sell    |100% VOO      |Do nothing |
|23|Overfunded/Neutral/Neutral |100% VOO      |Do nothing |
|24|Overfunded/Neutral/Buy     |100% VOO      |Buy little |
|25|Overfunded/Bullish/Sell    |100% VOO      |Do nothing |
|26|Overfunded/Bullish/Neutral |100% VOO      |Buy little |
|27|Overfunded/Bullish/Buy     |100% VOO      |Buy max    |

**Monotonicity of the intuition table:** All 27 axis-parallel lines were tested. The table passes the individual-dial no-reversal test — on every line, neither dial ever moves backward. However, it does not pass the strict aggregate increase criterion. Scenarios 22 (Overfunded/Neutral/Sell) and 23 (Overfunded/Neutral/Neutral) produce identical actions (“100% VOO + do nothing”), creating a flat aggregate step on line W8 regardless of any coordinate weighting. The same flat step appears on line T7, where scenarios 22 and 25 are also identical. These are clear violations of the strict increase standard — two different signal states producing the exact same action means the aggregate cannot be said to have increased. The intuition table was nonetheless valuable as a reference point for vocabulary and overall direction, even though it didn’t fully satisfy the formal monotonicity criterion.

The intuition table also naturally satisfies the non-contradicting dials property — no cell simultaneously pulls contributions in one direction while moving the balance in the other. This emerged without any deliberate effort, suggesting it reflects a genuine logical constraint rather than an artificial rule.

**What the intuition revealed about action vocabulary:** Looking across all 27 picks, the intuition never used the “Half-SPAXX split” contribution level that appeared in the double 3×3. The naturally used action space was:

- Contributions: 100% SPAXX / 50/50 / Maintain split / 100% VOO (4 levels)
- Balance: Max sell / Sell little / Do nothing / Buy little / Buy max (5 levels)

Setting aside the “max sell” (which would later be eliminated as too defensive an action for the balance dial), the balance vocabulary becomes: Sell little / Do nothing / Buy little / Buy max — 4 levels, asymmetric on the sell side.

-----

### Framework 3: The New Cube

**The approach:** The new cube kept the same geometric scoring structure as the original — signals ±1 each, scores −3 to +3, 7 action levels — but replaced the action table with one derived from the intuition vocabulary. The same signal scoring applied:

- Underfunded = −1, Funded = 0, Overfunded = +1
- Bearish = −1, Neutral = 0, Bullish = +1
- Sell = −1, Neutral = 0, Buy = +1

**Building the action space:** The dial options from the intuition exercise were formally scored by coordinate:

- Contributions: 100% SPAXX = −2, 50/50 = −1, Maintain split = 0, 100% VOO = +1
- Balance: Sell little = −1, Do nothing = 0, Buy little = +1, Buy a lot = +2

The full 4×4 grid has 16 possible combined actions. The 7 that were eliminated because they represent contradicting dials (contributions and balance pointing in opposite directions):

|Eliminated combination             |Why                                           |
|-----------------------------------|----------------------------------------------|
|100% SPAXX + buy little (−2, +1)   |Contributions defensive, balance aggressive   |
|100% SPAXX + buy a lot (−2, +2)    |Contributions defensive, balance aggressive   |
|50/50 + buy little (−1, +1)        |Contributions defensive, balance aggressive   |
|50/50 + buy a lot (−1, +2)         |Contributions defensive, balance aggressive   |
|Maintain split + buy little (0, +1)|Balance aggressive while contributions neutral|
|Maintain split + buy a lot (0, +2) |Balance aggressive while contributions neutral|
|100% VOO + sell little (+1, −1)    |Contributions aggressive, balance defensive   |

The 9 viable combinations that remain, with their coordinate totals:

|Action                      |Coordinates|Total|
|----------------------------|-----------|-----|
|100% SPAXX + sell little    |(−2, −1)   |−3   |
|100% SPAXX + do nothing     |(−2, 0)    |−2   |
|50/50 + sell little         |(−1, −1)   |−2   |
|50/50 + do nothing          |(−1, 0)    |−1   |
|Maintain split + sell little|(0, −1)    |−1   |
|Maintain split + do nothing |(0, 0)     |0    |
|100% VOO + do nothing       |(+1, 0)    |+1   |
|100% VOO + buy little       |(+1, +1)   |+2   |
|100% VOO + buy a lot        |(+1, +2)   |+3   |

Notably, these 9 viable actions account for 9 of the 10 actions that appeared in the intuition table — the only missing one being “max sell,” which was set aside as too defensive for the balance dial. This near-perfect alignment between the elimination process and the intuition vocabulary was a strong signal that the action space was correctly derived.

Two coordinate total values (−2 and −1) each have two valid options. The new cube resolves this by selecting one action per score level:

|Score|Action                     |
|-----|---------------------------|
|−3   |100% SPAXX + sell little   |
|−2   |100% SPAXX + do nothing    |
|−1   |50/50 + do nothing         |
|0    |Maintain split + do nothing|
|+1   |100% VOO + do nothing      |
|+2   |100% VOO + buy little      |
|+3   |100% VOO + buy a lot       |

*(The other viable options at −2 and −1 — “50/50 + sell little” and “Maintain split + sell little” — were set aside at this stage and would resurface in the rectangular prism as the flag-based override rules.)*

**All 27 combined actions (new cube):**

|# |Scenario                   |Score|Action                     |
|--|---------------------------|-----|---------------------------|
|1 |Underfunded/Bearish/Sell   |−3   |100% SPAXX + sell little   |
|2 |Underfunded/Bearish/Neutral|−2   |100% SPAXX + do nothing    |
|3 |Underfunded/Bearish/Buy    |−1   |50/50 + do nothing         |
|4 |Underfunded/Neutral/Sell   |−2   |100% SPAXX + do nothing    |
|5 |Underfunded/Neutral/Neutral|−1   |50/50 + do nothing         |
|6 |Underfunded/Neutral/Buy    |0    |Maintain split + do nothing|
|7 |Underfunded/Bullish/Sell   |−1   |50/50 + do nothing         |
|8 |Underfunded/Bullish/Neutral|0    |Maintain split + do nothing|
|9 |Underfunded/Bullish/Buy    |+1   |100% VOO + do nothing      |
|10|Funded/Bearish/Sell        |−2   |100% SPAXX + do nothing    |
|11|Funded/Bearish/Neutral     |−1   |50/50 + do nothing         |
|12|Funded/Bearish/Buy         |0    |Maintain split + do nothing|
|13|Funded/Neutral/Sell        |−1   |50/50 + do nothing         |
|14|Funded/Neutral/Neutral     |0    |Maintain split + do nothing|
|15|Funded/Neutral/Buy         |+1   |100% VOO + do nothing      |
|16|Funded/Bullish/Sell        |0    |Maintain split + do nothing|
|17|Funded/Bullish/Neutral     |+1   |100% VOO + do nothing      |
|18|Funded/Bullish/Buy         |+2   |100% VOO + buy little      |
|19|Overfunded/Bearish/Sell    |−1   |50/50 + do nothing         |
|20|Overfunded/Bearish/Neutral |0    |Maintain split + do nothing|
|21|Overfunded/Bearish/Buy     |+1   |100% VOO + do nothing      |
|22|Overfunded/Neutral/Sell    |0    |Maintain split + do nothing|
|23|Overfunded/Neutral/Neutral |+1   |100% VOO + do nothing      |
|24|Overfunded/Neutral/Buy     |+2   |100% VOO + buy little      |
|25|Overfunded/Bullish/Sell    |+1   |100% VOO + do nothing      |
|26|Overfunded/Bullish/Neutral |+2   |100% VOO + buy little      |
|27|Overfunded/Bullish/Buy     |+3   |100% VOO + buy a lot       |

**Assessment of the new cube:**

- **CAPE primacy:** **Fails.** Same equal-weighting structure as the first cube — underfunded can still be overruled by two favorable signals.
- **Non-contradicting dials:** **Passes** — elimination of contradicting combinations guarantees this.
- **Aggregate monotonicity:** **Passes** on all 27 lines by the scoring rule.
- **Individual dial monotonicity:** **Improved** over the first cube but still fails on some W lines.
- **Matching intuition:** Much closer than either previous framework — the action vocabulary was derived directly from the intuition exercise.

The new cube was taken as a clear upgrade over the first cube — better action vocabulary, no contradicting dials, and much closer to intuition. However, CAPE primacy still failed: underfunded could still be overruled by two favorable signals. That unresolved issue set up the final refinement.

-----

### Framework 4: The Rectangular Prism (Final System)

**The CAPE primacy solution:** The rectangular prism is a geometric extension of the cube — hence the name. Where a cube has equal dimensions on all three axes, a rectangular prism stretches one axis relative to the others. Here, the funding state axis is stretched to ±2 while trend and flag remain at ±1. This extends the aggregate score range from −3 to +3 (cube) to −4 to +4 (prism), adding the score levels needed to differentiate the additional weight given to CAPE. Mathematically, two non-CAPE signals at their most favorable (+1 each = +2 total) cannot fully override the most unfavorable funding state (−2). The best they can achieve against underfunded is −2+1+1 = 0, a neutral outcome — not an aggressive one. CAPE primacy is now enforced mathematically, not just implied by structure.

**Signal scoring:**

- Funding: Underfunded = −2, Funded = 0, Overfunded = +2
- MA Trend: Bearish = −1, Neutral = 0, Bullish = +1
- 52-Week Flag: Sell = −1, Neutral = 0, Buy = +1

**The action space:** The same 4-level contribution options and 4-level balance options from the new cube were kept, but rescored to span the wider −4 to +4 range. This also formalized the “sell/deploy a little” and “deploy a lot” vocabulary from the new cube into explicit percentages: a little = 5% of active portfolio, a lot = 10% of active portfolio.

- Contributions: 100% SPAXX = −2, 50/50 = −1, Maintain split = 0, 100% VOO = +2
- Balance: Sell 5% = −2, Do nothing = 0, Deploy 5% = +1, Deploy 10% = +2

With this rescoring, each of the 9 viable non-contradicting combinations maps to a unique aggregate coordinate total spanning −4 to +4:

|Score|Action                     |Coordinates|
|-----|---------------------------|-----------|
|−4   |100% SPAXX + sell 5%       |(−2, −2)   |
|−3   |50/50 + sell 5%            |(−1, −2)   |
|−2   |100% SPAXX + do nothing    |(−2, 0)    |
|−1   |50/50 + do nothing         |(−1, 0)    |
|0    |Maintain split + do nothing|(0, 0)     |
|+1   |100% VOO + do nothing      |(+2, 0)    |
|+2   |Maintain split + deploy 5% |(0, +1)    |
|+3   |100% VOO + deploy 5%       |(+2, +1)   |
|+4   |100% VOO + deploy 10%      |(+2, +2)   |

Two additional viable non-contradicting combinations — “Maintain split + sell 5%” and “50/50 + sell 5%” — don’t fit the standard mapping but are valid actions. These are used as override rules for the two score levels where the 52-week flag provides context that should change the action: when the flag signal is specifically buy or sell (rather than neutral), that direction is more intuitively expressed through the balance dial rather than the contribution dial alone.

- **Score −2 + Sell flag → Maintain split + sell 5%** (instead of 100% SPAXX + do nothing)
- **Score +3 + Buy flag → Maintain split + deploy 10%** (instead of 100% VOO + deploy 5%)

These are not arbitrary exceptions but a third layer of the decision framework.

**All 27 combined actions (rectangular prism):**

|# |Scenario                   |Score|Action                     |
|--|---------------------------|-----|---------------------------|
|1 |Underfunded/Bearish/Sell   |−4   |100% SPAXX + sell 5%       |
|2 |Underfunded/Bearish/Neutral|−3   |50/50 + sell 5%            |
|3 |Underfunded/Bearish/Buy    |−2   |100% SPAXX + do nothing    |
|4 |Underfunded/Neutral/Sell   |−3   |50/50 + sell 5%            |
|5 |Underfunded/Neutral/Neutral|−2   |100% SPAXX + do nothing    |
|6 |Underfunded/Neutral/Buy    |−1   |50/50 + do nothing         |
|7 |Underfunded/Bullish/Sell   |−2*  |Maintain split + sell 5%   |
|8 |Underfunded/Bullish/Neutral|−1   |50/50 + do nothing         |
|9 |Underfunded/Bullish/Buy    |0    |Maintain split + do nothing|
|10|Funded/Bearish/Sell        |−2*  |Maintain split + sell 5%   |
|11|Funded/Bearish/Neutral     |−1   |50/50 + do nothing         |
|12|Funded/Bearish/Buy         |0    |Maintain split + do nothing|
|13|Funded/Neutral/Sell        |−1   |50/50 + do nothing         |
|14|Funded/Neutral/Neutral     |0    |Maintain split + do nothing|
|15|Funded/Neutral/Buy         |+1   |100% VOO + do nothing      |
|16|Funded/Bullish/Sell        |0    |Maintain split + do nothing|
|17|Funded/Bullish/Neutral     |+1   |100% VOO + do nothing      |
|18|Funded/Bullish/Buy         |+2   |Maintain split + deploy 5% |
|19|Overfunded/Bearish/Sell    |0    |Maintain split + do nothing|
|20|Overfunded/Bearish/Neutral |+1   |100% VOO + do nothing      |
|21|Overfunded/Bearish/Buy     |+2   |Maintain split + deploy 5% |
|22|Overfunded/Neutral/Sell    |+1   |100% VOO + do nothing      |
|23|Overfunded/Neutral/Neutral |+2   |Maintain split + deploy 5% |
|24|Overfunded/Neutral/Buy     |+3*  |Maintain split + deploy 10%|
|25|Overfunded/Bullish/Sell    |+2   |Maintain split + deploy 5% |
|26|Overfunded/Bullish/Neutral |+3   |100% VOO + deploy 5%       |
|27|Overfunded/Bullish/Buy     |+4   |100% VOO + deploy 10%      |

*Asterisk denotes score overridden by flag-based rule.*

**Assessment of the rectangular prism:**

- **CAPE primacy:** **Passes** — funding state at ±2 means two non-CAPE signals can neutralize but not override it.
- **Non-contradicting dials:** **Passes** — the elimination of invalid combinations guarantees this.
- **Aggregate monotonicity:** **Passes on all 27 axis-parallel lines** — the weighted scoring rule guarantees this.
- **Individual dial monotonicity:** **Fails on some W lines** — the contribution dial is not strictly monotonic on certain W-axis lines. This is the residual imperfection accepted in exchange for all other properties being satisfied.
- **Matching intuition:** **Closely** — all scenarios align with or are very near the intuition table. The only notable divergence is at −4, where the intuition wanted a “max sell” but the system caps the sell action at 5%.

The rectangular prism was taken as the final accepted solution — the framework that satisfied CAPE primacy, eliminated contradicting dials, guaranteed aggregate monotonicity, and came closest to matching intuition of any approach considered.

-----

## Chapter 9: Tools and Implementation

### The Fidelity Balance Problem

With the system fully designed, the conversation turned to how to actually operate it. Every monthly decision requires three market-data inputs (CAPE, VOO moving averages, VOO 52-week extremes) and two account balance inputs (VOO value, SPAXX balance). Getting all of this together with minimal friction was the implementation challenge.

The first obstacle: Fidelity has no public retail API. A Playwright-based browser automation library (`fidelity-api` on PyPI) exists and can log in programmatically to read account data, but it is fragile, likely to break when Fidelity updates their website, and technically against Fidelity’s terms of service.

A two-way texting flow was also considered: the script texts the user with market signals, the user replies with their two balance figures, and the script computes and texts back the exact action. Both this and the browser automation approach were ultimately set aside for the same core reason: even if the balance retrieval were fully automated, the user would still need to log into Fidelity and manually adjust their contribution split or execute a balance trade. Automating the lookup of two numbers saves a small step but not the time of actually logging in and making the changes — so the complexity of either approach wasn’t worth the limited upside.

The solution adopted was a deliberate architectural separation: market data (CAPE, MAs, 52-week) would be fetched automatically by a scheduled script, while the account balances would be provided by the user through a calculator tool. The script outputs three conditional actions, one for each possible funding state (underfunded / funded / overfunded). The user checks their Fidelity balance, identifies which state they’re in, and picks the corresponding action. The calculator then takes those balance inputs alongside the market signals and produces the complete, precise action including exact dollar amounts.

### The Scenario Code

Since the script outputs market signals and the calculator takes both signals and balances, the two tools needed a common interface. A 3-character scenario code was designed to both encode the three signal states compactly and greatly ease use of the calculator by condensing what would otherwise be three separate signal inputs into a single string:

- Character 1: CAPE zone (S=Steal, C=Cheap, F=Fair, L=Elevated, E=Expensive, X=Extreme)
- Character 2: MA trend (1=Bearish, 5=Neutral, 9=Bullish)
- Character 3: 52-week flag (1=Sell, 5=Neutral, 9=Buy)

With 6 CAPE zones × 3 trend states × 3 flag states, there are 54 possible scenario codes. The script emits one code per run. The user enters it into the calculator alongside their balances, and the calculator handles the rest.

### The Monthly Flow

1. A Python script runs automatically on the first Wednesday of each month during market hours
1. The script texts the user: current CAPE, VOO price and MAs, 52-week data, three conditional actions (underfunded / funded / overfunded), and the Scenario Code
1. The user opens a calculator on their iPhone, enters the Scenario Code plus their VOO and SPAXX balances
1. The calculator outputs: funding state, prism score, exact action, exact VOO/SPAXX contribution split in dollars, and exact balance trade amount if applicable
1. The user logs into Fidelity and makes the changes

Total time: approximately 5 minutes including Fidelity login.

### The Script

A Python script (`cma_readout.py`) was built to handle all market-data computation and notification. It scrapes multpl.com for the current CAPE (the initially identified Shiller data API was later found to have stale data); uses yfinance to pull one year of VOO price history for moving average and 52-week calculations; computes all three signals; derives the three conditional actions by running each possible funding score (−2, 0, +2) through the prism scoring formula; formats the Scenario Code; and sends the full readout via Gmail SMTP.

**Text message format:**

```
CMA Readout - April 2026
CAPE: 39.35 (Expensive)
VOO: $624.60
MA: 50d $618.66 / 200d $607.51 / Spread +1.84% (Neutral)
52w High: $641.81 (-2.7%) / Low: $467.33 (+33.7%) (Sell)
----------------------
U: 50/50 + sell 5%
F: 50/50 + do nothing
O: 100% VOO + do nothing
----------------------
Scenario Code: E51
```

**SMS delivery:** Gmail SMTP to the Verizon MMS gateway (`PHONE_NUMBER@vzwpix.com`). Completely free — no Twilio, no third-party service. A Gmail App Password is required and stored as a GitHub secret.

**Scheduling:** A GitHub Actions workflow (`readout.yml`) runs the script on `cron: '30 16 1-7 * 3'` — the first Wednesday of every month at 16:30 UTC (11:30am EST / 12:30pm EDT). Wednesday was chosen because it’s always a weekday. The timing was chosen to fall during market hours so the user can act immediately upon receiving the notification.

### The Calculator

A self-contained HTML calculator (`cma-calculator.html`) was built using React and Babel loaded from CDN — no build step, no server, fully portable. It takes four inputs: the Scenario Code, VOO balance, SPAXX balance, SPAXX floor (slider, default $50), and weekly contribution amount. From these it derives the active portfolio, deployable SPAXX, current cash pool percentage, funding state, and prism score. It then outputs the exact action, the VOO/SPAXX contribution split in dollars, and the exact dollar amount of any balance trade.

The calculator is hosted on GitHub Pages at `shwyguy.github.io/shwy_investment_hub/cma-calculator.html` and can be added to an iPhone home screen from Safari as a full-screen web app.

**First live run:** April 10, 2026 — the full pipeline was tested end-to-end and confirmed working.

-----

## Epilogue: Paths Considered and Not Taken

**International CAPE blending:** Originally planned to drive a blended signal weighted in proportion to the VOO/VEU contribution ratio. Abandoned when no clean, freely accessible international CAPE series was found. Resolved by removing VEU from the CMA entirely.

**Three-way VOO/VEU/SPAXX management:** Explored as a way to use VOO and VEU divergence to improve signal quality. Rejected: designing a blended international CAPE signal was impractical, and the system would have needed redesigning entirely when a single ACWI fund eventually exists.

**Research Affiliates expected return as valuation signal:** Methodologically interesting. The valuation-dependent model is mathematically the same as CAPE. The yield-and-growth model adds a growth component — but as rigorously worked out in Chapter 3, growth was ruled out as a necessary addition: growth estimates are too stable to change the monthly signal, and the US growth advantage and international yield advantage cancel each other out in the blended portfolio context. With growth ruled out, the RA tool offers no meaningful advantage over raw CAPE and was set aside.

**Buffett Indicator:** Rejected as redundant with CAPE — both are valuation signals asking the same underlying question, and combining them adds complexity without independent information.

**Hysteresis MA signal:** Replace the three-zone (bearish/neutral/bullish) with a two-zone system that uses memory of prior state — switches to bullish at +2%, stays bullish until −5% is hit, etc. Eliminates the neutral zone entirely. Technically implementable via a small JSON state file written by GitHub Actions between runs. Deferred but not rejected.

**Variable/capped deployment amounts:** Rather than fixed 5%/10%, deploy exactly enough to bring the pool to the nearest zone boundary. Identified as strictly better once balance integration exists. Deferred until the Fidelity balance can be read automatically.

**Fidelity browser automation:** Reading balances via the `fidelity-api` Playwright library. Possible but fragile and technically against Fidelity’s ToS. Deferred until laptop testing can be done.

**Text-back reply flow:** User receives the monthly text, replies with two numbers (VOO and SPAXX values), script computes and replies with the specific action. Considered during the implementation design phase and identified as a cleaner future alternative to the current calculator approach. Set aside for the same reason as browser automation — logging into Fidelity to execute the action is unavoidable regardless.

**The ACWI watch item:** A permanent watch item was established early on to replace VOO + VEU with a single low-cost ACWI equivalent if one ever emerged. As a direct consequence of the account architecture decisions made throughout this conversation — VEU moving to Brokerage 2, the CMA becoming purely a VOO/SPAXX timing account — a single ACWI fund would no longer fit the CMA even if one appeared tomorrow. There is a certain irony in this: the first and only original goal of the account was to find the perfect single world blue chip fund, and that goal quietly resolved itself as a side effect of everything that followed.

All of the above represent paths that were explored but not taken, or features that are designed but deferred. Any of them can be revisited as the system matures.

-----

*This is the narrative of how the strategy was built. For the current system reference, see the strategy reference document.*
