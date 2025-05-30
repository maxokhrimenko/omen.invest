# ==============================================================
#  📈  PORTFOLIO ANALYZER (CONSOLIDATED)  –  v3.1.0  📊
# ==============================================================

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date
import os
from scipy.stats import norm

# ---------- 1) YOUR PORTFOLIO  (ticker  ↔  quantity) ----------
INPUT_FILE = "input/input.csv"

START = "2023-03-01"                     # date A
END   = date.today().isoformat()         # date B (today)
RF_ANNUAL = 0.05                         # 5% annual rate
# ---------------------------------------------------------------

# ---------- UTILITIES --------------------------------------------
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

def load_prices(tickers, start, end):
    """Downloads historical closing prices for a list of tickers."""
    ticker_list = list(tickers) # Convert Index to list if it's not already
    data = yf.download(ticker_list, start=start, end=end,
                       auto_adjust=True, progress=False, group_by="ticker")
    # Ensure data is a DataFrame, even for a single ticker
    if not isinstance(data.columns, pd.MultiIndex) and len(ticker_list) == 1:
        # For a single ticker, yf.download might return a Series or a DataFrame without MultiIndex
        # if group_by isn't effective. We'll restructure it.
        df_single = data[['Close']].copy()
        df_single.columns = pd.MultiIndex.from_product([ticker_list, ['Close']])
        data = df_single

    # Extract 'Close' prices, handling cases where some tickers might not have data
    price_series_list = []
    valid_tickers = [t for t in ticker_list if t in data.columns.levels[0]] if isinstance(data.columns, pd.MultiIndex) else ticker_list

    for t in valid_tickers:
        try:
            if isinstance(data.columns, pd.MultiIndex):
                price_series = data[t]["Close"]
            else: # Single ticker DataFrame not grouped by ticker
                price_series = data["Close"]
            price_series.name = t
            price_series_list.append(price_series)
        except KeyError:
            pass # Will be handled by later filtering

    if not price_series_list:
        return pd.DataFrame() # Return empty DataFrame if no valid price data

    return pd.concat(price_series_list, axis=1)

def sharpe_ratio(ret, rf_daily):
    """Calculates annualized Sharpe Ratio from daily returns."""
    if ret.std() == 0: # Avoid division by zero if returns are flat
        return np.nan if ret.mean() - rf_daily == 0 else np.inf * np.sign(ret.mean() - rf_daily)
    excess = ret - rf_daily
    return np.sqrt(252) * excess.mean() / excess.std()

def max_drawdown(curve):
    """Calculates Max Drawdown from a cumulative return curve."""
    if curve.empty or curve.iloc[0] == 0: # Avoid division by zero if curve starts at 0 or is empty
        return np.nan
    return ((curve - curve.cummax()) / curve.cummax()).min()

def pct(x):  return f"{x:7.1%}" if not pd.isna(x) else "   N/A "
def usd(x):  return f"${x:,.2f}" if not pd.isna(x) else "   N/A   "

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

def calmar_ratio(annual_return, max_drawdown):
    """Calculates Calmar ratio."""
    if pd.isna(annual_return) or pd.isna(max_drawdown) or max_drawdown == 0:
        return np.nan
    return annual_return / abs(max_drawdown)

def parametric_var(returns, confidence=0.95):
    """Calculates 1-day Parametric VaR at specified confidence level."""
    if returns.empty:
        return np.nan
    z_score = norm.ppf(1 - confidence)
    return -(z_score * returns.std() - returns.mean()) * 100  # Convert to percentage

def beta_calculation(portfolio_returns, benchmark_returns):
    """Calculates beta against benchmark."""
    if portfolio_returns.empty or benchmark_returns.empty:
        return np.nan
    # Align the returns
    aligned_returns = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    if len(aligned_returns) < 2:
        return np.nan
    # Calculate beta using covariance method
    covar = aligned_returns.iloc[:, 0].cov(aligned_returns.iloc[:, 1])
    benchmark_var = aligned_returns.iloc[:, 1].var()
    return covar / benchmark_var if benchmark_var != 0 else np.nan

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

