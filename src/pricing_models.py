"""
Pricing Models Module
=====================
Option pricing using Black-Scholes, Binomial Tree, and Monte Carlo methods.
"""

import numpy as np
from scipy.stats import norm
from typing import Literal, Optional
from dataclasses import dataclass
from enum import Enum


class OptionType(Enum):
    """Option type enumeration."""
    CALL = "call"
    PUT = "put"


class ExerciseStyle(Enum):
    """Exercise style enumeration."""
    EUROPEAN = "european"
    AMERICAN = "american"


@dataclass
class OptionContract:
    """
    Represents an option contract.
    
    Attributes:
        spot: Current underlying price
        strike: Strike price
        time_to_expiry: Time to expiration in years
        risk_free_rate: Annual risk-free rate (decimal)
        volatility: Annual volatility (decimal)
        option_type: CALL or PUT
        dividend_yield: Continuous dividend yield (decimal)
    """
    spot: float
    strike: float
    time_to_expiry: float
    risk_free_rate: float
    volatility: float
    option_type: OptionType = OptionType.CALL
    dividend_yield: float = 0.0
    
    def __post_init__(self):
        """Validate inputs."""
        if self.spot <= 0:
            raise ValueError("Spot price must be positive")
        if self.strike <= 0:
            raise ValueError("Strike price must be positive")
        if self.time_to_expiry < 0:
            raise ValueError("Time to expiry cannot be negative")
        if self.volatility < 0:
            raise ValueError("Volatility cannot be negative")


@dataclass
class PricingResult:
    """Container for pricing results."""
    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    model: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'price': self.price,
            'delta': self.delta,
            'gamma': self.gamma,
            'theta': self.theta,
            'vega': self.vega,
            'rho': self.rho,
            'model': self.model
        }


def black_scholes_d1_d2(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    q: float = 0.0
) -> tuple:
    """
    Calculate d1 and d2 for Black-Scholes formula.
    
    Parameters:
        S: Spot price
        K: Strike price
        T: Time to expiry (years)
        r: Risk-free rate
        sigma: Volatility
        q: Dividend yield
    
    Returns:
        Tuple of (d1, d2)
    """
    if T <= 0:
        # At expiry
        return (np.inf if S > K else -np.inf, np.inf if S > K else -np.inf)
    
    sqrt_T = np.sqrt(T)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    
    return d1, d2


def black_scholes_price(option: OptionContract) -> float:
    """
    Calculate option price using Black-Scholes model.
    
    Parameters:
        option: OptionContract object
    
    Returns:
        Option price
    """
    S = option.spot
    K = option.strike
    T = option.time_to_expiry
    r = option.risk_free_rate
    sigma = option.volatility
    q = option.dividend_yield
    
    # Handle expiry case
    if T <= 0:
        if option.option_type == OptionType.CALL:
            return max(S - K, 0)
        else:
            return max(K - S, 0)
    
    d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma, q)
    
    if option.option_type == OptionType.CALL:
        price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
    
    return max(price, 0)


