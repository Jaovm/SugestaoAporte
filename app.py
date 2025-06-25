import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# Importar módulos locais
from data_fetcher import get_company_profile, get_financial_statements
from valuation import (
    calculate_dcf, calculate_multiples_valuation, calculate_graham_valuation,
    calculate_bazin_valuation, calculate_ddm_valuation, calculate_patrimonial_value,
    calculate_opportunity_score, get_buy_signal
)
from portfolio_optimizer import (
    identify_asset_class, calculate_current_allocation, markowitz_optimization,
    hrp_optimization, risk_parity_optimization, macroeconomic_heuristic,
    suggest_rebalance, suggest_new_contribution_allocation
)

# Configuração da página
st.set_page_config(
    page_title="Otimizador de Carteira de Investimentos",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📈 Otimizador de Carteira de Investimentos")
st.markdown("### Análise fundamentalista e otimização quantitativa de portfólio")

# Sidebar para configurações
st.sidebar.header("⚙️ Configurações")

# Lista de ativos padrão
default_assets = {
    "Ações": ["ITUB3", "TOTS3", "MDIA3", "TAEE3", "BBSE3", "WEGE3", "PSSA3", "EGIE3", "PRIO3", "BBAS3", "BPAC11", "SBSP3", "SAPR4", "CMIG3", "AGRO3", "B3SA3", "VIVT3"],
    "FIIs": ["MXRF11", "XPIN11", "VISC11", "XPLG11", "HGLG11", "ALZR11", "BCRI11", "HGRU11", "VILG11", "VGHF11", "KNRI11", "HGRE11", "BRCO11", "HGCR11", "VGIA11", "MALL11", "BTLG11", "BTLG12", "XPML11", "LVBI11", "TRXF11"],
    "Exterior": ["IVV", "QQQM", "QUAL", "XLRE"],
    "Renda Fixa": ["LCA", "LFT", "LTN", "DEBENTURES"]
}

# Seção 1: Upload ou entrada manual da carteira
st.header("1. 📊 Carteira Atual")

upload_option = st.radio("Como deseja inserir sua carteira?", ["Upload CSV", "Entrada Manual"])

if upload_option == "Upload CSV":
    uploaded_file = st.file_uploader("Faça upload do arquivo CSV da sua carteira", type="csv")
    if uploaded_file is not None:
        portfolio_df = pd.read_csv(uploaded_file)
        st.success("Arquivo carregado com sucesso!")
        st.dataframe(portfolio_df)
    else:
        st.info("Por favor, faça upload de um arquivo CSV com as colunas: Ativo, Quantidade, PrecoUnitario")
        portfolio_df = None
else:
    st.subheader("Entrada Manual da Carteira")
    
    # Criar um formulário para entrada manual
    with st.form("portfolio_form"):
        num_assets = st.number_input("Número de ativos na carteira", min_value=1, max_value=50, value=5)
        
        portfolio_data = []
        for i in range(num_assets):
            col1, col2, col3 = st.columns(3)
            with col1:
                asset = st.text_input(f"Ativo {i+1}", key=f"asset_{i}")
            with col2:
                quantity = st.number_input(f"Quantidade {i+1}", min_value=0.0, key=f"quantity_{i}")
            with col3:
                price = st.number_input(f"Preço Unitário {i+1}", min_value=0.0, key=f"price_{i}")
            
            if asset and quantity > 0 and price > 0:
                portfolio_data.append({"Ativo": asset, "Quantidade": quantity, "PrecoUnitario": price})
        
        submitted = st.form_submit_button("Carregar Carteira")
        
        if submitted and portfolio_data:
            portfolio_df = pd.DataFrame(portfolio_data)
            st.success("Carteira carregada com sucesso!")
            st.dataframe(portfolio_df)
        else:
            portfolio_df = None

# Seção 2: Análise Fundamentalista
if portfolio_df is not None:
    st.header("2. 🔍 Análise Fundamentalista")
    
    # Adicionar classe de ativos
    portfolio_df['Classe'] = portfolio_df['Ativo'].apply(identify_asset_class)
    portfolio_df = calculate_current_allocation(portfolio_df)
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        selected_classes = st.multiselect("Filtrar por classe de ativo", 
                                        portfolio_df['Classe'].unique(), 
                                        default=portfolio_df['Classe'].unique())
    with col2:
        show_valuation = st.checkbox("Mostrar análise de valuation", value=True)
    
    # Filtrar dados
    filtered_portfolio = portfolio_df[portfolio_df['Classe'].isin(selected_classes)]
    
    # Mostrar carteira atual
    st.subheader("Carteira Atual")
    st.dataframe(filtered_portfolio)
    
    # Gráfico de alocação atual
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfico por ativo
    ax1.pie(filtered_portfolio['AlocacaoAtual'], labels=filtered_portfolio['Ativo'], autopct='%1.1f%%')
    ax1.set_title('Alocação por Ativo')
    
    # Gráfico por classe
    class_allocation = filtered_portfolio.groupby('Classe')['AlocacaoAtual'].sum()
    ax2.pie(class_allocation.values, labels=class_allocation.index, autopct='%1.1f%%')
    ax2.set_title('Alocação por Classe')
    
    st.pyplot(fig)
    
    # Análise de Valuation (se habilitada)
    if show_valuation:
        st.subheader("Análise de Valuation")
        
        # Nota sobre API
        st.warning("⚠️ Para obter dados reais de valuation, você precisa configurar uma chave da API FMP no arquivo data_fetcher.py")
        
        # Simulação de dados de valuation para demonstração
        valuation_data = []
        for _, row in filtered_portfolio.iterrows():
            asset = row['Ativo']
            current_price = row['PrecoUnitario']
            
            # Valores simulados para demonstração
            dcf_value = current_price * np.random.uniform(0.8, 1.3)
            graham_value = current_price * np.random.uniform(0.7, 1.4)
            bazin_value = current_price * np.random.uniform(0.6, 1.2)
            
            # Calcular score de oportunidade (usando DCF como referência)
            opportunity_score = calculate_opportunity_score(current_price, dcf_value)
            buy_signal = get_buy_signal(current_price, dcf_value)
            
            valuation_data.append({
                'Ativo': asset,
                'Preço Atual': current_price,
                'DCF': dcf_value,
                'Graham': graham_value,
                'Bazin': bazin_value,
                'Score Oportunidade (%)': opportunity_score,
                'Sinal': buy_signal
            })
        
        valuation_df = pd.DataFrame(valuation_data)
        st.dataframe(valuation_df.round(2))
        
        # Gráfico de scores de oportunidade
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(valuation_df['Ativo'], valuation_df['Score Oportunidade (%)'])
        
        # Colorir barras: verde para positivo, vermelho para negativo
        for i, bar in enumerate(bars):
            if valuation_df.iloc[i]['Score Oportunidade (%)'] > 0:
                bar.set_color('green')
            else:
                bar.set_color('red')
        
        ax.set_title('Score de Oportunidade por Ativo')
        ax.set_ylabel('Score (%)')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)

