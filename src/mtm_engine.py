"""
MTM Engine Module
=================
Mark-to-Market valuation engine for derivatives portfolios.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

from .instruments import (
    OptionPosition, FuturesPosition, SwapPosition,
    MarketData, PositionSide
)


@dataclass
class PortfolioMetrics:
    """
    Portfolio-level metrics and risk measures.
    
    Attributes:
        total_mtm: Total mark-to-market value
        total_pnl: Total unrealized P&L
        total_delta: Portfolio delta
        total_gamma: Portfolio gamma
        total_theta: Portfolio theta (daily)
        total_vega: Portfolio vega
        total_rho: Portfolio rho
        position_count: Number of positions
        underlying_exposure: Exposure by underlying
    """
    total_mtm: float
    total_pnl: float
    total_delta: float
    total_gamma: float
    total_theta: float
    total_vega: float
    total_rho: float
    position_count: int
    underlying_exposure: Dict[str, float]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'total_mtm': self.total_mtm,
            'total_pnl': self.total_pnl,
            'total_delta': self.total_delta,
            'total_gamma': self.total_gamma,
            'total_theta': self.total_theta,
            'total_vega': self.total_vega,
            'total_rho': self.total_rho,
            'position_count': self.position_count,
            'underlying_exposure': self.underlying_exposure
        }


class MTMEngine:
    """
    Mark-to-Market valuation engine.
    
    Calculates portfolio values, Greeks, and risk metrics.
    """
    
    def __init__(self, positions: Optional[List] = None):
        """
        Initialize MTM engine.
        
        Parameters:
            positions: List of derivative positions
        """
        self.positions = positions or []
        self.market_data_cache: Dict[str, MarketData] = {}
        self.valuation_history: List[Dict] = []
    
    def add_position(self, position: Union[OptionPosition, FuturesPosition, SwapPosition]):
        """Add a position to the portfolio."""
        self.positions.append(position)
    
    def remove_position(self, index: int):
        """Remove a position by index."""
        if 0 <= index < len(self.positions):
            self.positions.pop(index)
    
    def set_market_data(self, underlying: str, market_data: MarketData):
        """Set market data for an underlying."""
        self.market_data_cache[underlying] = market_data
    
    def get_market_data(self, underlying: str) -> Optional[MarketData]:
        """Get market data for an underlying."""
        return self.market_data_cache.get(underlying)
    
    def value_position(
        self,
        position: Union[OptionPosition, FuturesPosition, SwapPosition],
        market_data: Optional[MarketData] = None
    ) -> Dict:
        """
        Value a single position.
        
        Parameters:
            position: Derivative position
            market_data: Market data (optional, uses cache if not provided)
        
        Returns:
            Dictionary with valuation details
        """
        # Get market data
        if market_data is None:
            underlying = getattr(position, 'underlying', 'DEFAULT')
            market_data = self.market_data_cache.get(underlying)
            if market_data is None:
                raise ValueError(f"No market data for {underlying}")
        
        result = {
            'position': position.to_dict(),
            'mtm_value': position.value(market_data),
            'pnl': position.pnl(market_data)
        }
        
        # Add Greeks for options
        if isinstance(position, OptionPosition):
            greeks = position.greeks(market_data)
            result['greeks'] = greeks
        elif isinstance(position, FuturesPosition):
            result['greeks'] = {
                'delta': position.delta(market_data),
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': 0.0
            }
        elif isinstance(position, SwapPosition):
            result['dv01'] = position.dv01(market_data)
            result['greeks'] = {
                'delta': 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': -position.dv01(market_data) * 100  # Approximate
            }
        
        return result
    
    def value_portfolio(
        self,
        market_data_dict: Optional[Dict[str, MarketData]] = None
    ) -> PortfolioMetrics:
        """
        Value the entire portfolio.
        
        Parameters:
            market_data_dict: Dictionary of underlying -> MarketData
        
        Returns:
            PortfolioMetrics object
        """
        if market_data_dict:
            self.market_data_cache.update(market_data_dict)
        
        total_mtm = 0.0
        total_pnl = 0.0
        total_delta = 0.0
        total_gamma = 0.0
        total_theta = 0.0
        total_vega = 0.0
        total_rho = 0.0
        underlying_exposure = defaultdict(float)
        
        for position in self.positions:
            underlying = getattr(position, 'underlying', 'SWAP')
            market_data = self.market_data_cache.get(underlying)
            
            if market_data is None:
                # Use default market data for swaps
                if isinstance(position, SwapPosition):
                    market_data = MarketData(spot_price=100, risk_free_rate=0.05)
                else:
                    continue
            
            valuation = self.value_position(position, market_data)
            
            total_mtm += valuation['mtm_value']
            total_pnl += valuation['pnl']
            
            if 'greeks' in valuation:
                total_delta += valuation['greeks'].get('delta', 0)
                total_gamma += valuation['greeks'].get('gamma', 0)
                total_theta += valuation['greeks'].get('theta', 0)
                total_vega += valuation['greeks'].get('vega', 0)
                total_rho += valuation['greeks'].get('rho', 0)
            
            # Track exposure by underlying
            if isinstance(position, OptionPosition):
                delta = valuation['greeks']['delta']
                exposure = delta * market_data.spot_price
                underlying_exposure[underlying] += exposure
            elif isinstance(position, FuturesPosition):
                exposure = position.quantity * position.contract_size * market_data.spot_price
                if position.side == PositionSide.SHORT:
                    exposure = -exposure
                underlying_exposure[underlying] += exposure
        
        return PortfolioMetrics(
            total_mtm=total_mtm,
            total_pnl=total_pnl,
            total_delta=total_delta,
            total_gamma=total_gamma,
            total_theta=total_theta,
            total_vega=total_vega,
            total_rho=total_rho,
            position_count=len(self.positions),
            underlying_exposure=dict(underlying_exposure)
        )
    
    def generate_position_report(
        self,
        market_data_dict: Optional[Dict[str, MarketData]] = None
    ) -> pd.DataFrame:
        """
        Generate detailed position report.
        
        Returns:
            DataFrame with position details
        """
        if market_data_dict:
            self.market_data_cache.update(market_data_dict)
        
        rows = []
        
        for i, position in enumerate(self.positions):
            underlying = getattr(position, 'underlying', 'SWAP')
            market_data = self.market_data_cache.get(underlying)
            
            if market_data is None:
                if isinstance(position, SwapPosition):
                    market_data = MarketData(spot_price=100, risk_free_rate=0.05)
                else:
                    continue
            
            valuation = self.value_position(position, market_data)
            
            row = {
                'id': i + 1,
                'underlying': underlying,
                'type': type(position).__name__.replace('Position', ''),
                'mtm_value': valuation['mtm_value'],
                'pnl': valuation['pnl']
            }
            
            if isinstance(position, OptionPosition):
                row['strike'] = position.strike
                row['option_type'] = position.option_type.upper()
                row['side'] = position.side.value.upper()
                row['quantity'] = position.quantity
                row['expiry'] = position.expiry.strftime('%Y-%m-%d')
                row['delta'] = valuation['greeks']['delta']
                row['gamma'] = valuation['greeks']['gamma']
                row['theta'] = valuation['greeks']['theta']
                row['vega'] = valuation['greeks']['vega']
            elif isinstance(position, FuturesPosition):
                row['strike'] = position.futures_price
                row['option_type'] = 'N/A'
                row['side'] = position.side.value.upper()
                row['quantity'] = position.quantity
                row['expiry'] = position.expiry.strftime('%Y-%m-%d')
                row['delta'] = valuation['greeks']['delta']
                row['gamma'] = 0.0
                row['theta'] = 0.0
                row['vega'] = 0.0
            elif isinstance(position, SwapPosition):
                row['strike'] = position.fixed_rate
                row['option_type'] = 'PAY' if position.pay_fixed else 'RCV'
                row['side'] = 'FIXED' if position.pay_fixed else 'FLOAT'
                row['quantity'] = position.notional
                row['expiry'] = f"+{position.maturity_years}Y"
                row['delta'] = 0.0
                row['gamma'] = 0.0
                row['theta'] = 0.0
                row['vega'] = 0.0
            
            rows.append(row)
        
        if not rows:
            return pd.DataFrame()
        
        df = pd.DataFrame(rows)
        
        # Reorder columns
        col_order = [
            'id', 'underlying', 'type', 'option_type', 'strike', 'expiry',
            'side', 'quantity', 'mtm_value', 'pnl', 'delta', 'gamma', 'theta', 'vega'
        ]
        df = df[[c for c in col_order if c in df.columns]]
        
        return df
    
    def sensitivity_analysis(
        self,
        market_data: MarketData,
        spot_range: tuple = (-0.1, 0.1),
        vol_range: tuple = (-0.05, 0.05),
        n_points: int = 11
    ) -> Dict[str, pd.DataFrame]:
        """
        Perform sensitivity analysis on portfolio value.
        
        Parameters:
            market_data: Base market data
            spot_range: (min_pct, max_pct) spot price change
            vol_range: (min_abs, max_abs) volatility change
            n_points: Number of points in each dimension
        
        Returns:
            Dictionary with sensitivity DataFrames
        """
        base_spot = market_data.spot_price
        base_vol = market_data.volatility
        
        # Spot sensitivity
        spot_changes = np.linspace(spot_range[0], spot_range[1], n_points)
        spot_values = []
        
        for pct in spot_changes:
            test_market = MarketData(
                spot_price=base_spot * (1 + pct),
                risk_free_rate=market_data.risk_free_rate,
                dividend_yield=market_data.dividend_yield,
                volatility=market_data.volatility,
                valuation_date=market_data.valuation_date
            )
            
            # Apply to all underlyings
            for underlying in self.market_data_cache:
                base = self.market_data_cache[underlying]
                self.market_data_cache[underlying] = MarketData(
                    spot_price=base.spot_price * (1 + pct),
                    risk_free_rate=base.risk_free_rate,
                    dividend_yield=base.dividend_yield,
                    volatility=base.volatility,
                    valuation_date=base.valuation_date
                )
            
            metrics = self.value_portfolio()
            spot_values.append({
                'spot_change_pct': pct * 100,
                'portfolio_value': metrics.total_mtm,
                'portfolio_pnl': metrics.total_pnl
            })
            
            # Reset
            for underlying in self.market_data_cache:
                base = self.market_data_cache[underlying]
                self.market_data_cache[underlying] = MarketData(
                    spot_price=base.spot_price / (1 + pct),
                    risk_free_rate=base.risk_free_rate,
                    dividend_yield=base.dividend_yield,
                    volatility=base.volatility,
                    valuation_date=base.valuation_date
                )
        
        spot_df = pd.DataFrame(spot_values)
        
        # Vol sensitivity
        vol_changes = np.linspace(vol_range[0], vol_range[1], n_points)
        vol_values = []
        
        for delta_vol in vol_changes:
            for underlying in self.market_data_cache:
                base = self.market_data_cache[underlying]
                new_vol = max(0.01, base.volatility + delta_vol)
                self.market_data_cache[underlying] = MarketData(
                    spot_price=base.spot_price,
                    risk_free_rate=base.risk_free_rate,
                    dividend_yield=base.dividend_yield,
                    volatility=new_vol,
                    valuation_date=base.valuation_date
                )
            
            metrics = self.value_portfolio()
            vol_values.append({
                'vol_change_abs': delta_vol * 100,
                'portfolio_value': metrics.total_mtm,
                'portfolio_pnl': metrics.total_pnl
            })
            
            # Reset
            for underlying in self.market_data_cache:
                base = self.market_data_cache[underlying]
                self.market_data_cache[underlying] = MarketData(
                    spot_price=base.spot_price,
                    risk_free_rate=base.risk_free_rate,
                    dividend_yield=base.dividend_yield,
                    volatility=base.volatility - delta_vol,
                    valuation_date=base.valuation_date
                )
        
        vol_df = pd.DataFrame(vol_values)
        
        return {
            'spot_sensitivity': spot_df,
            'vol_sensitivity': vol_df
        }
    
    def scenario_analysis(
        self,
        scenarios: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Run scenario analysis.
        
        Parameters:
            scenarios: Dictionary of scenario_name -> {underlying: spot_change_pct}
        
        Returns:
            DataFrame with scenario results
        """
        results = []
        
        # Store original values
        original_cache = {k: v for k, v in self.market_data_cache.items()}
        
        for scenario_name, changes in scenarios.items():
            # Apply scenario
            for underlying, pct_change in changes.items():
                if underlying in self.market_data_cache:
                    base = self.market_data_cache[underlying]
                    self.market_data_cache[underlying] = MarketData(
                        spot_price=base.spot_price * (1 + pct_change),
                        risk_free_rate=base.risk_free_rate,
                        dividend_yield=base.dividend_yield,
                        volatility=base.volatility,
                        valuation_date=base.valuation_date
                    )
            
            metrics = self.value_portfolio()
            results.append({
                'scenario': scenario_name,
                'portfolio_mtm': metrics.total_mtm,
                'portfolio_pnl': metrics.total_pnl,
                'delta': metrics.total_delta
            })
            
            # Reset
            self.market_data_cache = {k: MarketData(
                spot_price=original_cache[k].spot_price,
                risk_free_rate=original_cache[k].risk_free_rate,
                dividend_yield=original_cache[k].dividend_yield,
                volatility=original_cache[k].volatility,
                valuation_date=original_cache[k].valuation_date
            ) for k in original_cache}
        
        return pd.DataFrame(results)
    
    def record_valuation(self):
        """Record current valuation for historical tracking."""
        metrics = self.value_portfolio()
        self.valuation_history.append({
            'timestamp': datetime.now(),
            'mtm': metrics.total_mtm,
            'pnl': metrics.total_pnl,
            'delta': metrics.total_delta,
            'gamma': metrics.total_gamma,
            'theta': metrics.total_theta,
            'vega': metrics.total_vega
        })
    
    def get_valuation_history(self) -> pd.DataFrame:
        """Get historical valuations as DataFrame."""
        if not self.valuation_history:
            return pd.DataFrame()
        return pd.DataFrame(self.valuation_history)


