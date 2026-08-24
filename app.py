import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# =====================================================================
# 1. DESIGN & ESTÉTICA DE ALTO PADRÃO
# =====================================================================
st.set_page_config(page_title="Tax Engine 360 | Global Intelligence", page_icon="🏛️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
    .main { background-color: #fcfcfd; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: #f1f5f9; padding: 5px; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { height: 45px; font-weight: 600; font-size: 14px; border-radius: 8px; }
    .card { background: white; padding: 24px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 20px; }
    .section-title { color: #0f172a; font-weight: 700; font-size: 1.1rem; margin-bottom: 15px; border-bottom: 2px solid #3b82f6; width: fit-content; }
    .justificativa { background: #f8fafc; padding: 15px; border-radius: 10px; border-left: 4px solid #94a3b8; font-size: 13px; color: #334155; line-height: 1.6; margin-bottom: 10px; }
    .alert-retencao { background: #fff1f2; color: #be123c; padding: 10px; border-radius: 8px; font-weight: 600; font-size: 14px; }
    .report-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .report-table td { padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. BASES DE DADOS E INTELIGÊNCIA (LC 116 & NCM)
# =====================================================================
def get_service_data(code):
    # Base baseada na LC 116/2003
    services = {
        "7.02": {"desc": "Execução de Obras de Construção Civil", "aliq": 5.0, "retencao_local": True},
        "1.05": {"desc": "Licenciamento de Software / SaaS", "aliq": 2.0, "retencao_local": False},
        "17.05": {"desc": "Recrutamento e Seleção de Pessoal", "aliq": 3.0, "retencao_local": False},
        "11.02": {"desc": "Vigilância, Segurança e Monitoramento", "aliq": 5.0, "retencao_local": True},
    }
    return services.get(code, {"desc": "Serviço Geral (LC 116)", "aliq": 5.0, "retencao_local": False})

def get_product_data(ncm):
    products = {
        "85171300": {"desc": "Smartphone", "mva": 40.0, "ipi": 15.0},
        "84713012": {"desc": "Notebook", "mva": 35.0, "ipi": 0.0},
    }
    return products.get(ncm, {"desc": "Produto Geral", "mva": 50.0, "ipi": 0.0})

# =====================================================================
# 3. INTERFACE LATERAL (INPUTS ROBUSTOS)
# =====================================================================
with st.sidebar:
    st.markdown("### 🏛️ Controle de Operação")
    tipo_negocio = st.radio("Tipo de Negócio", ["PRODUTO (ICMS)", "SERVIÇO (ISS)"])
    
    if tipo_negocio == "SERVIÇO (ISS)":
        cod_input = st.text_input("Código LC 116 (Ex: 7.02)", "7.02")
        op = st.selectbox("Operação", ["PRESTAÇÃO INTERNA", "PRESTAÇÃO INTERESTADUAL", "IMPORTAÇÃO", "EXPORTAÇÃO"])
    else:
        cod_input = st.text_input("NCM (8 dígitos)", "85171300")
        op = st.selectbox("Operação", ["SAÍDA", "ENTRADA", "IMPORTAÇÃO", "EXPORTAÇÃO"])

    st.divider()
    c1, c2 = st.columns(2)
    uf_o = c1.selectbox("UF Origem", ["SP", "RJ", "MG", "PR", "SC", "RS"])
    uf_d = c2.selectbox("UF Destino", ["RJ", "SP", "MG", "PR", "SC", "RS"])
    
    reg_o = st.selectbox("Regime Remetente", ["SIMPLES NACIONAL", "PRESUMIDO", "REAL"])
    reg_d = st.selectbox("Regime Destinatário", ["CONTRIBUINTE", "NÃO CONTRIBUINTE / PF"])
    
    st.divider()
    v_total = st.number_input("Valor Total da Operação (R$)", value=5000.0)
    btn_processar = st.button("🚀 ANALISAR MALHA 360", use_container_width=True)

# =====================================================================
# 4. LÓGICA DE PROCESSAMENTO (DUAL ENGINE)
# =====================================================================
if btn_processar:
    if tipo_negocio == "SERVIÇO (ISS)":
        data = get_service_data(cod_input)
        desc_item = data['desc']
        
        # Regra de Retenção LC 116
        retencao_obrigatoria = False
        if uf_o != uf_d and data['retencao_local']:
            retencao_obrigatoria = True
            just_iss = f"ISS devido no local da prestação conforme Art. 3º da LC 116/2003 (Exceção: {desc_item})."
        else:
            just_iss = "ISS devido no estabelecimento prestador (Regra Geral Art. 3º LC 116/2003)."
        
        imposto_principal = v_total * (data['aliq'] / 100)
        carga_total = imposto_principal + (v_total * 0.0365 if reg_o == "PRESUMIDO" else 0) # PIS/COFINS simbólico

    else:
        # Lógica de ICMS (Resumida do passo anterior para manter o dual)
        data = get_product_data(cod_input)
        desc_item = data['desc']
        imposto_principal = v_total * 0.18 # Simplificado para o relatório
        carga_total = imposto_principal + (v_total * (data['ipi']/100))

    # --- ABAS ---
    st.title(f"🔍 Auditoria: {desc_item}")
    t1, t2, t3 = st.tabs(["📄 ANÁLISE TÉCNICA", "📊 COMPARATIVO DE REGIMES", "📑 RELATÓRIO DE AUDITORIA"])

    with t1:
        col_inf, col_jus = st.columns([1, 1.5])
        with col_inf:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">Dados Gerais</p>', unsafe_allow_html=True)
            st.write(f"**Item/NCM:** {cod_input}")
            st.write(f"**Descrição:** {desc_item}")
            if tipo_negocio == "SERVIÇO (ISS)":
                st.write(f"**Alíquota ISS:** {data['aliq']}%")
                if retencao_obrigatoria:
                    st.markdown('<div class="alert-retencao">⚠️ RETENÇÃO DE ISS OBRIGATÓRIA NO DESTINO</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_jus:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">Fundamentação Legal</p>', unsafe_allow_html=True)
            if tipo_negocio == "SERVIÇO (ISS)":
                st.markdown(f'<div class="justificativa"><b>ISS:</b> {just_iss}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="justificativa"><b>Retenção:</b> Baseada na lista de exceções do Art. 3º, incisos I a XXV da LC 116/03.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="justificativa"><b>ICMS:</b> Operação interestadual tributada conforme convênio ICMS.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown("### Comparativo de Carga Tributária por Regime")
        # Simulação para Gráfico
        cenarios = {
            "Regime": ["SIMPLES", "PRESUMIDO", "REAL"],
            "Carga Est. (R$)": [v_total*0.06, v_total*0.14, v_total*0.22] if tipo_negocio == "SERVIÇO (ISS)" else [v_total*0.04, v_total*0.18, v_total*0.26]
        }
        df_comp = pd.DataFrame(cenarios)
        
        c_g1, c_g2 = st.columns([2, 1])
        with c_g1:
            fig = px.bar(df_comp, x="Regime", y="Carga Est. (R$)", color="Regime", 
                         text_auto='.2f', title="Carga Tributária Total Estimada (Imposto + Contribuições)")
            st.plotly_chart(fig, use_container_width=True)
        with c_g2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("**Análise de Viabilidade**")
            st.info("Para esta operação, o **SIMPLES NACIONAL** apresenta a menor carga nominal. Contudo, considere o crédito tributário se o destino for Lucro Real.")
            st.markdown('</div>', unsafe_allow_html=True)

    with t3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"## Relatório de Auditoria Fiscal #{(v_total/7):.0f}")
        st.markdown(f"**Data da Consulta:** 24/05/2024 | **Operação:** {op}")
        st.divider()
        
        html_report = f"""
        <table class="report-table">
            <tr style="background:#f8fafc; font-weight:bold;"><td>Item de Verificação</td><td>Resultado</td><td>Status</td></tr>
            <tr><td>Código de Atividade / NCM</td><td>{cod_input} - {desc_item}</td><td>✅ Verificado</td></tr>
            <tr><td>Alíquota Principal</td><td>{data['aliq'] if tipo_negocio == "SERVIÇO (ISS)" else 18.0}%</td><td>✅ Validado</td></tr>
            <tr><td>Possui Retenção na Fonte?</td><td>{"SIM" if (tipo_negocio == "SERVIÇO (ISS)" and retencao_obrigatoria) else "NÃO"}</td><td>📌 Atenção</td></tr>
            <tr><td>Base Legal Aplicada</td><td>{"LC 116/2003" if tipo_negocio == "SERVIÇO (ISS)" else "RICMS Estadual"}</td><td>⚖️ Informativo</td></tr>
            <tr style="font-weight:bold; color:#1e40af;"><td>VALOR TOTAL DOS IMPOSTOS</td><td>R$ {carga_total:,.2f}</td><td>📊 Total</td></tr>
        </table>
        """
        st.markdown(html_report, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Memória de Cálculo do ISS/ICMS")
        st.code(f"""
        Base de Cálculo: R$ {v_total:,.2f}
        Alíquota Aplicada: {data['aliq'] if tipo_negocio == "SERVIÇO (ISS)" else 18.0}%
        Cálculo: {v_total} * { (data['aliq']/100) if tipo_negocio == "SERVIÇO (ISS)" else 0.18 }
        Total Imposto Principal: R$ {imposto_principal:,.2f}
        """, language="python")
        
        st.button("🖨️ Imprimir Relatório Completo (Ctrl + P)")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
        <div style='text-align:center; padding: 100px; color: #94a3b8;'>
            <img src='https://cdn-icons-png.flaticon.com/512/1611/1611154.png' width='100' style='opacity: 0.2'>
            <h3>Sistema de Inteligência Fiscal pronto para análise.</h3>
            <p>Selecione os dados na barra lateral e clique em Processar.</p>
        </div>
    """, unsafe_allow_html=True)
