import pandas as pd
import numpy as np
from scipy.optimize import minimize

def identify_asset_class(ticker):
    ticker = ticker.upper()
    if any(char.isdigit() for char in ticker) and len(ticker) == 5 and ticker.endswith("F11"):
        return "FII"
    elif any(char.isdigit() for char in ticker) and len(ticker) == 5 and ticker.endswith("3"):
        return "Ações"
    elif any(char.isdigit() for char in ticker) and len(ticker) == 6 and ticker.endswith("11"):
        return "Ações (Units)"
    elif ticker in ["LCA", "LFT", "LTN", "DEBENTURES"]:
        return "Renda Fixa"
    elif ticker in ["IVV", "QQQM", "QUAL", "XLRE"]:
        return "Exterior"
    else:
        return "Outros"

def calculate_current_allocation(portfolio_df):
    # portfolio_df deve ter colunas: 'Ativo', 'Quantidade', 'PrecoUnitario'
    portfolio_df["ValorTotal"] = portfolio_df["Quantidade"] * portfolio_df["PrecoUnitario"]
    total_portfolio_value = portfolio_df["ValorTotal"].sum()
    
    if total_portfolio_value == 0:
        portfolio_df["AlocacaoAtual"] = 0
    else:
        portfolio_df["AlocacaoAtual"] = portfolio_df["ValorTotal"] / total_portfolio_value
    
    return portfolio_df

# --- Otimização de Carteira ---

def portfolio_volatility(weights, cov_matrix):
    return np.sqrt(weights.T @ cov_matrix @ weights)

def portfolio_return(weights, returns):
    return np.sum(weights * returns)

