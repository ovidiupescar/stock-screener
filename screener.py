import pandas as pd
import pandas_ta as ta
import yfinance as yf

def get_sp500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    table = pd.read_html(url)
    sp500_table = table[0]
    sp500 = sp500_table['Symbol'].tolist()
    return sp500

def get_qqq100():
    url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
    table = pd.read_html(url)
    qqq100_table = table[4]
    qqq100 = qqq100_table['Ticker'].tolist()
    return qqq100

def get_spqqq():
    qqq = set(get_qqq100())
    sp = set(get_sp500())

    return list(qqq.union(sp))

def get_y_prices(ticker, period='3mo', interval='1d', group_by='column', tag_price="Adj Close"):
    """
    tickers = "SPY AAPL MSFT"
    valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    valid intervals: 1m,2m,5m,15m,30m,60m,90m,1High,1d,5d,1wk,1mo,3mo
    group_by ticker/column)
    """
    data = yf.download(tickers=ticker, period=period, interval=interval, group_by=group_by)
    rows, cols = data.shape
    if rows <= 0:
        return pd.DataFrame()
    else:
        return data
    
def get_csv_prices(ticker):
    try:
        df = pd.read_csv(f"prices/{ticker}.csv")
        data = df[['Open', 'High', 'Low', 'Close']]

    except Exception:
        data = pd.DataFrame()

    return data

def get_all_tickers():
    tickers = get_spqqq()
    
    return tickers

def add_indicators(df):
    # Calculate Bollinger Bands and RSI using pandas_ta
    df.ta.bbands(append=True, length=30, std=2)
    df.ta.rsi(append=True, length=14)
    df["atr"] = ta.atr(low = df.Low, close = df.Close, high = df.High, length=14)

    # Rename columns for clarity if necessary
    df.rename(columns={
        'BBL_30_2.0': 'bbl', 'BBM_30_2.0': 'bbm', 'BBU_30_2.0': 'bbh', 'RSI_14': 'rsi'
    }, inplace=True)

    # Calculate Bollinger Bands Width
    df['bb_width'] = (df['bbh'] - df['bbl']) / df['bbm']

    return df

def apply_total_signal(df, rsi_threshold_low=30, rsi_threshold_high=70, bb_width_threshold = 0.003):
    # Initialize the 'TotalSignal' column
    df['TotalSignal'] = 0

    for i in range(1, len(df)):
        # Previous candle conditions
        prev_candle_closes_below_bb = df['Close'].iloc[i-1] < df['bbl'].iloc[i-1]
        prev_rsi_below_thr = df['rsi'].iloc[i-1] < rsi_threshold_low
        # Current candle conditions
        closes_above_prev_high = df['Close'].iloc[i] > df['High'].iloc[i-1]
        bb_width_greater_threshold = df['bb_width'].iloc[i] > bb_width_threshold

        # Combine conditions
        if (prev_candle_closes_below_bb and
            prev_rsi_below_thr and
            closes_above_prev_high and
            bb_width_greater_threshold):
            df.at[i, 'TotalSignal'] = 2  # Set the buy signal for the current candle

        # Previous candle conditions
        prev_candle_closes_above_bb = df['Close'].iloc[i-1] > df['bbh'].iloc[i-1]
        prev_rsi_above_thr = df['rsi'].iloc[i-1] > rsi_threshold_high
        # Current candle conditions
        closes_below_prev_low = df['Close'].iloc[i] < df['Low'].iloc[i-1]
        bb_width_greater_threshold = df['bb_width'].iloc[i] > bb_width_threshold

        # Combine conditions
        if (prev_candle_closes_above_bb and
            prev_rsi_above_thr and
            closes_below_prev_low and
            bb_width_greater_threshold):
            df.at[i, 'TotalSignal'] = 1  # Set the sell signal for the current candle

    return df

def parse_tickers():
    tickers = get_all_tickers()

    results = []

    for i, ticker in enumerate(tickers):
        ticker = ticker.replace('.', '-')
        print("====================")
        print(f"{ticker} --> {i+1} / {len(tickers)}")
        print("====================")
        df = get_csv_prices(ticker)

        if df.empty:
            continue

        df=df[df.High!=df.Low]
        df.reset_index(inplace=True, drop=True)

        df = add_indicators(df)
        df = apply_total_signal(df)

        df.to_csv(f"prices/{ticker}.csv")

        last_row = df.tail(1)

        print(last_row)

        signal = last_row['TotalSignal'].values[0]
        
        print(signal)

        if signal != 0:
            if signal == 1:
                order = 'sell'
            elif signal == 2:
                order = 'buy'

            results.append({
                'ticker': ticker,
                'order': order
            })

    df_r = pd.DataFrame(results)
    df_r.to_csv("results.csv")

parse_tickers()

        