def black_scholes_greeks(option: OptionContract) -> PricingResult:
    """
    Calculate option price and all Greeks using Black-Scholes.
    
    Parameters:
        option: OptionContract object
    
    Returns:
        PricingResult with price and Greeks
    """
    S = option.spot
    K = option.strike
    T = option.time_to_expiry
    r = option.risk_free_rate
    sigma = option.volatility
    q = option.dividend_yield
    
    # Handle expiry
    if T <= 0:
        intrinsic = max(S - K, 0) if option.option_type == OptionType.CALL else max(K - S, 0)
        delta = 1.0 if (option.option_type == OptionType.CALL and S > K) else (
            -1.0 if (option.option_type == OptionType.PUT and S < K) else 0.0
        )
        return PricingResult(
            price=intrinsic,
            delta=delta,
            gamma=0.0,
            theta=0.0,
            vega=0.0,
            rho=0.0,
            model="Black-Scholes"
        )
    
    d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma, q)
    sqrt_T = np.sqrt(T)
    
    # Common terms
    exp_qt = np.exp(-q * T)
    exp_rt = np.exp(-r * T)
    pdf_d1 = norm.pdf(d1)
    cdf_d1 = norm.cdf(d1)
    cdf_d2 = norm.cdf(d2)
    cdf_neg_d1 = norm.cdf(-d1)
    cdf_neg_d2 = norm.cdf(-d2)
    
    # Price
    if option.option_type == OptionType.CALL:
        price = S * exp_qt * cdf_d1 - K * exp_rt * cdf_d2
        delta = exp_qt * cdf_d1
        rho = K * T * exp_rt * cdf_d2 / 100  # Per 1% change
    else:
        price = K * exp_rt * cdf_neg_d2 - S * exp_qt * cdf_neg_d1
        delta = -exp_qt * cdf_neg_d1
        rho = -K * T * exp_rt * cdf_neg_d2 / 100
    
    # Greeks (same for call and put)
    gamma = exp_qt * pdf_d1 / (S * sigma * sqrt_T)
    theta = (
        -S * exp_qt * pdf_d1 * sigma / (2 * sqrt_T)
        - r * K * exp_rt * (cdf_d2 if option.option_type == OptionType.CALL else cdf_neg_d2)
        + q * S * exp_qt * (cdf_d1 if option.option_type == OptionType.CALL else cdf_neg_d1)
    ) / 365  # Per day
    
    if option.option_type == OptionType.PUT:
        theta = (
            -S * exp_qt * pdf_d1 * sigma / (2 * sqrt_T)
            + r * K * exp_rt * cdf_neg_d2
            - q * S * exp_qt * cdf_neg_d1
        ) / 365
    
    vega = S * exp_qt * pdf_d1 * sqrt_T / 100  # Per 1% vol change
    
    return PricingResult(
        price=max(price, 0),
        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
        rho=rho,
        model="Black-Scholes"
    )


def binomial_tree_price(
    option: OptionContract,
    n_steps: int = 100,
    exercise_style: ExerciseStyle = ExerciseStyle.EUROPEAN
) -> float:
    """
    Calculate option price using Cox-Ross-Rubinstein binomial tree.
    
    Parameters:
        option: OptionContract object
        n_steps: Number of time steps
        exercise_style: EUROPEAN or AMERICAN
    
    Returns:
        Option price
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
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    discount = np.exp(-r * dt)
    
    # Build price tree at maturity
    stock_prices = S * (u ** np.arange(n_steps, -1, -1)) * (d ** np.arange(0, n_steps + 1))
    
    # Option values at maturity
    if is_call:
        option_values = np.maximum(stock_prices - K, 0)
    else:
        option_values = np.maximum(K - stock_prices, 0)
    
    # Backward induction
    for step in range(n_steps - 1, -1, -1):
        stock_prices = S * (u ** np.arange(step, -1, -1)) * (d ** np.arange(0, step + 1))
        option_values = discount * (p * option_values[:-1] + (1 - p) * option_values[1:])
        
        if exercise_style == ExerciseStyle.AMERICAN:
            if is_call:
                intrinsic = np.maximum(stock_prices - K, 0)
            else:
                intrinsic = np.maximum(K - stock_prices, 0)
            option_values = np.maximum(option_values, intrinsic)
    
    return option_values[0]


def monte_carlo_price(
    option: OptionContract,
    n_simulations: int = 100000,
    n_steps: int = 252,
    random_seed: Optional[int] = None
) -> tuple:
    """
    Calculate option price using Monte Carlo simulation.
    
    Parameters:
        option: OptionContract object
        n_simulations: Number of simulation paths
        n_steps: Number of time steps per path
        random_seed: Random seed for reproducibility
    
    Returns:
        Tuple of (price, standard_error)
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    S = option.spot
    K = option.strike
    T = option.time_to_expiry
    r = option.risk_free_rate
    sigma = option.volatility
    q = option.dividend_yield
    is_call = option.option_type == OptionType.CALL
    
    if T <= 0:
        price = max(S - K, 0) if is_call else max(K - S, 0)
        return price, 0.0
    
    dt = T / n_steps
    drift = (r - q - 0.5 * sigma**2) * dt
    vol = sigma * np.sqrt(dt)
    
    # Generate paths
    Z = np.random.standard_normal((n_simulations, n_steps))
    log_returns = drift + vol * Z
    log_paths = np.cumsum(log_returns, axis=1)
    final_prices = S * np.exp(log_paths[:, -1])
    
    # Calculate payoffs
    if is_call:
        payoffs = np.maximum(final_prices - K, 0)
    else:
        payoffs = np.maximum(K - final_prices, 0)
    
    # Discount
    discount = np.exp(-r * T)
    discounted_payoffs = discount * payoffs
    
    price = np.mean(discounted_payoffs)
    std_error = np.std(discounted_payoffs) / np.sqrt(n_simulations)
    
    return price, std_error


