import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =====================================================================
# 1. CONFIGURAÇÃO DE DESIGN (SISTEMA PREMIUM)
# =====================================================================
st.set_page_config(page_title="Fiscal Engine 360", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
    .main { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background: transparent; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-weight: 600; font-size: 16px; }
    .card { background: white; padding: 25px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 20px; }
    .section-title { color: #2563eb; font-weight: 600; font-size: 1.2rem; margin-bottom: 15px; border-left: 4px solid #2563eb; padding-left: 10px; }
    .justificativa { background: #f1f5f9; padding: 12px; border-radius: 8px; font-size: 13px; color: #475569; margin-top: 5px; line-height: 1.5; }
    .metric-value { font-size: 24px; font-weight: 700; color: #0f172a; }
    .calc-box { border-top: 1px solid #f1f5f9; padding: 10px 0; display: flex; justify-content: space-between; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. INTELIGÊNCIA TRIBUTÁRIA (DADOS E REGRAS)
# =====================================================================
def carregar_dados_ncm(ncm):
    base = {
        "85171300": {"desc": "Smartphone / Terminal Portátil", "mva": 40.0, "ipi": 15.0},
        "84713012": {"desc": "Notebook / Laptop", "mva": 35.0, "ipi": 0.0},
        "22030000": {"desc": "Cerveja de Malte", "mva": 140.0, "ipi": 6.0},
        "30049099": {"desc": "Medicamentos Diversos", "mva": 38.0, "ipi": 0.0}
    }
    return base.get(ncm, {"desc": "Produto Geral / NCM não catalogado", "mva": 50.0, "ipi": 0.0})

def obter_aliquotas_icms(uf_o, uf_d):
    if uf_o == uf_d: return 18.0, 18.0
    # Regra Sul/Sudeste p/ Norte/Nordeste/Centro/ES = 7%. Outros = 12%.
    regiao_sul_sudeste = ["SP", "RJ", "MG", "PR", "RS", "SC"]
    inter = 7.0 if uf_o in regiao_sul_sudeste and uf_d not in regiao_sul_sudeste else 12.0
    return inter, 18.0

# =====================================================================
# 3. INTERFACE LATERAL (INPUTS)
# =====================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=80)
    st.title("Configurador")
    
    op = st.selectbox("Operação", ["SAÍDA", "ENTRADA", "IMPORTAÇÃO", "EXPORTAÇÃO"])
    ncm_cod = st.text_input("NCM", "85171300")
    
    st.divider()
    c1, c2 = st.columns(2)
    uf_o = c1.selectbox("Origem", ["SP", "RJ", "MG", "PR", "SC", "RS", "ES", "GO", "MT", "MS", "BA"])
    uf_d = c2.selectbox("Destino", ["RJ", "SP", "MG", "PR", "SC", "RS", "ES", "GO", "MT", "MS", "BA"])
    
    reg_o = st.selectbox("Regime Origem", ["SIMPLES NACIONAL", "PRESUMIDO", "REAL"])
    reg_d = st.selectbox("Regime Destino", ["SIMPLES NACIONAL", "PRESUMIDO", "REAL", "PESSOA FÍSICA", "NÃO CONTRIBUINTE"])
    
    st.divider()
    st.subheader("Valores da Nota")
    v_produto = st.number_input("Valor do Produto (R$)", value=1000.0)
    v_acessorios = st.number_input("Frete + Outras Desp. (R$)", value=0.0)
    
    pesquisar = st.button("🚀 PESQUISAR MALHA FISCAL", use_container_width=True)

# =====================================================================
# 4. LÓGICA DE CÁLCULO E JUSTIFICATIVAS
# =====================================================================
if pesquisar:
    ncm_data = carregar_dados_ncm(ncm_cod)
    aliq_inter, aliq_intra = obter_aliquotas_icms(uf_o, uf_d)
    is_nao_cont = reg_d in ["PESSOA FÍSICA", "NÃO CONTRIBUINTE"]
    is_inter = uf_o != uf_d
    
    # --- CÁLCULOS ---
    base_ipi = v_produto + v_acessorios
    valor_ipi = base_ipi * (ncm_data['ipi'] / 100)
    base_icms_proprio = base_ipi + valor_ipi
    icms_proprio = base_icms_proprio * (aliq_inter / 100)
    
    # MVA Ajustada (Fórmula: [(1+MVA)* (1-Inter)/(1-Intra)]-1 )
    mva_orig = ncm_data['mva'] / 100
    mva_ajustada = ((1 + mva_orig) * (1 - aliq_inter/100) / (1 - aliq_intra/100)) - 1
    mva_final = mva_ajustada if is_inter else mva_orig
    
    base_st = base_icms_proprio * (1 + mva_final)
    valor_st = max(0, (base_st * (aliq_intra / 100)) - icms_proprio)
    
    valor_difal = base_icms_proprio * ((aliq_intra - aliq_inter) / 100)
    
    # --- ABAS DE RESULTADO ---
    st.markdown(f"# Análise: {ncm_data['desc']}")
    tab_analise, tab_calculo, tab_relatorio = st.tabs(["📋 ANÁLISE TÉCNICA", "🧮 MEMÓRIA DE CÁLCULO", "📊 DASHBOARD & RELATÓRIO"])

    with tab_analise:
        col_a, col_b = st.columns(2)
        
        with col_a:
            # ICMS
            st.markdown('<p class="section-title">Dados de ICMS & IPI</p>', unsafe_allow_html=True)
            cst_icms = "10" if valor_st > 0 else "00"
            cfop_pref = {"SAÍDA": "6" if is_inter else "5", "ENTRADA": "2" if is_inter else "1", "IMPORTAÇÃO": "3", "EXPORTAÇÃO": "7"}[op]
            cfop = f"{cfop_pref}403" if valor_st > 0 else f"{cfop_pref}102"
            
            st.write(f"**CST ICMS:** {cst_icms} | **CFOP:** {cfop}")
            st.write(f"**Alíquota ICMS:** {aliq_inter}% | **Alíquota IPI:** {ncm_data['ipi']}%")
            st.markdown(f'<div class="justificativa"><b>Motivo ICMS:</b> CST {cst_icms} aplicado devido à natureza da operação {op}. CFOP {cfop} selecionado pela rota {uf_o}→{uf_d} com presença de Substituição Tributária.</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="justificativa"><b>Motivo IPI:</b> Incidência de {ncm_data["ipi"]}% conforme TIPI para o NCM {ncm_cod}.</div>', unsafe_allow_html=True)

            # PIS/COFINS
            st.markdown('<p class="section-title">Dados de PIS / COFINS</p>', unsafe_allow_html=True)
            cst_pc = "01" if reg_o != "SIMPLES NACIONAL" else "49"
            aliq_p = 1.65 if reg_o == "REAL" else 0.65
            aliq_c = 7.6 if reg_o == "REAL" else 3.0
            st.write(f"**CST:** {cst_pc} | **Regra:** {'Não Cumulativo' if reg_o == 'REAL' else 'Cumulativo'}")
            st.write(f"**Alíquotas:** PIS {aliq_p}% / COFINS {aliq_c}%")
            st.markdown(f'<div class="justificativa">Justificado pelo regime {reg_o}. PIS/COFINS apurados sobre a base total da operação.</div>', unsafe_allow_html=True)

        with col_b:
            # DIFAL
            st.markdown('<p class="section-title">Diferencial de Alíquota (DIFAL)</p>', unsafe_allow_html=True)
            tem_difal = "Sim" if (is_inter and is_nao_cont) else "Não"
            st.write(f"**Aplicável:** {tem_difal}")
            st.markdown(f'<div class="justificativa"><b>Regra DIFAL:</b> Conforme EC 87/2015, por ser destino {reg_d}, a responsabilidade do recolhimento do diferencial de {aliq_intra - aliq_inter}% é do {"Remetente" if is_nao_cont else "Destinatário"}.</div>', unsafe_allow_html=True)

            # ST
            st.markdown('<p class="section-title">Substituição Tributária (ST)</p>', unsafe_allow_html=True)
            tem_st = "Sim" if valor_st > 0 else "Não"
            st.write(f"**Aplicável:** {tem_st}")
            st.markdown(f'<div class="justificativa"><b>Regra ST:</b> Aplicada MVA {"Ajustada" if is_inter else "Original"} de {mva_final*100:.2f}% devido ao Convênio/Protocolo entre {uf_o} e {uf_d} para produtos do segmento {ncm_data["desc"]}.</div>', unsafe_allow_html=True)

    with tab_calculo:
        st.markdown(f"### Detalhamento Matemático (Origem: {uf_o} | Destino: {uf_d})")
        cl1, cl2 = st.columns(2)
        
        with cl1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("#### 1. Formação da Base")
            st.markdown(f'<div class="calc-box"><span>Valor Mercadoria</span><span>R$ {v_produto:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="calc-box"><span>(+) IPI ({ncm_data["ipi"]}%)</span><span>R$ {valor_ipi:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="calc-box"><span>(=) Base Cálculo ICMS</span><span>R$ {base_icms_proprio:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="calc-box"><span>ICMS Próprio ({aliq_inter}%)</span><span>R$ {icms_proprio:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with cl2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if is_nao_cont:
                st.write("#### 2. Cálculo do DIFAL (Consumidor Final)")
                st.markdown(f'<div class="calc-box"><span>Alíquota Interna Destino</span><span>{aliq_intra}%</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="calc-box"><span>Alíquota Inter (Origem)</span><span>{aliq_inter}%</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="calc-box"><span>Diferença</span><span>{aliq_intra - aliq_inter}%</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="total-row" style="font-size:20px; font-weight:bold; color:blue;"><span>TOTAL DIFAL</span><span>R$ {valor_difal:,.2f}</span></div>', unsafe_allow_html=True)
            else:
                st.write("#### 2. Cálculo do ICMS-ST")
                st.markdown(f'<div class="calc-box"><span>MVA Utilizada</span><span>{mva_final*100:.2f}%</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="calc-box"><span>Base Cálculo ST</span><span>R$ {base_st:,.2f}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="calc-box"><span>Débito ST (Base * {aliq_intra}%)</span><span>R$ {base_st * (aliq_intra/100):,.2f}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="total-row" style="font-size:20px; font-weight:bold; color:green;"><span>TOTAL ICMS-ST</span><span>R$ {valor_st:,.2f}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_relatorio:
        # Gráfico Comparativo de Carga
        st.subheader("Visualização de Impacto Tributário")
        labels = ['ICMS Próprio', 'IPI', 'ICMS ST', 'DIFAL']
        values = [icms_proprio, valor_ipi, valor_st, valor_difal if is_nao_cont else 0]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=['#2563eb', '#64748b', '#22c55e', '#f59e0b'])])
        fig.update_layout(title_text="Composição de Tributos da Nota")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("### Resumo do Relatório")
        st.write(f"A operação de **{op}** de **{uf_o}** para **{uf_d}** resulta em uma carga tributária total de **R$ {sum(values):,.2f}**. ")
        st.write(f"O produto **{ncm_data['desc']}** possui MVA de **{mva_final*100:.2f}%** e o responsável pelo recolhimento do imposto acessório é o **REMETENTE**.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Utilize a barra lateral para configurar a operação e clique em 'Pesquisar'.")
