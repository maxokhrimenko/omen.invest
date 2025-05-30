# ==============================================================
#  📈  PORTFOLIO ANALYZER (PER-TICKER)  –  v3.1.0  📊
# ==============================================================

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date
import os
from portfolio_analysis_consolidated import (
    START, END, RF_ANNUAL,
    load_prices, sharpe_ratio, max_drawdown,
    pct, usd
)

# ---------- 1) YOUR PORTFOLIO  (ticker  ↔  quantity) ----------
INPUT_FILE = "input/input.csv"

def parse_portfolio(csv_path: str) -> pd.Series:
    """Returns Series{ticker: quantity} with Yahoo-format tickers."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Portfolio file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    if 'ticker' not in df.columns or 'position' not in df.columns:
        raise ValueError("CSV must contain 'ticker' and 'position' columns")
    
    return pd.Series(
        {t.replace('.', '-'): float(q) for t, q in zip(df['ticker'], df['position'])},
        name="Qty"
    )

def get_yield_color(yield_value):
    """Returns ANSI color code based on yield percentage."""
    if not isinstance(yield_value, (int, float)):
        return ""  # No color for non-numeric values
    
    if yield_value < 2:
        return "\033[91m"  # Red
    elif yield_value < 6:
        return "\033[93m"  # Yellow
    else:
        return "\033[92m"  # Green

def get_annual_dividends_and_yields(ticker_symbol: str, 
                                    prices_for_ticker: pd.Series, 
                                    dividend_history_for_ticker: pd.Series, 
                                    overall_start_date_str: str, 
                                    overall_end_date_str: str) -> dict:
    """
    Calculates sum of dividends and dividend yield for each full calendar year 
    within the ticker's data range and the overall analysis period.
    For current year, includes both actual and expected dividends.
    Yield is calculated as (Total Dividends in Year / Price at Start of Year) * 100.

    Args:
        ticker_symbol (str): The ticker symbol.
        prices_for_ticker (pd.Series): Adjusted closing prices for the ticker (index: Timestamp, values: float).
        dividend_history_for_ticker (pd.Series): Dividends for the ticker (index: Timestamp, values: float).
        overall_start_date_str (str): The overall analysis start date (YYYY-MM-DD).
        overall_end_date_str (str): The overall analysis end date (YYYY-MM-DD).

    Returns:
        dict: {year (int): {"total_divs": float, "yield_pct": float, "price_at_year_start": float}}
              Returns empty dict if no valid years or data.
    """
    yearly_data = {}
    
    if prices_for_ticker.empty: # No price data, cannot calculate yield
        return yearly_data

    # Convert timezone-aware timestamps to timezone-naive
    if dividend_history_for_ticker.index.tz is not None:
        dividend_history_for_ticker.index = dividend_history_for_ticker.index.tz_localize(None)

    analysis_start_dt = pd.Timestamp(overall_start_date_str)
    analysis_end_dt = pd.Timestamp(overall_end_date_str)

    # Get the range of years from the analysis period
    start_year = analysis_start_dt.year
    end_year = analysis_end_dt.year
    
    # Get current year and date
    current_year = pd.Timestamp.now().year
    current_date = pd.Timestamp.now()
    
    for year in range(start_year, end_year + 1):
        calendar_year_start_dt = pd.Timestamp(f"{year}-01-01")
        calendar_year_end_dt = pd.Timestamp(f"{year}-12-31")

        # Get price at the start of this calendar year (first trading day of the year)
        prices_at_or_after_year_start = prices_for_ticker[prices_for_ticker.index >= calendar_year_start_dt]
        
        price_at_year_start_val = np.nan
        if not prices_at_or_after_year_start.empty:
            first_price_timestamp = prices_at_or_after_year_start.index[0]
            if pd.Timestamp(first_price_timestamp).year == year: # Ensure the price is from the current evaluating year
                price_at_year_start_val = prices_at_or_after_year_start.iloc[0]

        # Sum of dividends paid during this specific calendar year
        total_dividends_in_year = 0.0
        if not dividend_history_for_ticker.empty:
            dividends_in_year_series = dividend_history_for_ticker[
                (dividend_history_for_ticker.index >= calendar_year_start_dt) &
                (dividend_history_for_ticker.index <= calendar_year_end_dt)
            ]
            total_dividends_in_year = dividends_in_year_series.sum()

            # For current year, calculate expected annual yield
            if year == current_year:
                # Get the most recent dividend payment
                recent_divs = dividend_history_for_ticker[
                    (dividend_history_for_ticker.index >= calendar_year_start_dt) &
                    (dividend_history_for_ticker.index <= current_date)
                ]
                
                if not recent_divs.empty:
                    # Calculate average dividend payment and frequency
                    div_payments = recent_divs[recent_divs > 0]  # Only consider positive payments
                    if not div_payments.empty:
                        avg_div = div_payments.mean()
                        # Estimate number of payments per year (assuming quarterly, semi-annual, or annual)
                        if len(div_payments) >= 2:
                            time_between_payments = (div_payments.index[-1] - div_payments.index[0]).days / (len(div_payments) - 1)
                            payments_per_year = 365 / time_between_payments
                        else:
                            # If only one payment, assume quarterly (4 payments per year)
                            payments_per_year = 4
                        
                        # Calculate expected annual dividends
                        expected_annual_divs = avg_div * payments_per_year
                        # Add expected future dividends to actual dividends
                        total_dividends_in_year = max(total_dividends_in_year, expected_annual_divs)
        
        current_yield_pct = 0.0
        if total_dividends_in_year > 0 and not pd.isna(price_at_year_start_val) and price_at_year_start_val > 0:
            current_yield_pct = round((total_dividends_in_year / price_at_year_start_val) * 100, 1)
        
        yearly_data[year] = {
            "total_divs": round(total_dividends_in_year, 4),
            "yield_pct": current_yield_pct,
            "price_at_year_start": round(price_at_year_start_val, 2) if not pd.isna(price_at_year_start_val) else np.nan
        }
            
    return yearly_data

def annualized_volatility(returns):
    """Calculates annualized volatility from daily returns."""
    if returns.empty:
        return np.nan
    return returns.std() * np.sqrt(252)

def sortino_ratio(returns, rf_daily):
    """Calculates Sortino ratio from daily returns."""
    if returns.empty:
        return np.nan
    excess = returns - rf_daily
    downside = returns[returns < 0]
    if len(downside) == 0 or downside.std() == 0:
        return np.nan
    return np.sqrt(252) * excess.mean() / downside.std()

def historical_var(returns, confidence=0.95):
    """Calculates 1-day Historical VaR at specified confidence level."""
    if returns.empty:
        return np.nan
    return np.percentile(returns, (1 - confidence) * 100) * 100  # Convert to percentage

def beta_to_portfolio(ticker_returns, portfolio_returns):
    """Calculates beta against portfolio returns."""
    if ticker_returns.empty or portfolio_returns.empty:
        return np.nan
    # Align the returns
    aligned_returns = pd.concat([ticker_returns, portfolio_returns], axis=1).dropna()
    if len(aligned_returns) < 2:
        return np.nan
    # Calculate beta using covariance method
    covar = aligned_returns.iloc[:, 0].cov(aligned_returns.iloc[:, 1])
    portfolio_var = aligned_returns.iloc[:, 1].var()
    return covar / portfolio_var if portfolio_var != 0 else np.nan

def momentum_12_1(prices):
    """Calculates 12-1 momentum (skip last month)."""
    if len(prices) < 252:
        return np.nan
    # Get prices 252 days ago and 21 days ago
    price_252d = prices.iloc[-252]
    price_21d = prices.iloc[-21]
    return (price_21d - price_252d) / price_252d

def calculate_score(metrics, weights):
    """Calculates weighted score from normalized metrics."""
    if not metrics or not weights:
        return np.nan
    
    # Normalize metrics to 0-100
    normalized = {}
    for metric, value in metrics.items():
        if pd.isna(value):
            continue
        # For risk metrics (lower is better), multiply by -1
        if metric in ['Volatility', 'VaR', 'MaxDD', 'Beta']:
            value = -value
        normalized[metric] = value
    
    if not normalized:
        return np.nan
    
    # Get min and max for normalization
    min_val = min(normalized.values())
    max_val = max(normalized.values())
    
    if max_val == min_val:
        return 50  # Return middle score if all values are the same
    
    # Calculate weighted score
    score = 0
    total_weight = 0
    
    for metric, value in normalized.items():
        if metric in weights:
            # Normalize to 0-100
            norm_value = 100 * (value - min_val) / (max_val - min_val)
            score += norm_value * weights[metric]
            total_weight += weights[metric]
    
    return score / total_weight if total_weight > 0 else np.nan

def get_rating(score):
    """Maps score to rating (1-5)."""
    if pd.isna(score):
        return "N/A"
    if score < 20:
        return "1"
    elif score < 40:
        return "2"
    elif score < 60:
        return "3"
    elif score < 80:
        return "4"
    else:
        return "5"

def get_color(metric, value):
    """Returns color code based on metric thresholds."""
    if pd.isna(value):
        return ""
    
    thresholds = {
        'Annual Return': {'bad': 0.05, 'excellent': 0.20},
        'Sharpe': {'bad': 0.5, 'excellent': 1.5},
        'MaxDD': {'bad': 0.50, 'excellent': 0.30},
        'Vol': {'bad': 0.50, 'excellent': 0.30},
        'Sortino': {'bad': 0.8, 'excellent': 2.0},
        'Beta': {'bad': 1.5, 'excellent': 0.5},
        'VaR': {'bad': 0.04, 'excellent': 0.02},
        'Momentum': {'bad': 0.0, 'excellent': 0.20},
        'Current Yield': {'bad': 0.01, 'excellent': 0.04},
        'Avg Yield': {'bad': 0.01, 'excellent': 0.04},
        'Max Yield': {'bad': 0.02, 'excellent': 0.06}
    }
    
    if metric not in thresholds:
        return ""
        
    t = thresholds[metric]
    if metric in ['MaxDD', 'Vol', 'VaR', 'Beta']:
        if value <= t['excellent']:
            return "\033[92m"  # Green
        elif value >= t['bad']:
            return "\033[91m"  # Red
    else:
        if value >= t['excellent']:
            return "\033[92m"  # Green
        elif value <= t['bad']:
            return "\033[91m"  # Red
    return "\033[93m"  # Yellow

def do_per_ticker():
    # ---------- LOAD DATA ------------------------------------
    print("Parsing portfolio...")
    try:
        qty_ser = parse_portfolio(INPUT_FILE)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure input/input.csv exists with 'ticker' and 'position' columns")
        exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    print(f"\nLoading prices for {len(qty_ser)} tickers from {START} to {END}...")
    close   = load_prices(qty_ser.index, START, END)

    # Filter: prices exist both at A and B (overall period start/end)
    if not close.empty:
        mask_alive   = close.iloc[0].notna() & close.iloc[-1].notna()
        live_tickers = close.columns[mask_alive]
        excluded     = sorted(list(set(qty_ser.index) - set(live_tickers)))

        close   = close[live_tickers].dropna(axis=1, how='all') # Drop columns that are all NaN
        qty_ser = qty_ser.reindex(close.columns).dropna() # Align quantities with available price data
    else:
        print("No price data loaded. Exiting.")
        live_tickers = pd.Index([])
        excluded = list(qty_ser.index)
        qty_ser = pd.Series(dtype=float)

    if not close.empty:
        n_days   = len(pd.date_range(start=close.index.min(), end=close.index.max(), freq='B')) # Business days in actual data range
        rf_daily = RF_ANNUAL / 252 # Standard assumption
    else:
        n_days = 0
        rf_daily = RF_ANNUAL / 252

    if close.empty or live_tickers.empty:
        print("\nCannot perform per-ticker analysis: No valid price data for live tickers.")
        if excluded:
             print(f"\n⚠️  Tickers excluded due to missing price data at period start/end or other issues: {', '.join(excluded)}")
        return

    rows = []
    
    print("\nFetching dividend history...")
    all_dividend_histories = {}
    for t in live_tickers:
        try:
            ticker_obj = yf.Ticker(t)
            divs = ticker_obj.dividends
            all_dividend_histories[t] = divs
        except Exception as e:
            all_dividend_histories[t] = pd.Series(dtype='float64', index=pd.to_datetime([])) 
    print("Calculating metrics...")

    # Calculate portfolio returns for beta calculation
    port = (close * qty_ser).sum(axis=1)
    port_rts = port.pct_change().dropna()

    for t in live_tickers:
        ser = close[t].dropna()
        if ser.size < 2:
            continue
        
        rts = ser.pct_change().dropna()
        if rts.empty:
            curv = pd.Series([1] * len(ser), index=ser.index)
            s, e = ser.iloc[0], ser.iloc[-1]
            tot = e / s - 1 if s != 0 else np.nan
            ann = np.nan
            shp = np.nan
            mdd = 0.0 if s > 0 else np.nan
        else:
            curv = (1 + rts).cumprod()
            s, e = ser.iloc[0], ser.iloc[-1]
            tot = e / s - 1 if s != 0 else np.nan
            
            actual_ticker_trading_days = len(rts)
            if actual_ticker_trading_days > 0:
                ann = (1 + tot) ** (252 / actual_ticker_trading_days) - 1 if not pd.isna(tot) else np.nan
            else:
                ann = np.nan
            shp = sharpe_ratio(rts, rf_daily)
            mdd = max_drawdown(curv)

        # Calculate new metrics
        vol = annualized_volatility(rts)
        srt = sortino_ratio(rts, rf_daily)
        bta = beta_to_portfolio(rts, port_rts)
        var = historical_var(rts)
        mom = momentum_12_1(ser)

        ticker_dividend_history = all_dividend_histories.get(t, pd.Series(dtype='float64', index=pd.to_datetime([])))
        
        annual_div_data = get_annual_dividends_and_yields(
            t, 
            ser,
            ticker_dividend_history, 
            START,
            END
        )
        
        # Calculate yield metrics
        max_yield = 0.0
        avg_yield = 0.0
        current_yield = 0.0
        valid_yields = []
        
        if annual_div_data:
            for year, data in annual_div_data.items():
                yield_pct = data['yield_pct']
                if yield_pct > 0:
                    valid_yields.append(yield_pct)
                    max_yield = max(max_yield, yield_pct)
            
            if valid_yields:
                avg_yield = sum(valid_yields) / len(valid_yields)
                
            last_year = max(annual_div_data.keys())
            current_yield = annual_div_data[last_year]['yield_pct']

        # Calculate score
        metrics = {
            'Annual Return': ann,
            'Sharpe': shp,
            'MaxDD': mdd,
            'Vol': vol,
            'Sortino': srt,
            'Beta': bta,
            'VaR': var,
            'Momentum': mom,
            'Current Yield': current_yield,
            'Avg Yield': avg_yield,
            'Max Yield': max_yield
        }
        
        weights = {
            'Annual Return': 0.15,
            'Sharpe': 0.15,
            'MaxDD': 0.10,
            'Vol': 0.10,
            'Sortino': 0.10,
            'Beta': 0.05,
            'VaR': 0.10,
            'Momentum': 0.10,
            'Current Yield': 0.05,
            'Avg Yield': 0.05,
            'Max Yield': 0.05
        }
        
        score = calculate_score(metrics, weights)
        rating = get_rating(score)
        
        row_data = {
            "Ticker": t,
            "Start $": s,
            "End $": e,
            "TotRet": tot,
            "AnnRet": ann,
            "Sharpe": shp,
            "MaxDD": mdd,
            "Vol": vol,
            "Sortino": srt,
            "Beta": bta,
            "VaR": var,
            "Momentum": mom,
            "Max Yield": max_yield,
            "Avg Yield": avg_yield,
            "Current Yield": current_yield,
            "Score": score,
            "Rating": rating
        }
        
        rows.append(row_data)

    if not rows:
        print("No data to display for per-ticker metrics.")
        if excluded:
            print(f"\n⚠️  Tickers excluded due to missing price data at period start/end or other issues: {', '.join(excluded)}")
        return

    df = pd.DataFrame(rows)
    if "Score" in df.columns:
        df = df.sort_values("Score", ascending=False, na_position='last')

    # Define column order
    base_columns = ["Ticker", "Start $", "End $", "TotRet", "AnnRet", "Sharpe", "MaxDD", 
                   "Vol", "Sortino", "Beta", "VaR", "Momentum", 
                   "Max Yield", "Avg Yield", "Current Yield", "Score", "Rating"]
    all_columns = base_columns

    # Reorder columns and fill NaN values with "N/A"
    df = df.reindex(columns=all_columns).fillna("N/A")

    # Format the table
    col_widths = {
        "Ticker": 7,
        "Start $": 10,
        "End $": 9,
        "TotRet": 8,
        "AnnRet": 8,
        "Sharpe": 7,
        "MaxDD": 8,
        "Vol": 8,
        "Sortino": 8,
        "Beta": 6,
        "VaR": 6,
        "Momentum": 8,
        "Max Yield": 9,
        "Avg Yield": 9,
        "Current Yield": 12,
        "Score": 6,
        "Rating": 6
    }

    # Create header
    header_parts = ["#"] + all_columns
    header_str = " | ".join([h.center(col_widths.get(h, len(h))) for h in header_parts])
    separator_str = "-+-".join(["-" * col_widths.get(h, len(h)) for h in header_parts])
    
    total_table_width = len(header_str)

    print("\n" + "📑 PER-TICKER METRICS (Score ↓)".center(total_table_width, "─"))
    print(header_str)
    print(separator_str)

    # ANSI color reset code
    RESET = "\033[0m"

    for i, r in df.iterrows():
        row_parts = [f"{i+1:<3}"]
        for col in all_columns:
            if col == "Ticker":
                row_parts.append(f"{r[col]:<{col_widths[col]-1}}")
            elif col in ["Start $", "End $"]:
                row_parts.append(f"{r[col]:>{col_widths[col]-1}.2f}")
            elif col in ["TotRet", "AnnRet", "MaxDD", "Vol", "VaR", "Momentum"]:
                if isinstance(r[col], (int, float)):
                    color = get_color(col, r[col])
                    row_parts.append(f"{color}{pct(r[col]).strip():>{col_widths[col]-1}}{RESET}")
                else:
                    row_parts.append(f"{r[col]:>{col_widths[col]-1}}")
            elif col in ["Sharpe", "Sortino", "Beta", "Score"]:
                if isinstance(r[col], (int, float)):
                    color = get_color(col, r[col])
                    row_parts.append(f"{color}{r[col]:>{col_widths[col]-1}.2f}{RESET}")
                else:
                    row_parts.append(f"{r[col]:>{col_widths[col]-1}}")
            elif col in ["Max Yield", "Avg Yield", "Current Yield"]:
                if isinstance(r[col], (int, float)):
                    color = get_color(col, r[col])
                    row_parts.append(f"{color}{r[col]:>{col_widths[col]-1}.1f}%{RESET}")
                else:
                    row_parts.append(f"{r[col]:>{col_widths[col]-1}}")
            elif col == "Rating":
                row_parts.append(f"{r[col]:>{col_widths[col]-1}}")
        
        print(" | ".join(row_parts))
        
    if excluded:
        print("\n⚠️  Tickers excluded due to missing price data at period start/end or other issues: " + ", ".join(excluded))
    print("─"*total_table_width + "\n")

if __name__ == '__main__':
    do_per_ticker() 