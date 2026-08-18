"""Lightweight local mock of JoinQuant's proprietary ``jqdata`` platform module.

The strategy scripts (``A2``, ``As``) do ``from jqdata import *`` and rely on a
large surface of platform-injected globals (``g``, ``log``, ``query``, market
data helpers, order helpers, etc.). Those symbols only exist inside JoinQuant's
online backtesting environment and cannot be installed from PyPI.

This module reproduces just enough of that surface, backed by deterministic
synthetic data, so the real strategy code can be loaded and its
platform-independent analytics (beta / hedge-ratio, futures rollover) can be run
locally to prove the Python environment works. It is a development aid only and
does NOT replicate JoinQuant's trading semantics.
"""

import numpy as np
import pandas as pd


class _G:
    """Stand-in for JoinQuant's mutable global namespace object ``g``."""


g = _G()


class _Log:
    def _emit(self, level, msg, *args):
        if args:
            msg = msg % args
        print(f"[{level}] {msg}")

    def info(self, msg, *args):
        self._emit("info", msg, *args)

    def warning(self, msg, *args):
        self._emit("warning", msg, *args)

    def error(self, msg, *args):
        self._emit("error", msg, *args)

    def set_level(self, *_args, **_kwargs):
        pass


log = _Log()


def _synthetic_prices(n, cols, seed=0, start=100.0, vol=0.01):
    """Deterministic geometric-random-walk close prices as a DataFrame."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2015-01-01", periods=n, freq="D")
    data = {}
    for i, col in enumerate(cols):
        rets = rng.normal(0.0004, vol, size=n)
        data[col] = start * np.cumprod(1 + rets) * (1 + 0.05 * i)
    return pd.DataFrame(data, index=dates)


def history(count, unit, field, security_list, **_kwargs):
    return _synthetic_prices(count, list(security_list), seed=42)


def attribute_history(security, count, unit, field, **_kwargs):
    return _synthetic_prices(count, ["close"], seed=7)


class _Noop:
    """Callable/attribute placeholder for unused platform helpers."""

    def __init__(self, name="jqdata_stub"):
        self._name = name

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, item):
        return _Noop(f"{self._name}.{item}")


def get_all_trade_days():
    return list(pd.date_range("2005-01-01", "2025-12-31", freq="B").date)


get_all_securities = _Noop("get_all_securities")
get_fundamentals = _Noop("get_fundamentals")
get_price = _Noop("get_price")
get_current_data = _Noop("get_current_data")
query = _Noop("query")
income = _Noop("income")
balance = _Noop("balance")
valuation = _Noop("valuation")
set_option = _Noop("set_option")
set_slippage = _Noop("set_slippage")
set_commission = _Noop("set_commission")
set_subportfolios = _Noop("set_subportfolios")
order_target = _Noop("order_target")
order_target_value = _Noop("order_target_value")
transfer_cash = _Noop("transfer_cash")
FixedSlippage = _Noop("FixedSlippage")
PerTrade = _Noop("PerTrade")
SubPortfolioConfig = _Noop("SubPortfolioConfig")

__all__ = [
    "g", "log", "history", "attribute_history", "get_all_trade_days",
    "get_all_securities", "get_fundamentals", "get_price", "get_current_data",
    "query", "income", "balance", "valuation", "set_option", "set_slippage",
    "set_commission", "set_subportfolios", "order_target", "order_target_value",
    "transfer_cash", "FixedSlippage", "PerTrade", "SubPortfolioConfig",
]
