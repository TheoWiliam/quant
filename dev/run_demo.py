"""End-to-end smoke demo for the JoinQuant strategy scripts in this repo.

Because ``jqdata`` is proprietary, this loads the REAL strategy code (``A2`` /
``As``) on top of the local :mod:`jqdata` mock and then runs the strategy's
platform-independent analytics against deterministic synthetic data:

  * ``set_params()``            -> populates the strategy's global params on ``g``
  * ``compute_hedge_ratio(...)`` -> real numpy covariance/beta + hedge ratio
  * ``get_next_month_future(...)`` -> real datetime-based contract rollover

Run:  python dev/run_demo.py [A2|As]
"""

import datetime
import os
import sys

DEV_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(DEV_DIR)
sys.path.insert(0, DEV_DIR)  # make the mock `jqdata` importable


class _Ctx:
    """Minimal context object exposing what the run analytics read."""

    def __init__(self, current_dt):
        self.current_dt = current_dt


def load_strategy(name):
    """Exec a strategy file (no .py extension) into a fresh namespace."""
    path = os.path.join(REPO_ROOT, name)
    with open(path, "r", encoding="utf-8") as fh:
        source = fh.read()
    ns = {"__name__": f"strategy_{name}"}
    exec(compile(source, path, "exec"), ns)
    return ns


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "As"
    print(f"=== Loading real strategy '{name}' on the jqdata mock ===")
    strat = load_strategy(name)
    print(f"Loaded {len([k for k, v in strat.items() if callable(v)])} strategy callables\n")

    print("--- set_params(): populate strategy globals on g ---")
    strat["set_params"]()
    g = strat["g"]
    print(f"g.tc={g.tc}  g.yb={g.yb}  g.percentile={g.percentile}  "
          f"g.futures_symbol={g.futures_symbol}  g.futures_margin_rate={g.futures_margin_rate}\n")

    print("--- compute_hedge_ratio(): real beta + hedge ratio on synthetic prices ---")
    stocks = ["000001.XSHE", "600000.XSHG", "000002.XSHE", "600519.XSHG"]
    hedge_ratio, beta = strat["compute_hedge_ratio"](None, stocks)
    print(f"portfolio stocks: {stocks}")
    print(f"beta        = {beta:.6f}")
    print(f"hedge_ratio = {hedge_ratio:.6f}")
    assert isinstance(beta, float) and isinstance(hedge_ratio, float)
    assert hedge_ratio > 0, "hedge ratio should be positive"
    print("OK: analytics produced finite, well-typed results\n")

    print("--- get_next_month_future(): contract rollover across sample dates ---")
    samples = [
        datetime.datetime(2015, 9, 1),
        datetime.datetime(2015, 9, 21),
        datetime.datetime(2016, 12, 30),
    ]
    for dt in samples:
        contract = strat["get_next_month_future"](_Ctx(dt), g.futures_symbol)
        print(f"  {dt.date()} -> {contract}")
        assert contract.endswith(".CCFX") and contract.startswith(g.futures_symbol)
    print("OK: rollover produced valid contract codes\n")

    print("=== DEMO PASSED: environment runs the real strategy analytics end-to-end ===")


if __name__ == "__main__":
    main()
