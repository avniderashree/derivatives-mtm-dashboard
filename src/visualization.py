"""
Visualization Module
====================
Charts and dashboards for derivatives MTM analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Dict

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


def plot_portfolio_summary(
    metrics_dict: Dict,
    figsize: tuple = (14, 8),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create portfolio summary dashboard.
    
    Parameters:
        metrics_dict: Dictionary with portfolio metrics
        figsize: Figure size
        save_path: Path to save figure
    
    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # 1. MTM and P&L bars
    ax1 = axes[0, 0]
    values = [metrics_dict['total_mtm'], metrics_dict['total_pnl']]
    labels = ['Total MTM', 'Total P&L']
    colors = ['steelblue', 'green' if metrics_dict['total_pnl'] >= 0 else 'red']
    bars = ax1.bar(labels, values, color=colors, edgecolor='black', linewidth=0.5)
    
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'${height:,.0f}',
                    xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3 if height >= 0 else -15),
                    textcoords='offset points',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax1.set_title('Portfolio Value & P&L', fontsize=12, fontweight='bold')
    ax1.axhline(0, color='black', linewidth=0.5)
    ax1.grid(True, alpha=0.3)
    
    # 2. Greeks radar chart (simplified as bar)
    ax2 = axes[0, 1]
    greeks = ['Delta', 'Gamma', 'Theta', 'Vega']
    greek_values = [
        metrics_dict.get('total_delta', 0),
        metrics_dict.get('total_gamma', 0) * 100,  # Scale for visibility
        metrics_dict.get('total_theta', 0),
        metrics_dict.get('total_vega', 0)
    ]
    
    colors2 = plt.cm.Set2(np.linspace(0, 1, len(greeks)))
    ax2.barh(greeks, greek_values, color=colors2, edgecolor='black', linewidth=0.5)
    ax2.set_title('Portfolio Greeks', fontsize=12, fontweight='bold')
    ax2.axvline(0, color='black', linewidth=0.5)
    ax2.grid(True, alpha=0.3)
    
    # 3. Exposure by underlying
    ax3 = axes[1, 0]
    exposure = metrics_dict.get('underlying_exposure', {})
    if exposure:
        underlyings = list(exposure.keys())
        exposures = list(exposure.values())
        colors3 = ['green' if e >= 0 else 'red' for e in exposures]
        ax3.barh(underlyings, exposures, color=colors3, edgecolor='black', linewidth=0.5)
        ax3.set_title('Delta Exposure by Underlying', fontsize=12, fontweight='bold')
        ax3.axvline(0, color='black', linewidth=0.5)
        ax3.set_xlabel('Dollar Delta')
    else:
        ax3.text(0.5, 0.5, 'No exposure data', ha='center', va='center')
    ax3.grid(True, alpha=0.3)
    
    # 4. Summary stats text
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    summary_text = (
        f"Portfolio Summary\n"
        f"{'─' * 30}\n\n"
        f"Positions: {metrics_dict.get('position_count', 0)}\n\n"
        f"Total MTM: ${metrics_dict['total_mtm']:,.2f}\n"
        f"Total P&L: ${metrics_dict['total_pnl']:,.2f}\n\n"
        f"Greeks:\n"
        f"  Delta: {metrics_dict.get('total_delta', 0):,.2f}\n"
        f"  Gamma: {metrics_dict.get('total_gamma', 0):,.4f}\n"
        f"  Theta: ${metrics_dict.get('total_theta', 0):,.2f}/day\n"
        f"  Vega: ${metrics_dict.get('total_vega', 0):,.2f}/1%"
    )
    
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_position_breakdown(
    position_df: pd.DataFrame,
    figsize: tuple = (14, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot position breakdown by type and underlying.
    
    Parameters:
        position_df: DataFrame with position details
        figsize: Figure size
        save_path: Path to save figure
    
    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    # 1. MTM by instrument type
    ax1 = axes[0]
    if 'type' in position_df.columns and 'mtm_value' in position_df.columns:
        type_mtm = position_df.groupby('type')['mtm_value'].sum()
        colors = plt.cm.Set3(np.linspace(0, 1, len(type_mtm)))
        wedges, texts, autotexts = ax1.pie(
            np.abs(type_mtm.values),
            labels=type_mtm.index,
            autopct='%1.1f%%',
            colors=colors,
            explode=[0.02] * len(type_mtm)
        )
        ax1.set_title('MTM by Instrument Type', fontsize=12, fontweight='bold')
    else:
        ax1.text(0.5, 0.5, 'No data', ha='center', va='center')
    
    # 2. P&L by underlying
    ax2 = axes[1]
    if 'underlying' in position_df.columns and 'pnl' in position_df.columns:
        underlying_pnl = position_df.groupby('underlying')['pnl'].sum().sort_values()
        colors = ['green' if v >= 0 else 'red' for v in underlying_pnl.values]
        underlying_pnl.plot(kind='barh', ax=ax2, color=colors, edgecolor='black', linewidth=0.5)
        ax2.set_title('P&L by Underlying', fontsize=12, fontweight='bold')
        ax2.set_xlabel('P&L ($)')
        ax2.axvline(0, color='black', linewidth=0.5)
    else:
        ax2.text(0.5, 0.5, 'No data', ha='center', va='center')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_greeks_breakdown(
    position_df: pd.DataFrame,
    figsize: tuple = (14, 8),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot Greeks breakdown by position.
    
    Parameters:
        position_df: DataFrame with position Greeks
        figsize: Figure size
        save_path: Path to save figure
    
    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    greek_cols = ['delta', 'gamma', 'theta', 'vega']
    titles = ['Delta', 'Gamma', 'Theta ($/day)', 'Vega ($/1%)']
    
    for i, (greek, title) in enumerate(zip(greek_cols, titles)):
        ax = axes[i // 2, i % 2]
        
        if greek in position_df.columns and 'underlying' in position_df.columns:
            greek_by_underlying = position_df.groupby('underlying')[greek].sum()
            colors = plt.cm.Set2(np.linspace(0, 1, len(greek_by_underlying)))
            greek_by_underlying.plot(kind='bar', ax=ax, color=colors, edgecolor='black', linewidth=0.5)
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_xlabel('')
            ax.axhline(0, color='black', linewidth=0.5)
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_sensitivity(
    sensitivity_data: Dict[str, pd.DataFrame],
    figsize: tuple = (14, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot sensitivity analysis results.
    
    Parameters:
        sensitivity_data: Dictionary with spot_sensitivity and vol_sensitivity DataFrames
        figsize: Figure size
        save_path: Path to save figure
    
    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    # Spot sensitivity
    ax1 = axes[0]
    if 'spot_sensitivity' in sensitivity_data:
        df = sensitivity_data['spot_sensitivity']
        ax1.plot(df['spot_change_pct'], df['portfolio_value'], 
                'b-o', linewidth=2, markersize=6, label='Portfolio Value')
        ax1.fill_between(df['spot_change_pct'], df['portfolio_value'], alpha=0.3)
        ax1.axvline(0, color='black', linestyle='--', linewidth=1)
        ax1.axhline(df[df['spot_change_pct'] == 0]['portfolio_value'].iloc[0] if len(df) > 0 else 0,
                   color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax1.set_xlabel('Spot Price Change (%)', fontsize=11)
    ax1.set_ylabel('Portfolio Value ($)', fontsize=11)
    ax1.set_title('Spot Price Sensitivity', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Vol sensitivity
    ax2 = axes[1]
    if 'vol_sensitivity' in sensitivity_data:
        df = sensitivity_data['vol_sensitivity']
        ax2.plot(df['vol_change_abs'], df['portfolio_value'],
                'g-o', linewidth=2, markersize=6, label='Portfolio Value')
        ax2.fill_between(df['vol_change_abs'], df['portfolio_value'], alpha=0.3, color='green')
        ax2.axvline(0, color='black', linestyle='--', linewidth=1)
    ax2.set_xlabel('Volatility Change (pp)', fontsize=11)
    ax2.set_ylabel('Portfolio Value ($)', fontsize=11)
    ax2.set_title('Volatility Sensitivity', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_scenario_analysis(
    scenario_df: pd.DataFrame,
    figsize: tuple = (12, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot scenario analysis results.
    
    Parameters:
        scenario_df: DataFrame with scenario results
        figsize: Figure size
        save_path: Path to save figure
    
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if 'scenario' in scenario_df.columns and 'portfolio_pnl' in scenario_df.columns:
        scenarios = scenario_df['scenario']
        pnls = scenario_df['portfolio_pnl']
        colors = ['green' if p >= 0 else 'red' for p in pnls]
        
        bars = ax.bar(scenarios, pnls, color=colors, edgecolor='black', linewidth=0.5)
        
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'${height:,.0f}',
                       xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3 if height >= 0 else -15),
                       textcoords='offset points',
                       ha='center', va='bottom', fontsize=10)
    
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xlabel('Scenario', fontsize=11)
    ax.set_ylabel('Portfolio P&L ($)', fontsize=11)
    ax.set_title('Scenario Analysis', fontsize=14, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_option_payoff(
    spot_range: tuple,
    strike: float,
    premium: float,
    option_type: str = 'call',
    side: str = 'long',
    figsize: tuple = (10, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot option payoff diagram.
    
    Parameters:
        spot_range: (min_spot, max_spot)
        strike: Strike price
        premium: Premium paid/received
        option_type: 'call' or 'put'
        side: 'long' or 'short'
        figsize: Figure size
        save_path: Path to save
    
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    spots = np.linspace(spot_range[0], spot_range[1], 200)
    
    if option_type.lower() == 'call':
        intrinsic = np.maximum(spots - strike, 0)
    else:
        intrinsic = np.maximum(strike - spots, 0)
    
    if side.lower() == 'long':
        payoff = intrinsic - premium
    else:
        payoff = premium - intrinsic
    
    # Plot
    ax.plot(spots, payoff, 'b-', linewidth=2, label='P&L at Expiry')
    ax.fill_between(spots, payoff, where=(payoff >= 0), alpha=0.3, color='green', label='Profit')
    ax.fill_between(spots, payoff, where=(payoff < 0), alpha=0.3, color='red', label='Loss')
    
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(strike, color='gray', linestyle='--', linewidth=1, label=f'Strike (${strike})')
    
    # Break-even
    if option_type.lower() == 'call':
        be = strike + premium if side.lower() == 'long' else strike - premium
    else:
        be = strike - premium if side.lower() == 'long' else strike + premium
    
    if spot_range[0] <= be <= spot_range[1]:
        ax.axvline(be, color='orange', linestyle=':', linewidth=1.5, label=f'Break-even (${be:.2f})')
    
    ax.set_xlabel('Underlying Price at Expiry ($)', fontsize=11)
    ax.set_ylabel('Profit/Loss ($)', fontsize=11)
    title = f'{side.title()} {option_type.title()} Option Payoff (K=${strike}, Premium=${premium})'
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_volatility_surface(
    strikes: np.ndarray,
    expiries: np.ndarray,
    vols: np.ndarray,
    figsize: tuple = (12, 8),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot implied volatility surface.
    
    Parameters:
        strikes: Array of strike prices
        expiries: Array of expiries (years)
        vols: 2D array of implied vols (expiry x strike)
        figsize: Figure size
        save_path: Path to save
    
    Returns:
        Matplotlib figure
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    K, T = np.meshgrid(strikes, expiries)
    
    surf = ax.plot_surface(K, T, vols, cmap='viridis', edgecolor='none', alpha=0.8)
    
    ax.set_xlabel('Strike Price ($)', fontsize=10)
    ax.set_ylabel('Time to Expiry (years)', fontsize=10)
    ax.set_zlabel('Implied Volatility (%)', fontsize=10)
    ax.set_title('Implied Volatility Surface', fontsize=14, fontweight='bold')
    
    fig.colorbar(surf, shrink=0.5, aspect=10, label='IV (%)')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_historical_mtm(
    history_df: pd.DataFrame,
    figsize: tuple = (14, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot historical MTM values.
    
    Parameters:
        history_df: DataFrame with timestamp, mtm, pnl columns
        figsize: Figure size
        save_path: Path to save
    
    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)
    
    # MTM
    ax1 = axes[0]
    if 'timestamp' in history_df.columns and 'mtm' in history_df.columns:
        ax1.plot(history_df['timestamp'], history_df['mtm'], 'b-', linewidth=2)
        ax1.fill_between(history_df['timestamp'], history_df['mtm'], alpha=0.3)
    ax1.set_ylabel('MTM Value ($)', fontsize=11)
    ax1.set_title('Historical Mark-to-Market', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # P&L
    ax2 = axes[1]
    if 'timestamp' in history_df.columns and 'pnl' in history_df.columns:
        colors = ['green' if p >= 0 else 'red' for p in history_df['pnl']]
        ax2.bar(history_df['timestamp'], history_df['pnl'], color=colors, alpha=0.7)
    ax2.set_ylabel('P&L ($)', fontsize=11)
    ax2.set_xlabel('Time', fontsize=11)
    ax2.axhline(0, color='black', linewidth=1)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


if __name__ == "__main__":
    print("Visualization module loaded successfully.")
    print("\nAvailable functions:")
    print("  - plot_portfolio_summary()")
    print("  - plot_position_breakdown()")
    print("  - plot_greeks_breakdown()")
    print("  - plot_sensitivity()")
    print("  - plot_scenario_analysis()")
    print("  - plot_option_payoff()")
    print("  - plot_volatility_surface()")
    print("  - plot_historical_mtm()")
