"""
Unit Tests for Derivatives MTM Dashboard
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pandas as pd
import pytest
from datetime import datetime, timedelta


class TestPricingModels:
    """Tests for pricing_models module."""
    
    def test_black_scholes_call_price(self):
        """Test Black-Scholes call option pricing."""
        from src.pricing_models import OptionContract, OptionType, black_scholes_price
        
        option = OptionContract(
            spot=100,
            strike=100,
            time_to_expiry=1.0,
            risk_free_rate=0.05,
            volatility=0.2,
            option_type=OptionType.CALL
        )
        
        price = black_scholes_price(option)
        
        # Expected ~10.45 for ATM 1-year call
        assert 10 < price < 11
        assert price > 0
    
    def test_black_scholes_put_price(self):
        """Test Black-Scholes put option pricing."""
        from src.pricing_models import OptionContract, OptionType, black_scholes_price
        
        option = OptionContract(
            spot=100,
            strike=100,
            time_to_expiry=1.0,
            risk_free_rate=0.05,
            volatility=0.2,
            option_type=OptionType.PUT
        )
        
        price = black_scholes_price(option)
        
        # Put-call parity: P = C - S + K*exp(-rT)
        call_option = OptionContract(
            spot=100, strike=100, time_to_expiry=1.0,
            risk_free_rate=0.05, volatility=0.2, option_type=OptionType.CALL
        )
        call_price = black_scholes_price(call_option)
        expected_put = call_price - 100 + 100 * np.exp(-0.05 * 1.0)
        
        assert abs(price - expected_put) < 0.01
    
    def test_black_scholes_greeks(self):
        """Test Greeks calculation."""
        from src.pricing_models import OptionContract, OptionType, black_scholes_greeks
        
        option = OptionContract(
            spot=100, strike=100, time_to_expiry=0.25,
            risk_free_rate=0.05, volatility=0.2, option_type=OptionType.CALL
        )
        
        result = black_scholes_greeks(option)
        
        # Delta should be around 0.5-0.6 for ATM call
        assert 0.4 < result.delta < 0.7
        # Gamma should be positive
        assert result.gamma > 0
        # Theta should be negative for long options
        assert result.theta < 0
        # Vega should be positive
        assert result.vega > 0
    
    def test_binomial_tree_european(self):
        """Test binomial tree European option pricing."""
        from src.pricing_models import (
            OptionContract, OptionType, ExerciseStyle,
            black_scholes_price, binomial_tree_price
        )
        
        option = OptionContract(
            spot=100, strike=100, time_to_expiry=1.0,
            risk_free_rate=0.05, volatility=0.2, option_type=OptionType.CALL
        )
        
        bs_price = black_scholes_price(option)
        bt_price = binomial_tree_price(option, n_steps=200, exercise_style=ExerciseStyle.EUROPEAN)
        
        # Should match BS within 0.5%
        assert abs(bt_price - bs_price) / bs_price < 0.005
    
    def test_binomial_tree_american(self):
        """Test American option is >= European."""
        from src.pricing_models import (
            OptionContract, OptionType, ExerciseStyle, binomial_tree_price
        )
        
        option = OptionContract(
            spot=100, strike=100, time_to_expiry=1.0,
            risk_free_rate=0.05, volatility=0.2, option_type=OptionType.PUT
        )
        
        euro_price = binomial_tree_price(option, n_steps=100, exercise_style=ExerciseStyle.EUROPEAN)
        amer_price = binomial_tree_price(option, n_steps=100, exercise_style=ExerciseStyle.AMERICAN)
        
        # American >= European
        assert amer_price >= euro_price - 0.001
    
    def test_monte_carlo_convergence(self):
        """Test Monte Carlo pricing convergence."""
        from src.pricing_models import (
            OptionContract, OptionType, black_scholes_price, monte_carlo_price
        )
        
        option = OptionContract(
            spot=100, strike=100, time_to_expiry=0.5,
            risk_free_rate=0.05, volatility=0.2, option_type=OptionType.CALL
        )
        
        bs_price = black_scholes_price(option)
        mc_price, mc_error = monte_carlo_price(option, n_simulations=100000, random_seed=42)
        
        # MC should be within 3 standard errors of BS
        assert abs(mc_price - bs_price) < 3 * mc_error
    
    def test_implied_volatility(self):
        """Test implied volatility calculation."""
        from src.pricing_models import (
            OptionContract, OptionType, black_scholes_price, implied_volatility
        )
        
        true_vol = 0.25
        option = OptionContract(
            spot=100, strike=100, time_to_expiry=0.5,
            risk_free_rate=0.05, volatility=true_vol, option_type=OptionType.CALL
        )
        
        market_price = black_scholes_price(option)
        
        # Start with different initial guess
        option_guess = OptionContract(
            spot=100, strike=100, time_to_expiry=0.5,
            risk_free_rate=0.05, volatility=0.15, option_type=OptionType.CALL
        )
        
        iv = implied_volatility(market_price, option_guess)
        
        assert abs(iv - true_vol) < 0.001
    
    def test_option_at_expiry(self):
        """Test option value at expiry."""
        from src.pricing_models import OptionContract, OptionType, black_scholes_price
        
        # ITM call at expiry
        itm_call = OptionContract(
            spot=110, strike=100, time_to_expiry=0,
            risk_free_rate=0.05, volatility=0.2, option_type=OptionType.CALL
        )
        assert black_scholes_price(itm_call) == 10
        
        # OTM call at expiry
        otm_call = OptionContract(
            spot=90, strike=100, time_to_expiry=0,
            risk_free_rate=0.05, volatility=0.2, option_type=OptionType.CALL
        )
        assert black_scholes_price(otm_call) == 0


class TestInstruments:
    """Tests for instruments module."""
    
    def test_option_position_creation(self):
        """Test option position creation."""
        from src.instruments import OptionPosition, PositionSide
        
        option = OptionPosition(
            underlying='AAPL',
            strike=180,
            expiry=datetime.now() + timedelta(days=60),
            option_type='call',
            side=PositionSide.LONG,
            quantity=10,
            premium_paid=5.0
        )
        
        assert option.underlying == 'AAPL'
        assert option.strike == 180
        assert option.quantity == 10
    
    def test_option_position_valuation(self):
        """Test option position MTM valuation."""
        from src.instruments import OptionPosition, PositionSide, MarketData
        
        option = OptionPosition(
            underlying='AAPL',
            strike=180,
            expiry=datetime.now() + timedelta(days=60),
            option_type='call',
            side=PositionSide.LONG,
            quantity=10,
            premium_paid=5.0
        )
        
        market = MarketData(
            spot_price=175,
            risk_free_rate=0.05,
            volatility=0.25
        )
        
        value = option.value(market)
        
        # Value should be positive for long call
        assert value >= 0
    
    def test_option_position_greeks(self):
        """Test option position Greeks."""
        from src.instruments import OptionPosition, PositionSide, MarketData
        
        option = OptionPosition(
            underlying='AAPL',
            strike=180,
            expiry=datetime.now() + timedelta(days=60),
            option_type='call',
            side=PositionSide.LONG,
            quantity=10,
            premium_paid=5.0
        )
        
        market = MarketData(spot_price=175, risk_free_rate=0.05, volatility=0.25)
        greeks = option.greeks(market)
        
        assert 'delta' in greeks
        assert 'gamma' in greeks
        assert 'theta' in greeks
        assert 'vega' in greeks
    
    def test_futures_position(self):
        """Test futures position."""
        from src.instruments import FuturesPosition, PositionSide, MarketData
        
        futures = FuturesPosition(
            underlying='ES',
            futures_price=5100,
            expiry=datetime.now() + timedelta(days=45),
            side=PositionSide.LONG,
            quantity=2,
            contract_size=50.0,
            entry_price=5050
        )
        
        market = MarketData(spot_price=5080, risk_free_rate=0.05)
        
        pnl = futures.pnl(market)
        
        # Long from 5050, theoretical now > 5050, should have profit
        expected_pnl = (futures.theoretical_price(market) - 5050) * 2 * 50.0
        assert abs(pnl - expected_pnl) < 0.01
    
    def test_swap_position(self):
        """Test swap position."""
        from src.instruments import SwapPosition, MarketData
        
        swap = SwapPosition(
            notional=1000000,
            fixed_rate=0.045,
            payment_frequency=4,
            maturity_years=5.0,
            pay_fixed=False
        )
        
        market = MarketData(spot_price=100, risk_free_rate=0.05)
        
        value = swap.value(market)
        dv01 = swap.dv01(market)
        
        # DV01 should be positive for receive-fixed swap
        assert dv01 > 0
    
    def test_position_validation(self):
        """Test position input validation."""
        from src.instruments import OptionPosition, PositionSide
        
        with pytest.raises(ValueError):
            OptionPosition(
                underlying='AAPL',
                strike=-100,  # Invalid
                expiry=datetime.now() + timedelta(days=60),
                option_type='call',
                side=PositionSide.LONG,
                quantity=10
            )


class TestMTMEngine:
    """Tests for mtm_engine module."""
    
    def test_engine_creation(self):
        """Test MTM engine creation."""
        from src.mtm_engine import MTMEngine
        
        engine = MTMEngine()
        assert len(engine.positions) == 0
    
    def test_add_position(self):
        """Test adding positions."""
        from src.mtm_engine import MTMEngine
        from src.instruments import OptionPosition, PositionSide
        
        engine = MTMEngine()
        
        option = OptionPosition(
            underlying='AAPL',
            strike=180,
            expiry=datetime.now() + timedelta(days=60),
            option_type='call',
            side=PositionSide.LONG,
            quantity=10
        )
        
        engine.add_position(option)
        assert len(engine.positions) == 1
    
    def test_portfolio_valuation(self):
        """Test portfolio valuation."""
        from src.mtm_engine import create_sample_engine
        
        engine = create_sample_engine()
        metrics = engine.value_portfolio()
        
        assert metrics.position_count > 0
        assert metrics.total_mtm is not None
    
    def test_position_report(self):
        """Test position report generation."""
        from src.mtm_engine import create_sample_engine
        
        engine = create_sample_engine()
        report = engine.generate_position_report()
        
        assert isinstance(report, pd.DataFrame)
        assert 'mtm_value' in report.columns
        assert 'pnl' in report.columns
    
    def test_scenario_analysis(self):
        """Test scenario analysis."""
        from src.mtm_engine import create_sample_engine
        
        engine = create_sample_engine()
        
        scenarios = {
            'Base': {'AAPL': 0.0, 'SPY': 0.0, 'ES': 0.0},
            'Up 5%': {'AAPL': 0.05, 'SPY': 0.05, 'ES': 0.05}
        }
        
        results = engine.scenario_analysis(scenarios)
        
        assert len(results) == 2
        assert 'scenario' in results.columns
        assert 'portfolio_pnl' in results.columns


class TestVisualization:
    """Tests for visualization module."""
    
    def test_imports(self):
        """Test visualization functions can be imported."""
        from src.visualization import (
            plot_portfolio_summary,
            plot_position_breakdown,
            plot_greeks_breakdown,
            plot_sensitivity,
            plot_scenario_analysis,
            plot_option_payoff
        )
        
        assert callable(plot_portfolio_summary)
        assert callable(plot_position_breakdown)
        assert callable(plot_option_payoff)


class TestIntegration:
    """Integration tests."""
    
    def test_full_pipeline(self):
        """Test full MTM pipeline."""
        from src.instruments import OptionPosition, PositionSide, MarketData
        from src.mtm_engine import MTMEngine
        
        # Create engine
        engine = MTMEngine()
        
        # Add position
        option = OptionPosition(
            underlying='AAPL',
            strike=180,
            expiry=datetime.now() + timedelta(days=60),
            option_type='call',
            side=PositionSide.LONG,
            quantity=10,
            premium_paid=5.0
        )
        engine.add_position(option)
        
        # Set market data
        engine.set_market_data('AAPL', MarketData(
            spot_price=175,
            risk_free_rate=0.05,
            volatility=0.25
        ))
        
        # Value
        metrics = engine.value_portfolio()
        
        assert metrics.position_count == 1
        assert metrics.total_mtm >= 0
        
        # Generate report
        report = engine.generate_position_report()
        assert len(report) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
