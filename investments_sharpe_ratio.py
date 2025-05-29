# ==============================================================
#  📈  PORTFOLIO ANALYZER  –  v3.0 (annual dividends)  📊
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
            # print(f"Warning: No 'Close' data found for ticker {t} in the downloaded data structure.")
            pass # Will be handled by later filtering

    if not price_series_list:
        return pd.DataFrame() # Return empty DataFrame if no valid price data

    return pd.concat(price_series_list, axis=1)


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


# ======================= MODE 1 ===============================
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


# ======================= MODE 2 ===============================
def do_per_ticker():
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

    for t in live_tickers:
        ser = close[t].dropna()
        if ser.size < 2:
            continue
        
        rts   = ser.pct_change().dropna()
        if rts.empty:
            curv = pd.Series([1] * len(ser), index=ser.index)
            s, e = ser.iloc[0], ser.iloc[-1]
            tot = e / s - 1 if s != 0 else np.nan
            ann = np.nan
            shp = np.nan
            mdd = 0.0 if s > 0 else np.nan
        else:
            curv  = (1 + rts).cumprod()
            s, e  = ser.iloc[0], ser.iloc[-1]
            tot   = e / s - 1 if s != 0 else np.nan
            
            actual_ticker_trading_days = len(rts)
            if actual_ticker_trading_days > 0:
                 ann = (1 + tot) ** (252 / actual_ticker_trading_days) - 1 if not pd.isna(tot) else np.nan
            else:
                ann = np.nan
            shp = sharpe_ratio(rts, rf_daily)
            mdd = max_drawdown(curv)

        ticker_dividend_history = all_dividend_histories.get(t, pd.Series(dtype='float64', index=pd.to_datetime([])))
        
        annual_div_data = get_annual_dividends_and_yields(
            t, 
            ser,
            ticker_dividend_history, 
            START,
            END
        )
        
        # Create base row with common metrics
        row_data = {
            "Ticker": t,
            "Start $": s,
            "End $": e,
            "TotRet": tot,
            "AnnRet": ann,
            "Sharpe": shp,
            "MaxDD": mdd
        }
        
        # Calculate yield metrics
        max_yield = 0.0
        avg_yield = 0.0
        current_yield = 0.0
        valid_yields = []
        
        if annual_div_data:
            for year, data in annual_div_data.items():
                yield_pct = data['yield_pct']
                if yield_pct > 0:  # Only include non-zero yields in calculations
                    valid_yields.append(yield_pct)
                    max_yield = max(max_yield, yield_pct)
            
            if valid_yields:
                avg_yield = sum(valid_yields) / len(valid_yields)
                
            # Get current yield (last year in range)
            last_year = max(annual_div_data.keys())
            current_yield = annual_div_data[last_year]['yield_pct']
        
        row_data["Max Yield"] = max_yield
        row_data["Avg Yield"] = avg_yield
        row_data["Current Yield"] = current_yield
        rows.append(row_data)

    if not rows:
        print("No data to display for per-ticker metrics.")
        if excluded:
            print(f"\n⚠️  Tickers excluded due to missing price data at period start/end or other issues: {', '.join(excluded)}")
        return

    df = pd.DataFrame(rows)
    if "Sharpe" in df.columns:
        df = df.sort_values("Sharpe", ascending=False, na_position='last')

    # Define column order
    base_columns = ["Ticker", "Start $", "End $", "TotRet", "AnnRet", "Sharpe", "MaxDD", "Max Yield", "Avg Yield", "Current Yield"]
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
        "Max Yield": 9,
        "Avg Yield": 9,
        "Current Yield": 12
    }

    # Create header
    header_parts = ["#"] + all_columns
    header_str = " | ".join([h.center(col_widths.get(h, len(h))) for h in header_parts])
    separator_str = "-+-".join(["-" * col_widths.get(h, len(h)) for h in header_parts])
    
    total_table_width = len(header_str)

    print("\n" + "📑 PER-TICKER METRICS (Sharpe ↓)".center(total_table_width, "─"))
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
            elif col in ["TotRet", "AnnRet", "MaxDD"]:
                if isinstance(r[col], (int, float)):
                    row_parts.append(f"{pct(r[col]).strip():>{col_widths[col]-1}}")
                else:
                    row_parts.append(f"{r[col]:>{col_widths[col]-1}}")
            elif col == "Sharpe":
                if isinstance(r[col], (int, float)):
                    row_parts.append(f"{r[col]:>{col_widths[col]-1}.1f}")
                else:
                    row_parts.append(f"{r[col]:>{col_widths[col]-1}}")
            elif col in ["Max Yield", "Avg Yield", "Current Yield"]:
                if isinstance(r[col], (int, float)):
                    color = get_yield_color(r[col])
                    row_parts.append(f"{color}{r[col]:>{col_widths[col]-1}.1f}%{RESET}")
                else:
                    row_parts.append(f"{r[col]:>{col_widths[col]-1}}")
        
        print(" | ".join(row_parts))
        
    if excluded:
        print("\n⚠️  Tickers excluded due to missing price data at period start/end or other issues: " + ", ".join(excluded))
    print("─"*total_table_width + "\n")


# ======================== MENU ================================
if __name__ == '__main__':
    if close.empty and not live_tickers.any():
        print(f"Could not load price data for any tickers in the portfolio for the period {START} to {END}.")
        print("Please check your ticker symbols, portfolio definition, and network connection.")
    else:
        choice = input("Select mode: 1 – portfolio (aggregate), 2 – by tickers ▶ ")
        if choice.strip() == "2":
            do_per_ticker()
        else:
            do_aggregate()
