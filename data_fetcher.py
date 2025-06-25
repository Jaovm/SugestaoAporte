import requests
import pandas as pd
import yfinance as yf

FMP_API_KEY = '7a2Rn70FJUAnnDH0EV4YmHIsrGMCPo95'

def add_sa_suffix_if_needed(ticker):
    ticker = ticker.upper()
    if (
        not ticker.endswith(".SA") and
        any(ticker.endswith(suf) for suf in ["3", "4", "11"]) and
        len(ticker) in [5, 6]
    ):
        return ticker + ".SA"
    return ticker

def get_company_profile(ticker):
    try:
        # Ticker original para FMP
        url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]
    except Exception as e:
        print(f"[FMP] Erro ao buscar profile: {e}")

    # Fallback com yfinance (com .SA se necessário)
    try:
        yf_ticker = yf.Ticker(add_sa_suffix_if_needed(ticker))
        info = yf_ticker.info
        return {
            'companyName': info.get('shortName'),
            'price': info.get('currentPrice'),
            'dividendYield': info.get('dividendYield', 0),
            'sharesOutstanding': info.get('sharesOutstanding'),
            'bookValuePerShare': info.get('bookValue'),
        }
    except Exception as e:
        print(f"[Yahoo] Erro ao buscar profile: {e}")
        return None

def get_financial_statements(ticker, statement_type='income-statement', period='annual'):
    try:
        url = f"https://financialmodelingprep.com/api/v3/{statement_type}/{ticker}?period={period}&apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json():
            return pd.DataFrame(response.json())
    except Exception as e:
        print(f"[FMP] Erro ao buscar {statement_type}: {e}")
    return pd.DataFrame()

def get_historical_prices(ticker, period='1y'):
    try:
        yf_ticker = add_sa_suffix_if_needed(ticker)
        df = yf.download(yf_ticker, period=period, progress=False)
        return df
    except Exception as e:
        print(f"[Yahoo] Erro ao baixar preços históricos: {e}")
        return pd.DataFrame()
