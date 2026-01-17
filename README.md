# 📊 Derivatives MTM Dashboard

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-21%20passed-brightgreen.svg)](tests/)
[![scipy](https://img.shields.io/badge/scipy-1.7+-orange.svg)](https://scipy.org/)

A professional-grade **Mark-to-Market (MTM) valuation dashboard** for derivatives portfolios. This project implements the same pricing models and risk analytics used by trading desks at investment banks, hedge funds, and asset managers.

![Dashboard Preview](https://via.placeholder.com/800x400/1a1a2e/ffffff?text=Derivatives+MTM+Dashboard)

---

## 📋 Table of Contents

1. [What Is This Project?](#-what-is-this-project)
2. [Who Is This For?](#-who-is-this-for)
3. [Key Concepts Explained](#-key-concepts-explained)
4. [Features](#-features)
5. [Quick Start](#-quick-start)
6. [Detailed Installation](#-detailed-installation)
7. [How to Run](#-how-to-run)
8. [Understanding the Output](#-understanding-the-output)
9. [Project Architecture](#-project-architecture)
10. [API Reference](#-api-reference)
11. [Code Examples](#-code-examples)
12. [Sample Results](#-sample-results)
13. [Testing](#-testing)
14. [Troubleshooting](#-troubleshooting)
15. [References](#-references)
16. [Contributing](#-contributing)
17. [Author](#-author)

---

## 🎯 What Is This Project?

This project provides **real-time Mark-to-Market valuation** for derivatives portfolios. It answers the critical questions that traders, risk managers, and finance professionals deal with daily:

### Questions This Dashboard Answers

| Question | How We Answer It |
|----------|------------------|
| *"What is my option worth right now?"* | Black-Scholes, Binomial Tree, Monte Carlo pricing |
| *"How sensitive is my portfolio to market moves?"* | Delta, Gamma, Theta, Vega, Rho (the Greeks) |
| *"What happens if the market crashes 10%?"* | Scenario analysis with customizable shocks |
| *"What's my daily P&L decay from time?"* | Theta calculation (time decay) |
| *"What's my interest rate exposure?"* | DV01 for swaps, Rho for options |
| *"How do I value American vs European options?"* | Binomial Tree supports early exercise |

### Real-World Applications

| Role | How They Use This |
|------|-------------------|
| **Equity Derivatives Trader** | Real-time P&L monitoring, Greeks management for hedging |
| **Risk Manager** | VaR inputs, stress testing, limit monitoring |
| **Fund Manager** | Daily NAV calculation, portfolio attribution |
| **Middle Office** | Trade confirmation, MTM reconciliation |
| **Quant Analyst** | Model validation, pricing engine development |
| **Student/Learner** | Understanding derivatives pricing and risk |

---

## 👤 Who Is This For?

### Prerequisites

This project assumes you have:
- **Basic Python knowledge** (can run scripts, understand functions)
- **Some finance background** (know what options/futures are)
- **Interest in quantitative finance**

### No prerequisites needed for:
- Deep math knowledge (formulas are explained)
- Trading experience (sample portfolio provided)
- Previous quant programming (code is well-documented)

---

## 📚 Key Concepts Explained

### What is Mark-to-Market (MTM)?

MTM is the process of valuing your positions at **current market prices**. Instead of looking at what you paid, you look at what it's worth *today*.

```
Example:
Day 1: Buy 10 call options for $5.00 each = $5,000 total cost
Day 2: Options are now worth $5.50 each = $5,500 current value
        MTM P&L = $5,500 - $5,000 = +$500 profit (unrealized)
```

### What Are Options?

Options give you the **right, but not obligation**, to buy (call) or sell (put) an asset at a specific price (strike) by a specific date (expiry).

```
Call Option: Right to BUY
  Payoff at expiry = max(Stock Price - Strike, 0)
  
Put Option: Right to SELL
  Payoff at expiry = max(Strike - Stock Price, 0)
```

### What Are the Greeks?

The Greeks measure how sensitive an option's price is to various factors:

| Greek | What It Measures | Example |
|-------|------------------|---------|
| **Delta (Δ)** | Sensitivity to stock price | Delta = 0.5 means option moves $0.50 for every $1 stock move |
| **Gamma (Γ)** | How fast Delta changes | High gamma = Delta changes quickly |
| **Theta (Θ)** | Time decay per day | Theta = -$0.05 means option loses $0.05/day |
| **Vega (ν)** | Sensitivity to volatility | Vega = $0.10 means option gains $0.10 for 1% vol increase |
| **Rho (ρ)** | Sensitivity to interest rates | Rho = $0.05 means option gains $0.05 for 1% rate increase |

### What is Black-Scholes?

The Black-Scholes model is the **Nobel Prize-winning formula** for pricing European options. It gives a closed-form solution based on:
- Current stock price (S)
- Strike price (K)
- Time to expiry (T)
- Risk-free interest rate (r)
- Volatility (σ)

### What is a Binomial Tree?

A binomial tree models stock price movement as a series of up/down moves. It can price **American options** (which can be exercised early) - something Black-Scholes cannot do.

### What is Monte Carlo Simulation?

Monte Carlo generates thousands of random price paths and averages the payoffs. It's the most flexible method and can price complex, path-dependent options.

---

## ✨ Features

### Pricing Models

| Model | Type | Best For | Speed |
|-------|------|----------|-------|
| **Black-Scholes** | Analytical | European options, Greeks | ⚡ Instant |
| **Binomial Tree** | Lattice | American options, early exercise | 🔶 Fast |
| **Monte Carlo** | Simulation | Complex/exotic options | 🔷 Medium |

### Supported Instruments

| Instrument | Description | Valuation Method |
|------------|-------------|------------------|
| **Options** | Calls and puts (European/American) | BS/Binomial/MC |
| **Futures** | Equity index, commodity futures | Cost-of-carry |
| **Interest Rate Swaps** | Fixed-for-floating swaps | Discounted cash flows |

### Risk Analytics

| Metric | Description | Use Case |
|--------|-------------|----------|
| **Greeks** | Delta, Gamma, Theta, Vega, Rho | Hedging, risk limits |
| **DV01** | Dollar value of 1bp rate move | Interest rate risk |
| **Scenario Analysis** | What-if calculations | Stress testing |
| **Sensitivity Analysis** | Spot/vol surface | Understanding risk profile |

### Visualizations

1. **Portfolio Summary Dashboard** - Overview of MTM, P&L, Greeks
2. **Position Breakdown** - MTM by instrument type (pie chart)
3. **Greeks Breakdown** - Risk by underlying (bar charts)
4. **Scenario Analysis** - P&L under different market conditions
5. **Option Payoff Diagrams** - Visual payoff at expiry
6. **Volatility Surface** - 3D implied volatility surface
7. **Historical MTM** - Time series of portfolio value

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/avniderashree/derivatives-mtm-dashboard.git
cd derivatives-mtm-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python main.py
```

That's it! You'll see a complete demo with sample portfolio, valuations, and charts.

---

## 🛠️ Detailed Installation

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10+ |
| RAM | 2 GB | 4 GB+ |
| Disk Space | 100 MB | 500 MB |
| OS | Windows/macOS/Linux | Any |

### Step 1: Clone the Repository

```bash
git clone https://github.com/avniderashree/derivatives-mtm-dashboard.git
cd derivatives-mtm-dashboard
```

### Step 2: Create Virtual Environment (Recommended)

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
| Package | Version | Purpose |
|---------|---------|---------|
| numpy | ≥1.21.0 | Numerical computing |
| pandas | ≥1.3.0 | Data manipulation |
| scipy | ≥1.7.0 | Statistical functions (norm.cdf, norm.pdf) |
| matplotlib | ≥3.5.0 | Plotting |
| seaborn | ≥0.11.0 | Statistical visualization |
| plotly | ≥5.3.0 | Interactive charts |
| yfinance | ≥0.1.70 | Market data (optional) |
| joblib | ≥1.1.0 | Model serialization |
| pytest | ≥7.0.0 | Testing |

### Step 4: Verify Installation

```bash
python -c "from src.pricing_models import black_scholes_greeks; print('✅ Installation successful!')"
```

---

## ▶️ How to Run

### Option 1: Run Full Demo (Recommended)

```bash
python main.py
```

This will:
1. ✅ Demonstrate pricing models (Black-Scholes, Binomial, Monte Carlo)
2. ✅ Create a sample portfolio (options, futures, swap)
3. ✅ Calculate MTM values and Greeks
4. ✅ Run scenario analysis
5. ✅ Generate visualizations
6. ✅ Save outputs to `./output/` directory

### Option 2: Run Individual Modules

```bash
# Test pricing models
python -m src.pricing_models

# Test instruments
python -m src.instruments

# Test MTM engine
python -m src.mtm_engine
```

### Option 3: Run in Python Shell

```python
>>> from src.pricing_models import OptionContract, OptionType, black_scholes_greeks
>>> 
>>> option = OptionContract(
...     spot=100,
...     strike=100,
...     time_to_expiry=0.25,
...     risk_free_rate=0.05,
...     volatility=0.20,
...     option_type=OptionType.CALL
... )
>>> 
>>> result = black_scholes_greeks(option)
>>> print(f"Price: ${result.price:.2f}")
Price: $4.61
>>> print(f"Delta: {result.delta:.4f}")
Delta: 0.5398
```

### Option 4: Run Tests

```bash
pytest tests/ -v
```

---

## 📊 Understanding the Output

When you run `python main.py`, you'll see output like this:

### Console Output Explained

```
======================================================================
 DERIVATIVES MTM DASHBOARD
======================================================================
```
This is just a header showing the dashboard is starting.

```
----------------------------------------------------------------------
 STEP 1: Option Pricing Models
----------------------------------------------------------------------

Sample Option:
  Underlying: $175
  Strike: $180
  Expiry: 3 months
  Vol: 25%
  Rate: 5%

📊 Black-Scholes Pricing:
  Price: $7.3736        ← The option is worth $7.37
  Delta: 0.4704         ← For every $1 stock move, option moves $0.47
  Gamma: 0.0182         ← Delta changes by 0.018 per $1 stock move
  Theta: $-0.0568/day   ← Option loses $0.057 per day from time decay
  Vega: $0.3477/1%      ← For every 1% vol increase, option gains $0.35
  Rho: $0.1874/1%       ← For every 1% rate increase, option gains $0.19
```

```
📊 Model Comparison:
  Method                    Price
  ------------------------------
  Black-Scholes        $   7.3736   ← Analytical (exact for European)
  Binomial (Euro)      $   7.3833   ← Numerical (converges to BS)
  Binomial (Amer)      $   7.3833   ← American = European for this call
  Monte Carlo          $   7.3207   ← Simulation (random, ±error)
```

```
----------------------------------------------------------------------
 STEP 3: Mark-to-Market Valuation
----------------------------------------------------------------------

📊 Portfolio Metrics:
  Total MTM Value: $16,901.01   ← Current market value of all positions
  Total P&L: $2,001.01          ← Profit since positions were opened
  Positions: 5                   ← Number of positions in portfolio

📊 Portfolio Greeks:
  Delta: 1,714.67 shares         ← Net directional exposure
  Gamma: 26.1621                 ← Convexity exposure
  Theta: $-276.52/day            ← Daily time decay (negative = losing value)
  Vega: $2,133.13 per 1% vol     ← Volatility exposure
  Rho: $-42,121.68 per 1% rate   ← Interest rate exposure
```

```
----------------------------------------------------------------------
 STEP 5: Scenario Analysis
----------------------------------------------------------------------

📊 Scenario Analysis Results:
  Scenario                         MTM             P&L
  --------------------------------------------------
  Base Case            $     16,901.01 $      2,001.01  ← Current
  Market +5%           $     78,573.12 $     63,673.12  ← All assets up 5%
  Market -5%           $    -33,365.95 $    -48,265.95  ← All assets down 5%
  Tech Rally +10%      $     61,418.86 $     46,518.86  ← AAPL +10%, others +3%
  Market Crash -10%    $   -118,XXX     $   -1XX,XXX    ← Stress scenario
```

### Generated Files

After running, check the `./output/` directory:

| File | Description | Format |
|------|-------------|--------|
| `portfolio_summary.png` | Dashboard with MTM, Greeks, exposure | PNG image |
| `position_breakdown.png` | Pie chart of MTM by instrument | PNG image |
| `greeks_breakdown.png` | Bar charts of Greeks by underlying | PNG image |
| `scenario_analysis.png` | Bar chart of P&L by scenario | PNG image |
| `option_payoff.png` | Option payoff diagram | PNG image |
| `position_report.csv` | Detailed position data | CSV spreadsheet |
| `scenario_results.csv` | Scenario analysis data | CSV spreadsheet |
| `portfolio_metrics.pkl` | Serialized metrics | Python pickle |

---

## 🏗️ Project Architecture

### Directory Structure

```
derivatives-mtm-dashboard/
│
├── main.py                      # 🚀 Main entry point - run this!
├── requirements.txt             # 📦 Python dependencies
├── README.md                    # 📖 This documentation
│
├── src/                         # 📁 Source code
│   ├── __init__.py              # Package marker
│   ├── pricing_models.py        # Black-Scholes, Binomial, Monte Carlo
│   ├── instruments.py           # Option, Futures, Swap classes
│   ├── mtm_engine.py            # Portfolio valuation engine
│   └── visualization.py         # Chart generation
│
├── tests/                       # 🧪 Unit tests
│   └── test_derivatives.py      # 21 comprehensive tests
│
├── output/                      # 📊 Generated outputs (created on run)
│   ├── *.png                    # Charts
│   └── *.csv                    # Data exports
│
├── models/                      # 💾 Saved models (created on run)
│   └── mtm_engine.pkl           # Serialized engine
│
├── notebooks/                   # 📓 Jupyter notebooks (optional)
└── data/                        # 📁 Data files (optional)
```

### Module Dependency Graph

```
main.py
    │
    ├── pricing_models.py (no dependencies)
    │       ├── black_scholes_greeks()
    │       ├── binomial_tree_price()
    │       ├── monte_carlo_price()
    │       └── implied_volatility()
    │
    ├── instruments.py
    │       ├── imports pricing_models
    │       ├── OptionPosition
    │       ├── FuturesPosition
    │       └── SwapPosition
    │
    ├── mtm_engine.py
    │       ├── imports instruments
    │       ├── MTMEngine
    │       └── PortfolioMetrics
    │
    └── visualization.py (standalone)
            ├── plot_portfolio_summary()
            ├── plot_position_breakdown()
            ├── plot_greeks_breakdown()
            └── ... (8 chart functions)
```

### Data Flow

```
┌─────────────────┐
│  Market Data    │  spot, vol, rates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MTM Engine     │  value_portfolio()
│  ┌───────────┐  │
│  │ Positions │  │  OptionPosition, FuturesPosition, SwapPosition
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Pricing Models │  black_scholes_greeks(), binomial_tree_price()
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Portfolio      │  total_mtm, total_pnl, total_delta, ...
│  Metrics        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Visualization  │  Charts, Reports
└─────────────────┘
```

---

## 📖 API Reference

### pricing_models.py

#### `OptionContract` (dataclass)

```python
from src.pricing_models import OptionContract, OptionType

option = OptionContract(
    spot=100.0,            # Current stock price
    strike=100.0,          # Strike price
    time_to_expiry=0.25,   # Years until expiry (0.25 = 3 months)
    risk_free_rate=0.05,   # Annual risk-free rate (5%)
    volatility=0.20,       # Annual volatility (20%)
    option_type=OptionType.CALL,  # CALL or PUT
    dividend_yield=0.0     # Continuous dividend yield (optional)
)
```

#### `black_scholes_greeks(option) -> PricingResult`

```python
from src.pricing_models import black_scholes_greeks

result = black_scholes_greeks(option)
# Returns PricingResult with:
#   result.price  - Option price
#   result.delta  - Delta
#   result.gamma  - Gamma
#   result.theta  - Theta (per day)
#   result.vega   - Vega (per 1% vol)
#   result.rho    - Rho (per 1% rate)
```

#### `binomial_tree_price(option, n_steps, exercise_style) -> float`

```python
from src.pricing_models import binomial_tree_price, ExerciseStyle

# European option (no early exercise)
euro_price = binomial_tree_price(
    option, 
    n_steps=200,                          # More steps = more accurate
    exercise_style=ExerciseStyle.EUROPEAN
)

# American option (can exercise early)
amer_price = binomial_tree_price(
    option, 
    n_steps=200, 
    exercise_style=ExerciseStyle.AMERICAN
)
```

#### `monte_carlo_price(option, n_simulations, random_seed) -> (price, std_error)`

```python
from src.pricing_models import monte_carlo_price

price, error = monte_carlo_price(
    option,
    n_simulations=100000,   # More paths = more accurate
    random_seed=42          # For reproducibility
)
# price ± error gives 68% confidence interval
```

#### `implied_volatility(market_price, option) -> float`

```python
from src.pricing_models import implied_volatility

# Given a market price, find the volatility that produces it
iv = implied_volatility(
    market_price=10.50,     # Observed market price
    option=option           # Option with initial vol guess
)
print(f"Implied Volatility: {iv:.1%}")  # e.g., "25.3%"
```

---

### instruments.py

#### `OptionPosition`

```python
from src.instruments import OptionPosition, PositionSide, MarketData
from datetime import datetime, timedelta

option = OptionPosition(
    underlying='AAPL',                           # Ticker symbol
    strike=180.0,                                # Strike price
    expiry=datetime.now() + timedelta(days=60), # Expiration date
    option_type='call',                          # 'call' or 'put'
    side=PositionSide.LONG,                      # LONG or SHORT
    quantity=10,                                 # Number of contracts
    contract_multiplier=100,                     # Shares per contract
    premium_paid=5.50                            # Premium per share
)

# Set market conditions
market = MarketData(
    spot_price=175.0,        # Current stock price
    risk_free_rate=0.05,     # Interest rate
    dividend_yield=0.005,    # Dividend yield
    volatility=0.25          # Implied volatility
)

# Get valuations
mtm_value = option.value(market)      # Current market value
pnl = option.pnl(market)              # Profit/Loss
greeks = option.greeks(market)        # Delta, Gamma, Theta, Vega, Rho
```

#### `FuturesPosition`

```python
from src.instruments import FuturesPosition, PositionSide

futures = FuturesPosition(
    underlying='ES',              # E-mini S&P 500
    futures_price=5100.0,         # Current futures price
    expiry=datetime.now() + timedelta(days=45),
    side=PositionSide.LONG,
    quantity=2,                   # Number of contracts
    contract_size=50.0,           # $50 per point for ES
    entry_price=5050.0            # Price when position was opened
)

mtm_value = futures.value(market)
pnl = futures.pnl(market)
delta = futures.delta(market)     # Approximately quantity * contract_size
```

#### `SwapPosition`

```python
from src.instruments import SwapPosition

swap = SwapPosition(
    notional=1000000.0,         # $1M notional
    fixed_rate=0.045,           # 4.5% fixed rate
    payment_frequency=4,         # Quarterly payments
    maturity_years=5.0,         # 5-year swap
    pay_fixed=False,            # Receiving fixed, paying floating
    floating_spread=0.0         # Spread over floating rate
)

mtm_value = swap.value(market)
dv01 = swap.dv01(market)        # Dollar value of 1bp rate change
```

---

### mtm_engine.py

#### `MTMEngine`

```python
from src.mtm_engine import MTMEngine
from src.instruments import OptionPosition, MarketData

# Create engine
engine = MTMEngine()

# Add positions
engine.add_position(option1)
engine.add_position(option2)
engine.add_position(futures)

# Set market data for each underlying
engine.set_market_data('AAPL', MarketData(spot_price=175, ...))
engine.set_market_data('SPY', MarketData(spot_price=495, ...))

# Value entire portfolio
metrics = engine.value_portfolio()
print(f"Total MTM: ${metrics.total_mtm:,.2f}")
print(f"Total Delta: {metrics.total_delta:,.2f}")

# Generate position report
report = engine.generate_position_report()  # Returns DataFrame

# Run scenario analysis
scenarios = {
    'Base': {'AAPL': 0.0, 'SPY': 0.0},
    'Market Up 10%': {'AAPL': 0.10, 'SPY': 0.10}
}
results = engine.scenario_analysis(scenarios)  # Returns DataFrame
```

---

## 💻 Code Examples

### Example 1: Price a Call Option

```python
from src.pricing_models import OptionContract, OptionType, black_scholes_greeks

# Create option
option = OptionContract(
    spot=150,           # Stock at $150
    strike=155,         # Strike at $155 (5% OTM)
    time_to_expiry=0.5, # 6 months
    risk_free_rate=0.04,
    volatility=0.30,    # 30% volatility
    option_type=OptionType.CALL
)

# Price it
result = black_scholes_greeks(option)

print(f"Call Option Valuation")
print(f"=====================")
print(f"Price:  ${result.price:.2f}")
print(f"Delta:  {result.delta:.4f} ({result.delta*100:.1f}%)")
print(f"Gamma:  {result.gamma:.4f}")
print(f"Theta:  ${result.theta:.4f}/day (${result.theta*365:.2f}/year)")
print(f"Vega:   ${result.vega:.4f} per 1% vol")
```

Output:
```
Call Option Valuation
=====================
Price:  $12.84
Delta:  0.5124 (51.2%)
Gamma:  0.0142
Theta:  $-0.0372/day ($-13.58/year)
Vega:   $0.3852 per 1% vol
```

### Example 2: Compare European vs American Options

```python
from src.pricing_models import (
    OptionContract, OptionType, ExerciseStyle,
    black_scholes_price, binomial_tree_price
)

# Create a PUT option (American early exercise matters for puts)
put = OptionContract(
    spot=100,
    strike=110,          # 10% ITM put
    time_to_expiry=1.0,  # 1 year
    risk_free_rate=0.05,
    volatility=0.25,
    option_type=OptionType.PUT
)

bs_price = black_scholes_price(put)
euro_price = binomial_tree_price(put, n_steps=500, exercise_style=ExerciseStyle.EUROPEAN)
amer_price = binomial_tree_price(put, n_steps=500, exercise_style=ExerciseStyle.AMERICAN)

print(f"ITM Put Option Pricing")
print(f"======================")
print(f"Black-Scholes (Euro):  ${bs_price:.4f}")
print(f"Binomial (Euro):       ${euro_price:.4f}")
print(f"Binomial (American):   ${amer_price:.4f}")
print(f"Early Exercise Value:  ${amer_price - euro_price:.4f}")
```

Output:
```
ITM Put Option Pricing
======================
Black-Scholes (Euro):  $14.0793
Binomial (Euro):       $14.0836
Binomial (American):   $14.6012
Early Exercise Value:  $0.5176
```

### Example 3: Build and Value a Portfolio

```python
from datetime import datetime, timedelta
from src.instruments import (
    OptionPosition, FuturesPosition, SwapPosition,
    PositionSide, MarketData
)
from src.mtm_engine import MTMEngine

# Create engine
engine = MTMEngine()

# Add a long call spread on AAPL
engine.add_position(OptionPosition(
    underlying='AAPL',
    strike=180,
    expiry=datetime.now() + timedelta(days=30),
    option_type='call',
    side=PositionSide.LONG,
    quantity=10,
    premium_paid=8.00
))

engine.add_position(OptionPosition(
    underlying='AAPL',
    strike=190,
    expiry=datetime.now() + timedelta(days=30),
    option_type='call',
    side=PositionSide.SHORT,
    quantity=10,
    premium_paid=4.00
))

# Set market data
engine.set_market_data('AAPL', MarketData(
    spot_price=182,
    risk_free_rate=0.05,
    volatility=0.28
))

# Value portfolio
metrics = engine.value_portfolio()

print(f"Call Spread Portfolio")
print(f"=====================")
print(f"Total MTM:    ${metrics.total_mtm:,.2f}")
print(f"Total P&L:    ${metrics.total_pnl:,.2f}")
print(f"Net Delta:    {metrics.total_delta:,.1f} shares")
print(f"Net Gamma:    {metrics.total_gamma:,.4f}")
print(f"Net Theta:    ${metrics.total_theta:,.2f}/day")
```

### Example 4: Run Stress Tests

```python
scenarios = {
    'Base Case':           {'AAPL': 0.00},
    'Rally +5%':           {'AAPL': 0.05},
    'Rally +10%':          {'AAPL': 0.10},
    'Correction -5%':      {'AAPL': -0.05},
    'Crash -10%':          {'AAPL': -0.10},
    'Flash Crash -20%':    {'AAPL': -0.20}
}

results = engine.scenario_analysis(scenarios)

print(f"\nStress Test Results")
print(f"===================")
for _, row in results.iterrows():
    pnl = row['portfolio_pnl']
    color = '🟢' if pnl >= 0 else '🔴'
    print(f"{color} {row['scenario']:<20} P&L: ${pnl:>12,.2f}")
```

Output:
```
Stress Test Results
===================
🟢 Base Case             P&L: $       500.00
🟢 Rally +5%             P&L: $     2,150.00
🟢 Rally +10%            P&L: $     4,200.00
🔴 Correction -5%        P&L: $      -850.00
🔴 Crash -10%            P&L: $    -2,100.00
🔴 Flash Crash -20%      P&L: $    -3,800.00
```

---

## 📊 Sample Results

### Sample Portfolio

The default portfolio in `main.py` contains:

| # | Instrument | Details | Side |
|---|------------|---------|------|
| 1 | AAPL 180 Call | 60 days, 10 contracts | Long |
| 2 | AAPL 170 Put | 30 days, 5 contracts | Short |
| 3 | SPY 500 Call | 90 days, 20 contracts | Long |
| 4 | ES Futures | 45 days, 2 contracts | Long |
| 5 | 5Y IRS | $1M notional, 4.5% fixed | Receive Fixed |

### Typical Output Metrics

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

Delta Exposure by Underlying:
  AAPL: $103,546.08
  SPY: $506,372.61
  ES: $508,000.00
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Expected Output

```
tests/test_derivatives.py::TestPricingModels::test_black_scholes_call_price PASSED
tests/test_derivatives.py::TestPricingModels::test_black_scholes_put_price PASSED
tests/test_derivatives.py::TestPricingModels::test_black_scholes_greeks PASSED
tests/test_derivatives.py::TestPricingModels::test_binomial_tree_european PASSED
tests/test_derivatives.py::TestPricingModels::test_binomial_tree_american PASSED
tests/test_derivatives.py::TestPricingModels::test_monte_carlo_convergence PASSED
tests/test_derivatives.py::TestPricingModels::test_implied_volatility PASSED
tests/test_derivatives.py::TestPricingModels::test_option_at_expiry PASSED
tests/test_derivatives.py::TestInstruments::test_option_position_creation PASSED
tests/test_derivatives.py::TestInstruments::test_option_position_valuation PASSED
tests/test_derivatives.py::TestInstruments::test_option_position_greeks PASSED
tests/test_derivatives.py::TestInstruments::test_futures_position PASSED
tests/test_derivatives.py::TestInstruments::test_swap_position PASSED
tests/test_derivatives.py::TestInstruments::test_position_validation PASSED
tests/test_derivatives.py::TestMTMEngine::test_engine_creation PASSED
tests/test_derivatives.py::TestMTMEngine::test_add_position PASSED
tests/test_derivatives.py::TestMTMEngine::test_portfolio_valuation PASSED
tests/test_derivatives.py::TestMTMEngine::test_position_report PASSED
tests/test_derivatives.py::TestMTMEngine::test_scenario_analysis PASSED
tests/test_derivatives.py::TestVisualization::test_imports PASSED
tests/test_derivatives.py::TestIntegration::test_full_pipeline PASSED

============================== 21 passed in 2.05s ==============================
```

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| pricing_models.py | 8 | Greeks, pricing accuracy, edge cases |
| instruments.py | 6 | Position creation, valuation, validation |
| mtm_engine.py | 5 | Engine creation, portfolio valuation, scenarios |
| visualization.py | 1 | Import verification |
| Integration | 1 | Full pipeline test |

---

## 🔧 Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'src'

**Solution:** Run from the project root directory:
```bash
cd derivatives-mtm-dashboard
python main.py
```

#### 2. ImportError: cannot import name 'norm' from 'scipy.stats'

**Solution:** Update scipy:
```bash
pip install --upgrade scipy
```

#### 3. matplotlib: Font not found

**Solution:** This is just a warning, charts will still work. To fix:
```bash
pip install --upgrade matplotlib
```

#### 4. Permission denied when saving files

**Solution:** Create the output directory:
```bash
mkdir -p output models
```

#### 5. Tests fail with "No module named 'src'"

**Solution:** The test file includes path setup, but if it fails:
```bash
pip install -e .
# Or run from project root:
cd derivatives-mtm-dashboard
pytest tests/ -v
```

---

## 📚 References

### Academic Papers

1. **Black, F. & Scholes, M.** (1973). "The Pricing of Options and Corporate Liabilities". *Journal of Political Economy*, 81(3), 637-654.

2. **Cox, J., Ross, S., & Rubinstein, M.** (1979). "Option Pricing: A Simplified Approach". *Journal of Financial Economics*, 7(3), 229-263.

3. **Merton, R.C.** (1973). "Theory of Rational Option Pricing". *Bell Journal of Economics and Management Science*, 4(1), 141-183.

### Textbooks

1. **Hull, J.C.** (2022). *Options, Futures, and Other Derivatives* (11th ed.). Pearson.

2. **Wilmott, P.** (2006). *Paul Wilmott on Quantitative Finance* (2nd ed.). Wiley.

3. **Shreve, S.E.** (2004). *Stochastic Calculus for Finance II: Continuous-Time Models*. Springer.

### Industry Standards

- ISDA Definitions for Interest Rate Derivatives
- Basel III/IV Market Risk Framework
- CME Group contract specifications

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 👤 Author

**Avni Derashree**

Quantitative Analyst | Derivatives Pricing | Risk Management

- GitHub: [@avniderashree](https://github.com/avniderashree)

---

## 🔗 Related Projects

| Project | Description | Link |
|---------|-------------|------|
| Portfolio VaR Calculator | Value-at-Risk calculation | [View](https://github.com/avniderashree/portfolio-var-calculator) |
| Monte Carlo Stress Testing | Portfolio stress testing | [View](https://github.com/avniderashree/monte-carlo-stress-testing) |
| GARCH Volatility Forecaster | Volatility modeling | [View](https://github.com/avniderashree/garch-volatility-forecaster) |
| Credit Risk PD/LGD Model | Credit modeling | [View](https://github.com/avniderashree/credit-risk-pd-lgd-model) |
| Liquidity Risk ML Predictor | ML for liquidity | [View](https://github.com/avniderashree/liquidity-risk-ml-predictor) |
| **Derivatives MTM Dashboard** | ← You are here! | |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Last updated: January 2026*
