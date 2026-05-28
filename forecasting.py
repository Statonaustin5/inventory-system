"""
forecasting.py
--------------
Demand forecasting using OLS linear regression.

Model: ŷ = β₀ + β₁x
  - x = week number (1-indexed)
  - y = units sold that week
  - β₁ (slope) captures demand trend over time
  - β₀ (intercept) is the baseline
  - R² measures how well the line fits historical data
"""

import numpy as np


def linear_regression_forecast(sales: list[int], next_week: int) -> dict:
    """
    Fit an OLS regression line to historical sales and predict a future week.

    Parameters
    ----------
    sales     : list of weekly units sold (chronological order)
    next_week : the week number to predict (e.g. len(sales) + 1)

    Returns
    -------
    dict with keys: b0, b1, r2, predicted, trend
    """
    if len(sales) < 2:
        raise ValueError("Need at least 2 data points to fit a regression line.")

    x = np.arange(1, len(sales) + 1, dtype=float)
    y = np.array(sales, dtype=float)

    x_mean = x.mean()
    y_mean = y.mean()

    # OLS formulas
    b1 = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
    b0 = y_mean - b1 * x_mean

    # R² — proportion of variance explained
    y_hat    = b0 + b1 * x
    ss_res   = np.sum((y - y_hat) ** 2)
    ss_tot   = np.sum((y - y_mean) ** 2)
    r2       = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0

    predicted = max(0, round(float(b0 + b1 * next_week)))
    trend     = _classify_trend(b1)

    return {
        "b0":        round(float(b0), 3),
        "b1":        round(float(b1), 3),
        "r2":        round(float(r2), 3),
        "predicted": predicted,
        "trend":     trend,
    }


def _classify_trend(slope: float) -> str:
    """Map slope magnitude to a human-readable trend label."""
    if slope > 0.3:
        return "↑ Growing"
    if slope < -0.3:
        return "↓ Declining"
    return "→ Stable"
