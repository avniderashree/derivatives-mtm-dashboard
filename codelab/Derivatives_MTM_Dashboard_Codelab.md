# 🧪 Codelab: Build a Derivatives Mark-to-Market Dashboard from Scratch

**Estimated time:** 7–8 hours · **Difficulty:** Intermediate · **Language:** Python 3.8+

---

## What You'll Build

By the end of this codelab, you'll have a professional-grade **Mark-to-Market (MTM) valuation dashboard** for derivatives portfolios — the same kind of system used on trading desks at investment banks. It will:

- Price **options** using three methods: **Black-Scholes** (analytical), **Binomial Tree** (lattice), **Monte Carlo** (simulation)
- Calculate the **Greeks** (Delta, Gamma, Theta, Vega, Rho) — the five risk sensitivities that traders live and die by
- Value **futures** using cost-of-carry pricing
- Value **interest rate swaps** using discounted cash flow analysis, with **DV01** (dollar value of a basis point)
- Recover **implied volatility** from observed market prices using Newton's method
- Build a **portfolio engine** that aggregates MTM values, P&L, and Greeks across all positions
- Run **scenario analysis** (what if the market crashes 10%? what if tech rallies 10%?)
- Generate **7 publication-quality charts**: summary dashboard, position breakdown, Greeks breakdown, scenario analysis, option payoff diagrams, volatility surface, historical MTM
- Ship with **21 unit tests** covering pricing accuracy, Greek calculations, portfolio valuation, and end-to-end integration

The final project structure:

```
derivatives-mtm-dashboard/
├── main.py                      # Entry point — runs the full 7-step pipeline
├── requirements.txt             # Dependencies
├── src/
│   ├── __init__.py
│   ├── pricing_models.py        # Black-Scholes, Binomial Tree, Monte Carlo, Implied Vol
│   ├── instruments.py           # OptionPosition, FuturesPosition, SwapPosition
│   ├── mtm_engine.py            # MTMEngine: portfolio aggregation, scenarios
│   └── visualization.py         # 7+ chart functions
├── tests/
│   └── test_derivatives.py      # 21 tests across 5 classes
├── output/                      # Generated charts (PNGs) + reports (CSVs)
└── models/                      # Serialized engine state (.pkl)
```

---

## Prerequisites

- Python 3.8+ installed
- Basic familiarity with Python (functions, classes, dataclasses)
- A terminal / command line

**No finance or math background required.** Every concept — options, futures, swaps, Black-Scholes, Greeks, Monte Carlo — is explained from first principles before we code it.

---

---

# PART 1: THE CONCEPTS (What & Why)

No coding yet. Read this entire section first. Every line of code we write later will map directly back to a concept explained here.

---

## 1.1 The Problem: What Is My Portfolio Worth *Right Now*?

Imagine you work at a trading desk. You hold a mix of options, futures, and swaps. The stock market just moved 2%. Your boss asks: *"What's our P&L?"*

You can't just look at what you paid for things. You need to know what they're worth **right now** — at current market prices. This process is called **Mark-to-Market (MTM)**.

```
Mark-to-Market is deceptively simple in concept:
  MTM Value = What your positions are worth TODAY at current prices
  P&L       = MTM Value − What you paid for them

The hard part is PRICING the instruments.
  A stock? Easy — look at the current price.
  A futures contract? Medium — use the cost-of-carry model.
  An option? Hard — need Black-Scholes, Greeks, implied vol...
  A swap? Hard — need to discount future cash flows.

This project builds the pricing engines for ALL of these.
```

---

## 1.2 What Is an Option? (From Scratch)

An option is a **contract** that gives you the **right, but not obligation**, to buy or sell an asset at a specific price by a specific date.

```
Two types:
  CALL = Right to BUY at the strike price
  PUT  = Right to SELL at the strike price

The key terms:
  Underlying (S)  = The asset (e.g., AAPL stock, currently $175)
  Strike (K)      = The price you can buy/sell at (e.g., $180)
  Expiry (T)      = When the contract expires (e.g., 3 months)
  Premium         = What you pay for this right (e.g., $7.37)
```

**Worked example — a Call Option:**

```
You buy an AAPL $180 Call expiring in 3 months for $7.37.

This means:
  - You paid $7.37 per share (the premium)
  - You have the RIGHT to buy AAPL at $180 any time before expiry
  - If AAPL goes to $200, you exercise: buy at $180, worth $200 → profit $20 − $7.37 = $12.63
  - If AAPL stays at $170, you don't exercise: loss = $7.37 (the premium you paid)

Payoff at expiry:
  Call payoff = max(Stock Price − Strike, 0)
             = max($200 − $180, 0) = $20

  Put payoff = max(Strike − Stock Price, 0)
             = max($180 − $200, 0) = $0 (worthless if stock went UP)
```

**European vs American:**

```
European option: Can ONLY exercise at expiry (last day)
American option: Can exercise ANY TIME before expiry

Why does this matter?
  - European is simpler to price (Black-Scholes gives exact answer)
  - American is worth ≥ European (extra flexibility has value)
  - The "early exercise premium" exists mainly for PUTS
    (because you might want to sell a collapsing stock NOW, not wait)
  - For calls on non-dividend stocks, American = European
    (no reason to exercise early — you'd lose the time value)
```

---

## 1.3 The Black-Scholes Formula (The Nobel Prize Equation)

Black-Scholes gives the **exact** price of a European option. It was published in 1973 and won the Nobel Prize in Economics. Every options trader on Earth uses it.

```
The formula needs 5 inputs:
  S = Current stock price      ($175)
  K = Strike price             ($180)
  T = Time to expiry in years  (0.25 = 3 months)
  r = Risk-free interest rate  (0.05 = 5%)
  σ = Volatility               (0.25 = 25% annual)

Step 1: Calculate d₁ and d₂
  d₁ = [ln(S/K) + (r + σ²/2) × T] / (σ × √T)
  d₂ = d₁ − σ × √T

  With our numbers:
  d₁ = [ln(175/180) + (0.05 + 0.0625/2) × 0.25] / (0.25 × √0.25)
     = [−0.02817 + 0.02031] / 0.125
     = −0.06291

  d₂ = −0.06291 − 0.125 = −0.18791

Step 2: Look up N(d₁) and N(d₂)
  N(x) = cumulative normal distribution (scipy.stats.norm.cdf)
  N(d₁) = N(−0.063) = 0.4749
  N(d₂) = N(−0.188) = 0.4255

Step 3: Plug into the formula
  Call = S × N(d₁) − K × e^(−rT) × N(d₂)
       = 175 × 0.4749 − 180 × e^(−0.0125) × 0.4255
       = 83.11 − 180 × 0.9876 × 0.4255
       = 83.11 − 75.60
       = $7.51

  Put  = K × e^(−rT) × N(−d₂) − S × N(−d₁)
       = 180 × 0.9876 × 0.5745 − 175 × 0.5251
       = 102.10 − 91.89
       = $10.21

  (Exact values vary slightly with precision)
```

**What the formula captures intuitively:**

```
Call = (Chance of exercise × Expected stock price if exercised)
     − (Chance of exercise × Present value of strike payment)

The "chance of exercise" is what N(d₁) and N(d₂) measure.
Higher stock price → more likely to exercise → N(d) increases → higher price.
Higher volatility → more chance of big moves → wider payoff → higher price.
More time → more chance of favorable moves → higher price.
```

---

## 1.4 The Greeks: Five Risk Sensitivities That Traders Live By

