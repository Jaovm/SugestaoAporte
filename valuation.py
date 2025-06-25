
import pandas as pd
from data_fetcher import get_financial_statements, get_company_profile

# --- Métodos de Valuation ---

def calculate_dcf(ticker, growth_rate=0.05, discount_rate=0.10, terminal_growth_rate=0.02, years=5):
    # Simplificação: DCF requer projeções detalhadas de fluxo de caixa livre
    # Para este exemplo, usaremos um placeholder baseado em receita ou lucro
    try:
        income_statement = get_financial_statements(ticker, 'income-statement', period='annual')
        if income_statement.empty:
            return None

        # Usar a receita como base para uma projeção simplificada de FCF
        # Em um modelo real, FCF seria calculado a partir de DRE e Balanço
        latest_revenue = income_statement.loc[0, 'revenue']

        projected_fcf = []
        for i in range(years):
            # Crescimento anual simplificado
            fcf_year = latest_revenue * ((1 + growth_rate) ** (i + 1))
            projected_fcf.append(fcf_year)

        # Valor Terminal (Perpetual Growth Model)
        terminal_value = (projected_fcf[-1] * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)

        # Valor Presente dos Fluxos de Caixa Projetados
        pv_projected_fcf = sum([fcf / ((1 + discount_rate) ** (i + 1)) for i, fcf in enumerate(projected_fcf)])

        # Valor Presente do Valor Terminal
        pv_terminal_value = terminal_value / ((1 + discount_rate) ** years)

        intrinsic_value = pv_projected_fcf + pv_terminal_value
        return intrinsic_value
    except Exception as e:
        print(f"Erro ao calcular DCF para {ticker}: {e}")
        return None

def calculate_multiples_valuation(ticker):
    try:
        income_statement = get_financial_statements(ticker, 'income-statement', period='annual')
        balance_sheet = get_financial_statements(ticker, 'balance-sheet-statement', period='annual')
        profile = get_company_profile(ticker)

        if income_statement.empty or balance_sheet.empty or not profile:
            return None

        # Dados mais recentes
        latest_income = income_statement.loc[0]
        latest_balance = balance_sheet.loc[0]

        # Preço da ação e número de ações
        price = profile.get('price')
        shares_outstanding = profile.get('sharesOutstanding')

        if not price or not shares_outstanding:
            return None

        # Cálculo de Múltiplos
        eps = latest_income.get('eps')
        book_value_per_share = latest_balance.get('bookValuePerShare')
        ebitda = latest_income.get('ebitda')

        valuation_metrics = {}

        # P/L (Price/Earnings)
        if eps and eps != 0:
            valuation_metrics['P/L'] = price / eps

        # P/VP (Price/Book Value)
        if book_value_per_share and book_value_per_share != 0:
            valuation_metrics['P/VP'] = price / book_value_per_share

        # EV/EBITDA (Enterprise Value / EBITDA)
        # EV = Market Cap + Total Debt - Cash & Equivalents
        market_cap = price * shares_outstanding
        total_debt = latest_balance.get('totalDebt', 0)
        cash_and_equivalents = latest_balance.get('cashAndShortTermInvestments', 0)
        enterprise_value = market_cap + total_debt - cash_and_equivalents

        if ebitda and ebitda != 0:
            valuation_metrics['EV/EBITDA'] = enterprise_value / ebitda

        return valuation_metrics
    except Exception as e:
        print(f"Erro ao calcular valuation por múltiplos para {ticker}: {e}")
        return None

def calculate_graham_valuation(ticker):
    try:
        income_statement = get_financial_statements(ticker, 'income-statement', period='annual')
        profile = get_company_profile(ticker)

        if income_statement.empty or not profile:
            return None

        latest_income = income_statement.loc[0]
        eps = latest_income.get('eps')
        book_value_per_share = profile.get('bookValuePerShare') # FMP tem no profile tb

        if not eps or not book_value_per_share or book_value_per_share <= 0:
            return None

        # Fórmula de Graham revisada (para empresas em crescimento)
        # V = EPS * (8.5 + 2G) * 4.4 / Y
        # Onde: V = Valor intrínseco, EPS = Lucro por Ação, 8.5 = P/L de uma empresa sem crescimento
        # G = Taxa de crescimento esperada (estimativa, pode ser média histórica de EPS)
        # 4.4 = Rendimento médio de títulos corporativos AAA em 1962
        # Y = Rendimento atual de títulos corporativos AAA (usaremos uma taxa de juros de referência, ex: 10 anos)

        # Para G, vamos usar uma estimativa simples, ou buscar um histórico de crescimento
        # Por simplicidade, vamos usar um valor fixo ou tentar estimar do histórico de EPS
        # Aqui, um placeholder para G
        growth_rate_g = 0.05 # 5% de crescimento anual (exemplo)

        # Para Y, usar uma taxa de juros de referência (ex: Selic ou títulos de longo prazo)
        # No Brasil, pode ser a taxa de juros de longo prazo ou Selic
        # Placeholder para Y
        current_aaa_bond_yield = 0.06 # 6% (exemplo)

        if current_aaa_bond_yield == 0:
            return None

        intrinsic_value = eps * (8.5 + 2 * growth_rate_g) * 4.4 / current_aaa_bond_yield
        return intrinsic_value
    except Exception as e:
        print(f"Erro ao calcular valuation de Graham para {ticker}: {e}")
        return None