def implied_volatility(
    market_price: float,
    option: OptionContract,
    max_iterations: int = 100,
    tolerance: float = 1e-6
) -> float:
    """
    Calculate implied volatility using Newton-Raphson method.
    
    Parameters:
        market_price: Observed market price
        option: OptionContract with initial volatility guess
        max_iterations: Maximum iterations
        tolerance: Convergence tolerance
    
    Returns:
        Implied volatility
    """
    sigma = option.volatility if option.volatility > 0 else 0.2
    
    for _ in range(max_iterations):
        # Create option with current sigma guess
        test_option = OptionContract(
            spot=option.spot,
            strike=option.strike,
            time_to_expiry=option.time_to_expiry,
            risk_free_rate=option.risk_free_rate,
            volatility=sigma,
            option_type=option.option_type,
            dividend_yield=option.dividend_yield
        )
        
        result = black_scholes_greeks(test_option)
        price_diff = result.price - market_price
        
        if abs(price_diff) < tolerance:
            return sigma
        
        # Vega for Newton-Raphson (convert from per 1% to per 100%)
        vega = result.vega * 100
        
        if abs(vega) < 1e-10:
            # Vega too small, try bisection
            break
        
        sigma = sigma - price_diff / vega
        sigma = max(0.001, min(sigma, 5.0))  # Keep sigma in reasonable range
    
    # Fallback: bisection method
    sigma_low, sigma_high = 0.001, 3.0
    
    for _ in range(100):
        sigma_mid = (sigma_low + sigma_high) / 2
        test_option = OptionContract(
            spot=option.spot,
            strike=option.strike,
            time_to_expiry=option.time_to_expiry,
            risk_free_rate=option.risk_free_rate,
            volatility=sigma_mid,
            option_type=option.option_type,
            dividend_yield=option.dividend_yield
        )
        
        price = black_scholes_price(test_option)
        
        if abs(price - market_price) < tolerance:
            return sigma_mid
        
        if price < market_price:
            sigma_low = sigma_mid
        else:
            sigma_high = sigma_mid
    
    return sigma_mid


if __name__ == "__main__":
    print("Testing Pricing Models...")
    
    # Create a sample option
    option = OptionContract(
        spot=100,
        strike=100,
        time_to_expiry=0.25,  # 3 months
        risk_free_rate=0.05,
        volatility=0.2,
        option_type=OptionType.CALL
    )
    
    # Black-Scholes
    result = black_scholes_greeks(option)
    print(f"\nBlack-Scholes Call Option:")
    print(f"  Price: ${result.price:.4f}")
    print(f"  Delta: {result.delta:.4f}")
    print(f"  Gamma: {result.gamma:.4f}")
    print(f"  Theta: ${result.theta:.4f}/day")
    print(f"  Vega: ${result.vega:.4f}/1%")
    print(f"  Rho: ${result.rho:.4f}/1%")
    
    # Binomial Tree
    euro_price = binomial_tree_price(option, n_steps=200, exercise_style=ExerciseStyle.EUROPEAN)
    amer_price = binomial_tree_price(option, n_steps=200, exercise_style=ExerciseStyle.AMERICAN)
    print(f"\nBinomial Tree (200 steps):")
    print(f"  European: ${euro_price:.4f}")
    print(f"  American: ${amer_price:.4f}")
    
    # Monte Carlo
    mc_price, mc_error = monte_carlo_price(option, n_simulations=100000, random_seed=42)
    print(f"\nMonte Carlo (100k paths):")
    print(f"  Price: ${mc_price:.4f} ± ${mc_error:.4f}")
    
    # Implied Volatility
    iv = implied_volatility(result.price, option)
    print(f"\nImplied Volatility: {iv:.4f} (expected: 0.2000)")
