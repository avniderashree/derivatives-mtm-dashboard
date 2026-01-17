"""
Instruments Module
==================
Derivative instrument classes for options, futures, forwards, and swaps.
"""

import numpy as np
import pandas as pd
from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from abc import ABC, abstractmethod


class InstrumentType(Enum):
    """Derivative instrument types."""
    OPTION = "option"
    FUTURE = "future"
    FORWARD = "forward"
    SWAP = "swap"


class PositionSide(Enum):
    """Position direction."""
    LONG = "long"
    SHORT = "short"


@dataclass
class MarketData:
    """
    Market data for valuation.
    
    Attributes:
        spot_price: Current underlying price
        risk_free_rate: Annual risk-free rate
        dividend_yield: Annual dividend yield
        volatility: Implied or historical volatility
        valuation_date: Date of valuation
    """
    spot_price: float
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0
    volatility: float = 0.2
    valuation_date: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.spot_price <= 0:
            raise ValueError("Spot price must be positive")


class Instrument(ABC):
    """Abstract base class for derivative instruments."""
    
    @abstractmethod
    def value(self, market_data: MarketData) -> float:
        """Calculate mark-to-market value."""
        pass
    
    @abstractmethod
    def pnl(self, market_data: MarketData) -> float:
        """Calculate P&L from initial value."""
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        pass


@dataclass
class OptionPosition:
    """
    Option position with valuation.
    
    Attributes:
        underlying: Underlying asset symbol
        strike: Strike price
        expiry: Expiration date
        option_type: 'call' or 'put'
        side: LONG or SHORT
        quantity: Number of contracts
        contract_multiplier: Shares per contract (usually 100)
        premium_paid: Premium paid/received per share
    """
    underlying: str
    strike: float
    expiry: datetime
    option_type: str  # 'call' or 'put'
    side: PositionSide
    quantity: int
    contract_multiplier: int = 100
    premium_paid: float = 0.0
    
    def __post_init__(self):
        if self.strike <= 0:
            raise ValueError("Strike must be positive")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.option_type.lower() not in ['call', 'put']:
            raise ValueError("Option type must be 'call' or 'put'")
        self.option_type = self.option_type.lower()
    
    def time_to_expiry(self, valuation_date: datetime) -> float:
        """Calculate time to expiry in years."""
        if isinstance(self.expiry, date) and not isinstance(self.expiry, datetime):
            expiry_dt = datetime.combine(self.expiry, datetime.min.time())
        else:
            expiry_dt = self.expiry
        
        if isinstance(valuation_date, date) and not isinstance(valuation_date, datetime):
            val_dt = datetime.combine(valuation_date, datetime.min.time())
        else:
            val_dt = valuation_date
        
        days = (expiry_dt - val_dt).days
        return max(days / 365.0, 0)
    
    def value(self, market_data: MarketData) -> float:
        """
        Calculate current mark-to-market value.
        
        Returns:
            Total position value (can be negative for short positions)
        """
        from .pricing_models import (
            OptionContract, OptionType, black_scholes_price
        )
        
        T = self.time_to_expiry(market_data.valuation_date)
        
        opt_type = OptionType.CALL if self.option_type == 'call' else OptionType.PUT
        
        option = OptionContract(
            spot=market_data.spot_price,
            strike=self.strike,
            time_to_expiry=T,
            risk_free_rate=market_data.risk_free_rate,
            volatility=market_data.volatility,
            option_type=opt_type,
            dividend_yield=market_data.dividend_yield
        )
        
        unit_price = black_scholes_price(option)
        total_value = unit_price * self.quantity * self.contract_multiplier
        
        if self.side == PositionSide.SHORT:
            total_value = -total_value
        
        return total_value
    
    def pnl(self, market_data: MarketData) -> float:
        """
        Calculate P&L from premium paid/received.
        
        Returns:
            Unrealized P&L
        """
        current_value = self.value(market_data)
        initial_cost = self.premium_paid * self.quantity * self.contract_multiplier
        
        if self.side == PositionSide.LONG:
            return current_value - initial_cost
        else:
            return initial_cost + current_value  # Short: received premium, now owe value
    
    def greeks(self, market_data: MarketData) -> dict:
        """
        Calculate position Greeks.
        
        Returns:
            Dictionary with Delta, Gamma, Theta, Vega, Rho
        """
        from .pricing_models import (
            OptionContract, OptionType, black_scholes_greeks
        )
        
        T = self.time_to_expiry(market_data.valuation_date)
        opt_type = OptionType.CALL if self.option_type == 'call' else OptionType.PUT
        
        option = OptionContract(
            spot=market_data.spot_price,
            strike=self.strike,
            time_to_expiry=T,
            risk_free_rate=market_data.risk_free_rate,
            volatility=market_data.volatility,
            option_type=opt_type,
            dividend_yield=market_data.dividend_yield
        )
        
        result = black_scholes_greeks(option)
        multiplier = self.quantity * self.contract_multiplier
        
        if self.side == PositionSide.SHORT:
            multiplier = -multiplier
        
        return {
            'delta': result.delta * multiplier,
            'gamma': result.gamma * multiplier,
            'theta': result.theta * multiplier,
            'vega': result.vega * multiplier,
            'rho': result.rho * multiplier
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'instrument_type': 'option',
            'underlying': self.underlying,
            'strike': self.strike,
            'expiry': self.expiry.isoformat() if isinstance(self.expiry, datetime) else str(self.expiry),
            'option_type': self.option_type,
            'side': self.side.value,
            'quantity': self.quantity,
            'contract_multiplier': self.contract_multiplier,
            'premium_paid': self.premium_paid
        }


