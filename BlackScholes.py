from numpy import exp, sqrt, log
from scipy.stats import norm


class BlackScholes:
    """Minimal Black-Scholes engine with intrinsic-value fallback.

    If *time_to_maturity* is 0 (or < 0) the class returns intrinsic
    value (pay-off at expiry) and sets Greeks accordingly.  Otherwise it
    returns discounted Black-Scholes prices and the usual Δ/Γ.
    """

    def __init__(
        self,
        time_to_maturity: float,
        strike: float,
        current_price: float,
        volatility: float,
        interest_rate: float,
    ) -> None:
        self.time_to_maturity = max(0.0, time_to_maturity)
        self.strike = strike
        self.current_price = current_price
        self.volatility = volatility
        self.interest_rate = interest_rate

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def calculate_prices(self):
        """Return (call_price, put_price) and populate Greek attributes."""
        if self.time_to_maturity == 0:
            return self._intrinsic_values()
        else:
            return self._bs_values()

    # ------------------------------------------------------------------
    # --- internal helpers ------------------------------------------------
    # ------------------------------------------------------------------
    def _intrinsic_values(self):
        """Intrinsic (expiry) prices + simple Greeks."""
        call_price = max(0.0, self.current_price - self.strike)
        put_price = max(0.0, self.strike - self.current_price)

        # Greeks at expiry: delta is ±1 if ITM, 0 if OTM; gamma/theta/vega->0
        self.call_delta = 1.0 if call_price > 0.0 else 0.0
        self.put_delta = -1.0 if put_price > 0.0 else 0.0
        self.call_gamma = self.put_gamma = 0.0

        self.call_price, self.put_price = call_price, put_price
        return call_price, put_price

    def _bs_values(self):
        """Black-Scholes analytical prices and Δ/Γ."""
        T = self.time_to_maturity
        S = self.current_price
        K = self.strike
        r = self.interest_rate
        sigma = self.volatility

        d1 = (
            log(S / K)
            + (r + 0.5 * sigma ** 2) * T
        ) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)

        call_price = S * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
        put_price = K * exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        # Greeks we actually use (Δ and Γ)
        self.call_delta = norm.cdf(d1)
        self.put_delta = self.call_delta - 1.0
        self.call_gamma = self.put_gamma = (
            norm.pdf(d1) / (S * sigma * sqrt(T))
        )

        self.call_price, self.put_price = call_price, put_price
        return call_price, put_price
