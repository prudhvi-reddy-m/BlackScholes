import math
import pytest

from BlackScholes import BlackScholes


def test_intrinsic_values():
    bs = BlackScholes(0.0, 100, 120, 0.2, 0.05)
    call, put = bs.calculate_prices()
    assert call == pytest.approx(20.0)
    assert put == pytest.approx(0.0)


def test_black_scholes_values():
    bs = BlackScholes(1.0, 100, 100, 0.2, 0.05)
    call, put = bs.calculate_prices()
    assert call == pytest.approx(10.4506, rel=1e-4)
    assert put == pytest.approx(5.5735, rel=1e-4)
