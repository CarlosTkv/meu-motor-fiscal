import streamlit as st
import pandas as pd

# =====================================================================
# 1. DESIGN & ESTÉTICA (MINIMALISMO EXECUTIVO)
# =====================================================================
st.set_page_config(page_title="Fiscal Engine Pro", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #2d3748; }
    .main { background-color: #f7fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-weight: 600; color: #718096; }
    .stTabs [data-baseweb="tab--active"] { color: #2b6cb0; border-bottom-color: #2b6cb0; }
    .card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #edf2f7; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .cst-box { background: #f1f5f9; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; margin-top: 10px; }
    .calc-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f5f9; }
    .total-row { display: flex; justify-content: space-between; padding: 12px 0; font-weight: bold; font-size: 1.1em; color: #2b6cb0; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. INTELIGÊNCIA DE DADOS (BASE FISCAL)
# =====================================================================
def get_ncm_data(ncm):
    # Mock de base de dados - Expansível
    db = {
        "85171300": {"nome": "Smartphone", "mva_orig": 40.0, "aliq_ipi": 15.0},
        "84713012": {"nome": "Notebook", "mva_orig": 35.0, "aliq_ipi": 0.0},
        "22030000": {"nome": "Cerveja", "mva_orig": 140.0, "aliq_ipi": 6.0}
    }
    return db.get(ncm, {"nome": "Produto Geral", "mva_orig": 50.0, "aliq_ipi": 0.0})

def get_icms_rates(orig, dest):
    # Simplificação de alíquotas interestaduais
    if orig == dest: return 18.0, 18.0
    interestadual = 7.0 if orig in ["SP", "RJ", "MG", "PR", "RS", "SC"] and dest not in ["SP", "RJ", "MG", "PR", "RS", "SC"] else 12.0
    return interestadual, 18.0 # Inter, Intra (Média)

# =====================================================================
# 3. INTERFACE LATERAL
# =====================================================================
with st.sidebar:
    st.title("⚙️ Parâmetros")
    ncm_in = st.text_input("NCM do Produto", "85171300")
    tipo_op = st.selectbox("Operação", ["SAÍDA", "IMPORTAÇÃO", "EXPORTAÇÃO"])
    
    st.divider()
    uf_o = st.selectbox("UF Origem", ["SP", "RJ", "MG", "PR", "SC", "RS"])
    uf_d = st.selectbox("UF Destino", ["RJ", "SP", "MG", "PR", "SC", "RS"])
    
    reg_o = st.selectbox("Regime Remetente", ["LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL"])
    reg_d = st.selectbox("Regime Destinatário", ["LUCRO REAL", "SIMPLES NACIONAL", "NÃO CONTRIBUINTE (PF)", "NÃO CONTRIBUINTE (PJ)"])

    st.divider()
    st.subheader("💰 Valores da Nota")
    v_prod = st.number_input("Valor dos Produtos (R$)", value=1000.0)
    v_frete = st.number_input("Frete (R$)", value=0.0)
    v_seguro = st.number_input("Seguro (R$)", value=0.0)
    v_outros = st.number_input("Outras Desp. (R$)", value=0.0)

# =====================================================================
# 4. LÓGICA DE CÁLCULO & JUSTIFICATIVA
# =====================================================================
data_ncm = get_ncm_data(ncm_in)
aliq_inter, aliq_intra = get_icms_rates(uf_o, uf_d)
mva_original = data_ncm['mva_orig'] / 100

# Cálculo MVA Ajustada
mva_ajustada = ((1 + mva_original) * (1 - aliq_inter/100) / (1 - aliq_intra/100)) - 1
mva_final = mva_ajustada if uf_o != uf_d else mva_original

# Cálculo de Impostos
base_calculo_ipi = v_prod + v_frete + v_seguro + v_outros
valor_ipi = base_calculo_ipi * (data_ncm['aliq_ipi'] / 100)

base_icms_proprio = base_calculo_ipi + valor_ipi
icms_proprio = base_icms_proprio * (aliq_inter / 100)

base_st = base_icms_proprio * (1 + mva_final)
icms_st = (base_st * (aliq_intra / 100)) - icms_proprio

# DIFAL
valor_difal = base_icms_proprio * ((aliq_intra - aliq_inter) / 100)

# =====================================================================
# 5. ABAS DE RESULTADO
# =====================================================================
tab1, tab2 = st.tabs(["📄 Análise & CSTs", "🧮 Calculadora de ST / DIFAL"])

with tab1:
    st.markdown(f"### Análise de Operação: {data_ncm['nome']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Justificativa CST ICMS**")
        if "NÃO CONTRIBUINTE" in reg_d:
            cst_icms, motivo_icms = "00", "Operação tributada integralmente. Utiliza-se CST 00 pois o destinatário é Não Contribuinte, logo não há ST por antecipação do comprador, mas sim recolhimento de DIFAL pelo remetente."
        elif mva_final > 0:
            cst_icms, motivo_icms = "10", "Operação tributada com cobrança de ICMS por Substituição Tributária (ST). Justificado pela existência de Protocolo/Convênio entre as UFs para este NCM."
        else:
            cst_icms, motivo_icms = "00", "Operação tributada integralmente. Sem incidência de ST para este NCM na rota informada."
        
        st.markdown(f"""<div class="cst-box"><b>CST {cst_icms}</b><br><small>{motivo_icms}</small></div>""", unsafe_allow_html=True)

        st.markdown("**Justificativa CST PIS/COFINS**")
        if reg_o == "LUCRO REAL":
            cst_pc, motivo_pc = "01", "Operação tributada com alíquota básica (Regime Não-Cumulativo). Incidência de 1,65% e 7,6%."
        elif reg_o == "SIMPLES NACIONAL":
            cst_pc, motivo_pc = "49", "Outras operações. No Simples Nacional, os tributos são unificados no PGDAS, não gerando crédito ou débito individual de CST 01."
        else:
            cst_pc, motivo_pc = "01", "Operação tributada com alíquota básica (Regime Cumulativo). Incidência de 0,65% e 3,0%."
            
        st.markdown(f"""<div class="cst-box"><b>CST {cst_pc}</b><br><small>{motivo_pc}</small></div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("**Alíquotas Aplicadas**")
        st.write(f"🔹 **ICMS Interestadual:** {aliq_inter}%")
        st.write(f"🔹 **ICMS Interno (Destino):** {aliq_intra}%")
        st.write(f"🔹 **IPI (NCM):** {data_ncm['aliq_ipi']}%")
        
        st.info(f"**Responsabilidade DIFAL:** {'Remetente' if 'NÃO CONTRIBUINTE' in reg_d else 'Destinatário'}")
        st.info(f"**Responsabilidade ST:** {'Remetente (Substituto)' if uf_o != uf_d else 'Contribuinte Próprio'}")

with tab2:
    st.markdown("### Memória de Cálculo (Passo a Passo)")
    
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("1. Variáveis de ST")
        st.write(f"MVA Original: {mva_original*100:.2f}%")
        st.write(f"MVA Ajustada: {mva_ajustada*100:.2f}%")
        st.success(f"MVA Utilizada: {mva_final*100:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("2. Composição da Base")
        st.markdown(f'<div class="calc-row"><span>Valor Produtos</span><span>R$ {v_prod:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc-row"><span>(+) IPI</span><span>R$ {valor_ipi:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc-row"><span>(+) Frete/Outros</span><span>R$ {v_frete+v_outros:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="total-row"><span>(=) Base Cálculo ST</span><span>R$ {base_st:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("3. Impostos Apurados")
        st.markdown(f'<div class="calc-row"><span>ICMS Próprio ({aliq_inter}%)</span><span>R$ {icms_proprio:,.2f}</span></div>', unsafe_allow_html=True)
        
        if "NÃO CONTRIBUINTE" in reg_d:
            st.markdown(f'<div class="calc-row"><span>DIFAL (EC 87/15)</span><span>R$ {valor_difal:,.2f}</span></div>', unsafe_allow_html=True)
            st.warning("Nota: Operação para Não Contribuinte não incide ICMS-ST, apenas DIFAL.")
        else:
            st.markdown(f'<div class="calc-row"><span>ICMS ST Final</span><span>R$ {max(0, icms_st):,.2f}</span></div>', unsafe_allow_html=True)
            
        st.markdown(f'<div class="total-row"><span>Total Impostos Extra-Nota</span><span>R$ {valor_ipi + max(0, icms_st) + (valor_difal if "NÃO CONTRIBUINTE" in reg_d else 0):,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        <small style="color:gray;">* Cálculo baseado na fórmula: ST = [(Base * MVA) * Aliq Intra] - ICMS Próprio. 
        A MVA Ajustada é aplicada quando a Alíquota Interestadual é menor que a Alíquota Interna do Destino.</small>
    """, unsafe_allow_html=True)
