import requests
import pandas as pd

# Chave da API FMP (substitua pela sua chave real)
FMP_API_KEY = 7a2Rn70FJUAnnDH0EV4YmHIsrGMCPo95 # TODO: Substituir pela chave real

def get_company_profile(ticker):
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[0] if response.json() else None
    return None

def get_financial_statements(ticker, statement_type='income-statement', period='annual'):
    url = f"https://financialmodelingprep.com/api/v3/{statement_type}/{ticker}?period={period}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json()) if response.json() else pd.DataFrame()
    return pd.DataFrame()

def get_historical_prices(ticker, period='1y'):
    # Para Yahoo Finance, usaremos uma abordagem mais simples ou uma biblioteca como yfinance
    # Por enquanto, um placeholder
    print(f"Obtendo preços históricos para {ticker} (placeholder)")
    return pd.DataFrame()

# Exemplo de uso (para testes)
if __name__ == '__main__':
    # Exemplo de uso
    ticker = 'ITUB3.SA' # Exemplo de ticker para FMP (ações brasileiras podem precisar de .SA)
    profile = get_company_profile(ticker)
    if profile:
        print(f"Profile for {ticker}: {profile['companyName']}")

    income_statement = get_financial_statements(ticker, 'income-statement')
    if not income_statement.empty:
        print(f"Income Statement for {ticker}:\n{income_statement.head()}")

    balance_sheet = get_financial_statements(ticker, 'balance-sheet')
    if not balance_sheet.empty:
        print(f"Balance Sheet for {ticker}:\n{balance_sheet.head()}")

    cash_flow = get_financial_statements(ticker, 'cash-flow-statement')
    if not cash_flow.empty:
        print(f"Cash Flow Statement for {ticker}:\n{cash_flow.head()}")