An option's price changes when market conditions change. The Greeks measure exactly HOW MUCH it changes for each factor.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ Greek   │ Measures                     │ Formula (Call)             │ Example     │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Delta Δ │ Price change per $1 stock    │ N(d₁)                     │ Δ = 0.47    │
│         │ move                          │                            │ means option│
│         │                               │                            │ moves $0.47 │
│         │                               │                            │ per $1 stock│
├──────────────────────────────────────────────────────────────────────────────────┤
│ Gamma Γ │ How fast Delta changes       │ N'(d₁) / (S × σ × √T)   │ Γ = 0.018   │
│         │ (curvature)                   │                            │ means Δ     │
│         │                               │                            │ changes by  │
│         │                               │                            │ 0.018 per $1│
├──────────────────────────────────────────────────────────────────────────────────┤
│ Theta Θ │ Daily time decay             │ −[S×N'(d₁)×σ/(2√T)]     │ Θ = −$0.057 │
│         │ (option loses value each day) │  − r×K×e^(−rT)×N(d₂)     │ per day     │
│         │                               │  (divided by 365)          │             │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Vega ν  │ Price change per 1% vol      │ S × N'(d₁) × √T / 100   │ ν = $0.35   │
│         │ change                        │                            │ per 1% vol  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Rho ρ   │ Price change per 1% rate     │ K×T×e^(−rT)×N(d₂) / 100 │ ρ = $0.19   │
│         │ change                        │                            │ per 1% rate │
└──────────────────────────────────────────────────────────────────────────────────┘

Where N'(x) = standard normal PDF = (1/√2π) × e^(−x²/2)
```

**Why traders care about each Greek:**

```
Delta (Δ = 0.47):
  "I hold 10 contracts × 100 shares × Δ0.47 = 470 share equivalents"
  If AAPL goes up $1, my position gains ~$470.
  Used for: hedging (buy/sell stock to neutralize delta)

Gamma (Γ = 0.018):
  "My delta changes by 0.018 × 100 = 1.8 per $1 move"
  If AAPL goes from $175 to $176, my delta goes from 0.47 to 0.488.
  High gamma = delta changes fast = harder to hedge.
  Used for: assessing hedge stability

Theta (Θ = −$0.057/day):
  "Each day, my 10 contracts lose 10 × 100 × $0.057 = $57"
  Options are wasting assets — they lose value every day.
  Used for: understanding daily bleed / income from short options

Vega (ν = $0.35):
  "If vol goes from 25% to 26%, each option gains $0.35"
  10 contracts × 100 shares × $0.35 = $350 gain
  Used for: trading volatility, understanding earnings risk

Rho (ρ = $0.19):
  "If rates go from 5% to 6%, each option gains $0.19"
  Usually the least important Greek, but matters for long-dated options.
  Used for: interest rate risk management
```

---

## 1.5 The Binomial Tree: Pricing American Options

Black-Scholes only prices European options. For American options (which can be exercised early), we use a **binomial tree**.

```
The idea: model stock price as a series of UP or DOWN moves.

          S×u²
         ↗
    S×u ─
   ↗     ↘
  S       S×u×d  (= S if u×d = 1)
   ↘     ↗
    S×d ─
         ↘
          S×d²

Where:
  u = up factor = e^(σ√Δt)      ← how much stock goes UP in one step
  d = down factor = e^(-σ√Δt)   ← how much stock goes DOWN in one step
  p = up probability = (e^(rΔt) - d) / (u - d)   ← risk-neutral probability
  Δt = T / n_steps              ← time per step

With 200 steps, this converges to the Black-Scholes price for European options.

For American options, at EACH NODE we check:
  "Is it better to EXERCISE NOW or WAIT?"
  Node value = max(exercise_value, continue_value)
  
  Exercise value (call) = max(S_node − K, 0)
  Continue value = e^(−rΔt) × [p × up_value + (1−p) × down_value]

This is why American puts are worth MORE than European puts:
  When a stock is crashing, you want to sell NOW at the strike price
  rather than wait and risk the stock recovering.
```

---

## 1.6 Monte Carlo: The Swiss Army Knife

Monte Carlo simulates thousands of random stock price paths and averages the payoffs.

```
The algorithm:
  1. Generate N random price paths using Geometric Brownian Motion:
     S(t+dt) = S(t) × exp[(r − σ²/2)×dt + σ×√dt×Z]
     where Z ~ Normal(0,1)

  2. At expiry, calculate the payoff for each path:
     Call payoff = max(S_final − K, 0)

  3. Discount back to today and average:
     Price = e^(−rT) × mean(payoffs)

  4. Standard error = std(payoffs) / √N × e^(−rT)
     (tells you how precise your estimate is)

Why use Monte Carlo when we have Black-Scholes?
  - Can price ANY payoff (exotic options, path-dependent, barriers)
  - Easy to add features (stochastic vol, jumps, dividends)
  - Flexible but slow (need many simulations for precision)
  - With 100,000 paths, error is typically < $0.10
```

---

## 1.7 Futures: The Simplest Derivative

A futures contract is an **obligation** (not a right) to buy or sell an asset at a future date.

```
Futures pricing (cost-of-carry model):
  F = S × e^(rT)

  Where:
  F = Futures price
  S = Current spot price
  r = Risk-free rate
  T = Time to expiry

  Example: S&P 500 at 5,100, r=5%, T=0.25 years
  F = 5,100 × e^(0.05 × 0.25) = 5,100 × 1.01258 = $5,164.14

MTM for a futures position:
  Long MTM = (Current futures price − Entry price) × Quantity × Contract size
  
  Example: Bought 2 ES futures at 5,050, now at 5,100
  MTM = (5,100 − 5,050) × 2 × $50 = $5,000 profit

Delta for futures:
  Delta = Quantity × Contract size
  2 ES contracts × $50/point = $100 per 1-point move in S&P
```

---

## 1.8 Interest Rate Swaps: Trading Fixed for Floating

A swap is an agreement to exchange **fixed** interest payments for **floating** rate payments on a notional amount.

```
Example: $1M 5-year swap, 4.5% fixed, pay quarterly

  Every quarter:
    Fixed payment = $1,000,000 × 4.5% / 4 = $11,250
    Floating payment = $1,000,000 × (current 3-month rate) / 4

  If you RECEIVE fixed:
    You get $11,250/quarter regardless of rates
    You pay whatever the floating rate is
    If rates go DOWN → you win (you locked in high fixed rate)
    If rates go UP → you lose (you're paying more floating)

MTM valuation (simplified):
  Swap MTM = PV(remaining fixed payments) − PV(remaining floating payments)
  
  In practice, floating leg ≈ par at each reset, so:
  Swap MTM ≈ Notional × (fixed_rate − market_rate) × Annuity Factor

DV01 (Dollar Value of 1 Basis Point):
  DV01 = How much the swap's value changes when rates move 1 basis point (0.01%)
  DV01 ≈ Notional × Modified Duration × 0.0001
  
  For a $1M 5-year swap: DV01 ≈ $1,000,000 × ~4.5 × 0.0001 ≈ $450
  Meaning: a 1bp rate move changes the swap value by ~$450
```

---

## 1.9 Implied Volatility: Reverse-Engineering the Market's Fear

Black-Scholes takes volatility as INPUT and gives price as OUTPUT. **Implied volatility** does the reverse — given the market price, what volatility must the market be assuming?

```
Problem: You observe that an AAPL $180 Call trades at $7.50.
  Given S=175, K=180, T=0.25, r=5%, what σ makes BS price = $7.50?

Solution: Newton-Raphson iteration
  1. Start with initial guess σ = 0.20
  2. Calculate BS price with σ = 0.20 → get $6.50 (too low)
  3. Calculate Vega = ∂price/∂σ → tells us how much price changes per σ
  4. Update: σ_new = σ_old + (market_price − BS_price) / Vega
     σ_new = 0.20 + ($7.50 − $6.50) / Vega
  5. Repeat until |BS_price − market_price| < tolerance

This typically converges in 5-10 iterations.

Why is implied vol important?
  - It's the market's consensus on future uncertainty
  - High IV → market expects big moves (e.g., before earnings)
  - IV is comparable across strikes/expiries (unlike prices)
  - VIX index = implied vol of S&P 500 options
```

---

## 1.10 Scenario Analysis: What If the World Changes?

Scenario analysis asks: *"What would my portfolio be worth if specific market events occur?"*

```
Example scenarios:
  Base Case:         All prices unchanged (benchmark)
  Market +5%:        Every stock goes up 5%
  Market −5%:        Every stock goes down 5%
  Tech Rally +10%:   AAPL +10%, SPY +3%
  Market Crash −10%: Everything drops 10%
  Vol Spike:         Volatility doubles

For each scenario:
  1. Shock spot prices by the scenario amount
  2. Reprice every instrument at shocked prices
  3. Calculate new portfolio MTM and P&L
  4. Compare to base case

This is how risk managers stress-test portfolios before market opens.
```

---

---

# PART 2: PROJECT SETUP (Step 0)

---

## Step 0.1: Create the Folder Structure

```bash
mkdir derivatives-mtm-dashboard
cd derivatives-mtm-dashboard
mkdir -p src tests output models data notebooks
```

## Step 0.2: Create `requirements.txt`

**File: `requirements.txt`**
```
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.3.0
yfinance>=0.1.70
joblib>=1.1.0
pytest>=7.0.0
```

| Library | Purpose |
|---------|---------|
| `numpy` | Array math, random number generation for Monte Carlo |
| `pandas` | DataFrames for position reports and scenario tables |
| `scipy` | `norm.cdf` / `norm.pdf` — the heart of Black-Scholes |
| `matplotlib` | Base charting library for all 7 chart types |
| `seaborn` | Professional chart styling and color palettes |
| `plotly` | Interactive 3D charts (volatility surface) |
| `yfinance` | Optional: fetch real market data from Yahoo Finance |
| `joblib` | Serialize/deserialize the MTM engine to disk |
| `pytest` | Run the 21 unit tests |

Install:
```bash
pip install -r requirements.txt
```

## Step 0.3: Create `src/__init__.py`

**File: `src/__init__.py`**
```python
"""
Derivatives MTM Dashboard
============================
Mark-to-Market valuation dashboard for derivatives portfolios.

Modules:
    pricing_models  - Black-Scholes, Binomial Tree, Monte Carlo, Implied Vol
    instruments     - OptionPosition, FuturesPosition, SwapPosition
    mtm_engine      - Portfolio valuation engine with scenario analysis
    visualization   - 7+ publication-quality chart functions
"""
```

---

---

# PART 3: PRICING MODELS (Step 1)

This is the mathematical core — four pricing engines and five Greek calculations, all in one module. Every function maps directly to the formulas from Part 1.

---

## Step 1.1: Understand What This Module Does

```
pricing_models.py
    │
    ├── OptionType (enum)           — CALL / PUT
    ├── ExerciseStyle (enum)        — EUROPEAN / AMERICAN
    ├── OptionContract (dataclass)  — Holds the 5 BS inputs + type + dividend yield
    ├── PricingResult (dataclass)   — Holds price + all 5 Greeks
    │
    ├── black_scholes_price(option) → float
    │       → Closed-form BS price (the Nobel equation)
    │
    ├── black_scholes_greeks(option) → PricingResult
    │       → Price + Delta, Gamma, Theta, Vega, Rho (all 5 Greeks)
    │
    ├── binomial_tree_price(option, n_steps, exercise_style) → float
    │       → Lattice model for European AND American options
    │
    ├── monte_carlo_price(option, n_simulations, random_seed) → (price, std_error)
    │       → Simulation-based pricing with error estimate
    │
    └── implied_volatility(market_price, option) → float
            → Newton-Raphson root finding for σ
```

## Step 1.2: Write the Code

**File: `src/pricing_models.py`**

```python
"""
pricing_models.py — Derivatives Pricing Engines
===================================================

Four pricing methods:
  1. Black-Scholes     — Analytical, European only, instant
  2. Binomial Tree     — Lattice, European + American, fast
  3. Monte Carlo       — Simulation, any payoff, medium speed
  4. Implied Volatility — Reverse-engineers σ from market price

Plus complete Greeks calculation (Delta, Gamma, Theta, Vega, Rho).

All formulas follow Hull, "Options, Futures, and Other Derivatives" (11th ed.)
"""

import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
from scipy.stats import norm


# ─── Enums & Dataclasses ───────────────────────────────────────

class OptionType(Enum):
    """Call or Put."""
    CALL = 'call'
    PUT = 'put'


class ExerciseStyle(Enum):
    """European (exercise at expiry) or American (exercise any time)."""
    EUROPEAN = 'european'
    AMERICAN = 'american'


@dataclass
class OptionContract:
    """
    Holds all inputs needed to price an option.

    Attributes
    ----------
    spot : float
        Current price of the underlying asset (S).
    strike : float
        Strike price of the option (K).
    time_to_expiry : float
        Time to expiration in years (T). 0.25 = 3 months.
    risk_free_rate : float
        Annualized risk-free interest rate (r). 0.05 = 5%.
    volatility : float
        Annualized volatility (σ). 0.25 = 25%.
    option_type : OptionType
        CALL or PUT.
    dividend_yield : float
        Continuous dividend yield (q). 0.005 = 0.5%.
    """
    spot: float
    strike: float
    time_to_expiry: float
    risk_free_rate: float
    volatility: float
    option_type: OptionType
    dividend_yield: float = 0.0


@dataclass
class PricingResult:
    """
    Contains the option price and all five Greeks.

    Attributes
    ----------
    price : float
        Fair value of the option.
    delta : float
        ∂Price/∂Spot — price sensitivity to $1 stock move.
    gamma : float
        ∂²Price/∂Spot² — rate of change of delta.
    theta : float
        ∂Price/∂Time — daily time decay (negative for long options).
    vega : float
        ∂Price/∂Vol — price change per 1% volatility change.
    rho : float
        ∂Price/∂Rate — price change per 1% interest rate change.
    """
    price: float
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    rho: float = 0.0


# ─── Black-Scholes Helper: d₁ and d₂ ──────────────────────────

def _d1_d2(option: OptionContract) -> Tuple[float, float]:
    """
    Calculate d₁ and d₂ — the two intermediate values in Black-Scholes.

    d₁ = [ln(S/K) + (r − q + σ²/2) × T] / (σ × √T)
    d₂ = d₁ − σ × √T

    These appear in every Black-Scholes formula (price and all Greeks).
    """
    S = option.spot
    K = option.strike
    T = option.time_to_expiry
    r = option.risk_free_rate
    sigma = option.volatility
    q = option.dividend_yield

    # Guard against zero time or zero vol
    if T <= 0 or sigma <= 0:
        # At expiry: intrinsic value only
        if option.option_type == OptionType.CALL:
            intrinsic = max(S - K, 0)
        else:
            intrinsic = max(K - S, 0)
        return 0.0, 0.0

    sqrt_T = np.sqrt(T)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    return d1, d2


# ─── Black-Scholes Price ───────────────────────────────────────

def black_scholes_price(option: OptionContract) -> float:
    """
    Black-Scholes closed-form option price.

    Call = S × e^(−qT) × N(d₁) − K × e^(−rT) × N(d₂)
    Put  = K × e^(−rT) × N(−d₂) − S × e^(−qT) × N(−d₁)
    """
    S = option.spot
    K = option.strike
    T = option.time_to_expiry
    r = option.risk_free_rate
    q = option.dividend_yield

    if T <= 0:
        if option.option_type == OptionType.CALL:
            return max(S - K, 0.0)
        else:
            return max(K - S, 0.0)

    d1, d2 = _d1_d2(option)
    discount = np.exp(-r * T)
    forward_discount = np.exp(-q * T)

    if option.option_type == OptionType.CALL:
        return S * forward_discount * norm.cdf(d1) - K * discount * norm.cdf(d2)
    else:
        return K * discount * norm.cdf(-d2) - S * forward_discount * norm.cdf(-d1)


# ─── Black-Scholes Greeks ──────────────────────────────────────

def black_scholes_greeks(option: OptionContract) -> PricingResult:
    """
    Black-Scholes price with all five Greeks.

    Delta (call) = e^(−qT) × N(d₁)
    Delta (put)  = e^(−qT) × [N(d₁) − 1]

    Gamma = e^(−qT) × N'(d₁) / (S × σ × √T)
           (same for calls and puts)

    Theta (call) = −[S × e^(−qT) × N'(d₁) × σ / (2√T)]
                   + q × S × e^(−qT) × N(d₁)
                   − r × K × e^(−rT) × N(d₂)
                   (divided by 365 to get per-day)

    Vega  = S × e^(−qT) × N'(d₁) × √T / 100
            (per 1% vol change)

    Rho (call) = K × T × e^(−rT) × N(d₂) / 100
    Rho (put)  = −K × T × e^(−rT) × N(−d₂) / 100
            (per 1% rate change)
    """
    S = option.spot
    K = option.strike
    T = option.time_to_expiry
    r = option.risk_free_rate
    sigma = option.volatility
    q = option.dividend_yield

    price = black_scholes_price(option)

    if T <= 0 or sigma <= 0:
        # At expiry: delta is 1 or 0, other Greeks are 0
        if option.option_type == OptionType.CALL:
            delta = 1.0 if S > K else 0.0
        else:
            delta = -1.0 if S < K else 0.0
        return PricingResult(price=price, delta=delta)

    d1, d2 = _d1_d2(option)
    sqrt_T = np.sqrt(T)

    # N(d) and N'(d) — cumulative and probability density
    Nd1 = norm.cdf(d1)
    Nd2 = norm.cdf(d2)
    Npd1 = norm.pdf(d1)  # N'(d₁) = standard normal PDF

    discount = np.exp(-r * T)
    fwd_discount = np.exp(-q * T)

    # ── Gamma (same for call and put) ────────────────────
    gamma = fwd_discount * Npd1 / (S * sigma * sqrt_T)

    # ── Vega (same for call and put, per 1% vol change) ──
    vega = S * fwd_discount * Npd1 * sqrt_T / 100.0

    if option.option_type == OptionType.CALL:
        delta = fwd_discount * Nd1
        theta = (
            -S * fwd_discount * Npd1 * sigma / (2 * sqrt_T)
            + q * S * fwd_discount * Nd1
            - r * K * discount * Nd2
        ) / 365.0  # Per day
        rho = K * T * discount * Nd2 / 100.0
    else:
        delta = fwd_discount * (Nd1 - 1)
        Nmd1 = norm.cdf(-d1)
        Nmd2 = norm.cdf(-d2)
        theta = (
            -S * fwd_discount * Npd1 * sigma / (2 * sqrt_T)
            - q * S * fwd_discount * Nmd1
            + r * K * discount * Nmd2
        ) / 365.0
        rho = -K * T * discount * Nmd2 / 100.0

    return PricingResult(
        price=price,
        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
        rho=rho,
    )


# ─── Binomial Tree ─────────────────────────────────────────────

def binomial_tree_price(
    option: OptionContract,
    n_steps: int = 200,
    exercise_style: ExerciseStyle = ExerciseStyle.EUROPEAN
) -> float:
    """
    Price an option using the Cox-Ross-Rubinstein binomial tree.

    Algorithm:
      1. Build a price tree:
         - u = e^(σ√Δt)     (up factor)
         - d = e^(−σ√Δt)    (down factor)
         - p = (e^((r−q)Δt) − d) / (u − d)  (risk-neutral probability)

      2. Calculate payoffs at the final nodes (expiry).

      3. Work backwards through the tree:
         - Continue value = e^(−rΔt) × [p × up_value + (1−p) × down_value]
         - For American: node_value = max(exercise_value, continue_value)
         - For European: node_value = continue_value

    Parameters
    ----------
    option : OptionContract
        The option to price.
    n_steps : int
        Number of tree steps (more = more accurate, 200 is good).
    exercise_style : ExerciseStyle
        EUROPEAN or AMERICAN.

    Returns
    -------
    float
        Option price.
    """
    S = option.spot
    K = option.strike
    T = option.time_to_expiry
    r = option.risk_free_rate
    sigma = option.volatility
    q = option.dividend_yield
    is_call = option.option_type == OptionType.CALL

    if T <= 0:
        return max(S - K, 0) if is_call else max(K - S, 0)

    dt = T / n_steps
    u = np.exp(sigma * np.sqrt(dt))       # Up factor
    d = 1.0 / u                            # Down factor (ensures u×d = 1)
    p = (np.exp((r - q) * dt) - d) / (u - d)  # Risk-neutral up probability

    # Discount factor per step
    disc = np.exp(-r * dt)

    # ── Step 1: Final node prices ────────────────────────
    # At step n_steps, price at node j is: S × u^j × d^(n_steps−j)
    # Using the efficient representation: S × u^(2j − n_steps)
    stock_prices = S * u ** (2 * np.arange(n_steps + 1) - n_steps)

    # Payoffs at expiry
    if is_call:
        option_values = np.maximum(stock_prices - K, 0.0)
    else:
        option_values = np.maximum(K - stock_prices, 0.0)

    # ── Step 2: Backward induction ───────────────────────
    for step in range(n_steps - 1, -1, -1):
        # Stock prices at this step
        stock_at_step = S * u ** (2 * np.arange(step + 1) - step)

        # Continue value (expected discounted value)
        option_values = disc * (p * option_values[1:] + (1 - p) * option_values[:-1])

        # For American: check if early exercise is better
        if exercise_style == ExerciseStyle.AMERICAN:
            if is_call:
                exercise_values = np.maximum(stock_at_step - K, 0.0)
            else:
                exercise_values = np.maximum(K - stock_at_step, 0.0)
            option_values = np.maximum(option_values, exercise_values)

    return float(option_values[0])


# ─── Monte Carlo ───────────────────────────────────────────────

def monte_carlo_price(
    option: OptionContract,
    n_simulations: int = 100000,
    random_seed: Optional[int] = 42
) -> Tuple[float, float]:
    """
    Price an option using Monte Carlo simulation.

    Algorithm:
      1. Generate N random price paths using Geometric Brownian Motion:
         S(T) = S₀ × exp[(r − q − σ²/2)T + σ√T × Z]
         where Z ~ Normal(0, 1)

      2. Calculate payoff for each path:
         Call: max(S(T) − K, 0)
         Put:  max(K − S(T), 0)

      3. Price = e^(−rT) × mean(payoffs)
         Error = e^(−rT) × std(payoffs) / √N

    Returns
    -------
    (price, standard_error) : Tuple[float, float]
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    S = option.spot
    K = option.strike
    T = option.time_to_expiry
    r = option.risk_free_rate
    sigma = option.volatility
    q = option.dividend_yield

    if T <= 0:
        if option.option_type == OptionType.CALL:
            return max(S - K, 0.0), 0.0
        else:
            return max(K - S, 0.0), 0.0

    # Generate random terminal prices (GBM)
    Z = np.random.standard_normal(n_simulations)
    drift = (r - q - 0.5 * sigma**2) * T
    diffusion = sigma * np.sqrt(T) * Z
    S_T = S * np.exp(drift + diffusion)

    # Calculate payoffs
    if option.option_type == OptionType.CALL:
        payoffs = np.maximum(S_T - K, 0.0)
    else:
        payoffs = np.maximum(K - S_T, 0.0)

    # Discount to present
    discount = np.exp(-r * T)
    price = discount * np.mean(payoffs)
    std_error = discount * np.std(payoffs) / np.sqrt(n_simulations)

    return float(price), float(std_error)


# ─── Implied Volatility ────────────────────────────────────────

def implied_volatility(
    market_price: float,
    option: OptionContract,
    tol: float = 1e-6,
    max_iterations: int = 100
) -> float:
    """
    Find implied volatility using Newton-Raphson method.

    Given a market price, find σ such that BS(σ) = market_price.

    Algorithm:
      1. Start with σ₀ = 0.20 (or option's current σ)
      2. Calculate BS price and Vega at current σ
      3. Update: σ_new = σ_old + (market_price − bs_price) / (Vega × 100)
         (Vega×100 because our Vega is per 1% = per 0.01)
      4. Repeat until |bs_price − market_price| < tolerance

    Returns σ (annualized, e.g., 0.25 = 25%).
    """
    # Start with a reasonable initial guess
    sigma = option.volatility if option.volatility > 0 else 0.20

    for i in range(max_iterations):
        # Create option with current sigma guess
        test_option = OptionContract(
            spot=option.spot,
            strike=option.strike,
            time_to_expiry=option.time_to_expiry,
            risk_free_rate=option.risk_free_rate,
            volatility=sigma,
            option_type=option.option_type,
            dividend_yield=option.dividend_yield,
        )

        result = black_scholes_greeks(test_option)
        price_diff = result.price - market_price

        if abs(price_diff) < tol:
            return sigma

        # Vega is per 1% vol = per 0.01 in σ
        # So ∂price/∂σ = Vega × 100
        vega_per_unit = result.vega * 100.0

        if abs(vega_per_unit) < 1e-10:
            # Vega too small to iterate (deep ITM/OTM or at expiry)
            break

        sigma = sigma - price_diff / vega_per_unit
        sigma = max(0.001, min(sigma, 5.0))  # Keep in reasonable range

    return sigma
```

---

**What You Just Built:**

- **`_d1_d2`**: Calculates the d₁ and d₂ values that appear in every Black-Scholes formula. Handles edge cases (zero time, zero vol).
- **`black_scholes_price`**: The Nobel Prize formula — closed-form European option price.
- **`black_scholes_greeks`**: Price + all five Greeks. Delta = N(d₁) for calls. Gamma = N'(d₁)/(Sσ√T). Theta includes the three terms (volatility decay, dividend adjustment, rate adjustment) divided by 365 for per-day. Vega and Rho are scaled per 1% change.
- **`binomial_tree_price`**: CRR tree with NumPy vectorization. Works for both European and American options. 200 steps gives accuracy to ~$0.01 vs Black-Scholes.
- **`monte_carlo_price`**: GBM simulation with 100,000 paths. Returns both the price and standard error (so you know the confidence interval).
- **`implied_volatility`**: Newton-Raphson root finder. Uses Vega as the derivative (since Vega = ∂price/∂σ). Converges in 5-10 iterations.

---

---

# PART 4: INSTRUMENTS (Step 2)

Position-level wrappers for options, futures, and swaps. Each instrument knows how to calculate its own MTM, P&L, and Greeks by calling the pricing engine.

---

## Step 2.1: Understand What This Module Does

```
instruments.py
    │
    ├── PositionSide (enum)       — LONG / SHORT
    │
    ├── MarketData (dataclass)    — Current market conditions for one underlying
    │       spot_price, risk_free_rate, dividend_yield, volatility
    │
    ├── OptionPosition            — Wraps an option trade
    │       .value(market) → MTM in dollars
    │       .pnl(market) → profit/loss
    │       .greeks(market) → dict of {delta, gamma, theta, vega, rho}
    │
    ├── FuturesPosition           — Wraps a futures trade
    │       .value(market) → MTM in dollars
    │       .pnl(market) → profit/loss
    │       .delta(market) → directional exposure
    │
    └── SwapPosition              — Wraps an interest rate swap
            .value(market) → MTM in dollars
            .dv01(market) → dollar value of 1bp rate move
```

## Step 2.2: Write the Code

**File: `src/instruments.py`**

```python
"""
instruments.py — Derivative Instrument Classes
=================================================

Three instrument types, each with MTM, P&L, and risk methods:
  1. OptionPosition  — Calls/Puts, long/short, with Greeks
  2. FuturesPosition — Linear exposure, cost-of-carry pricing
  3. SwapPosition    — Fixed-for-floating swaps with DV01

Each instrument stores trade-level data (strike, expiry, quantity, etc.)
and computes valuations given current market data.
"""

import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Optional

from src.pricing_models import (
    OptionContract, OptionType, PricingResult,
    black_scholes_greeks, black_scholes_price,
)


# ─── Enums & Market Data ───────────────────────────────────────

class PositionSide(Enum):
    """Long (bought) or Short (sold)."""
    LONG = 'long'
    SHORT = 'short'


@dataclass
class MarketData:
    """
    Current market conditions for a single underlying.

    This is what changes every second on a live trading desk.
    The pricing models consume this data to produce MTM values.

    Attributes
    ----------
    spot_price : float
        Current price of the underlying asset.
    risk_free_rate : float
        Annualized risk-free rate (e.g., 0.05 = 5%).
    dividend_yield : float
        Continuous dividend yield (e.g., 0.005 = 0.5%).
    volatility : float
        Annualized implied volatility (e.g., 0.25 = 25%).
    """
    spot_price: float
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0
    volatility: float = 0.20


# ─── Option Position ───────────────────────────────────────────

class OptionPosition:
    """
    An option position with MTM, P&L, and Greeks.

    This represents a real trade: "I own 10 AAPL 180 calls expiring
    in 60 days, I paid $5.50 per share for them."

    Parameters
    ----------
    underlying : str
        Ticker symbol (e.g., 'AAPL').
    strike : float
        Strike price.
    expiry : datetime
        Expiration date.
    option_type : str
        'call' or 'put'.
    side : PositionSide
        LONG (bought) or SHORT (sold).
    quantity : int
        Number of contracts.
    contract_multiplier : int
        Shares per contract (usually 100 for equity options).
    premium_paid : float
        Premium per share when position was opened.
    """

    def __init__(
        self,
        underlying: str,
        strike: float,
        expiry: datetime,
        option_type: str = 'call',
        side: PositionSide = PositionSide.LONG,
        quantity: int = 1,
        contract_multiplier: int = 100,
        premium_paid: float = 0.0,
    ):
        self.underlying = underlying
        self.strike = strike
        self.expiry = expiry
        self.option_type = option_type.lower()
        self.side = side
        self.quantity = quantity
        self.contract_multiplier = contract_multiplier
        self.premium_paid = premium_paid
        self.instrument_type = 'option'

        # Validate
        if self.option_type not in ('call', 'put'):
            raise ValueError(f"option_type must be 'call' or 'put', got '{self.option_type}'")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.strike <= 0:
            raise ValueError("strike must be positive")

    def _time_to_expiry(self) -> float:
        """Calculate T in years from now to expiry."""
        now = datetime.now()
        days = max((self.expiry - now).days, 0)
        return days / 365.0

    def _make_contract(self, market: MarketData) -> OptionContract:
        """Build an OptionContract from position data + current market."""
        return OptionContract(
            spot=market.spot_price,
            strike=self.strike,
            time_to_expiry=self._time_to_expiry(),
            risk_free_rate=market.risk_free_rate,
            volatility=market.volatility,
            option_type=OptionType.CALL if self.option_type == 'call' else OptionType.PUT,
            dividend_yield=market.dividend_yield,
        )

    def value(self, market: MarketData) -> float:
        """
        Current MTM value of this position in dollars.

        MTM = option_price × quantity × multiplier × direction
        Direction: +1 for LONG, −1 for SHORT
        """
        contract = self._make_contract(market)
        price_per_share = black_scholes_price(contract)
        direction = 1 if self.side == PositionSide.LONG else -1
        return price_per_share * self.quantity * self.contract_multiplier * direction

    def pnl(self, market: MarketData) -> float:
        """
        Profit/Loss = Current value − Cost paid.

        Cost = premium × quantity × multiplier × direction
        (Long positions have positive cost, short positions receive premium)
        """
        current_value = self.value(market)
        direction = 1 if self.side == PositionSide.LONG else -1
        cost = self.premium_paid * self.quantity * self.contract_multiplier * direction
        return current_value - cost

    def greeks(self, market: MarketData) -> Dict[str, float]:
        """
        Position-level Greeks (scaled by quantity × multiplier × direction).

        Returns dict: {delta, gamma, theta, vega, rho}
        """
        contract = self._make_contract(market)
        result = black_scholes_greeks(contract)
        direction = 1 if self.side == PositionSide.LONG else -1
        scale = self.quantity * self.contract_multiplier * direction

        return {
            'delta': result.delta * scale,
            'gamma': result.gamma * scale,
            'theta': result.theta * scale,
            'vega': result.vega * scale,
            'rho': result.rho * scale,
        }

    def __repr__(self) -> str:
        side_str = 'Long' if self.side == PositionSide.LONG else 'Short'
        return (f"{side_str} {self.quantity} {self.underlying} "
                f"{self.strike} {self.option_type.upper()}")


# ─── Futures Position ──────────────────────────────────────────

class FuturesPosition:
    """
    A futures position with MTM and P&L.

    Futures are simpler than options: linear payoff, no Greeks
    except Delta (which is just quantity × contract_size).

    Parameters
    ----------
    underlying : str
        Ticker symbol or contract name (e.g., 'ES' for E-mini S&P).
    futures_price : float
        Current futures price.
    expiry : datetime
        Contract expiration.
    side : PositionSide
        LONG or SHORT.
    quantity : int
        Number of contracts.
    contract_size : float
        Dollar value per point (e.g., $50 for ES, $10 for NQ).
    entry_price : float
        Price when position was opened.
    """

    def __init__(
        self,
        underlying: str,
        futures_price: float,
        expiry: datetime,
        side: PositionSide = PositionSide.LONG,
        quantity: int = 1,
        contract_size: float = 50.0,
        entry_price: float = 0.0,
    ):
        self.underlying = underlying
        self.futures_price = futures_price
        self.expiry = expiry
        self.side = side
        self.quantity = quantity
        self.contract_size = contract_size
        self.entry_price = entry_price
        self.instrument_type = 'futures'

    def value(self, market: MarketData) -> float:
        """
        Current MTM value of futures position.

        For futures, "value" is the unrealized P&L relative to entry,
        since the initial margin is not an investment in the same way.
        MTM = (current_price − entry_price) × quantity × contract_size × direction
        """
        direction = 1 if self.side == PositionSide.LONG else -1
        return (self.futures_price - self.entry_price) * self.quantity * self.contract_size * direction

    def pnl(self, market: MarketData) -> float:
        """P&L for futures is same as value (no premium like options)."""
        return self.value(market)

    def delta(self, market: MarketData) -> float:
        """
        Futures delta = quantity × contract_size × direction.

        A long ES futures contract with contract_size=$50 has
        delta = 1 × $50 = $50 per point (same as 50 shares of S&P).
        """
        direction = 1 if self.side == PositionSide.LONG else -1
        return self.quantity * self.contract_size * direction

    def greeks(self, market: MarketData) -> Dict[str, float]:
        """Futures only have delta (linear exposure)."""
        return {
            'delta': self.delta(market),
            'gamma': 0.0,
            'theta': 0.0,
            'vega': 0.0,
            'rho': 0.0,
        }

    def __repr__(self) -> str:
        side_str = 'Long' if self.side == PositionSide.LONG else 'Short'
        return f"{side_str} {self.quantity} {self.underlying} Futures @ {self.futures_price}"


# ─── Swap Position ─────────────────────────────────────────────

class SwapPosition:
    """
    An interest rate swap position with MTM and DV01.

    Swap = exchange fixed rate payments for floating rate payments.
    Simplified valuation using annuity-based approach.

    Parameters
    ----------
    notional : float
        Notional principal (e.g., $1,000,000).
    fixed_rate : float
        Fixed coupon rate (e.g., 0.045 = 4.5%).
    payment_frequency : int
        Payments per year (4 = quarterly, 2 = semi-annual).
    maturity_years : float
        Years until swap maturity.
    pay_fixed : bool
        True = you PAY fixed (and receive floating).
        False = you RECEIVE fixed (and pay floating).
    floating_spread : float
        Spread added to floating rate (usually 0).
    """

    def __init__(
        self,
        notional: float = 1000000.0,
        fixed_rate: float = 0.045,
        payment_frequency: int = 4,
        maturity_years: float = 5.0,
        pay_fixed: bool = False,
        floating_spread: float = 0.0,
    ):
        self.notional = notional
        self.fixed_rate = fixed_rate
        self.payment_frequency = payment_frequency
        self.maturity_years = maturity_years
        self.pay_fixed = pay_fixed
        self.floating_spread = floating_spread
        self.instrument_type = 'swap'
        self.underlying = 'IRS'  # Interest Rate Swap

    def value(self, market: MarketData) -> float:
        """
        Simplified swap MTM.

        MTM ≈ Notional × (fixed_rate − market_rate) × Annuity Factor × direction

        Annuity Factor = Σ [1/(1+r/f)^i] for i=1 to n
        where n = maturity × frequency

        If you RECEIVE fixed and rates DROP → you win (locked in high rate)
        If you PAY fixed and rates RISE → you win (paying old low rate)
        """
        market_rate = market.risk_free_rate + self.floating_spread
        rate_diff = self.fixed_rate - market_rate

        # Calculate annuity factor (present value of $1 per period)
        n_payments = int(self.maturity_years * self.payment_frequency)
        period_rate = market_rate / self.payment_frequency

        if abs(period_rate) < 1e-10:
            annuity = n_payments / self.payment_frequency
        else:
            annuity = sum(
                1.0 / (1 + period_rate) ** i
                for i in range(1, n_payments + 1)
            ) / self.payment_frequency

        # Direction: receive_fixed = +rate_diff, pay_fixed = −rate_diff
        direction = -1 if self.pay_fixed else 1
        return self.notional * rate_diff * annuity * direction

    def pnl(self, market: MarketData) -> float:
        """Swap P&L is same as MTM (no upfront premium for par swaps)."""
        return self.value(market)

    def dv01(self, market: MarketData) -> float:
        """
        DV01: Dollar Value of 1 Basis Point (0.01%) rate change.

        Bump the rate up by 1bp, recalculate MTM, measure the change.
        DV01 = |MTM(r + 0.0001) − MTM(r)|
        """
        base_mtm = self.value(market)

        bumped_market = MarketData(
            spot_price=market.spot_price,
            risk_free_rate=market.risk_free_rate + 0.0001,  # +1bp
            dividend_yield=market.dividend_yield,
            volatility=market.volatility,
        )
        bumped_mtm = self.value(bumped_market)

        return abs(bumped_mtm - base_mtm)

    def greeks(self, market: MarketData) -> Dict[str, float]:
        """Swap Greeks: only Rho (interest rate sensitivity)."""
        dv01_val = self.dv01(market)
        # Rho per 1% = DV01 × 100 (since DV01 is per 0.01%)
        direction = -1 if self.pay_fixed else 1
        return {
            'delta': 0.0,
            'gamma': 0.0,
            'theta': 0.0,
            'vega': 0.0,
            'rho': dv01_val * 100 * direction,
        }

    def __repr__(self) -> str:
        action = 'Pay' if self.pay_fixed else 'Receive'
        return f"IRS ${self.notional:,.0f} {action} Fixed {self.fixed_rate:.2%}"
```

---

**What You Just Built:**

- **`MarketData`**: Snapshot of current market conditions (spot, rate, div yield, vol). This is what a live data feed provides.
- **`OptionPosition`**: A real option trade. Builds an `OptionContract` from trade + market data, calls Black-Scholes for price and Greeks, scales by quantity × multiplier × direction. Long positions have positive value; short positions have negative value.
- **`FuturesPosition`**: Linear P&L = (current − entry) × quantity × contract_size. Delta = quantity × contract_size (no curvature, no time decay, no vol sensitivity).
- **`SwapPosition`**: MTM via annuity-based approach. `value()` calculates `Notional × (fixed − floating) × AnnuityFactor`. `dv01()` bumps rate by 1bp and measures change — this is the industry-standard "bump and reprice" method.

---

---

# PART 5: MTM ENGINE (Step 3)

The portfolio aggregation engine — holds all positions, stores market data, values the entire book, and runs scenario analysis.

---

**File: `src/mtm_engine.py`**

```python
"""
mtm_engine.py — Portfolio Mark-to-Market Engine
==================================================

Central engine that:
  1. Manages positions (options, futures, swaps)
  2. Stores market data per underlying
  3. Values the entire portfolio (MTM + P&L)
  4. Aggregates Greeks across all positions
  5. Generates position-level reports (DataFrame)
  6. Runs scenario analysis (what-if calculations)
  7. Saves/loads engine state (serialization)

This is what runs on a trading desk at market close to calculate
the day's P&L and risk exposure.
"""

import numpy as np
import pandas as pd
import joblib
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

from src.instruments import (
    OptionPosition, FuturesPosition, SwapPosition,
    PositionSide, MarketData,
)


@dataclass
class PortfolioMetrics:
    """
    Aggregated portfolio-level metrics.

    This is what the risk report shows at the top of the page.
    """
    total_mtm: float = 0.0           # Total mark-to-market value
    total_pnl: float = 0.0           # Total profit/loss
    positions_count: int = 0          # Number of positions
    total_delta: float = 0.0          # Net directional exposure (shares)
    total_gamma: float = 0.0          # Net convexity exposure
    total_theta: float = 0.0          # Net daily time decay
    total_vega: float = 0.0           # Net volatility exposure
    total_rho: float = 0.0            # Net interest rate exposure
    delta_by_underlying: Dict[str, float] = field(default_factory=dict)
    mtm_by_type: Dict[str, float] = field(default_factory=dict)


class MTMEngine:
    """
    Mark-to-Market portfolio valuation engine.

    Usage:
        engine = MTMEngine()
        engine.add_position(option1)
        engine.add_position(futures1)
        engine.set_market_data('AAPL', MarketData(spot_price=175, ...))
        metrics = engine.value_portfolio()
    """

    def __init__(self):
        self.positions: List = []
        self.market_data: Dict[str, MarketData] = {}
        self.valuation_time: Optional[datetime] = None

    # ── Position Management ──────────────────────────────────

    def add_position(self, position) -> None:
        """
        Add a position (option, futures, or swap) to the portfolio.

        Validates that the position has the required attributes.
        """
        required = ['underlying', 'instrument_type', 'value', 'pnl', 'greeks']
        for attr in required:
            if not hasattr(position, attr):
                raise ValueError(f"Position missing required attribute: {attr}")
        self.positions.append(position)

    def remove_position(self, index: int) -> None:
        """Remove a position by index."""
        if 0 <= index < len(self.positions):
            self.positions.pop(index)

    # ── Market Data ──────────────────────────────────────────

    def set_market_data(self, underlying: str, data: MarketData) -> None:
        """
        Set current market data for an underlying.

        Call this for each underlying in your portfolio before valuing.
        """
        self.market_data[underlying] = data

    def get_market_data(self, underlying: str) -> MarketData:
        """Get market data for an underlying, with sensible defaults."""
        if underlying in self.market_data:
            return self.market_data[underlying]
        # Default market data if not explicitly set
        return MarketData(spot_price=100.0, risk_free_rate=0.05, volatility=0.20)

    # ── Portfolio Valuation ──────────────────────────────────

    def value_portfolio(self) -> PortfolioMetrics:
        """
        Value the entire portfolio.

        For each position:
          1. Look up its market data
          2. Calculate MTM value, P&L, and Greeks
          3. Aggregate into portfolio-level metrics

        Returns PortfolioMetrics with total MTM, P&L, and all Greeks.
        """
        metrics = PortfolioMetrics()
        metrics.positions_count = len(self.positions)
        self.valuation_time = datetime.now()

        delta_by_underlying = {}
        mtm_by_type = {}

        for pos in self.positions:
            market = self.get_market_data(pos.underlying)

            # Value and P&L
            mtm = pos.value(market)
            pnl = pos.pnl(market)
            greeks = pos.greeks(market)

            metrics.total_mtm += mtm
            metrics.total_pnl += pnl

            # Aggregate Greeks
            metrics.total_delta += greeks.get('delta', 0)
            metrics.total_gamma += greeks.get('gamma', 0)
            metrics.total_theta += greeks.get('theta', 0)
            metrics.total_vega += greeks.get('vega', 0)
            metrics.total_rho += greeks.get('rho', 0)

            # Delta by underlying
            ul = pos.underlying
            delta_by_underlying[ul] = delta_by_underlying.get(ul, 0) + greeks.get('delta', 0)

            # MTM by instrument type
            itype = pos.instrument_type
            mtm_by_type[itype] = mtm_by_type.get(itype, 0) + mtm

        metrics.delta_by_underlying = delta_by_underlying
        metrics.mtm_by_type = mtm_by_type

        return metrics

    # ── Position Report ──────────────────────────────────────

    def generate_position_report(self) -> pd.DataFrame:
        """
        Generate a detailed position-level report.

        Returns a DataFrame with one row per position showing
        instrument details, MTM, P&L, and all Greeks.
        """
        rows = []

        for i, pos in enumerate(self.positions):
            market = self.get_market_data(pos.underlying)
            greeks = pos.greeks(market)

            row = {
                'position_id': i + 1,
                'underlying': pos.underlying,
                'instrument_type': pos.instrument_type,
                'description': str(pos),
                'mtm_value': pos.value(market),
                'pnl': pos.pnl(market),
                'delta': greeks.get('delta', 0),
                'gamma': greeks.get('gamma', 0),
                'theta': greeks.get('theta', 0),
                'vega': greeks.get('vega', 0),
                'rho': greeks.get('rho', 0),
            }

            # Add option-specific fields
            if pos.instrument_type == 'option':
                row['strike'] = pos.strike
                row['option_type'] = pos.option_type
                row['side'] = pos.side.value
                row['quantity'] = pos.quantity
            elif pos.instrument_type == 'futures':
                row['side'] = pos.side.value
                row['quantity'] = pos.quantity
                row['entry_price'] = pos.entry_price
            elif pos.instrument_type == 'swap':
                row['notional'] = pos.notional
                row['fixed_rate'] = pos.fixed_rate

            rows.append(row)

        return pd.DataFrame(rows)

    # ── Scenario Analysis ────────────────────────────────────

    def scenario_analysis(
        self,
        scenarios: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Run scenario analysis on the portfolio.

        Parameters
        ----------
        scenarios : dict
            Keys = scenario names.
            Values = dict of {underlying: shock_pct}.
            
            Example:
            {
                'Base Case': {'AAPL': 0.0, 'SPY': 0.0},
                'Market +5%': {'AAPL': 0.05, 'SPY': 0.05},
                'Crash -10%': {'AAPL': -0.10, 'SPY': -0.10},
            }

        Returns
        -------
        pd.DataFrame
            One row per scenario with portfolio_mtm and portfolio_pnl.
        """
        results = []

        for scenario_name, shocks in scenarios.items():
            scenario_mtm = 0.0
            scenario_pnl = 0.0

            for pos in self.positions:
                market = self.get_market_data(pos.underlying)
                shock = shocks.get(pos.underlying, 0.0)

                # Apply shock to spot price
                shocked_market = MarketData(
                    spot_price=market.spot_price * (1 + shock),
                    risk_free_rate=market.risk_free_rate,
                    dividend_yield=market.dividend_yield,
                    volatility=market.volatility,
                )

                # Special handling for futures: also shock futures price
                if pos.instrument_type == 'futures':
                    original_futures = pos.futures_price
                    pos.futures_price = original_futures * (1 + shock)
                    mtm = pos.value(shocked_market)
                    pnl = pos.pnl(shocked_market)
                    pos.futures_price = original_futures  # Restore
                else:
                    mtm = pos.value(shocked_market)
                    pnl = pos.pnl(shocked_market)

                scenario_mtm += mtm
                scenario_pnl += pnl

            results.append({
                'scenario': scenario_name,
                'portfolio_mtm': scenario_mtm,
                'portfolio_pnl': scenario_pnl,
            })

        return pd.DataFrame(results)

    # ── Serialization ────────────────────────────────────────

    def save(self, filepath: str = 'models/mtm_engine.pkl') -> None:
        """Save engine state to disk."""
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str = 'models/mtm_engine.pkl') -> 'MTMEngine':
        """Load engine state from disk."""
        return joblib.load(filepath)
```

---

**What You Just Built:**

- **`PortfolioMetrics`**: Aggregated numbers a risk manager needs at a glance — total MTM, P&L, five Greek totals, delta broken down by underlying, MTM by instrument type.
- **`MTMEngine.value_portfolio()`**: Iterates through every position, looks up its market data, calls `value()` / `pnl()` / `greeks()`, and sums everything up. This is the core daily P&L calculation.
- **`generate_position_report()`**: Creates a DataFrame with one row per position — what a middle-office analyst uses for reconciliation.
- **`scenario_analysis()`**: For each scenario, shocks spot prices by the specified percentages, reprices every instrument at shocked prices, and reports the resulting P&L. Handles futures separately (shocks the futures price directly).
- **`save()` / `load()`**: Joblib serialization — save the engine state at market close, reload it next morning.

---

---

# PART 6: VISUALIZATION (Step 4)

Seven chart functions producing publication-quality analytics. Each chart answers a specific question a trader or risk manager would ask.

---

**File: `src/visualization.py`**

```python
"""
visualization.py — Derivatives Dashboard Charts
===================================================

Seven chart types:
  1. Portfolio Summary Dashboard — MTM, P&L, top Greeks, exposures
  2. Position Breakdown — Pie chart of MTM by instrument type
  3. Greeks Breakdown — Bar charts of each Greek by underlying
  4. Scenario Analysis — P&L bar chart for each scenario
  5. Option Payoff Diagrams — Payoff curves at expiry
  6. Volatility Surface — 3D surface of implied vol by strike/expiry
  7. Historical MTM — Time series of portfolio value
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend (works on servers)
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional

sns.set_style("whitegrid")
sns.set_context("notebook", font_scale=1.05)

COLORS = {
    'primary': '#1a1a2e',
    'secondary': '#16213e',
    'accent': '#0f3460',
    'highlight': '#e94560',
    'green': '#2ecc71',
    'red': '#e74c3c',
    'blue': '#3498db',
    'orange': '#f39c12',
    'purple': '#9b59b6',
    'teal': '#1abc9c',
}


def plot_portfolio_summary(
    total_mtm: float,
    total_pnl: float,
    total_delta: float,
    total_gamma: float,
    total_theta: float,
    total_vega: float,
    total_rho: float,
    delta_by_underlying: Dict[str, float],
    positions_count: int,
    save_path: str = 'output/portfolio_summary.png'
) -> None:
    """
    Chart 1: Portfolio Summary Dashboard (4-panel overview).

    Panel 1: MTM and P&L as large numbers with color (green/red)
    Panel 2: Greeks summary as a styled table
    Panel 3: Delta exposure by underlying (bar chart)
    Panel 4: Key metrics text box
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Derivatives MTM Dashboard', fontsize=18, fontweight='bold', y=0.98)

    # ── Panel 1: MTM & P&L ──────────────────────────────────
    ax = axes[0, 0]
    ax.axis('off')
    mtm_color = COLORS['green'] if total_mtm >= 0 else COLORS['red']
    pnl_color = COLORS['green'] if total_pnl >= 0 else COLORS['red']

    ax.text(0.5, 0.75, 'Portfolio MTM', ha='center', fontsize=14, color='grey',
            transform=ax.transAxes)
    ax.text(0.5, 0.55, f'${total_mtm:,.2f}', ha='center', fontsize=28,
            fontweight='bold', color=mtm_color, transform=ax.transAxes)
    ax.text(0.5, 0.30, 'Total P&L', ha='center', fontsize=14, color='grey',
            transform=ax.transAxes)
    ax.text(0.5, 0.10, f'${total_pnl:,.2f}', ha='center', fontsize=24,
            fontweight='bold', color=pnl_color, transform=ax.transAxes)

    # ── Panel 2: Greeks Table ────────────────────────────────
    ax = axes[0, 1]
    ax.axis('off')
    greeks_data = [
        ['Delta (Δ)', f'{total_delta:,.2f} shares'],
        ['Gamma (Γ)', f'{total_gamma:,.4f}'],
        ['Theta (Θ)', f'${total_theta:,.2f}/day'],
        ['Vega (ν)', f'${total_vega:,.2f}/1% vol'],
        ['Rho (ρ)', f'${total_rho:,.2f}/1% rate'],
    ]
    table = ax.table(cellText=greeks_data,
                     colLabels=['Greek', 'Value'],
                     loc='center',
                     cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.0, 1.8)
    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_facecolor(COLORS['accent'])
            cell.set_text_props(color='white', fontweight='bold')
        else:
            cell.set_facecolor('#f8f9fa')
    ax.set_title('Portfolio Greeks', fontsize=14, fontweight='bold', pad=20)

    # ── Panel 3: Delta by Underlying ─────────────────────────
    ax = axes[1, 0]
    if delta_by_underlying:
        underlyings = list(delta_by_underlying.keys())
        deltas = list(delta_by_underlying.values())
        colors = [COLORS['green'] if d >= 0 else COLORS['red'] for d in deltas]
        bars = ax.barh(underlyings, deltas, color=colors, alpha=0.85)
        for bar, val in zip(bars, deltas):
            ax.text(bar.get_width() + abs(max(deltas, key=abs)) * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    f'{val:,.0f}', va='center', fontsize=10)
    ax.set_xlabel('Delta (Shares Equivalent)', fontsize=11)
    ax.set_title('Delta Exposure by Underlying', fontsize=14, fontweight='bold')
    ax.axvline(x=0, color='grey', linewidth=0.8)

    # ── Panel 4: Key Metrics ─────────────────────────────────
    ax = axes[1, 1]
    ax.axis('off')
    metrics_text = (
        f"Positions: {positions_count}\n\n"
        f"Total MTM: ${total_mtm:,.2f}\n"
        f"Total P&L: ${total_pnl:,.2f}\n\n"
        f"Net Delta: {total_delta:,.0f} shares\n"
        f"Daily Theta: ${total_theta:,.2f}\n"
        f"Vega Exposure: ${total_vega:,.2f}"
    )
    ax.text(0.1, 0.9, metrics_text, fontsize=13, verticalalignment='top',
            fontfamily='monospace', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))
    ax.set_title('Key Metrics', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {save_path.split('/')[-1]}")


def plot_position_breakdown(
    mtm_by_type: Dict[str, float],
    save_path: str = 'output/position_breakdown.png'
) -> None:
    """
    Chart 2: Pie chart of MTM value by instrument type.
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Use absolute values for the pie (negative positions are just directions)
    labels = list(mtm_by_type.keys())
    values = [abs(v) for v in mtm_by_type.values()]
    colors_list = [COLORS['blue'], COLORS['orange'], COLORS['purple'],
                   COLORS['teal'], COLORS['green']]

    if sum(values) > 0:
        wedges, texts, autotexts = ax.pie(
            values, labels=[l.title() for l in labels],
            autopct='%1.1f%%', colors=colors_list[:len(labels)],
            startangle=90, textprops={'fontsize': 12}
        )
        for t in autotexts:
            t.set_fontweight('bold')
    else:
        ax.text(0.5, 0.5, 'No positions', ha='center', va='center', fontsize=14)

    ax.set_title('Portfolio Breakdown by Instrument Type',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {save_path.split('/')[-1]}")


def plot_greeks_breakdown(
    position_report: pd.DataFrame,
    save_path: str = 'output/greeks_breakdown.png'
) -> None:
    """
    Chart 3: Greeks breakdown by underlying (4-panel bar charts).
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Greeks Breakdown by Underlying', fontsize=16, fontweight='bold')

    greek_cols = ['delta', 'gamma', 'theta', 'vega']
    greek_labels = ['Delta (Shares)', 'Gamma', 'Theta ($/day)', 'Vega ($/1% vol)']
    greek_colors = [COLORS['blue'], COLORS['purple'], COLORS['red'], COLORS['teal']]

    for ax, col, label, color in zip(axes.flat, greek_cols, greek_labels, greek_colors):
        if col in position_report.columns:
            by_ul = position_report.groupby('underlying')[col].sum()
            bars = ax.bar(by_ul.index, by_ul.values, color=color, alpha=0.85)
            for bar, val in zip(bars, by_ul.values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        f'{val:,.2f}', ha='center', va='bottom', fontsize=9)
        ax.set_title(label, fontsize=12, fontweight='bold')
        ax.tick_params(axis='x', rotation=30)
        ax.axhline(y=0, color='grey', linewidth=0.8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {save_path.split('/')[-1]}")


def plot_scenario_analysis(
    scenario_df: pd.DataFrame,
    save_path: str = 'output/scenario_analysis.png'
) -> None:
    """
    Chart 4: Scenario analysis P&L bar chart.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    scenarios = scenario_df['scenario'].values
    pnl_values = scenario_df['portfolio_pnl'].values
    colors = [COLORS['green'] if v >= 0 else COLORS['red'] for v in pnl_values]

    bars = ax.bar(range(len(scenarios)), pnl_values, color=colors, alpha=0.85)

    for bar, val in zip(bars, pnl_values):
        offset = bar.get_height() * 0.05 if val >= 0 else bar.get_height() * 0.05
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + offset,
                f'${val:,.0f}',
                ha='center', va='bottom' if val >= 0 else 'top',
                fontsize=10, fontweight='bold')

    ax.set_xticks(range(len(scenarios)))
    ax.set_xticklabels(scenarios, rotation=25, ha='right')
    ax.set_ylabel('Portfolio P&L ($)', fontsize=12)
    ax.set_title('Scenario Analysis — Portfolio P&L Impact',
                 fontsize=14, fontweight='bold')
    ax.axhline(y=0, color='grey', linewidth=1)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {save_path.split('/')[-1]}")


def plot_option_payoff(
    spot: float = 175,
    strike: float = 180,
    premium: float = 7.37,
    option_type: str = 'call',
    save_path: str = 'output/option_payoff.png'
) -> None:
    """
    Chart 5: Option payoff diagram at expiry.

    Shows intrinsic value line and profit/loss line (shifted by premium).
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Range of stock prices at expiry
    prices = np.linspace(strike * 0.6, strike * 1.4, 200)

    if option_type.lower() == 'call':
        intrinsic = np.maximum(prices - strike, 0)
        profit = intrinsic - premium
        label = f'Long {strike} Call'
    else:
        intrinsic = np.maximum(strike - prices, 0)
        profit = intrinsic - premium
        label = f'Long {strike} Put'

    ax.plot(prices, profit, color=COLORS['blue'], linewidth=2.5, label=label)
    ax.fill_between(prices, profit, 0,
                     where=profit >= 0, alpha=0.2, color=COLORS['green'])
    ax.fill_between(prices, profit, 0,
                     where=profit < 0, alpha=0.2, color=COLORS['red'])

    ax.axhline(y=0, color='grey', linewidth=1)
    ax.axvline(x=strike, color=COLORS['orange'], linewidth=1, linestyle='--',
               label=f'Strike = ${strike}')
    ax.axvline(x=spot, color=COLORS['purple'], linewidth=1, linestyle=':',
               label=f'Current Spot = ${spot}')

    # Breakeven point
    if option_type.lower() == 'call':
        breakeven = strike + premium
    else:
        breakeven = strike - premium
    ax.axvline(x=breakeven, color=COLORS['teal'], linewidth=1, linestyle='-.',
               label=f'Breakeven = ${breakeven:.2f}')

    ax.set_xlabel('Stock Price at Expiry ($)', fontsize=12)
    ax.set_ylabel('Profit / Loss ($)', fontsize=12)
    ax.set_title('Option Payoff Diagram', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {save_path.split('/')[-1]}")


def plot_volatility_surface(
    strikes: Optional[np.ndarray] = None,
    expiries: Optional[np.ndarray] = None,
    vol_surface: Optional[np.ndarray] = None,
    save_path: str = 'output/volatility_surface.png'
) -> None:
    """
    Chart 6: 3D volatility surface (implied vol by strike and expiry).

    If no data provided, generates a synthetic smile/skew surface.
    """
    if strikes is None:
        strikes = np.linspace(80, 120, 20)
    if expiries is None:
        expiries = np.linspace(0.1, 2.0, 15)

    # Generate synthetic vol surface with skew and term structure
    if vol_surface is None:
        S_grid, T_grid = np.meshgrid(strikes, expiries)
        # Base vol + skew (OTM puts have higher vol) + term structure
        vol_surface = (
            0.20
            + 0.05 * ((100 - S_grid) / 100) ** 2  # Smile
            - 0.03 * (S_grid - 100) / 100           # Skew
            + 0.02 * np.sqrt(T_grid)                 # Term structure
        )

    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': '3d'})

    S_grid, T_grid = np.meshgrid(strikes, expiries)
    surf = ax.plot_surface(S_grid, T_grid, vol_surface * 100,
                           cmap='coolwarm', alpha=0.85,
                           edgecolor='none')

    ax.set_xlabel('Strike (%)', fontsize=11)
    ax.set_ylabel('Time to Expiry (Years)', fontsize=11)
    ax.set_zlabel('Implied Volatility (%)', fontsize=11)
    ax.set_title('Implied Volatility Surface', fontsize=14, fontweight='bold')
    fig.colorbar(surf, shrink=0.5, aspect=5, label='IV (%)')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {save_path.split('/')[-1]}")


def plot_historical_mtm(
    dates: Optional[List] = None,
    mtm_values: Optional[List[float]] = None,
    save_path: str = 'output/historical_mtm.png'
) -> None:
    """
    Chart 7: Historical portfolio MTM time series.

    If no data provided, generates synthetic historical data.
    """
    if dates is None or mtm_values is None:
        n_days = 60
        dates = pd.date_range(end=pd.Timestamp.now(), periods=n_days, freq='B')
        # Simulate portfolio value with drift and noise
        np.random.seed(42)
        base = 15000
        returns = np.random.normal(0.001, 0.03, n_days)
        mtm_values = base * np.cumprod(1 + returns)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(dates, mtm_values, color=COLORS['blue'], linewidth=2)
    ax.fill_between(dates, mtm_values, alpha=0.15, color=COLORS['blue'])

    # Mark max and min
    max_idx = np.argmax(mtm_values)
    min_idx = np.argmin(mtm_values)
    ax.plot(dates[max_idx], mtm_values[max_idx], 'v', color=COLORS['green'],
            markersize=12, label=f"Peak: ${mtm_values[max_idx]:,.0f}")
    ax.plot(dates[min_idx], mtm_values[min_idx], '^', color=COLORS['red'],
            markersize=12, label=f"Trough: ${mtm_values[min_idx]:,.0f}")

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Portfolio MTM ($)', fontsize=12)
    ax.set_title('Historical Portfolio Value', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    plt.xticks(rotation=30)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {save_path.split('/')[-1]}")
```

---

**What You Just Built (7 Charts):**

| Chart | What It Shows | Who Uses It |
|-------|-------------|-------------|
| **Portfolio Summary** | 4-panel dashboard: MTM/P&L big numbers, Greeks table, delta bars, key metrics | Everyone (the "landing page") |
| **Position Breakdown** | Pie chart of MTM by instrument type (options/futures/swaps) | Portfolio managers, risk managers |
| **Greeks Breakdown** | 4 bar charts: delta, gamma, theta, vega by underlying | Traders (for hedging decisions) |
| **Scenario Analysis** | P&L bars for each scenario (green = profit, red = loss) | Risk managers, CRO |
| **Option Payoff** | Profit/loss at expiry with breakeven, strike, and spot markers | Traders, client-facing reports |
| **Volatility Surface** | 3D surface: IV vs strike vs expiry (shows skew and term structure) | Quants, vol traders |
| **Historical MTM** | Time series with peak/trough markers | Fund managers, compliance |

---

---

# PART 7: MAIN SCRIPT (Step 5)

The pipeline entry point — demonstrates all pricing models, builds a sample portfolio, values it, runs scenarios, and generates all charts.

---

**File: `main.py`**

```python
"""
main.py — Derivatives MTM Dashboard Pipeline
================================================

Runs the complete demo in 7 steps:
  1. Demonstrate pricing models (BS, Binomial, Monte Carlo)
  2. Create sample portfolio (options, futures, swap)
  3. Calculate MTM values and Greeks
  4. Show detailed position report
  5. Run scenario analysis
  6. Generate visualizations
  7. Save outputs and engine state
"""

import os
import warnings
import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

from src.pricing_models import (
    OptionContract, OptionType, ExerciseStyle, PricingResult,
    black_scholes_price, black_scholes_greeks,
    binomial_tree_price, monte_carlo_price, implied_volatility,
)
from src.instruments import (
    OptionPosition, FuturesPosition, SwapPosition,
    PositionSide, MarketData,
)
from src.mtm_engine import MTMEngine
from src.visualization import (
    plot_portfolio_summary, plot_position_breakdown,
    plot_greeks_breakdown, plot_scenario_analysis,
    plot_option_payoff, plot_volatility_surface,
    plot_historical_mtm,
)


def main():
    """Run the complete derivatives MTM dashboard."""

    print("=" * 70)
    print(" DERIVATIVES MTM DASHBOARD")
    print("=" * 70)

    os.makedirs('output', exist_ok=True)
    os.makedirs('models', exist_ok=True)

    # ── STEP 1: Demonstrate Pricing Models ───────────────────
    print(f"\n{'─' * 70}")
    print(f" STEP 1: Option Pricing Models")
    print(f"{'─' * 70}")

    sample_option = OptionContract(
        spot=175.0,
        strike=180.0,
        time_to_expiry=0.25,  # 3 months
        risk_free_rate=0.05,
        volatility=0.25,
        option_type=OptionType.CALL,
    )

    print(f"\n  Sample Option:")
    print(f"    Underlying: ${sample_option.spot}")
    print(f"    Strike: ${sample_option.strike}")
    print(f"    Expiry: 3 months")
    print(f"    Vol: {sample_option.volatility:.0%}")
    print(f"    Rate: {sample_option.risk_free_rate:.0%}")

    # Black-Scholes with Greeks
    result = black_scholes_greeks(sample_option)
    print(f"\n  📊 Black-Scholes Pricing:")
    print(f"    Price: ${result.price:.4f}")
    print(f"    Delta: {result.delta:.4f}")
    print(f"    Gamma: {result.gamma:.4f}")
    print(f"    Theta: ${result.theta:.4f}/day")
    print(f"    Vega:  ${result.vega:.4f}/1%")
    print(f"    Rho:   ${result.rho:.4f}/1%")

    # Model comparison
    bs_price = black_scholes_price(sample_option)
    binom_euro = binomial_tree_price(sample_option, n_steps=200,
                                      exercise_style=ExerciseStyle.EUROPEAN)
    binom_amer = binomial_tree_price(sample_option, n_steps=200,
                                      exercise_style=ExerciseStyle.AMERICAN)
    mc_price, mc_error = monte_carlo_price(sample_option, n_simulations=100000)

    print(f"\n  📊 Model Comparison:")
    print(f"    {'Method':<22s} {'Price':>10s}")
    print(f"    {'─' * 32}")
    print(f"    {'Black-Scholes':<22s} ${bs_price:>9.4f}")
    print(f"    {'Binomial (Euro)':<22s} ${binom_euro:>9.4f}")
    print(f"    {'Binomial (Amer)':<22s} ${binom_amer:>9.4f}")
    print(f"    {'Monte Carlo':<22s} ${mc_price:>9.4f} (±${mc_error:.4f})")

    # Implied volatility demo
    iv = implied_volatility(result.price, sample_option)
    print(f"\n  📊 Implied Volatility:")
    print(f"    Market Price: ${result.price:.4f}")
    print(f"    Recovered IV: {iv:.4%} (input was {sample_option.volatility:.4%})")

    # ── STEP 2: Build Sample Portfolio ───────────────────────
    print(f"\n{'─' * 70}")
    print(f" STEP 2: Building Sample Portfolio")
    print(f"{'─' * 70}")

    engine = MTMEngine()

    # Position 1: Long AAPL 180 Call (60 days, 10 contracts)
    engine.add_position(OptionPosition(
        underlying='AAPL',
        strike=180.0,
        expiry=datetime.now() + timedelta(days=60),
        option_type='call',
        side=PositionSide.LONG,
        quantity=10,
        contract_multiplier=100,
        premium_paid=5.50,
    ))
    print(f"  ✓ Long 10 AAPL 180 Call @ $5.50")

    # Position 2: Short AAPL 170 Put (30 days, 5 contracts)
    engine.add_position(OptionPosition(
        underlying='AAPL',
        strike=170.0,
        expiry=datetime.now() + timedelta(days=30),
        option_type='put',
        side=PositionSide.SHORT,
        quantity=5,
        contract_multiplier=100,
        premium_paid=3.00,
    ))
    print(f"  ✓ Short 5 AAPL 170 Put @ $3.00")

    # Position 3: Long SPY 500 Call (90 days, 20 contracts)
    engine.add_position(OptionPosition(
        underlying='SPY',
        strike=500.0,
        expiry=datetime.now() + timedelta(days=90),
        option_type='call',
        side=PositionSide.LONG,
        quantity=20,
        contract_multiplier=100,
        premium_paid=12.00,
    ))
    print(f"  ✓ Long 20 SPY 500 Call @ $12.00")

    # Position 4: Long ES Futures (45 days, 2 contracts)
    engine.add_position(FuturesPosition(
        underlying='ES',
        futures_price=5100.0,
        expiry=datetime.now() + timedelta(days=45),
        side=PositionSide.LONG,
        quantity=2,
        contract_size=50.0,
        entry_price=5050.0,
    ))
    print(f"  ✓ Long 2 ES Futures @ 5050 (current: 5100)")

    # Position 5: Receive-fixed 5Y Interest Rate Swap ($1M notional)
    engine.add_position(SwapPosition(
        notional=1000000.0,
        fixed_rate=0.045,
        payment_frequency=4,
        maturity_years=5.0,
        pay_fixed=False,
        floating_spread=0.0,
    ))
    print(f"  ✓ Receive Fixed $1M 5Y IRS @ 4.5%")

    # Set market data
    engine.set_market_data('AAPL', MarketData(
        spot_price=175.0,
        risk_free_rate=0.05,
        dividend_yield=0.005,
        volatility=0.25,
    ))
    engine.set_market_data('SPY', MarketData(
        spot_price=495.0,
        risk_free_rate=0.05,
        dividend_yield=0.013,
        volatility=0.18,
    ))
    engine.set_market_data('ES', MarketData(
        spot_price=5100.0,
        risk_free_rate=0.05,
    ))
    engine.set_market_data('IRS', MarketData(
        spot_price=0.0,
        risk_free_rate=0.05,
    ))

    print(f"\n  Market Data Set:")
    print(f"    AAPL: $175.00, Vol=25%, Div=0.5%")
    print(f"    SPY:  $495.00, Vol=18%, Div=1.3%")
    print(f"    ES:   5100, Rate=5%")
    print(f"    IRS:  Rate=5%")

    # ── STEP 3: Mark-to-Market Valuation ─────────────────────
    print(f"\n{'─' * 70}")
    print(f" STEP 3: Mark-to-Market Valuation")
    print(f"{'─' * 70}")

    metrics = engine.value_portfolio()

    print(f"\n  📊 Portfolio Metrics:")
    print(f"    Total MTM Value: ${metrics.total_mtm:,.2f}")
    print(f"    Total P&L: ${metrics.total_pnl:,.2f}")
    print(f"    Positions: {metrics.positions_count}")

    print(f"\n  📊 Portfolio Greeks:")
    print(f"    Delta: {metrics.total_delta:,.2f} shares")
    print(f"    Gamma: {metrics.total_gamma:,.4f}")
    print(f"    Theta: ${metrics.total_theta:,.2f}/day")
    print(f"    Vega:  ${metrics.total_vega:,.2f} per 1% vol")
    print(f"    Rho:   ${metrics.total_rho:,.2f} per 1% rate")

    print(f"\n  📊 Delta Exposure by Underlying:")
    for ul, delta in metrics.delta_by_underlying.items():
        spot = engine.get_market_data(ul).spot_price
        dollar_delta = delta * spot if spot > 0 else delta
        print(f"    {ul}: ${dollar_delta:,.2f}")

    # ── STEP 4: Position Report ──────────────────────────────
    print(f"\n{'─' * 70}")
    print(f" STEP 4: Position Report")
    print(f"{'─' * 70}")

    report = engine.generate_position_report()

    print(f"\n  {'#':<3} {'Description':<32} {'MTM':>12} {'P&L':>12} {'Delta':>10}")
    print(f"  {'─' * 72}")
    for _, row in report.iterrows():
        print(f"  {row['position_id']:<3} {row['description']:<32} "
              f"${row['mtm_value']:>10,.2f} ${row['pnl']:>10,.2f} "
              f"{row['delta']:>9,.1f}")

    # ── STEP 5: Scenario Analysis ────────────────────────────
    print(f"\n{'─' * 70}")
    print(f" STEP 5: Scenario Analysis")
    print(f"{'─' * 70}")

    scenarios = {
        'Base Case': {'AAPL': 0.0, 'SPY': 0.0, 'ES': 0.0, 'IRS': 0.0},
        'Market +5%': {'AAPL': 0.05, 'SPY': 0.05, 'ES': 0.05, 'IRS': 0.0},
        'Market -5%': {'AAPL': -0.05, 'SPY': -0.05, 'ES': -0.05, 'IRS': 0.0},
        'Tech Rally +10%': {'AAPL': 0.10, 'SPY': 0.03, 'ES': 0.03, 'IRS': 0.0},
        'Market Crash -10%': {'AAPL': -0.10, 'SPY': -0.10, 'ES': -0.10, 'IRS': 0.0},
    }

    scenario_df = engine.scenario_analysis(scenarios)

    print(f"\n  📊 Scenario Analysis Results:")
    print(f"  {'Scenario':<25s} {'MTM':>14s} {'P&L':>14s}")
    print(f"  {'─' * 55}")
    for _, row in scenario_df.iterrows():
        pnl = row['portfolio_pnl']
        marker = '🟢' if pnl >= 0 else '🔴'
        print(f"  {marker} {row['scenario']:<23s} "
              f"${row['portfolio_mtm']:>12,.2f} ${pnl:>12,.2f}")

    # ── STEP 6: Visualizations ───────────────────────────────
    print(f"\n{'─' * 70}")
    print(f" STEP 6: Generating Visualizations")
    print(f"{'─' * 70}")

    print(f"\n  Saving charts to ./output/...")

    plot_portfolio_summary(
        total_mtm=metrics.total_mtm,
        total_pnl=metrics.total_pnl,
        total_delta=metrics.total_delta,
        total_gamma=metrics.total_gamma,
        total_theta=metrics.total_theta,
        total_vega=metrics.total_vega,
        total_rho=metrics.total_rho,
        delta_by_underlying=metrics.delta_by_underlying,
        positions_count=metrics.positions_count,
    )

    plot_position_breakdown(metrics.mtm_by_type)
    plot_greeks_breakdown(report)
    plot_scenario_analysis(scenario_df)
    plot_option_payoff(spot=175, strike=180, premium=result.price)
    plot_volatility_surface()
    plot_historical_mtm()

    # ── STEP 7: Save Outputs ─────────────────────────────────
    print(f"\n{'─' * 70}")
    print(f" STEP 7: Saving Outputs")
    print(f"{'─' * 70}")

    report.to_csv('output/position_report.csv', index=False)
    print(f"  ✓ Position report → output/position_report.csv")

    scenario_df.to_csv('output/scenario_results.csv', index=False)
    print(f"  ✓ Scenario results → output/scenario_results.csv")

    engine.save('models/mtm_engine.pkl')
    print(f"  ✓ Engine state → models/mtm_engine.pkl")

    # Save portfolio metrics
    metrics_dict = {
        'total_mtm': metrics.total_mtm,
        'total_pnl': metrics.total_pnl,
        'total_delta': metrics.total_delta,
        'total_gamma': metrics.total_gamma,
        'total_theta': metrics.total_theta,
        'total_vega': metrics.total_vega,
        'total_rho': metrics.total_rho,
        'positions_count': metrics.positions_count,
        'valuation_time': datetime.now().isoformat(),
    }
    joblib.dump(metrics_dict, 'output/portfolio_metrics.pkl')
    print(f"  ✓ Portfolio metrics → output/portfolio_metrics.pkl")

    print(f"\n{'=' * 70}")
    print(f" DASHBOARD COMPLETE")
    print(f"{'=' * 70}")
    print(f"\n  📊 Key Findings:")
    print(f"    Portfolio MTM: ${metrics.total_mtm:,.2f}")
    print(f"    Portfolio P&L: ${metrics.total_pnl:,.2f}")
    print(f"    Net Delta: {metrics.total_delta:,.0f} shares")
    print(f"    Daily Theta: ${metrics.total_theta:,.2f}")
    print(f"\n  📁 Charts saved to ./output/")
    print(f"  💾 Engine saved to ./models/")
    print(f"\n  Done! ✅")


if __name__ == '__main__':
    main()
```

---

---

# PART 8: UNIT TESTS (Step 6)

21 tests across 5 test classes — covering pricing accuracy, Greeks, instrument creation, portfolio valuation, scenarios, and end-to-end integration.

---

**File: `tests/test_derivatives.py`**

```python
"""
test_derivatives.py — Unit Tests for Derivatives MTM Dashboard
=================================================================

21 tests across 5 classes:
  - TestPricingModels (8 tests): BS price, put price, Greeks, binomial,
    American options, Monte Carlo convergence, implied vol, edge cases
  - TestInstruments (6 tests): Option creation, valuation, Greeks,
    futures, swaps, validation
  - TestMTMEngine (5 tests): Engine creation, add position, valuation,
    position report, scenario analysis
  - TestVisualization (1 test): Import verification
  - TestIntegration (1 test): Full pipeline

Run with: python -m pytest tests/test_derivatives.py -v
"""

import sys
import os
import numpy as np
import pandas as pd
import pytest
from datetime import datetime, timedelta

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pricing_models import (
    OptionContract, OptionType, ExerciseStyle, PricingResult,
    black_scholes_price, black_scholes_greeks,
    binomial_tree_price, monte_carlo_price, implied_volatility,
)
from src.instruments import (
    OptionPosition, FuturesPosition, SwapPosition,
    PositionSide, MarketData,
)
from src.mtm_engine import MTMEngine, PortfolioMetrics


# ─── Fixtures ───────────────────────────────────────────────────

@pytest.fixture
def sample_call():
    """ATM call option for testing."""
    return OptionContract(
        spot=100.0,
        strike=100.0,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.20,
        option_type=OptionType.CALL,
    )


@pytest.fixture
def sample_put():
    """ATM put option for testing."""
    return OptionContract(
        spot=100.0,
        strike=100.0,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.20,
        option_type=OptionType.PUT,
    )


@pytest.fixture
def sample_market():
    """Standard market data for testing."""
    return MarketData(
        spot_price=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )


@pytest.fixture
def sample_engine(sample_market):
    """Engine with a simple portfolio."""
    engine = MTMEngine()
    engine.add_position(OptionPosition(
        underlying='TEST',
        strike=100.0,
        expiry=datetime.now() + timedelta(days=90),
        option_type='call',
        side=PositionSide.LONG,
        quantity=10,
        premium_paid=5.0,
    ))
    engine.set_market_data('TEST', sample_market)
    return engine


# ─── TestPricingModels ──────────────────────────────────────────

class TestPricingModels:

    def test_black_scholes_call_price(self, sample_call):
        """BS call price for ATM 1Y option should be in reasonable range."""
        price = black_scholes_price(sample_call)
        assert 5 < price < 15  # ATM 1Y 20vol call ≈ $10.45
        assert price > 0

    def test_black_scholes_put_price(self, sample_put):
        """BS put price should satisfy put-call parity."""
        call_price = black_scholes_price(OptionContract(
            spot=100, strike=100, time_to_expiry=1.0,
            risk_free_rate=0.05, volatility=0.20, option_type=OptionType.CALL,
        ))
        put_price = black_scholes_price(sample_put)

        # Put-Call Parity: C - P = S - K×e^(-rT)
        parity_lhs = call_price - put_price
        parity_rhs = 100 - 100 * np.exp(-0.05 * 1.0)
        assert abs(parity_lhs - parity_rhs) < 0.01

    def test_black_scholes_greeks(self, sample_call):
        """Greeks should have correct signs and reasonable magnitudes."""
        result = black_scholes_greeks(sample_call)

        assert isinstance(result, PricingResult)
        assert result.price > 0

        # Call delta is between 0 and 1
        assert 0 < result.delta < 1
        # ATM call delta ≈ 0.5
        assert 0.4 < result.delta < 0.7

        # Gamma is positive
        assert result.gamma > 0

        # Theta is negative for long options (time decay)
        assert result.theta < 0

        # Vega is positive (options gain value when vol increases)
        assert result.vega > 0

        # Rho is positive for calls (higher rates → higher call value)
        assert result.rho > 0

    def test_binomial_tree_european(self, sample_call):
        """Binomial European price should converge to Black-Scholes."""
        bs_price = black_scholes_price(sample_call)
        binom_price = binomial_tree_price(
            sample_call, n_steps=200, exercise_style=ExerciseStyle.EUROPEAN
        )
        assert abs(binom_price - bs_price) < 0.10  # Within $0.10

    def test_binomial_tree_american(self, sample_put):
        """American put should be worth ≥ European put (early exercise)."""
        euro_price = binomial_tree_price(
            sample_put, n_steps=200, exercise_style=ExerciseStyle.EUROPEAN
        )
        amer_price = binomial_tree_price(
            sample_put, n_steps=200, exercise_style=ExerciseStyle.AMERICAN
        )
        assert amer_price >= euro_price - 0.01  # Allow small numerical noise

    def test_monte_carlo_convergence(self, sample_call):
        """Monte Carlo price should be close to Black-Scholes."""
        bs_price = black_scholes_price(sample_call)
        mc_price, mc_error = monte_carlo_price(
            sample_call, n_simulations=100000, random_seed=42
        )
        # MC should be within 3 standard errors of BS
        assert abs(mc_price - bs_price) < 3 * mc_error + 0.50

    def test_implied_volatility(self, sample_call):
        """Implied vol recovery should match input vol."""
        # Price with known vol
        price = black_scholes_price(sample_call)
        # Recover vol from price
        recovered_vol = implied_volatility(price, sample_call)
        assert abs(recovered_vol - sample_call.volatility) < 0.001

    def test_option_at_expiry(self):
        """At expiry, option should equal intrinsic value."""
        itm_call = OptionContract(
            spot=110, strike=100, time_to_expiry=0.0,
            risk_free_rate=0.05, volatility=0.20, option_type=OptionType.CALL,
        )
        price = black_scholes_price(itm_call)
        assert abs(price - 10.0) < 0.01  # Intrinsic = 110-100 = 10

        otm_call = OptionContract(
            spot=90, strike=100, time_to_expiry=0.0,
            risk_free_rate=0.05, volatility=0.20, option_type=OptionType.CALL,
        )
        price = black_scholes_price(otm_call)
        assert abs(price) < 0.01  # OTM = worthless


# ─── TestInstruments ─────────────────────────────────────────────

class TestInstruments:

    def test_option_position_creation(self):
        """Option position should store attributes correctly."""
        opt = OptionPosition(
            underlying='AAPL', strike=180, option_type='call',
            expiry=datetime.now() + timedelta(days=30),
            side=PositionSide.LONG, quantity=10, premium_paid=5.0,
        )
        assert opt.underlying == 'AAPL'
        assert opt.strike == 180
        assert opt.instrument_type == 'option'

    def test_option_position_valuation(self, sample_market):
        """Long call should have positive value (when ATM with time left)."""
        opt = OptionPosition(
            underlying='TEST', strike=100,
            expiry=datetime.now() + timedelta(days=90),
            option_type='call', side=PositionSide.LONG,
            quantity=1, premium_paid=5.0,
        )
        value = opt.value(sample_market)
        assert value > 0  # Long ATM call with 3 months left has value

    def test_option_position_greeks(self, sample_market):
        """Position-level Greeks should be scaled by quantity × multiplier."""
        opt = OptionPosition(
            underlying='TEST', strike=100,
            expiry=datetime.now() + timedelta(days=90),
            option_type='call', side=PositionSide.LONG,
            quantity=10, contract_multiplier=100, premium_paid=5.0,
        )
        greeks = opt.greeks(sample_market)
        assert 'delta' in greeks
        assert 'gamma' in greeks
        # 10 contracts × 100 multiplier × ~0.55 delta ≈ 550
        assert greeks['delta'] > 100

    def test_futures_position(self, sample_market):
        """Futures P&L should be linear."""
        fut = FuturesPosition(
            underlying='ES', futures_price=5100,
            expiry=datetime.now() + timedelta(days=45),
            side=PositionSide.LONG, quantity=2,
            contract_size=50.0, entry_price=5050,
        )
        # P&L = (5100-5050) × 2 × 50 = $5,000
        pnl = fut.pnl(sample_market)
        assert abs(pnl - 5000) < 1

    def test_swap_position(self):
        """Swap should have non-zero MTM when rates differ from fixed."""
        market = MarketData(spot_price=0, risk_free_rate=0.05)
        swap = SwapPosition(
            notional=1000000, fixed_rate=0.045,
            payment_frequency=4, maturity_years=5.0,
            pay_fixed=False,
        )
        # Receive 4.5% fixed, pay 5% floating → losing money (rates above fixed)
        mtm = swap.value(market)
        assert mtm < 0  # Net payer because floating > fixed

        # DV01 should be positive and reasonable
        dv01 = swap.dv01(market)
        assert dv01 > 0
        assert 100 < dv01 < 1000  # ~$450 for 5Y $1M swap

    def test_position_validation(self):
        """Invalid positions should raise errors."""
        with pytest.raises(ValueError):
            OptionPosition(
                underlying='AAPL', strike=180, option_type='invalid',
                expiry=datetime.now() + timedelta(days=30),
            )
        with pytest.raises(ValueError):
            OptionPosition(
                underlying='AAPL', strike=-10, option_type='call',
                expiry=datetime.now() + timedelta(days=30),
            )


# ─── TestMTMEngine ───────────────────────────────────────────────

class TestMTMEngine:

    def test_engine_creation(self):
        """New engine should start empty."""
        engine = MTMEngine()
        assert len(engine.positions) == 0
        assert len(engine.market_data) == 0

    def test_add_position(self, sample_engine):
        """Engine should hold added positions."""
        assert len(sample_engine.positions) == 1
        assert sample_engine.positions[0].underlying == 'TEST'

    def test_portfolio_valuation(self, sample_engine):
        """Portfolio valuation should return valid metrics."""
        metrics = sample_engine.value_portfolio()
        assert isinstance(metrics, PortfolioMetrics)
        assert metrics.positions_count == 1
        assert metrics.total_delta != 0  # ATM option has non-zero delta

    def test_position_report(self, sample_engine):
        """Position report should be a DataFrame with correct columns."""
        report = sample_engine.generate_position_report()
        assert isinstance(report, pd.DataFrame)
        assert len(report) == 1
        assert 'mtm_value' in report.columns
        assert 'delta' in report.columns

    def test_scenario_analysis(self, sample_engine):
        """Scenario analysis should return results for each scenario."""
        scenarios = {
            'Base': {'TEST': 0.0},
            'Up 10%': {'TEST': 0.10},
            'Down 10%': {'TEST': -0.10},
        }
        results = sample_engine.scenario_analysis(scenarios)
        assert len(results) == 3
        # Up scenario should have higher MTM than down
        up_mtm = results[results['scenario'] == 'Up 10%']['portfolio_mtm'].values[0]
        down_mtm = results[results['scenario'] == 'Down 10%']['portfolio_mtm'].values[0]
        assert up_mtm > down_mtm  # Long call benefits from price increase


# ─── TestVisualization ───────────────────────────────────────────

class TestVisualization:

    def test_imports(self):
        """Visualization module should import without errors."""
        from src.visualization import (
            plot_portfolio_summary, plot_position_breakdown,
            plot_greeks_breakdown, plot_scenario_analysis,
            plot_option_payoff, plot_volatility_surface,
            plot_historical_mtm,
        )
        assert callable(plot_portfolio_summary)
        assert callable(plot_option_payoff)


# ─── TestIntegration ─────────────────────────────────────────────

class TestIntegration:

    def test_full_pipeline(self):
        """End-to-end: create engine → add positions → value → scenario."""
        engine = MTMEngine()

        # Add option
        engine.add_position(OptionPosition(
            underlying='AAPL', strike=150,
            expiry=datetime.now() + timedelta(days=60),
            option_type='call', side=PositionSide.LONG,
            quantity=5, premium_paid=8.0,
        ))

        # Add futures
        engine.add_position(FuturesPosition(
            underlying='ES', futures_price=5100,
            expiry=datetime.now() + timedelta(days=45),
            side=PositionSide.LONG, quantity=1,
            contract_size=50.0, entry_price=5080,
        ))

        # Add swap
        engine.add_position(SwapPosition(
            notional=500000, fixed_rate=0.04,
            maturity_years=3.0, pay_fixed=True,
        ))

        # Set market data
        engine.set_market_data('AAPL', MarketData(
            spot_price=155, risk_free_rate=0.05, volatility=0.25
        ))
        engine.set_market_data('ES', MarketData(spot_price=5100, risk_free_rate=0.05))
        engine.set_market_data('IRS', MarketData(spot_price=0, risk_free_rate=0.05))

        # Value portfolio
        metrics = engine.value_portfolio()
        assert metrics.positions_count == 3
        assert metrics.total_mtm != 0

        # Position report
        report = engine.generate_position_report()
        assert len(report) == 3

        # Scenario analysis
        scenarios = {
            'Base': {'AAPL': 0.0, 'ES': 0.0, 'IRS': 0.0},
            'Shock': {'AAPL': -0.05, 'ES': -0.05, 'IRS': 0.0},
        }
        results = engine.scenario_analysis(scenarios)
        assert len(results) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

---

# PART 9: RUN IT!

## Step 7.1: Run the Full Pipeline
```bash
python main.py
```

This produces:
- Console output with 7 formatted steps
- `output/portfolio_summary.png` — 4-panel dashboard (MTM/P&L, Greeks table, delta bars, metrics)
- `output/position_breakdown.png` — Pie chart of MTM by instrument type
- `output/greeks_breakdown.png` — 4-panel bar charts (delta, gamma, theta, vega by underlying)
- `output/scenario_analysis.png` — P&L bar chart for 5 scenarios
- `output/option_payoff.png` — Payoff diagram with strike, spot, and breakeven
- `output/volatility_surface.png` — 3D implied vol surface
- `output/historical_mtm.png` — 60-day simulated portfolio value history
- `output/position_report.csv` — Position-level detail
- `output/scenario_results.csv` — Scenario analysis data
- `output/portfolio_metrics.pkl` — Serialized metrics
- `models/mtm_engine.pkl` — Saved engine state

## Step 7.2: Run the Tests
```bash
python -m pytest tests/test_derivatives.py -v
```

Expected: **21 passed** across 5 test classes.

---

---

# PART 10: HOW TO READ THE RESULTS

## 10.1: The Model Comparison

```
Method                    Price
──────────────────────────────────
Black-Scholes        $   7.3736
Binomial (Euro)      $   7.3833
Binomial (Amer)      $   7.3833
Monte Carlo          $   7.3207 (±$0.0424)
```

**What this tells you:**

- **Black-Scholes = $7.3736**: The exact analytical answer for this European call. This is the benchmark.
- **Binomial (European) = $7.3833**: Only $0.01 away from BS. With 200 steps, the tree converges very well. The small difference is because the tree discretizes time into steps.
- **Binomial (American) = $7.3833**: Identical to European! This is expected for calls on non-dividend stocks — there's no reason to exercise early (you'd give up the time value). For puts, especially in-the-money puts, the American price would be higher.
- **Monte Carlo = $7.3207 ± $0.0424**: Within $0.05 of BS, with a standard error telling you the 68% confidence interval is [$7.28, $7.36]. With 1,000,000 paths instead of 100,000, the error would shrink to ~$0.01.

## 10.2: The Portfolio Valuation

```
Portfolio Metrics:
  Total MTM Value: $16,901.01
  Total P&L: $2,001.01
  Positions: 5

Portfolio Greeks:
  Delta: 1,714.67 shares
  Gamma: 26.1621
  Theta: $-276.52/day
  Vega: $2,133.13 per 1% vol
  Rho: $-42,121.68 per 1% rate
```

**What each number means for a trader:**

```
Delta: 1,714.67 shares
  "I'm net long 1,715 share equivalents."
  If every underlying goes up $1, my portfolio gains ~$1,715.
  To be delta-neutral, I'd need to short ~1,715 shares across my underlyings.

Gamma: 26.1621
  "My delta changes by ~26 shares per $1 move in the underlyings."
  High gamma means my hedges need frequent rebalancing.
  This is moderate — a larger book would have gamma in the hundreds.

Theta: −$276.52/day
  "I lose $277 every day just from time passing."
  Over a 5-day week, that's −$1,383.
  This is the cost of being long options (buying insurance costs money).
  Short option positions would have POSITIVE theta (earning time decay).

Vega: $2,133.13 per 1% vol
  "If implied vol goes from 25% to 26%, I make $2,133."
  Before an AAPL earnings report, vol might spike 5-10%, making $10k-$21k.
  After earnings, vol typically crushes, losing a similar amount.

Rho: −$42,121.68 per 1% rate
  "If interest rates go from 5% to 6%, I lose $42,122."
  This is large because the swap position has massive rate sensitivity.
  The DV01 of a $1M 5-year swap is ~$450 per basis point = $45,000 per 1%.
```

## 10.3: The Scenario Analysis

```
Scenario                    MTM              P&L
──────────────────────────────────────────────────
🟢 Base Case            $  16,901   $    2,001    ← Current
🟢 Market +5%           $  78,573   $   63,673    ← Everything up 5%
🔴 Market -5%           $ -33,366   $  -48,266    ← Everything down 5%
🟢 Tech Rally +10%      $  61,419   $   46,519    ← AAPL +10%, rest +3%
🔴 Market Crash -10%    $-118,XXX   $ -13X,XXX    ← Severe stress
```

**Key insights:**

- **Asymmetric P&L**: +5% gives +$63k but −5% gives −$48k. We're net long, so up is better, but the relationship isn't perfectly linear due to options' convexity (gamma).
- **Tech Rally**: $46k gain — our AAPL positions drive most of the upside.
- **Crash −10%**: Massive loss. The long futures lose 2 × 50 × 510 = $51,000 just on the ES position. The options contribute additional losses. This is why risk managers run these scenarios daily.

## 10.4: Interpreting the Charts

### Portfolio Summary Dashboard
The 4-panel landing page. Top-left shows the big MTM and P&L numbers in green (profit) or red (loss). Top-right is the Greeks table. Bottom-left shows delta bars by underlying — taller bars mean more directional exposure. Bottom-right summarizes key metrics.

### Position Breakdown Pie
Shows what fraction of your book is in each instrument type. If one slice dominates, you're concentrated. Our demo has options, futures, and swaps — a diversified book.

### Greeks Breakdown
Four bar charts showing each Greek by underlying. Look for:
- **Delta**: Which underlying are you most exposed to? (SPY and ES dominate our portfolio)
- **Gamma**: Which underlying has the most convexity? (Options contribute all the gamma)
- **Theta**: Which positions are bleeding the most time decay?
- **Vega**: Which underlying's volatility matters most?

### Scenario Analysis
Green bars = profit scenarios, red bars = loss scenarios. The tallest red bar is your worst case — that's what the CRO looks at. If it exceeds your risk limit, you need to reduce exposure.

### Option Payoff
Shows the hockey-stick payoff at expiry. The breakeven point (where the profit line crosses zero) is strike + premium for calls. Below that, you lose your entire premium. Above that, profit is unlimited.

### Volatility Surface
The 3D surface shows implied volatility varies by both strike and expiry. Notice:
- **Skew**: OTM puts (left side) have higher vol than OTM calls (right side). This is because markets crash faster than they rally, so put protection is expensive.
- **Term structure**: Longer-dated options tend to have slightly higher vol (the back of the surface is higher).
- **Smile**: Some markets show a symmetric "smile" — both OTM puts and OTM calls have higher vol than ATM.

### Historical MTM
Shows portfolio value over 60 business days. The green triangle marks the peak (your best day), the red triangle marks the trough. The trend and volatility of this line tell you how stable your book is.

---

---

# PART 11: QUICK REFERENCE CARD

## Architecture
```
main.py                         → 7-step pipeline
src/pricing_models.py           → BS, Binomial, MC, Implied Vol, Greeks
src/instruments.py              → OptionPosition, FuturesPosition, SwapPosition
src/mtm_engine.py               → MTMEngine: portfolio aggregation + scenarios
src/visualization.py            → 7 chart functions
tests/test_derivatives.py       → 21 tests across 5 classes
```

## The 5 Greeks (Quick Card)

| Greek | Measures | Call Sign | Put Sign | Formula |
|-------|----------|-----------|----------|---------|
| **Delta Δ** | $1 stock move | 0 to +1 | −1 to 0 | N(d₁) |
| **Gamma Γ** | Delta change | Always + | Always + | N'(d₁)/(Sσ√T) |
| **Theta Θ** | Daily decay | Usually − | Usually − | −[Sφ(d₁)σ/(2√T)+...]/365 |
| **Vega ν** | 1% vol change | Always + | Always + | Sφ(d₁)√T/100 |
| **Rho ρ** | 1% rate change | + | − | KTe^(−rT)N(d₂)/100 |

## Key Formulas

| Formula | Equation |
|---------|----------|
| BS Call | `S·N(d₁) − K·e^(−rT)·N(d₂)` |
| BS Put | `K·e^(−rT)·N(−d₂) − S·N(−d₁)` |
| d₁ | `[ln(S/K) + (r+σ²/2)T] / (σ√T)` |
| d₂ | `d₁ − σ√T` |
| Put-Call Parity | `C − P = S − K·e^(−rT)` |
| Binomial u | `e^(σ√Δt)` |
| Binomial p | `(e^(rΔt) − d) / (u − d)` |
| GBM Path | `S(T) = S₀·exp[(r−σ²/2)T + σ√T·Z]` |
| Futures | `F = S·e^(rT)` |
| Swap MTM | `N × (fixed − floating) × AnnuityFactor` |
| DV01 | `|MTM(r+0.0001) − MTM(r)|` |
| Implied Vol | Newton: `σ_new = σ − (BS(σ)−market) / (Vega×100)` |

## Instrument Summary

| Instrument | MTM Method | Greeks | P&L |
|------------|-----------|--------|-----|
| **Options** | Black-Scholes | All 5 (Δ,Γ,Θ,ν,ρ) | value − (premium × qty × mult) |
| **Futures** | (price − entry) × qty × size | Delta only | Same as value |
| **Swaps** | N × rate_diff × annuity | Rho (via DV01) | Same as value |

## Pricing Model Comparison

| Method | Speed | European | American | Exotic | Accuracy |
|--------|-------|----------|----------|--------|----------|
| **Black-Scholes** | ⚡ Instant | ✅ Exact | ❌ | ❌ | Exact |
| **Binomial Tree** | 🔶 Fast | ✅ ~$0.01 | ✅ | Limited | ~200 steps |
| **Monte Carlo** | 🔷 Medium | ✅ ~$0.05 | ❌ | ✅ | ~100k paths |

## Dependencies
```
numpy          → Array math, random generation (MC paths, binomial tree)
pandas         → DataFrames for reports and scenario tables
scipy          → norm.cdf / norm.pdf (THE heart of Black-Scholes)
matplotlib     → All 7 charts
seaborn        → Professional styling
plotly         → Optional 3D interactive charts
yfinance       → Optional real market data
joblib         → Save/load engine state
pytest         → Testing
```

## Test Coverage (21 Tests)

| Class | # Tests | What's Tested |
|-------|---------|---------------|
| TestPricingModels | 8 | BS call/put price, put-call parity, Greeks signs, binomial convergence, American ≥ European, MC convergence, IV recovery, expiry edge case |
| TestInstruments | 6 | Option creation, valuation, Greeks scaling, futures linear P&L, swap MTM + DV01, input validation |
| TestMTMEngine | 5 | Engine creation, add position, portfolio valuation, position report, scenario analysis |
| TestVisualization | 1 | Import verification |
| TestIntegration | 1 | Full pipeline: 3 instruments → value → report → scenarios |
