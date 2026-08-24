import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA (VISUAL PREMIUM)
st.set_page_config(
    page_title="Fiscal Pro | 2026",
    page_icon="⚖️",
    layout="wide"
)

# Estilo CSS para deixar o visual "Clean" e Moderno
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .resumo-card { 
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #007bff;
    }
    .reforma-card { 
        background-color: #e8f4fd; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #28a745;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR FISCAL (LÓGICA UNIFICADA)
def calcular_malha_fiscal(ncm, uf_orig, uf_dest, reg_orig, reg_dest, operacao):
    is_interestadual = uf_orig != uf_dest
    
    # Simulação de Regra de NCM (Ex: Eletrônicos tem ST)
    tem_st = True if ncm.startswith(("8517", "8471")) else False
    
    # Lógica de CFOP
    if operacao == "SAÍDA":
        pref = "6" if is_interestadual else "5"
        cfop = f"{pref}403" if tem_st else f"{pref}102"
    else: # ENTRADA
        pref = "2" if is_interestadual else "1"
        cfop = f"{pref}403" if tem_st else f"{pref}102"

    # Lógica PIS/COFINS (Regime Simples vs Normal)
    if reg_orig == "SIMPLES NACIONAL":
        cst_pc, aliq_p, aliq_c = "49", 0.0, 0.0
    else:
        cst_pc, aliq_p, aliq_c = "01", 1.65, 7.6

    return {
        "cfop": cfop,
        "st": "SIM" if tem_st else "NÃO",
        "cst_pc": cst_pc,
        "aliq_pis": f"{aliq_p}%",
        "aliq_cof": f"{aliq_c}%",
        "icms_origem": "18%" if not is_interestadual else "12%",
        "difal": "SIM" if is_interestadual and reg_dest == "SIMPLES NACIONAL" else "NÃO",
        "ibs_2026": "17.7%",
        "cbs_2026": "8.8%"
    }

# 3. INTERFACE DO USUÁRIO
st.title("⚖️ Sistema Fiscal Inteligente Unificado")
st.subheader("Simulador de Regras Tributárias & Transição 2026")

with st.sidebar:
    st.header("⚙️ Parâmetros")
    ncm_input = st.text_input("NCM do Produto (8 dígitos)", value="85171300")
    op_input = st.selectbox("Operação", ["SAÍDA", "ENTRADA"])
    
    col_u1, col_u2 = st.columns(2)
    origem = col_u1.selectbox("UF Origem", ["SP", "RJ", "MG", "PR", "RS", "SC", "GO"])
    destino = col_u2.selectbox("UF Destino", ["RJ", "SP", "MG", "PR", "RS", "SC", "GO"])
    
    reg_o = st.selectbox("Regime Origem", ["LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL"])
    reg_d = st.selectbox("Regime Destino", ["LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL"])
    
    btn = st.button("PROCESSAR REGRAS")

if btn:
    if len(ncm_input) != 8:
        st.error("ERRO: O NCM deve ter 8 dígitos.")
    else:
        res = calcular_malha_fiscal(ncm_input, origem, destino, reg_o, reg_d, op_input)
        
        # Dashboard Principal
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("CFOP SUGERIDO", res['cfop'])
        c2.metric("POSSUI ST?", res['st'])
        c3.metric("DIFAL", res['difal'])
        c4.metric("CST PIS/COFINS", res['cst_pc'])

        st.markdown("---")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.markdown(f"""
            <div class="resumo-card">
                <h3>📦 Detalhes da Operação Vigente</h3>
                <p><b>Alíquota ICMS:</b> {res['icms_origem']}</p>
                <p><b>PIS:</b> {res['aliq_pis']} | <b>COFINS:</b> {res['aliq_cof']}</p>
                <p><b>NCM:</b> {ncm_input}</p>
                <p><small>Regras baseadas no regulamento de {origem} para {destino}.</small></p>
            </div>
            """, unsafe_allow_html=True)

        with col_res2:
            st.markdown(f"""
            <div class="reforma-card">
                <h3>🌿 Reforma Tributária (Projeção 2026)</h3>
                <p><b>CBS (IVA Federal):</b> {res['cbs_2026']}</p>
                <p><b>IBS (IVA Estadual/Mun):</b> {res['ibs_2026']}</p>
                <p><b>Status:</b> Em transição conforme EC 132/2023.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.success("Análise Fiscal concluída com sucesso!")
else:
    st.info("Configure os dados na barra lateral e clique em 'Processar Regras' para iniciar a malha.")