# Seção 3: Otimização de Carteira
if portfolio_df is not None:
    st.header("3. ⚖️ Otimização de Carteira")
    
    # Seleção do método de otimização
    optimization_method = st.selectbox(
        "Método de Otimização",
        ["Markowitz (Mínima Variância)", "HRP (Hierarchical Risk Parity)", "Risk Parity", "Heurística Macroeconômica"]
    )
    
    # Configurações específicas para heurística macroeconômica
    if optimization_method == "Heurística Macroeconômica":
        scenario = st.selectbox("Cenário Macroeconômico", ["expansionista", "neutro", "restritivo"])
        
        # Mostrar alocação ideal por classe
        ideal_allocation = macroeconomic_heuristic(portfolio_df['Ativo'].tolist(), scenario)
        
        st.subheader(f"Alocação Ideal - Cenário {scenario.title()}")
        allocation_df = pd.DataFrame(list(ideal_allocation.items()), columns=['Classe', 'Alocação Ideal'])
        st.dataframe(allocation_df)
        
        # Gráfico da alocação ideal
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(allocation_df['Alocação Ideal'], labels=allocation_df['Classe'], autopct='%1.1f%%')
        ax.set_title(f'Alocação Ideal - Cenário {scenario.title()}')
        st.pyplot(fig)
    
    else:
        st.info("Para métodos quantitativos (Markowitz, HRP, Risk Parity), são necessários dados históricos de retorno dos ativos.")
        
        # Simulação de otimização para demonstração
        if st.button("Simular Otimização"):
            # Criar dados fictícios de retorno para demonstração
            returns_data = {}
            for asset in portfolio_df['Ativo']:
                returns_data[asset] = np.random.normal(0.001, 0.02, 252)  # 252 dias úteis
            
            returns_df = pd.DataFrame(returns_data)
            
            if optimization_method == "Markowitz (Mínima Variância)":
                optimal_weights = markowitz_optimization(returns_df)
            elif optimization_method == "HRP (Hierarchical Risk Parity)":
                optimal_weights = hrp_optimization(returns_df)
            else:  # Risk Parity
                optimal_weights = risk_parity_optimization(returns_df)
            
            st.subheader("Pesos Ótimos")
            weights_df = pd.DataFrame({
                'Ativo': optimal_weights.index,
                'Peso Ótimo': optimal_weights.values
            })
            st.dataframe(weights_df)
            
            # Gráfico dos pesos ótimos
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(weights_df['Ativo'], weights_df['Peso Ótimo'])
            ax.set_title(f'Pesos Ótimos - {optimization_method}')
            ax.set_ylabel('Peso')
            plt.xticks(rotation=45)
            st.pyplot(fig)