def create_sample_engine() -> MTMEngine:
    """
    Create a sample MTM engine with positions and market data.
    
    Returns:
        Configured MTMEngine
    """
    from .instruments import create_sample_portfolio
    
    positions = create_sample_portfolio()
    engine = MTMEngine(positions)
    
    # Set market data
    today = datetime.now()
    
    engine.set_market_data('AAPL', MarketData(
        spot_price=175,
        risk_free_rate=0.05,
        dividend_yield=0.005,
        volatility=0.25,
        valuation_date=today
    ))
    
    engine.set_market_data('SPY', MarketData(
        spot_price=495,
        risk_free_rate=0.05,
        dividend_yield=0.013,
        volatility=0.18,
        valuation_date=today
    ))
    
    engine.set_market_data('ES', MarketData(
        spot_price=5080,
        risk_free_rate=0.05,
        dividend_yield=0.013,
        volatility=0.18,
        valuation_date=today
    ))
    
    return engine


if __name__ == "__main__":
    print("Testing MTM Engine...")
    
    # Create engine with sample portfolio
    engine = create_sample_engine()
    
    # Value portfolio
    metrics = engine.value_portfolio()
    
    print(f"\nPortfolio Metrics:")
    print(f"  Total MTM: ${metrics.total_mtm:,.2f}")
    print(f"  Total P&L: ${metrics.total_pnl:,.2f}")
    print(f"  Positions: {metrics.position_count}")
    
    print(f"\nPortfolio Greeks:")
    print(f"  Delta: {metrics.total_delta:,.2f}")
    print(f"  Gamma: {metrics.total_gamma:,.4f}")
    print(f"  Theta: ${metrics.total_theta:,.2f}/day")
    print(f"  Vega: ${metrics.total_vega:,.2f}/1%")
    
    print(f"\nExposure by Underlying:")
    for underlying, exposure in metrics.underlying_exposure.items():
        print(f"  {underlying}: ${exposure:,.2f}")
    
    # Generate report
    report = engine.generate_position_report()
    print(f"\nPosition Report:")
    print(report.to_string(index=False))