@dataclass
class FuturesPosition:
    """
    Futures/Forward position.
    
    Attributes:
        underlying: Underlying asset symbol
        futures_price: Contracted futures price
        expiry: Expiration date
        side: LONG or SHORT
        quantity: Number of contracts
        contract_size: Size per contract
        entry_price: Price at position entry
    """
    underlying: str
    futures_price: float
    expiry: datetime
    side: PositionSide
    quantity: int
    contract_size: float = 1.0
    entry_price: Optional[float] = None
    
    def __post_init__(self):
        if self.futures_price <= 0:
            raise ValueError("Futures price must be positive")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.entry_price is None:
            self.entry_price = self.futures_price
    
    def time_to_expiry(self, valuation_date: datetime) -> float:
        """Calculate time to expiry in years."""
        if isinstance(self.expiry, date) and not isinstance(self.expiry, datetime):
            expiry_dt = datetime.combine(self.expiry, datetime.min.time())
        else:
            expiry_dt = self.expiry
        
        if isinstance(valuation_date, date) and not isinstance(valuation_date, datetime):
            val_dt = datetime.combine(valuation_date, datetime.min.time())
        else:
            val_dt = valuation_date
        
        days = (expiry_dt - val_dt).days
        return max(days / 365.0, 0)
    
    def theoretical_price(self, market_data: MarketData) -> float:
        """
        Calculate theoretical futures price using cost-of-carry.
        
        F = S * exp((r - q) * T)
        """
        T = self.time_to_expiry(market_data.valuation_date)
        r = market_data.risk_free_rate
        q = market_data.dividend_yield
        S = market_data.spot_price
        
        return S * np.exp((r - q) * T)
    
    def value(self, market_data: MarketData) -> float:
        """
        Calculate mark-to-market value.
        
        For futures, value is the daily settlement (mark-to-market).
        """
        current_futures = self.theoretical_price(market_data)
        price_diff = current_futures - self.futures_price
        
        notional = price_diff * self.quantity * self.contract_size
        
        if self.side == PositionSide.SHORT:
            notional = -notional
        
        return notional
    
    def pnl(self, market_data: MarketData) -> float:
        """
        Calculate P&L from entry price.
        """
        current_futures = self.theoretical_price(market_data)
        
        if self.side == PositionSide.LONG:
            price_diff = current_futures - self.entry_price
        else:
            price_diff = self.entry_price - current_futures
        
        return price_diff * self.quantity * self.contract_size
    
    def delta(self, market_data: MarketData) -> float:
        """Futures delta is approximately 1 per contract."""
        multiplier = self.quantity * self.contract_size
        if self.side == PositionSide.SHORT:
            multiplier = -multiplier
        return multiplier
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'instrument_type': 'futures',
            'underlying': self.underlying,
            'futures_price': self.futures_price,
            'expiry': self.expiry.isoformat() if isinstance(self.expiry, datetime) else str(self.expiry),
            'side': self.side.value,
            'quantity': self.quantity,
            'contract_size': self.contract_size,
            'entry_price': self.entry_price
        }