# Seção 4: Sugestão de Rebalanceamento
if portfolio_df is not None:
    st.header("4. 🔄 Sugestão de Rebalanceamento")
    
    allow_sales = st.checkbox("Permitir vendas para rebalanceamento", value=True)
    
    if st.button("Gerar Sugestões de Rebalanceamento"):
        # Para demonstração, usar pesos iguais como ideal
        ideal_weights = pd.Series(1/len(portfolio_df), index=portfolio_df['Ativo'])
        
        rebalance_suggestions = suggest_rebalance(portfolio_df, ideal_weights, allow_sales)
        
        if not rebalance_suggestions.empty:
            st.subheader("Sugestões de Rebalanceamento")
            st.dataframe(rebalance_suggestions)
            
            # Resumo por ação
            total_to_buy = rebalance_suggestions[rebalance_suggestions['Acao'] == 'Comprar']['Valor'].sum()
            total_to_sell = rebalance_suggestions[rebalance_suggestions['Acao'] == 'Vender']['Valor'].sum()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total a Comprar", f"R$ {total_to_buy:,.2f}")
            with col2:
                st.metric("Total a Vender", f"R$ {total_to_sell:,.2f}")
        else:
            st.info("Nenhum rebalanceamento necessário com os parâmetros atuais.")

# Seção 5: Alocação de Novos Aportes
if portfolio_df is not None:
    st.header("5. 💸 Alocação de Novos Aportes")
    
    new_contribution = st.number_input("Valor do novo aporte (R$)", min_value=0.0, value=1000.0)
    
    if st.button("Sugerir Alocação do Aporte"):
        # Para demonstração, usar pesos iguais como ideal
        ideal_weights = pd.Series(1/len(portfolio_df), index=portfolio_df['Ativo'])
        
        # Simular scores de valuation (em um cenário real, viria da análise fundamentalista)
        valuation_scores = {asset: np.random.uniform(-20, 30) for asset in portfolio_df['Ativo']}
        
        allocation_suggestions = suggest_new_contribution_allocation(
            portfolio_df, ideal_weights, new_contribution, valuation_scores
        )
        
        if not allocation_suggestions.empty:
            st.subheader("Sugestão de Alocação do Aporte")
            st.dataframe(allocation_suggestions)
            
            # Gráfico da alocação sugerida
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(allocation_suggestions['Ativo'], allocation_suggestions['ValorAlocado'])
            ax.set_title('Alocação Sugerida do Novo Aporte')
            ax.set_ylabel('Valor (R$)')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            
            # Carteira após aporte
            st.subheader("Carteira Após Aporte")
            portfolio_after = portfolio_df.copy()
            
            for _, row in allocation_suggestions.iterrows():
                asset = row['Ativo']
                value_allocated = row['ValorAlocado']
                asset_price = portfolio_df[portfolio_df['Ativo'] == asset]['PrecoUnitario'].iloc[0]
                additional_quantity = value_allocated / asset_price
                
                portfolio_after.loc[portfolio_after['Ativo'] == asset, 'Quantidade'] += additional_quantity
            
            portfolio_after['ValorTotal'] = portfolio_after['Quantidade'] * portfolio_after['PrecoUnitario']
            portfolio_after = calculate_current_allocation(portfolio_after)
            
            st.dataframe(portfolio_after)
        else:
            st.info("Não foi possível gerar sugestões de alocação com os parâmetros atuais.")

