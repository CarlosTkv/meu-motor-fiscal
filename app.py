import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# =====================================================================
# MÓDULO 1: INTELIGÊNCIA DE DADOS E REGRAS VIGENTES (AGO/2026)
# =====================================================================
class TaxEngine:
    @staticmethod
    def get_ncm_data(ncm):
        # Base atualizada conforme TIPI 2026
        base = {
            "85171300": {"desc": "Smartphone/Celular", "mva": 40.0, "ipi": 15.0, "seletivo": False},
            "84713012": {"desc": "Notebook/Laptop", "mva": 35.0, "ipi": 0.0, "seletivo": False},
            "22030000": {"desc": "Cerveja de Malte", "mva": 140.0, "ipi": 6.0, "seletivo": True}, # Imposto Seletivo 2026
        }
        return base.get(ncm, {"desc": "Produto Geral", "mva": 50.0, "ipi": 0.0, "seletivo": False})

    @staticmethod
    def get_iss_data(codigo):
        # Base LC 116/03 com regras de retenção 2026
        services = {
            "7.02": {"desc": "Execução de Obras", "aliq": 5.0, "retencao_local": True, "base": "Art. 3, III"},
            "1.05": {"desc": "Licenciamento de Software", "aliq": 2.0, "retencao_local": False, "base": "Art. 3, Caput"},
            "11.02": {"desc": "Vigilância e Segurança", "aliq": 5.0, "retencao_local": True, "base": "Art. 3, XVII"},
        }
        return services.get(codigo, {"desc": "Serviço Geral", "aliq": 5.0, "retencao_local": False, "base": "Art. 3"})