@dataclass
class SwapPosition:
    """
    Interest Rate Swap position.
    
    Attributes:
        notional: Notional principal
        fixed_rate: Fixed leg rate (annual)
        payment_frequency: Payments per year (e.g., 4 for quarterly)
        maturity_years: Years until maturity
        pay_fixed: True if paying fixed (receiving floating)
        floating_spread: Spread over floating rate
    """
    notional: float
    fixed_rate: float
    payment_frequency: int
    maturity_years: float
    pay_fixed: bool = True
    floating_spread: float = 0.0
    
    def __post_init__(self):
        if self.notional <= 0:
            raise ValueError("Notional must be positive")
        if self.payment_frequency <= 0:
            raise ValueError("Payment frequency must be positive")
        if self.maturity_years <= 0:
            raise ValueError("Maturity must be positive")
    
    def value(self, market_data: MarketData) -> float:
        """
        Calculate swap MTM value.
        
        Simple model: PV of fixed leg - PV of floating leg (at par).
        """
        r = market_data.risk_free_rate  # Use as floating rate proxy
        
        n_payments = int(self.maturity_years * self.payment_frequency)
        period = 1 / self.payment_frequency
        
        # PV of fixed leg
        fixed_payment = self.notional * self.fixed_rate / self.payment_frequency
        pv_fixed = 0.0
        for i in range(1, n_payments + 1):
            t = i * period
            pv_fixed += fixed_payment * np.exp(-r * t)
        # Add notional at maturity
        pv_fixed += self.notional * np.exp(-r * self.maturity_years)
        
        # PV of floating leg (at par when discounted at floating rate)
        floating_rate = r + self.floating_spread
        floating_payment = self.notional * floating_rate / self.payment_frequency
        pv_floating = 0.0
        for i in range(1, n_payments + 1):
            t = i * period
            pv_floating += floating_payment * np.exp(-r * t)
        pv_floating += self.notional * np.exp(-r * self.maturity_years)
        
        if self.pay_fixed:
            return pv_floating - pv_fixed  # Receive floating, pay fixed
        else:
            return pv_fixed - pv_floating  # Receive fixed, pay floating
    
    def pnl(self, market_data: MarketData) -> float:
        """Swap PnL is same as current value (entered at par)."""
        return self.value(market_data)
    
    def dv01(self, market_data: MarketData) -> float:
        """
        Calculate DV01 (dollar value of 1bp rate change).
        """
        r = market_data.risk_free_rate
        
        # Bump up
        market_up = MarketData(
            spot_price=market_data.spot_price,
            risk_free_rate=r + 0.0001,
            dividend_yield=market_data.dividend_yield,
            volatility=market_data.volatility,
            valuation_date=market_data.valuation_date
        )
        
        # Bump down
        market_down = MarketData(
            spot_price=market_data.spot_price,
            risk_free_rate=r - 0.0001,
            dividend_yield=market_data.dividend_yield,
            volatility=market_data.volatility,
            valuation_date=market_data.valuation_date
        )
        
        value_up = self.value(market_up)
        value_down = self.value(market_down)
        
        return (value_down - value_up) / 2  # DV01 is positive for value decrease
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'instrument_type': 'swap',
            'notional': self.notional,
            'fixed_rate': self.fixed_rate,
            'payment_frequency': self.payment_frequency,
            'maturity_years': self.maturity_years,
            'pay_fixed': self.pay_fixed,
            'floating_spread': self.floating_spread
        }