def calculate_bazin_valuation(ticker):
    try:
        profile = get_company_profile(ticker)
        if not profile:
            return None

        # Preço Teto de Bazin = Dividendo por Ação / Yield Mínimo Desejado
        # Yield Mínimo Desejado geralmente é 6% (0.06)
        min_desired_yield = 0.06

        # Precisamos do dividendo por ação (DPS)
        # FMP tem 'lastDividend' no perfil, mas é o último dividendo, não anualizado
        # Idealmente, buscaríamos o histórico de dividendos para calcular a média ou o último ano fiscal
        # Placeholder: assumir um DPS anualizado para o exemplo
        # Em um cenário real, buscaríamos dados de dividendos mais robustos
        # Por exemplo, via Yahoo Finance ou outra API de dividendos
        # Para FMP, podemos tentar usar o 'dividendYield' e o 'price' para estimar o DPS
        dividend_yield = profile.get('dividendYield')
        price = profile.get('price')

        if not dividend_yield or not price or min_desired_yield == 0:
            return None

        # Estimar DPS anualizado
        estimated_dps = dividend_yield * price

        if estimated_dps <= 0:
            return None

        price_teto = estimated_dps / min_desired_yield
        return price_teto
    except Exception as e:
        print(f"Erro ao calcular valuation de Bazin para {ticker}: {e}")
        return None

def calculate_ddm_valuation(ticker, required_rate_of_return=0.10, growth_rate=0.03):
    # DDM (Dividend Discount Model) - Modelo de Gordon (crescimento constante)
    # Valor = Dividendo do Próximo Ano / (Taxa de Retorno Exigida - Taxa de Crescimento)
    try:
        profile = get_company_profile(ticker)
        if not profile:
            return None

        dividend_yield = profile.get('dividendYield')
        price = profile.get('price')

        if not dividend_yield or not price:
            return None

        current_dps = dividend_yield * price

        # Dividendo do próximo ano
        next_dps = current_dps * (1 + growth_rate)

        if (required_rate_of_return - growth_rate) <= 0:
            return None # Crescimento maior ou igual à taxa exigida, modelo não aplicável

        intrinsic_value = next_dps / (required_rate_of_return - growth_rate)
        return intrinsic_value
    except Exception as e:
        print(f"Erro ao calcular DDM para {ticker}: {e}")
        return None

def calculate_patrimonial_value(ticker):
    try:
        balance_sheet = get_financial_statements(ticker, 'balance-sheet-statement', period='annual')
        profile = get_company_profile(ticker)

        if balance_sheet.empty or not profile:
            return None

        latest_balance = balance_sheet.loc[0]
        shares_outstanding = profile.get('sharesOutstanding')

        if not shares_outstanding or shares_outstanding <= 0:
            return None

        # Valor Patrimonial por Ação = Patrimônio Líquido / Número de Ações
        # FMP tem 'totalEquity' ou 'commonStock' para patrimônio líquido
        total_equity = latest_balance.get('totalEquity')

        if not total_equity:
            return None

        patrimonial_value_per_share = total_equity / shares_outstanding
        return patrimonial_value_per_share
    except Exception as e:
        print(f"Erro ao calcular Valor Patrimonial para {ticker}: {e}")
        return None

def calculate_opportunity_score(current_price, intrinsic_value):
    if intrinsic_value is None or current_price is None or current_price <= 0:
        return 0
    
    # Score de Oportunidade: quanto maior o desconto, maior o score
    # (Valor Intrínseco - Preço Atual) / Preço Atual * 100
    # Um score positivo indica que o ativo está subvalorizado
    return ((intrinsic_value - current_price) / current_price) * 100

def get_buy_signal(current_price, intrinsic_value):
    if intrinsic_value is None or current_price is None:
        return "N/A"
    if intrinsic_value > current_price:
        return "COMPRA"
    elif intrinsic_value < current_price:
        return "VENDA"
    else:
        return "NEUTRO"

# Exemplo de uso (para testes)
if __name__ == '__main__':
    # Lembre-se de substituir 'SUA_CHAVE_FMP_AQUI' em data_fetcher.py
    ticker_test = 'ITUB3.SA'
    
    print(f"\n--- Valuation para {ticker_test} ---")

    # DCF
    dcf_value = calculate_dcf(ticker_test)
    print(f"DCF Valuation: {dcf_value:.2f}" if dcf_value else "DCF Valuation: N/A")

    # Múltiplos
    multiples = calculate_multiples_valuation(ticker_test)
    print(f"Multiples Valuation: {multiples}" if multiples else "Multiples Valuation: N/A")

    # Graham
    graham_value = calculate_graham_valuation(ticker_test)
    print(f"Graham Valuation: {graham_value:.2f}" if graham_value else "Graham Valuation: N/A")

    # Bazin
    bazin_value = calculate_bazin_valuation(ticker_test)
    print(f"Bazin Valuation (Preço Teto): {bazin_value:.2f}" if bazin_value else "Bazin Valuation: N/A")

    # DDM
    ddm_value = calculate_ddm_valuation(ticker_test)
    print(f"DDM Valuation: {ddm_value:.2f}" if ddm_value else "DDM Valuation: N/A")

    # Valor Patrimonial
    patrimonial_value = calculate_patrimonial_value(ticker_test)
    print(f"Valor Patrimonial por Ação: {patrimonial_value:.2f}" if patrimonial_value else "Valor Patrimonial: N/A")

    # Exemplo de Score de Oportunidade e Sinal de Compra (usando DCF como valor intrínseco)
    current_price_example = 25.00 # Preço atual fictício para ITUB3.SA
    if dcf_value:
        score = calculate_opportunity_score(current_price_example, dcf_value)
        signal = get_buy_signal(current_price_example, dcf_value)
        print(f"\nPreço Atual (Exemplo): {current_price_example:.2f}")
        print(f"Score de Oportunidade (vs DCF): {score:.2f}%")
        print(f"Sinal de Compra (vs DCF): {signal}")