# Seção 6: Resumo e Métricas
if portfolio_df is not None:
    st.header("6. 📋 Resumo da Carteira")
    
    total_value = portfolio_df['ValorTotal'].sum()
    num_assets = len(portfolio_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Valor Total da Carteira", f"R$ {total_value:,.2f}")
    
    with col2:
        st.metric("Número de Ativos", num_assets)
    
    with col3:
        most_allocated = portfolio_df.loc[portfolio_df['AlocacaoAtual'].idxmax(), 'Ativo']
        max_allocation = portfolio_df['AlocacaoAtual'].max()
        st.metric("Maior Alocação", f"{most_allocated} ({max_allocation:.1%})")
    
    with col4:
        num_classes = portfolio_df['Classe'].nunique()
        st.metric("Classes de Ativos", num_classes)

# Footer
st.markdown("---")
st.markdown("### 📚 Sobre o Sistema")
st.markdown("""
Este sistema oferece:
- **Análise Fundamentalista**: Valuation por DCF, múltiplos, Graham, Bazin, DDM e valor patrimonial
- **Otimização Quantitativa**: Markowitz, HRP, Risk Parity e heurística macroeconômica
- **Gestão de Aportes**: Sugestões inteligentes para novos investimentos
- **Rebalanceamento**: Estratégias para manter a carteira alinhada aos objetivos

⚠️ **Importante**: Este é um sistema de apoio à decisão. Sempre consulte um profissional qualificado antes de tomar decisões de investimento.
""")

# Configurações avançadas na sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Configurações Avançadas")

# Parâmetros de valuation
st.sidebar.markdown("**Parâmetros de Valuation**")
dcf_growth_rate = st.sidebar.slider("Taxa de Crescimento DCF (%)", 0.0, 20.0, 5.0) / 100
dcf_discount_rate = st.sidebar.slider("Taxa de Desconto DCF (%)", 5.0, 20.0, 10.0) / 100
bazin_min_yield = st.sidebar.slider("Yield Mínimo Bazin (%)", 3.0, 10.0, 6.0) / 100

# Parâmetros de otimização
st.sidebar.markdown("**Parâmetros de Otimização**")
risk_free_rate = st.sidebar.slider("Taxa Livre de Risco (%)", 0.0, 15.0, 5.0) / 100
max_weight_per_asset = st.sidebar.slider("Peso Máximo por Ativo (%)", 5.0, 50.0, 20.0) / 100

# Informações sobre APIs
st.sidebar.markdown("---")
st.sidebar.subheader("🔑 Configuração de APIs")
st.sidebar.markdown("""
Para obter dados reais:
1. **FMP API**: Cadastre-se em financialmodelingprep.com
2. **Yahoo Finance**: Use a biblioteca yfinance
3. Configure as chaves no arquivo `data_fetcher.py`
""")

