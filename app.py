import pandas as pd
import streamlit as st
import os
import sys

# Adicionar caminho para importar utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import DatabaseProdutos

st.set_page_config(
    page_title="Programa Alimentar Tilápia Tanque Rede",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state='auto'
)

st.title('Programa Alimentar Tilápia Tanque Rede')
st.markdown('-----------------------------------------------------')

@st.cache_resource
def carregar_database():
    """Carrega o database uma única vez e mantém em cache"""
    db = DatabaseProdutos('data/produtos_racao.json')
    return db

db = carregar_database()

# Validar cobertura ao carregar
validacao = db.validar_cobertura(57)
if not validacao['valido']:
    st.warning(f"⚠ Database incompleto! Semanas sem cobertura: {validacao['semanas_sem_cobertura']}")

with st.expander("Parâmetros de Cultivo 🐟", expanded=True):
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            especie = st.radio(
                "Espécie:",
                options=['Tilápia'],
                key="especie")
            
            tipo_cultivo = st.radio(
                "Tipo de Cultivo:",
                options=['Tanque-Rede'],
                key="tipo_cultivo")
                    
        with col2:
            densidade = st.text_input(
                "Densidade (peixes/m³):",
                key="densidade")

            sobrevivencia = st.number_input(
                "Sobrevivência Final (%):",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key="sobrevivencia")
                        
            tamanho_alevino = st.number_input(
                "Tamanho do Alevino (g):",
                min_value=0.1,
                step=0.1,
                key="tamanho_alevino")
            
            participacao_racao = st.number_input(
                "Participação da Ração (%):",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key="participacao_racao")
        
        with col3:
            qtd_peixes = st.text_input(
                "Quantidade de Peixes:",
                key="qtd_peixes")

            valor_milheiro_input = st.text_input(
                "Valor do Milheiro (R$/1000):",
                key="valor_milheiro")
            
            if valor_milheiro_input:
                try:
                    valor = float(valor_milheiro_input)
                    valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    st.write(f"**Valor formatado:** {valor_formatado}")
                except ValueError:
                    st.error("Por favor, insira um valor numérico válido")
            
            temperatura = st.number_input(
                "Temperatura (ºC):",
                step=0.1,
                key="temperatura")

st.divider()

def criar_dataframe_arracoamento(tamanho_alevino, num_semanas=57):
    """
    Cria o dataframe de arraçoamento usando dados do database.
    """
    cresc_inicial = 0.79
    
    # Listas para armazenar dados
    idade_semana = []
    pi_grama = []
    pf_grama = []
    cresc_g_dia = []
    produto = []
    proteina = []
    granulometria = []
    
    # Preencher as listas
    for i in range(1, num_semanas + 1):
        # Coluna: Idade/Semana
        idade_semana.append(i)
        
        # Coluna: CRESC G/DIA (começa em 0,79 e incrementa 0.01)
        cresc = cresc_inicial + (i - 1) * 0.01
        cresc_g_dia.append(round(cresc, 2))
        
        # Coluna: PI/grama
        if i == 1:
            pi = tamanho_alevino
        else:
            pi = pf_grama[i - 2]
        pi_grama.append(round(pi, 2))
        
        # Coluna: PF grama = PI/grama + (cresc g/dia * 7)
        pf = pi + (cresc * 7)
        pf_grama.append(round(pf, 2))
        
        # DADOS DO DATABASE
        prod = db.obter_produto(i)
        produto.append(prod)
        
        prot = db.obter_proteina(i)
        proteina.append(prot)
        
        gran = db.obter_granulometria(i)
        granulometria.append(gran)
    
    # Criar o dataframe
    df = pd.DataFrame({
        "Semana": idade_semana,
        "PI (g)": pi_grama,
        "PF (g)": pf_grama,
        "Cresc (g/dia)": cresc_g_dia,
        "Produto": produto,
        "Proteína (%)": proteina,
        "Granulometria": granulometria
    })
    
    return df

# Criar dataframe
df = criar_dataframe_arracoamento(tamanho_alevino, num_semanas=57)

st.subheader('📊 Tabela de Arraçoamento')

col_tabela, col_grafico = st.columns(2)

with col_tabela:
    st.write("**Dados de Crescimento**")
    st.dataframe(
        df,
        column_config={
            "Semana": st.column_config.NumberColumn(
                "Semana",
                format="%d",
                width="small"
            ),
            "PI (g)": st.column_config.NumberColumn(
                "PI (g)",
                help="Peso Inicial",
                format="%.2f",
                width="small"
            ),
            "PF (g)": st.column_config.NumberColumn(
                "PF (g)",
                help="Peso Final",
                format="%.2f",
                width="small"
            ),
            "Cresc (g/dia)": st.column_config.NumberColumn(
                "Cresc (g/dia)",
                help="Crescimento em gramas por dia",
                format="%.2f",
                width="small"
            ),
            "Produto": st.column_config.TextColumn(
                "Produto",
                help="Ração utilizada nesta semana",
                width="large"
            ),
            "Proteína (%)": st.column_config.NumberColumn(
                "Proteína (%)",
                help="Percentual de proteína",
                format="%d%%",
                width="small"
            ),
            "Granulometria": st.column_config.TextColumn(
                "Granulometria",
                help="Tamanho do grão",
                width="medium"
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

with col_grafico:
    st.write("**Gráfico de Crescimento Diário**")
    chart_data = pd.DataFrame({
        "Semana": df["Semana"],
        "Crescimento (g/dia)": df["Cresc (g/dia)"]
    })
    
    st.line_chart(
        chart_data.set_index("Semana"),
        use_container_width=True,
        height=400
    )

st.divider()