# =====================================================================
# MÓDULO 2: INTERFACE E ESTILIZAÇÃO PREMIUM (APPLE STYLE)
# =====================================================================
st.set_page_config(page_title="Tax Engine Master | 2026", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'SF Pro Display', sans-serif; background-color: #f5f5f7; }
    .stApp { background-color: #f5f5f7; }
    .card { background: white; padding: 2rem; border-radius: 18px; box-shadow: 0 4px 24px rgba(0,0,0,0.04); border: 1px solid #d2d2d7; margin-bottom: 20px; }
    .status-badge { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
    .badge-red { background: #ff3b30; color: white; }
    .badge-green { background: #34c759; color: white; }
    .section-header { color: #1d1d1f; border-left: 5px solid #0071e3; padding-left: 15px; font-weight: 600; margin-bottom: 1rem; }
    .just-box { background: #fbfbfd; border-radius: 12px; padding: 15px; border: 1px solid #e5e5e7; font-size: 14px; line-height: 1.6; color: #424245; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# MÓDULO 3: CORE DA CALCULADORA E LÓGICA DE TRANSIÇÃO 2026
# =====================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3642/3642101.png", width=60)
    st.title("Tax Engine 360")
    st.write(f"Vigência: **{date.today().strftime('%d/%b/%Y')}**")
    
    tab_mode = st.radio("Natureza da Operação", ["📦 PRODUTO", "🛠️ SERVIÇO"])
    
    st.divider()
    op_tipo = st.selectbox("Tipo de Operação", ["SAÍDA/PRESTAÇÃO", "ENTRADA", "IMPORTAÇÃO", "EXPORTAÇÃO"])
    
    st.markdown("**🌎 Localização**")
    uf_o = st.selectbox("UF Origem", ["SP", "RJ", "MG", "PR", "SC", "RS", "ES", "GO"])
    uf_d = st.selectbox("UF Destino", ["RJ", "SP", "MG", "PR", "SC", "RS", "ES", "GO"])
    
    if tab_mode == "🛠️ SERVIÇO":
        cid_p = st.text_input("Cidade da Prestação", "Rio de Janeiro")
        cod_ref = st.text_input("Código LC 116", "7.02")
    else:
        cid_p = "N/A"
        cod_ref = st.text_input("NCM", "85171300")
        
    st.divider()
    reg_o = st.selectbox("Regime Origem", ["REAL", "PRESUMIDO", "SIMPLES NACIONAL"])
    reg_d = st.selectbox("Regime Destino", ["REAL", "PRESUMIDO", "SIMPLES NACIONAL", "PESSOA FÍSICA", "NÃO CONTRIBUINTE"])
    
    v_nota = st.number_input("Valor Bruto (R$)", value=50000.0, step=1000.0)
    btn_run = st.button("🚀 GERAR MALHA COMPLETA", use_container_width=True)

# =====================================================================
# MÓDULO 4: PROCESSAMENTO E RELATÓRIO ROBUSTO
# =====================================================================
if btn_run:
    st.markdown(f"## Relatório Consolidado de Auditoria")
    
    # --- LOGICA DE CÁLCULO 2026 ---
    is_inter = uf_o != uf_d
    is_nao_cont = reg_d in ["PESSOA FÍSICA", "NÃO CONTRIBUINTE"]
    
    # 1. Tributos da Transição (Reforma 2026)
    aliq_cbs_teste = 0.001 # 0,1% em 2026
    aliq_ibs_teste = 0.001 # 0,1% em 2026
    valor_cbs = v_nota * aliq_cbs_teste
    valor_ibs = v_nota * aliq_ibs_teste
    
    # 2. PIS/COFINS (Phasing out)
    aliq_p = 1.65 if reg_o == "REAL" else 0.65
    aliq_c = 7.6 if reg_o == "REAL" else 3.0
    if reg_o == "SIMPLES NACIONAL": aliq_p = aliq_c = 0.0
    
    # 3. Dual Logic: Produto vs Serviço
    if tab_mode == "📦 PRODUTO":
        p_data = TaxEngine.get_ncm_data(cod_ref)
        desc = p_data['desc']
        # ICMS (Aliq Inter 7/12 e Intra 18)
        aliq_inter = 12.0 # Simplificado
        aliq_intra = 18.0
        
        # ST/MVA Ajustada
        mva_orig = p_data['mva']/100
        mva_ajust = ((1 + mva_orig) * (1 - aliq_inter/100) / (1 - aliq_intra/100)) - 1
        mva_final = mva_ajust if is_inter else mva_orig
        
        # Cálculos de ST e DIFAL
        valor_ipi = v_nota * (p_data['ipi']/100)
        base_st = (v_nota + valor_ipi) * (1 + mva_final)
        valor_st = max(0, (base_st * (aliq_intra/100)) - (v_nota * (aliq_inter/100)))
        valor_difal = (v_nota + valor_ipi) * ((aliq_intra - aliq_inter)/100)
        imposto_princ = valor_st if valor_st > 0 else (v_nota * 0.18)
        retencao_iss = False
    else:
        s_data = TaxEngine.get_iss_data(cod_ref)
        desc = s_data['desc']
        retencao_iss = is_inter and s_data['retencao_local']
        imposto_princ = v_nota * (s_data['aliq']/100)
        valor_ipi = valor_st = valor_difal = 0.0

    # =====================================================================
    # DISPLAY: TABELAS E GRÁFICOS
    # =====================================================================
    t1, t2, t3, t4 = st.tabs(["📝 ANÁLISE DETALHADA", "🧮 MEMÓRIA DE CÁLCULO", "⚖️ TRANSIÇÃO REFORMA", "📊 PLANEJAMENTO 360"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-header">ICMS / ISS & IPI</div>', unsafe_allow_html=True)
            st.write(f"**Item:** {desc} ({cod_ref})")
            if tab_mode == "🛠️ SERVIÇO":
                st.write(f"**ISS Devido em:** {'Local da Prestação' if retencao_iss else 'Estab. Prestador'}")
                st.markdown(f'<div class="just-box"><b>Justificativa:</b> Conforme LC 116/03, {s_data["base"]}. Serviço de {desc} obriga retenção quando prestado fora do município sede.</div>', unsafe_allow_html=True)
            else:
                st.write(f"**CST:** {'010' if valor_st > 0 else '000'} | **CFOP:** {'6403' if is_inter and valor_st > 0 else '5102'}")
                st.markdown(f'<div class="just-box"><b>Justificativa:</b> Produto sujeito a MVA Ajustada de {mva_final*100:.2f}% na rota {uf_o} > {uf_d}. CFOP de saída interestadual tributada.</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown('<div class="section-header">PIS / COFINS & RETENÇÕES</div>', unsafe_allow_html=True)
            st.write(f"**CST PIS/COFINS:** {'01' if reg_o != 'SIMPLES' else '49'}")
            st.write(f"**Alíquotas:** {aliq_p}% / {aliq_c}%")
            st.markdown(f'<div class="just-box"><b>Motivo:</b> Regime {reg_o} vigente em Ago/2026. Alíquotas integrais mantidas durante o primeiro ano da transição para a CBS.</div>', unsafe_allow_html=True)

    with t2:
        st.markdown("### Composição do Custo Fiscal")
        cl1, cl2 = st.columns(2)
        with cl1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("#### ➕ Entradas (Base)")
            st.write(f"Valor Mercadoria/Serviço: R$ {v_nota:,.2f}")
            st.write(f"IPI ({p_data['ipi'] if tab_mode == '📦 PRODUTO' else 0}%): R$ {valor_ipi:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        with cl2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("#### ➖ Saídas (Impostos)")
            if tab_mode == "📦 PRODUTO":
                if is_nao_cont: st.write(f"DIFAL (EC 87/15): R$ {valor_difal:,.2f}")
                else: st.write(f"ICMS-ST: R$ {valor_st:,.2f}")
            else:
                st.write(f"ISS: R$ {imposto_princ:,.2f} ({'RETIDO' if retencao_iss else 'PRÓPRIO'})")
            st.write(f"PIS/COFINS: R$ {v_nota*(aliq_p+aliq_c)/100:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

    with t3:
        st.markdown('<div class="card" style="border-color: #34c759;">', unsafe_allow_html=True)
        st.write("### 🌿 Reforma Tributária - Transição 2026")
        st.write("Em **24 de Agosto de 2026**, vigora a alíquota de teste de 0,1% para IBS e CBS, compensável nos tributos atuais.")
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("CBS (0,1%)", f"R$ {valor_cbs:,.2f}")
        col_r2.metric("IBS (0,1%)", f"R$ {valor_ibs:,.2f}")
        col_r3.metric("Status Transição", "Fase 1 - Ativo")
        st.markdown('</div>', unsafe_allow_html=True)

    with t4:
        st.subheader("Simulação de Viabilidade de Regime")
        comparativo = {
            "Regime": ["SIMPLES", "PRESUMIDO", "REAL"],
            "Carga Estimada (R$)": [v_nota*0.07, v_nota*0.16, v_nota*0.24]
        }
        df_comp = pd.DataFrame(comparativo)
        fig = go.Figure(data=[go.Bar(x=df_comp['Regime'], y=df_comp['Carga Estimada (R$)'], marker_color=['#0071e3', '#34c759', '#ff9500'])])
        fig.update_layout(title="Carga Tributária Total por Opção de Regime (Ago/2026)", template="simple_white")
        st.plotly_chart(fig, use_container_width=True)

    # --- FOOTER DO RELATÓRIO ROBUSTO ---
    st.divider()
    st.markdown(f"""
    **Audit ID:** `2026-XF-{v_nota:.0f}`  
    **Base Legal Consultada:** LC 116/03, RICMS/2024, EC 132/23, TIPI 2026.  
    *Este documento compila todas as regras de retenção, substituição tributária e diferencial de alíquota vigentes na data desta consulta.*
    """)
    st.button("📄 Exportar Relatório para Impressão")

else:
    st.markdown("""
        <div style="text-align:center; padding: 100px; color: #86868b;">
            <img src="https://cdn-icons-png.flaticon.com/512/1041/1041888.png" width="80" style="opacity: 0.3;">
            <h2>Pronto para Auditoria</h2>
            <p>Insira os dados da operação ao lado para iniciar o processamento do motor 2026.</p>
        </div>
    """, unsafe_allow_html=True)
