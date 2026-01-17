#!/usr/bin/env python3
"""
Derivatives MTM Dashboard
=========================
Main execution script for mark-to-market valuation.

Author: Avni Derashree
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from src.pricing_models import (
    OptionContract, OptionType, ExerciseStyle,
    black_scholes_greeks, binomial_tree_price, monte_carlo_price, implied_volatility
)
from src.instruments import (
    OptionPosition, FuturesPosition, SwapPosition,
    PositionSide, MarketData, create_sample_portfolio
)
from src.mtm_engine import MTMEngine, create_sample_engine
from src.visualization import (
    plot_portfolio_summary, plot_position_breakdown,
    plot_greeks_breakdown, plot_sensitivity,
    plot_scenario_analysis, plot_option_payoff
)


def print_header(text: str, char: str = "="):
    """Print formatted section header."""
    print(f"\n{char * 70}")
    print(f" {text}")
    print(f"{char * 70}")


def main():
    """Main execution function."""
    
    print_header("DERIVATIVES MTM DASHBOARD", "=")
    print("\nThis dashboard provides:")
    print("  1. Option pricing (Black-Scholes, Binomial, Monte Carlo)")
    print("  2. Portfolio valuation with Greeks")
    print("  3. Sensitivity and scenario analysis")
    print("  4. Risk metrics visualization")
    
    # =========================================================================
    # STEP 1: Option Pricing Demo
    # =========================================================================
    print_header("STEP 1: Option Pricing Models", "-")
    
    # Create a sample option
    option = OptionContract(
        spot=175,
        strike=180,
        time_to_expiry=0.25,  # 3 months
        risk_free_rate=0.05,
        volatility=0.25,
        option_type=OptionType.CALL,
        dividend_yield=0.005
    )
    
    print(f"\nSample Option:")
    print(f"  Underlying: $175")
    print(f"  Strike: $180")
    print(f"  Expiry: 3 months")
    print(f"  Vol: 25%")
    print(f"  Rate: 5%")
    
    # Black-Scholes
    bs_result = black_scholes_greeks(option)
    print(f"\n📊 Black-Scholes Pricing:")
    print(f"  Price: ${bs_result.price:.4f}")
    print(f"  Delta: {bs_result.delta:.4f}")
    print(f"  Gamma: {bs_result.gamma:.4f}")
    print(f"  Theta: ${bs_result.theta:.4f}/day")
    print(f"  Vega: ${bs_result.vega:.4f}/1%")
    print(f"  Rho: ${bs_result.rho:.4f}/1%")
    
    # Binomial Tree
    euro_price = binomial_tree_price(option, n_steps=200, exercise_style=ExerciseStyle.EUROPEAN)
    amer_price = binomial_tree_price(option, n_steps=200, exercise_style=ExerciseStyle.AMERICAN)
    print(f"\n📊 Binomial Tree (200 steps):")
    print(f"  European: ${euro_price:.4f}")
    print(f"  American: ${amer_price:.4f}")
    
    # Monte Carlo
    mc_price, mc_error = monte_carlo_price(option, n_simulations=100000, random_seed=42)
    print(f"\n📊 Monte Carlo (100k paths):")
    print(f"  Price: ${mc_price:.4f} ± ${mc_error:.4f}")
    
    # Model comparison
    print(f"\n📊 Model Comparison:")
    print(f"  {'Method':<20} {'Price':>10}")
    print(f"  {'-'*30}")
    print(f"  {'Black-Scholes':<20} ${bs_result.price:>9.4f}")
    print(f"  {'Binomial (Euro)':<20} ${euro_price:>9.4f}")
    print(f"  {'Binomial (Amer)':<20} ${amer_price:>9.4f}")
    print(f"  {'Monte Carlo':<20} ${mc_price:>9.4f}")
    
    # =========================================================================
    # STEP 2: Create Sample Portfolio
    # =========================================================================
    print_header("STEP 2: Portfolio Construction", "-")
    
    engine = create_sample_engine()
    
    print(f"\nPortfolio contains {len(engine.positions)} positions:")
    for i, pos in enumerate(engine.positions, 1):
        if isinstance(pos, OptionPosition):
            print(f"  {i}. {pos.underlying} {pos.strike} {pos.option_type.upper()} "
                  f"({pos.side.value}, {pos.quantity} contracts)")
        elif isinstance(pos, FuturesPosition):
            print(f"  {i}. {pos.underlying} Futures @ {pos.futures_price} "
                  f"({pos.side.value}, {pos.quantity} contracts)")
        elif isinstance(pos, SwapPosition):
            print(f"  {i}. IRS ${pos.notional:,.0f} notional, {pos.fixed_rate:.2%} fixed, "
                  f"{pos.maturity_years}Y")
    
    # =========================================================================
    # STEP 3: Portfolio Valuation
    # =========================================================================
    print_header("STEP 3: Mark-to-Market Valuation", "-")
    
    metrics = engine.value_portfolio()
    
    print(f"\n📊 Portfolio Metrics:")
    print(f"  Total MTM Value: ${metrics.total_mtm:,.2f}")
    print(f"  Total P&L: ${metrics.total_pnl:,.2f}")
    print(f"  Positions: {metrics.position_count}")
    
    print(f"\n📊 Portfolio Greeks:")
    print(f"  Delta: {metrics.total_delta:,.2f} shares")
    print(f"  Gamma: {metrics.total_gamma:,.4f}")
    print(f"  Theta: ${metrics.total_theta:,.2f}/day")
    print(f"  Vega: ${metrics.total_vega:,.2f} per 1% vol")
    print(f"  Rho: ${metrics.total_rho:,.2f} per 1% rate")
    
    print(f"\n📊 Delta Exposure by Underlying:")
    for underlying, exposure in metrics.underlying_exposure.items():
        print(f"  {underlying}: ${exposure:,.2f}")
    
    # =========================================================================
    # STEP 4: Position Report
    # =========================================================================
    print_header("STEP 4: Position Report", "-")
    
    report = engine.generate_position_report()
    print(f"\nDetailed Position Report:")
    
    # Format for display
    display_cols = ['id', 'underlying', 'type', 'option_type', 'strike', 
                   'side', 'quantity', 'mtm_value', 'pnl', 'delta']
    display_cols = [c for c in display_cols if c in report.columns]
    
    print(report[display_cols].to_string(index=False))
    
    # =========================================================================
    # STEP 5: Scenario Analysis
    # =========================================================================
    print_header("STEP 5: Scenario Analysis", "-")
    
    scenarios = {
        'Base Case': {'AAPL': 0.0, 'SPY': 0.0, 'ES': 0.0},
        'Market +5%': {'AAPL': 0.05, 'SPY': 0.05, 'ES': 0.05},
        'Market -5%': {'AAPL': -0.05, 'SPY': -0.05, 'ES': -0.05},
        'Tech Rally +10%': {'AAPL': 0.10, 'SPY': 0.03, 'ES': 0.03},
        'Market Crash -10%': {'AAPL': -0.10, 'SPY': -0.10, 'ES': -0.10},
        'Volatility Spike': {'AAPL': -0.03, 'SPY': -0.03, 'ES': -0.03}
    }
    
    scenario_results = engine.scenario_analysis(scenarios)
    
    print(f"\n📊 Scenario Analysis Results:")
    print(f"  {'Scenario':<20} {'MTM':>15} {'P&L':>15}")
    print(f"  {'-'*50}")
    for _, row in scenario_results.iterrows():
        print(f"  {row['scenario']:<20} ${row['portfolio_mtm']:>14,.2f} ${row['portfolio_pnl']:>14,.2f}")
    
    # =========================================================================
    # STEP 6: Generate Visualizations
    # =========================================================================
    print_header("STEP 6: Generating Visualizations", "-")
    
    os.makedirs('output', exist_ok=True)
    
    print("\nSaving charts to ./output/ directory...")
    
    # Chart 1: Portfolio summary
    fig1 = plot_portfolio_summary(metrics.to_dict())
    fig1.savefig('output/portfolio_summary.png', dpi=150, bbox_inches='tight')
    print("  ✓ portfolio_summary.png")
    
    # Chart 2: Position breakdown
    fig2 = plot_position_breakdown(report)
    fig2.savefig('output/position_breakdown.png', dpi=150, bbox_inches='tight')
    print("  ✓ position_breakdown.png")
    
    # Chart 3: Greeks breakdown
    fig3 = plot_greeks_breakdown(report)
    fig3.savefig('output/greeks_breakdown.png', dpi=150, bbox_inches='tight')
    print("  ✓ greeks_breakdown.png")
    
    # Chart 4: Scenario analysis
    fig4 = plot_scenario_analysis(scenario_results)
    fig4.savefig('output/scenario_analysis.png', dpi=150, bbox_inches='tight')
    print("  ✓ scenario_analysis.png")
    
    # Chart 5: Option payoff diagram
    fig5 = plot_option_payoff(
        spot_range=(150, 200),
        strike=180,
        premium=5.50,
        option_type='call',
        side='long'
    )
    fig5.savefig('output/option_payoff.png', dpi=150, bbox_inches='tight')
    print("  ✓ option_payoff.png")
    
    plt.close('all')
    
    # =========================================================================
    # STEP 7: Save Results
    # =========================================================================
    print_header("STEP 7: Saving Results", "-")
    
    # Save position report
    report.to_csv('output/position_report.csv', index=False)
    print("  ✓ Saved position report to output/position_report.csv")
    
    # Save scenario results
    scenario_results.to_csv('output/scenario_results.csv', index=False)
    print("  ✓ Saved scenario results to output/scenario_results.csv")
    
    # Save metrics summary
    import joblib
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(engine, 'models/mtm_engine.pkl')
    print("  ✓ Saved MTM engine to models/mtm_engine.pkl")
    
    metrics_dict = metrics.to_dict()
    joblib.dump(metrics_dict, 'output/portfolio_metrics.pkl')
    print("  ✓ Saved portfolio metrics to output/portfolio_metrics.pkl")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print_header("ANALYSIS COMPLETE", "=")
    
    print("\n📊 Key Results:")
    print(f"\n  Portfolio:")
    print(f"    • Positions: {metrics.position_count}")
    print(f"    • Total MTM: ${metrics.total_mtm:,.2f}")
    print(f"    • Total P&L: ${metrics.total_pnl:,.2f}")
    
    print(f"\n  Greeks:")
    print(f"    • Portfolio Delta: {metrics.total_delta:,.2f}")
    print(f"    • Daily Theta: ${metrics.total_theta:,.2f}")
    
    print(f"\n  Scenarios:")
    best_scenario = scenario_results.loc[scenario_results['portfolio_pnl'].idxmax()]
    worst_scenario = scenario_results.loc[scenario_results['portfolio_pnl'].idxmin()]
    print(f"    • Best: {best_scenario['scenario']} (${best_scenario['portfolio_pnl']:,.2f})")
    print(f"    • Worst: {worst_scenario['scenario']} (${worst_scenario['portfolio_pnl']:,.2f})")
    
    print("\n📁 Output files saved to ./output/")
    print("📁 Models saved to ./models/")
    
    print("\nDone! ✅")
    
    return engine, metrics, report


if __name__ == "__main__":
    engine, metrics, report = main()
