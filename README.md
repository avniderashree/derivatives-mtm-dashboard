# Derivatives MTM Dashboard

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![scipy](https://img.shields.io/badge/scipy-1.7+-orange.svg)](https://scipy.org/)

A comprehensive **Mark-to-Market (MTM) valuation dashboard** for derivatives portfolios including options, futures, and interest rate swaps. This project implements industry-standard pricing models used by trading desks, risk managers, and quantitative analysts at investment banks and hedge funds.

---

## 📋 Table of Contents

1. [What Is This Project?](#-what-is-this-project)
2. [Key Concepts](#-key-concepts)
3. [Features](#-features)
4. [Installation](#-installation)
5. [How to Run](#-how-to-run)
6. [Understanding the Output](#-understanding-the-output)
7. [Project Structure](#-project-structure)
8. [Module Documentation](#-module-documentation)
9. [Pricing Models](#-pricing-models)
10. [Sample Results](#-sample-results)
11. [Code Examples](#-code-examples)
12. [References](#-references)

---

## 🎯 What Is This Project?

This project provides **daily Mark-to-Market valuation** for derivatives portfolios. It answers critical questions:

| Question | Solution |
|----------|----------|
| *"What is my option worth today?"* | **Black-Scholes, Binomial, Monte Carlo** |
| *"What are my portfolio Greeks?"* | **Delta, Gamma, Theta, Vega, Rho** |
| *"How will my P&L change if the market moves?"* | **Scenario Analysis** |
| *"What is my swap DV01?"* | **Interest Rate Sensitivity** |

### Real-World Applications

| Role | Use Case |
|------|----------|
| **Traders** | Real-time P&L monitoring, Greeks management |
| **Risk Managers** | VaR calculation, stress testing |
| **Fund Managers** | Portfolio valuation, NAV calculation |
| **Middle Office** | Trade confirmation, MTM reconciliation |
| **Regulators** | Basel III/IV compliance reporting |

---

## 📚 Key Concepts

### Mark-to-Market (MTM)

MTM is the process of valuing assets at current market prices:

```
Day 1: Buy call option for $5.00
Day 2: Option now worth $5.50
       MTM P&L = $5.50 - $5.00 = $0.50 profit
```

### The Greeks

Option sensitivities to various risk factors:

| Greek | Measures | Formula |
|-------|----------|---------|
| **Delta (Δ)** | Price sensitivity to underlying | ∂V/∂S |
| **Gamma (Γ)** | Delta sensitivity to underlying | ∂²V/∂S² |
| **Theta (Θ)** | Time decay | ∂V/∂t |
| **Vega (ν)** | Volatility sensitivity | ∂V/∂σ |
| **Rho (ρ)** | Interest rate sensitivity | ∂V/∂r |

### Option Payoffs

```
Call Payoff = max(S - K, 0)    "Right to buy"
Put Payoff  = max(K - S, 0)    "Right to sell"

Where:
  S = Spot price at expiry
  K = Strike price
```

---

## ✨ Features

### Pricing Models

| Model | Method | Best For |
|-------|--------|----------|
| **Black-Scholes** | Closed-form | European options, speed |
| **Binomial Tree** | CRR lattice | American options |
| **Monte Carlo** | Simulation | Path-dependent options |

### Derivative Instruments

| Instrument | Description |
|------------|-------------|
| **Options** | Calls, puts (European/American) |
| **Futures** | Equity index futures |
| **Swaps** | Interest rate swaps |

### Risk Analytics

| Metric | Description |
|--------|-------------|
| **Greeks** | Delta, Gamma, Theta, Vega, Rho |
| **DV01** | Dollar value of 1bp rate move |
| **Scenario Analysis** | What-if calculations |
| **Sensitivity Analysis** | Spot/vol surface |

### Visualizations

1. Portfolio summary dashboard
2. Position breakdown by type
3. Greeks breakdown by underlying
4. Scenario analysis chart
5. Option payoff diagrams
6. Volatility surface (3D)

---

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip

### Step 1: Clone Repository

```bash
git clone https://github.com/avniderashree/derivatives-mtm-dashboard.git
cd derivatives-mtm-dashboard
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

### Run Main Script

```bash
python main.py
```

**What happens:**
1. Demonstrates option pricing (BS, Binomial, MC)
2. Creates sample portfolio
3. Values portfolio with Greeks
4. Runs scenario analysis
5. Generates visualizations

### Run Tests

```bash
pytest tests/ -v
```

---

## 📊 Understanding the Output

### Console Output

```
======================================================================
 DERIVATIVES MTM DASHBOARD
======================================================================

----------------------------------------------------------------------
 STEP 1: Option Pricing Models
----------------------------------------------------------------------

📊 Black-Scholes Pricing:
  Price: $7.3736
  Delta: 0.4704
  Gamma: 0.0182
  Theta: $-0.0568/day
  Vega: $0.3477/1%

📊 Model Comparison:
  Method                    Price
  Black-Scholes        $   7.3736
  Binomial (Euro)      $   7.3833
  Monte Carlo          $   7.3207

----------------------------------------------------------------------
 STEP 3: Mark-to-Market Valuation
----------------------------------------------------------------------

📊 Portfolio Metrics:
  Total MTM Value: $16,901.01
  Total P&L: $2,001.01
  Positions: 5

📊 Portfolio Greeks:
  Delta: 1,714.67 shares
  Gamma: 26.1621
  Theta: $-276.52/day
  Vega: $2,133.13 per 1% vol

----------------------------------------------------------------------
 STEP 5: Scenario Analysis
----------------------------------------------------------------------

📊 Scenario Analysis Results:
  Scenario                         MTM             P&L
  Base Case            $     16,901.01 $      2,001.01
  Market +5%           $     78,573.12 $     63,673.12
  Market -5%           $    -33,365.95 $    -48,265.95
```

### Generated Files

| File | Description |
|------|-------------|
| `output/portfolio_summary.png` | Portfolio overview dashboard |
| `output/position_breakdown.png` | MTM by instrument type |
| `output/greeks_breakdown.png` | Greeks by underlying |
| `output/scenario_analysis.png` | Scenario P&L chart |
| `output/option_payoff.png` | Payoff diagram |
| `output/position_report.csv` | Detailed positions |

---

## 📁 Project Structure

```
derivatives-mtm-dashboard/
│
├── main.py                      # Main execution script
├── requirements.txt             # Dependencies
├── README.md                    # Documentation
│
├── src/
│   ├── __init__.py
│   ├── pricing_models.py        # BS, Binomial, MC pricing
│   ├── instruments.py           # Option, Futures, Swap classes
│   ├── mtm_engine.py            # Portfolio valuation engine
│   └── visualization.py         # Charts
│
├── tests/
│   └── test_derivatives.py      # Unit tests
│
├── output/                      # Generated charts
└── models/                      # Saved engines
```

---

## 📖 Module Documentation

### `src/pricing_models.py`

**Black-Scholes Pricing:**

```python
from src.pricing_models import OptionContract, OptionType, black_scholes_greeks

option = OptionContract(
    spot=100,
    strike=100,
    time_to_expiry=0.25,  # 3 months
    risk_free_rate=0.05,
    volatility=0.20,
    option_type=OptionType.CALL
)

result = black_scholes_greeks(option)
print(f"Price: ${result.price:.4f}")
print(f"Delta: {result.delta:.4f}")
```

**Binomial Tree:**

```python
from src.pricing_models import binomial_tree_price, ExerciseStyle

price = binomial_tree_price(
    option,
    n_steps=200,
    exercise_style=ExerciseStyle.AMERICAN
)
```

**Monte Carlo:**

```python
from src.pricing_models import monte_carlo_price

price, std_error = monte_carlo_price(
    option,
    n_simulations=100000,
    random_seed=42
)
```

### `src/instruments.py`

**Create Option Position:**

```python
from src.instruments import OptionPosition, PositionSide, MarketData

option = OptionPosition(
    underlying='AAPL',
    strike=180,
    expiry=datetime.now() + timedelta(days=60),
    option_type='call',
    side=PositionSide.LONG,
    quantity=10,
    premium_paid=5.50
)

market = MarketData(spot_price=175, risk_free_rate=0.05, volatility=0.25)

value = option.value(market)
pnl = option.pnl(market)
greeks = option.greeks(market)
```

### `src/mtm_engine.py`

**Portfolio Valuation:**

```python
from src.mtm_engine import MTMEngine, create_sample_engine

engine = create_sample_engine()
metrics = engine.value_portfolio()

print(f"Total MTM: ${metrics.total_mtm:,.2f}")
print(f"Delta: {metrics.total_delta:,.2f}")

report = engine.generate_position_report()
```

---

## 📈 Pricing Models

### Black-Scholes Formula

For a European call option:

```
C = S₀·e^(-qT)·N(d₁) - K·e^(-rT)·N(d₂)

Where:
d₁ = [ln(S₀/K) + (r-q+σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T
```

### Cox-Ross-Rubinstein Binomial Tree

```
u = e^(σ√Δt)     Up factor
d = 1/u          Down factor
p = (e^((r-q)Δt) - d) / (u - d)    Risk-neutral probability
```

### Monte Carlo Simulation

```
S(T) = S₀ × exp[(r-q-σ²/2)T + σ√T × Z]

Where Z ~ N(0,1)
```

---

## 📊 Sample Results

### Portfolio Summary

| Position | Type | MTM Value | P&L | Delta |
|----------|------|-----------|-----|-------|
| AAPL 180 Call | Long 10 | $5,389 | -$111 | 437 |
| AAPL 170 Put | Short 5 | -$1,272 | $328 | 155 |
| SPY 500 Call | Long 20 | $34,495 | $18,495 | 1,023 |
| ES Futures | Long 2 | $271 | $5,271 | 100 |
| IRS 5Y | Recv Fixed | -$21,982 | -$21,982 | 0 |

### Scenario Analysis

| Scenario | Portfolio MTM | P&L |
|----------|---------------|-----|
| Base Case | $16,901 | $2,001 |
| Market +5% | $78,573 | $63,673 |
| Market -5% | -$33,366 | -$48,266 |
| Tech Rally +10% | $61,419 | $46,519 |

---

## 💻 Code Examples

### Example 1: Price an Option

```python
from src.pricing_models import OptionContract, OptionType, black_scholes_greeks

option = OptionContract(
    spot=150,
    strike=155,
    time_to_expiry=0.5,
    risk_free_rate=0.04,
    volatility=0.30,
    option_type=OptionType.PUT
)

result = black_scholes_greeks(option)
print(f"Put Price: ${result.price:.2f}")
print(f"Delta: {result.delta:.4f}")
```

### Example 2: Value a Portfolio

```python
from src.mtm_engine import MTMEngine
from src.instruments import OptionPosition, PositionSide, MarketData

engine = MTMEngine()

# Add positions
engine.add_position(OptionPosition(
    underlying='NVDA',
    strike=500,
    expiry=datetime.now() + timedelta(days=30),
    option_type='call',
    side=PositionSide.LONG,
    quantity=5
))

# Set market data
engine.set_market_data('NVDA', MarketData(
    spot_price=480,
    volatility=0.45
))

# Value
metrics = engine.value_portfolio()
print(f"Portfolio Value: ${metrics.total_mtm:,.2f}")
```

---

## 📚 References

### Academic

1. Black, F. & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities"
2. Cox, J., Ross, S., & Rubinstein, M. (1979). "Option Pricing: A Simplified Approach"
3. Hull, J. (2022). *Options, Futures, and Other Derivatives* (11th ed.)

### Industry

- ISDA Definitions for Interest Rate Derivatives
- Basel III Market Risk Framework

---

## 👤 Author

**Avni Derashree**  
Quantitative Analyst | Derivatives Pricing | Risk Management

---

## 🔗 Related Projects

| Project | Description |
|---------|-------------|
| [Portfolio VaR Calculator](https://github.com/avniderashree/portfolio-var-calculator) | Value-at-Risk calculation |
| [Monte Carlo Stress Testing](https://github.com/avniderashree/monte-carlo-stress-testing) | Portfolio stress testing |
| [Liquidity Risk ML Predictor](https://github.com/avniderashree/liquidity-risk-ml-predictor) | ML for liquidity |
| **Derivatives MTM Dashboard** | ← You are here! |

---

*Last updated: January 2026*
