# ==============================================================
#  📈  PORTFOLIO ANALYZER (CONSOLIDATED)  –  v3.0.0  📊
# ==============================================================

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date

# ---------- 1) YOUR PORTFOLIO  (ticker  ↔  quantity) ----------
RAW_PORTFOLIO = """
TUYA	25
UNH	0.1
BRK.B	0.6
AAPL	0.75
FICO	0.02
UPST	1
CPRT	0.5
GPI	0.2
GLPI	2
MRK	0.25
XOM	0.2
BJ	0.5
COST	0.1
SPG	1
AZN	0.5
MO	1
OKE	1
PBA	1
MCK	0.1
ANET	0.3
SGOV	3
ENB	1
PFF	2
QCOM	0.2
L	0.25
ICSH	10
VZ	1
MCD	0.2
T	1
BIL	1
BND	1
KR	0.5
TDG	0.02
BX	0.2
HYG	1
EPD	1.3
VTIP	1
PG	0.5
BSM	2
VYM	0.2
JEPI	5
CPRX	1
KMI	1
CASY	0.2
PSO	2
WCN	0.5
CINF	0.2
MET	0.3
LIN	0.1
RLI	0.2
MPLX	1
GFI	2
WM	0.1
TKO	0.2
ALL	0.1
DUOL	0.05
KO	0.25
RIO	1
VFH	0.2
ET	2
CLS	0.2
IBM	0.1
MKL	0.02
OHI	1
MELI	0.01
ARCC	1
SPY	0.05
IAU	1
UBS	1
ASX	2
WRB	0.5
AXP	0.1
ROL	0.5
STWD	2
GLP	1
CEG	0.1
BLK	0.1
VRNA	0.5
VTI	0.2
CAAP	2
SCHG	1
HD	0.25
ASML	0.09
MNDY	0.1
NTRA	0.2
IBN	1
NU	2
KLAC	0.05
TTWO	0.2
GOOGL	0.7
PM	0.2
CAT	0.2
LYG	10
ORCL	0.2
AMZN	0.5
BCS	2
BKNG	0.006
SAP	0.2
UBER	0.5
TRI	0.25
VOO	0.4
TSM	0.2
META	0.1
QQQ	0.2
MAIN	2
AFRM	1
GLDM	3
TSLA	0.1
MCO	0.3
VUG	0.2
MA	0.25
URI	0.1
SPOT	0.1
WMT	1
MSFT	0.2
V	0.5
COF	0.5
NVDA	0.5
CHWY	1
GRND	2
SHOP	1
AVGO	0.3
NOW	0.1
APP	0.2
LIF	1
HOOD	2
PLTR	2
"""

START = "2023-03-01"                     # date A
END   = date.today().isoformat()         # date B (today)
RF_ANNUAL = 0.05                         # 5% annual rate
# ---------------------------------------------------------------

# ---------- UTILITIES --------------------------------------------
def parse_portfolio(raw: str) -> pd.Series:
    """Returns Series{ticker: quantity} with Yahoo-format tickers."""
    return pd.Series(
        {t.replace('.', '-'): float(q) for t, q in
         (ln.split() for ln in raw.strip().splitlines())},
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

# ---------- LOAD DATA ------------------------------------
print("Parsing portfolio...")
qty_ser = parse_portfolio(RAW_PORTFOLIO)
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
    if port.empty or port.nunique() < 2 : # Need at least two different portfolio values to calculate returns
        print("\nCannot perform aggregate analysis: Portfolio value is constant or insufficient data.")
        return

    rts  = port.pct_change().dropna()
    if rts.empty:
        print("\nCannot perform aggregate analysis: No returns could be calculated.")
        return
        
    curv = (1 + rts).cumprod()

    s_val, e_val = port.iloc[0], port.iloc[-1] # Use actual first and last available portfolio values
    
    tot = e_val / s_val - 1 if s_val != 0 else np.nan
    
    # Calculate annualized return based on the actual number of trading days in the data for the portfolio
    actual_trading_days_in_period = len(rts) # Number of returns periods
    if actual_trading_days_in_period > 0:
        ann = (1 + tot) ** (252 / actual_trading_days_in_period) - 1 if not pd.isna(tot) else np.nan
    else:
        ann = np.nan

    shp = sharpe_ratio(rts, rf_daily)
    mdd = max_drawdown(curv)

    print("\n" + "📊 PORTFOLIO RESULTS".center(60, "─"))
    print(f"🗓  {close.index.min().date()} → {close.index.max().date()} ({actual_trading_days_in_period} trading days)")
    print(f"💸  Start:    {usd(s_val)}")
    print(f"💰  End:      {usd(e_val)}")
    print(f"{'🔺' if not pd.isna(tot) and tot>=0 else '🔻'}  Return:    {pct(tot)}")
    print(f"📈  Annual:   {pct(ann)}")
    print(f"📏  Sharpe:   {shp:7.2f}" if not pd.isna(shp) else "Sharpe:     N/A")
    print(f"📉  MaxDD:    {pct(mdd)}")
    if excluded:
        print(f"\n⚠️  Tickers excluded due to missing price data at period start/end or other issues: {', '.join(excluded)}")
    print("─"*60, "\n")

if __name__ == '__main__':
    if close.empty and not live_tickers.any():
        print(f"Could not load price data for any tickers in the portfolio for the period {START} to {END}.")
        print("Please check your ticker symbols, portfolio definition, and network connection.")
    else:
        do_aggregate() 