def do_aggregate():
    if close.empty or qty_ser.empty:
        print("\nCannot perform aggregate analysis: No valid price or quantity data.")
        if excluded:
             print(f"\n⚠️  Tickers excluded due to missing price data at period start/end or other issues: {', '.join(excluded)}")
        return

    port = (close * qty_ser).sum(axis=1)
    if port.empty or port.nunique() < 2:
        print("\nCannot perform aggregate analysis: Portfolio value is constant or insufficient data.")
        return

    rts = port.pct_change().dropna()
    if rts.empty:
        print("\nCannot perform aggregate analysis: No returns could be calculated.")
        return
        
    curv = (1 + rts).cumprod()

    s_val, e_val = port.iloc[0], port.iloc[-1]
    tot = e_val / s_val - 1 if s_val != 0 else np.nan
    
    actual_trading_days_in_period = len(rts)
    if actual_trading_days_in_period > 0:
        ann = (1 + tot) ** (252 / actual_trading_days_in_period) - 1 if not pd.isna(tot) else np.nan
    else:
        ann = np.nan

    # Calculate all metrics
    shp = sharpe_ratio(rts, rf_daily)
    mdd = max_drawdown(curv)
    vol = annualized_volatility(rts)
    srt = sortino_ratio(rts, rf_daily)
    clm = calmar_ratio(ann, mdd)
    var = parametric_var(rts)
    
    # Calculate beta against SPY as benchmark
    try:
        spy = yf.download('SPY', start=START, end=END, progress=False)['Adj Close']
        spy_rts = spy.pct_change().dropna()
        bta = beta_calculation(rts, spy_rts)
    except:
        bta = np.nan

    # Define color thresholds
    def get_color(metric, value):
        if pd.isna(value):
            return ""
        
        thresholds = {
            'Annual Return': {'bad': 0.05, 'excellent': 0.15},
            'Sharpe': {'bad': 0.5, 'excellent': 1.5},
            'MaxDD': {'bad': 0.30, 'excellent': 0.15},
            'Volatility': {'bad': 0.20, 'excellent': 0.10},
            'Sortino': {'bad': 1.0, 'excellent': 2.0},
            'Calmar': {'bad': 0.5, 'excellent': 1.0},
            'VaR': {'bad': 0.02, 'excellent': 0.01},
            'Beta': {'bad': 1.3, 'excellent': 0.7}
        }
        
        if metric not in thresholds:
            return ""
            
        t = thresholds[metric]
        if metric in ['MaxDD', 'Volatility', 'VaR', 'Beta']:
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

    RESET = "\033[0m"

    print("\n" + "📊 PORTFOLIO RESULTS".center(60, "─"))
    print(f"🗓  {close.index.min().date()} → {close.index.max().date()} ({actual_trading_days_in_period} trading days)")
    print(f"💸  Start:    {usd(s_val)}")
    print(f"💰  End:      {usd(e_val)}")
    
    # Print all metrics with color coding
    print(f"{'🔺' if not pd.isna(tot) and tot>=0 else '🔻'}  Return:    {get_color('Annual Return', ann)}{pct(tot)}{RESET}")
    print(f"📈  Annual:   {get_color('Annual Return', ann)}{pct(ann)}{RESET}")
    print(f"📏  Sharpe:   {get_color('Sharpe', shp)}{shp:7.2f}{RESET}" if not pd.isna(shp) else "Sharpe:     N/A")
    print(f"📉  MaxDD:    {get_color('MaxDD', mdd)}{pct(mdd)}{RESET}")
    print(f"📊  Vol:      {get_color('Volatility', vol)}{pct(vol)}{RESET}")
    print(f"📈  Sortino:  {get_color('Sortino', srt)}{srt:7.2f}{RESET}" if not pd.isna(srt) else "Sortino:    N/A")
    print(f"📊  Calmar:   {get_color('Calmar', clm)}{clm:7.2f}{RESET}" if not pd.isna(clm) else "Calmar:     N/A")
    print(f"⚠️  VaR:      {get_color('VaR', var)}{var:7.2f}%{RESET}" if not pd.isna(var) else "VaR:        N/A")
    print(f"β   Beta:     {get_color('Beta', bta)}{bta:7.2f}{RESET}" if not pd.isna(bta) else "Beta:       N/A")
    
    if excluded:
        print(f"\n⚠️  Tickers excluded due to missing price data at period start/end or other issues: {', '.join(excluded)}")
    print("─"*60, "\n")

if __name__ == '__main__':
    if close.empty and not live_tickers.any():
        print(f"Could not load price data for any tickers in the portfolio for the period {START} to {END}.")
        print("Please check your ticker symbols, portfolio definition, and network connection.")
    else:
        do_aggregate() 