def markowitz_optimization(returns_df):
    # returns_df: DataFrame com retornos diários/mensais dos ativos
    num_assets = len(returns_df.columns)
    returns = returns_df.mean()
    cov_matrix = returns_df.cov()

    # Função objetivo para minimizar a volatilidade
    def minimize_volatility(weights):
        return portfolio_volatility(weights, cov_matrix)

    # Restrições: soma dos pesos = 1, pesos >= 0
    constraints = ({"type": "eq", "fun": lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    initial_weights = num_assets * [1. / num_assets,]

    # Otimização para carteira de mínima variância
    optimal_weights_min_vol = minimize(minimize_volatility, initial_weights, method="SLSQP", bounds=bounds, constraints=constraints)
    
    # Retorna os pesos ótimos
    return pd.Series(optimal_weights_min_vol.x, index=returns_df.columns)

# Placeholder para HRP e Risk Parity
def hrp_optimization(returns_df):
    # Implementação HRP (Hierarchical Risk Parity) aqui
    # Isso é complexo e requer clustering e cálculo de correlação
    print("HRP Optimization: Placeholder")
    return pd.Series(1/len(returns_df.columns), index=returns_df.columns) # Retorno pesos iguais por enquanto

def risk_parity_optimization(returns_df):
    # Implementação Risk Parity aqui
    # Isso envolve igualar a contribuição de risco de cada ativo
    print("Risk Parity Optimization: Placeholder")
    return pd.Series(1/len(returns_df.columns), index=returns_df.columns) # Retorno pesos iguais por enquanto

def macroeconomic_heuristic(portfolio_assets, scenario='neutro'):
    # portfolio_assets: lista de tickers ou DataFrame com ativos
    # scenario: 'expansionista', 'neutro', 'restritivo'
    
    # Esta é uma heurística simplificada. Em um modelo real, seria muito mais complexa.
    # Mapeamento de setores/classes para cenários
    sector_allocation = {
        'expansionista': {
            'Ações': 0.60,
            'FII': 0.20,
            'Exterior': 0.15,
            'Renda Fixa': 0.05
        },
        'neutro': {
            'Ações': 0.40,
            'FII': 0.25,
            'Exterior': 0.20,
            'Renda Fixa': 0.15
        },
        'restritivo': {
            'Ações': 0.20,
            'FII': 0.15,
            'Exterior': 0.25,
            'Renda Fixa': 0.40
        }
    }
    
    if scenario not in sector_allocation:
        scenario = 'neutro'
        
    # Retorna uma alocação ideal baseada no cenário macroeconômico
    # Isso precisaria ser refinado para alocar dentro de cada classe de ativo
    return sector_allocation[scenario]

# Sugestão de Rebalanceamento
def suggest_rebalance(current_portfolio_df, ideal_weights, allow_sales=True):
    # current_portfolio_df: DataFrame com 'Ativo', 'Quantidade', 'PrecoUnitario', 'ValorTotal', 'AlocacaoAtual'
    # ideal_weights: Series com pesos ideais para cada ativo
    
    rebalance_suggestions = []
    total_value = current_portfolio_df["ValorTotal"].sum()

    for index, row in current_portfolio_df.iterrows():
        asset = row["Ativo"]
        current_allocation = row["AlocacaoAtual"]
        ideal_allocation = ideal_weights.get(asset, 0) # Se o ativo não estiver nos pesos ideais, alocação ideal é 0

        diff_allocation = ideal_allocation - current_allocation
        
        if diff_allocation > 0.001: # Precisa comprar
            value_to_buy = diff_allocation * total_value
            rebalance_suggestions.append({"Ativo": asset, "Acao": "Comprar", "Valor": value_to_buy})
        elif diff_allocation < -0.001: # Precisa vender
            if allow_sales:
                value_to_sell = abs(diff_allocation) * total_value
                rebalance_suggestions.append({"Ativo": asset, "Acao": "Vender", "Valor": value_to_sell})
            else:
                # Se não permite vendas, o ativo ficará acima do peso ideal
                pass
                
    return pd.DataFrame(rebalance_suggestions)

# Exemplo de uso (para testes)
if __name__ == '__main__':
    # Exemplo de carteira atual
    portfolio_data = {
        'Ativo': ['ITUB3', 'MXRF11', 'IVV', 'LFT', 'WEGE3'],
        'Quantidade': [100, 200, 10, 1, 50],
        'PrecoUnitario': [25.00, 10.00, 400.00, 10000.00, 35.00]
    }
    portfolio_df = pd.DataFrame(portfolio_data)

    # 1. Identificação da classe de ativos
    portfolio_df['Classe'] = portfolio_df['Ativo'].apply(identify_asset_class)
    print("\n--- Carteira com Classes de Ativos ---")
    print(portfolio_df)

    # 2. Cálculo da alocação atual
    portfolio_df = calculate_current_allocation(portfolio_df)
    print("\n--- Alocação Atual da Carteira ---")
    print(portfolio_df)

    # 3. Otimização de Carteira (Markowitz - exemplo com dados fictícios de retorno)
    # Em um cenário real, você obteria retornos históricos dos ativos
    returns_data = {
        'ITUB3': np.random.rand(252) - 0.5,
        'MXRF11': np.random.rand(252) - 0.5,
        'IVV': np.random.rand(252) - 0.5,
        'LFT': np.random.rand(252) - 0.5,
        'WEGE3': np.random.rand(252) - 0.5
    }
    returns_df = pd.DataFrame(returns_data)
    
    print("\n--- Otimização Markowitz ---")
    optimal_weights_markowitz = markowitz_optimization(returns_df)
    print(optimal_weights_markowitz)

    print("\n--- Heurística Macroeconômica (Cenário Expansionista) ---")
    macro_ideal_allocation = macroeconomic_heuristic(portfolio_df['Ativo'].tolist(), scenario='expansionista')
    print(macro_ideal_allocation)

    # 4. Sugestão de Rebalanceamento (exemplo com Markowitz)
    # Criar um Series de pesos ideais para o exemplo de rebalanceamento
    # Para este exemplo, vamos usar os pesos do Markowitz, mas para as classes de ativos
    # Isso precisaria de um mapeamento mais complexo para ativos individuais
    # Por simplicidade, vamos criar um ideal_weights fictício para o rebalanceamento
    ideal_weights_example = pd.Series({
        'ITUB3': 0.30,
        'MXRF11': 0.20,
        'IVV': 0.25,
        'LFT': 0.15,
        'WEGE3': 0.10
    })
    
    rebalance_suggestions_df = suggest_rebalance(portfolio_df, ideal_weights_example, allow_sales=True)
    print("\n--- Sugestões de Rebalanceamento ---")
    print(rebalance_suggestions_df)




def suggest_new_contribution_allocation(current_portfolio_df, ideal_weights, new_contribution_value, valuation_scores=None):
    # current_portfolio_df: DataFrame com a carteira atual
    # ideal_weights: Series com os pesos ideais para cada ativo
    # new_contribution_value: Valor do novo aporte
    # valuation_scores: Dicionário com scores de valuation para cada ativo (opcional)

    # Calcular o valor total da carteira após o aporte
    total_portfolio_value_after_contribution = current_portfolio_df["ValorTotal"].sum() + new_contribution_value

    # Calcular o valor ideal de cada ativo na carteira final
    ideal_values_after_contribution = (ideal_weights * total_portfolio_value_after_contribution).fillna(0)

    # Calcular a diferença entre o valor ideal e o valor atual de cada ativo
    # Merge para garantir que todos os ativos (atuais e ideais) sejam considerados
    merged_portfolio = pd.merge(current_portfolio_df, ideal_values_after_contribution.rename("IdealValue"),
                                left_on="Ativo", right_index=True, how="outer").fillna(0)

    merged_portfolio["CurrentValue"] = merged_portfolio["Quantidade"] * merged_portfolio["PrecoUnitario"]
    merged_portfolio["ValueDifference"] = merged_portfolio["IdealValue"] - merged_portfolio["CurrentValue"]

    # Filtrar apenas ativos que precisam ser comprados (ValueDifference > 0)
    assets_to_buy = merged_portfolio[merged_portfolio["ValueDifference"] > 0].copy()

    # Se houver scores de valuation, priorizar ativos com maior score (mais descontados)
    if valuation_scores:
        assets_to_buy["ValuationScore"] = assets_to_buy["Ativo"].map(valuation_scores).fillna(0)
        assets_to_buy = assets_to_buy.sort_values(by="ValuationScore", ascending=False)

    # Alocar o novo aporte
    allocation_suggestions = []
    remaining_contribution = new_contribution_value

    for index, row in assets_to_buy.iterrows():
        asset = row["Ativo"]
        needed_value = row["ValueDifference"]

        if remaining_contribution > 0:
            # Alocar o mínimo entre o que é necessário e o que resta do aporte
            amount_to_allocate = min(remaining_contribution, needed_value)
            allocation_suggestions.append({"Ativo": asset, "ValorAlocado": amount_to_allocate})
            remaining_contribution -= amount_to_allocate
        else:
            break

    return pd.DataFrame(allocation_suggestions)