def create_sample_portfolio() -> List:
    """
    Create a sample derivatives portfolio.
    
    Returns:
        List of derivative positions
    """
    from datetime import timedelta
    
    today = datetime.now()
    
    portfolio = [
        # Long call options on AAPL
        OptionPosition(
            underlying='AAPL',
            strike=180,
            expiry=today + timedelta(days=60),
            option_type='call',
            side=PositionSide.LONG,
            quantity=10,
            premium_paid=5.50
        ),
        
        # Short put options on AAPL (covered)
        OptionPosition(
            underlying='AAPL',
            strike=170,
            expiry=today + timedelta(days=30),
            option_type='put',
            side=PositionSide.SHORT,
            quantity=5,
            premium_paid=3.20
        ),
        
        # Long call options on SPY
        OptionPosition(
            underlying='SPY',
            strike=500,
            expiry=today + timedelta(days=90),
            option_type='call',
            side=PositionSide.LONG,
            quantity=20,
            premium_paid=8.00
        ),
        
        # Long futures on ES (S&P 500)
        FuturesPosition(
            underlying='ES',
            futures_price=5100,
            expiry=today + timedelta(days=45),
            side=PositionSide.LONG,
            quantity=2,
            contract_size=50.0,
            entry_price=5050
        ),
        
        # Receive fixed swap
        SwapPosition(
            notional=1000000,
            fixed_rate=0.045,
            payment_frequency=4,
            maturity_years=5.0,
            pay_fixed=False
        )
    ]
    
    return portfolio


if __name__ == "__main__":
    print("Testing Instruments Module...")
    
    # Create market data
    market = MarketData(
        spot_price=175,
        risk_free_rate=0.05,
        dividend_yield=0.01,
        volatility=0.25
    )
    
    # Test option
    option = OptionPosition(
        underlying='AAPL',
        strike=180,
        expiry=datetime.now() + pd.Timedelta(days=60),
        option_type='call',
        side=PositionSide.LONG,
        quantity=10,
        premium_paid=5.00
    )
    
    print(f"\nOption Position: {option.underlying} {option.strike} Call")
    print(f"  Value: ${option.value(market):,.2f}")
    print(f"  P&L: ${option.pnl(market):,.2f}")
    
    greeks = option.greeks(market)
    print(f"  Delta: {greeks['delta']:,.2f}")
    print(f"  Gamma: {greeks['gamma']:,.4f}")
    
    # Test futures
    futures = FuturesPosition(
        underlying='ES',
        futures_price=5100,
        expiry=datetime.now() + pd.Timedelta(days=45),
        side=PositionSide.LONG,
        quantity=2,
        contract_size=50.0,
        entry_price=5050
    )
    
    market_es = MarketData(spot_price=5080, risk_free_rate=0.05)
    print(f"\nFutures Position: {futures.underlying}")
    print(f"  Value: ${futures.value(market_es):,.2f}")
    print(f"  P&L: ${futures.pnl(market_es):,.2f}")
    
    # Test swap
    swap = SwapPosition(
        notional=1000000,
        fixed_rate=0.045,
        payment_frequency=4,
        maturity_years=5.0,
        pay_fixed=False
    )
    
    print(f"\nSwap Position: ${swap.notional:,.0f} notional")
    print(f"  Value: ${swap.value(market):,.2f}")
    print(f"  DV01: ${swap.dv01(market):,.2f}")
