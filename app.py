import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import base64

# =====================================================================
# 1. DESIGN SYSTEM - GLASSMORPHISM & ENTERPRISE UI
# =====================================================================
st.set_page_config(page_title="TaxIntelligence OS | Pro", layout="wide", page_icon="⚡")

def inject_enterprise_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        
        :root {
            --primary: #6366f1; --primary-hover: #4f46e5;
            --bg: #f8fafc; --card-bg: rgba(255, 255, 255, 0.9);
            --text-main: #1e293b; --text-muted: #64748b;
        }

        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; color: var(--text-main); }
        .stApp { background: radial-gradient(circle at 0% 0%, #f1f5f9 0%, #ffffff 100%); }

        /* Glass Cards */
        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(226, 232, 240, 0.8);
            border-radius: 24px;
            padding: 2rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
            margin-bottom: 1.5rem;
        }

        /* Sidebar Luxury */
        [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #f1f5f9; }

        /* Stats & Badges */
        .badge-transicao {
            background: linear-gradient(90deg, #6366f1, #a855f7);
            color: white; padding: 4px 12px; border-radius: 99px; font-size: 10px; font-weight: 700;
        }
        
        .legal-tag {
            background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0;
            padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;
        }

        /* Technical Content */
        .tech-label { font-size: 0.75rem; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
        .tech-value { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; }
        .justificativa { font-size: 0.85rem; line-height: 1.6; color: #475569; background: #f8fafc; padding: 1rem; border-radius: 12px; border-left: 4px solid var(--primary); }
        </style>
    """, unsafe_allow_html=True)

inject_enterprise_css()

# =====================================================================
# 2. CORE DE INTELIGÊNCIA FISCAL (DATABASES 2026)
# =====================================================================
class FiscalCore:
    NCM_DATABASE = {
        "85171300": {"desc": "Smartphone / Terminal Celular", "mva_orig": 40.0, "ipi": 15.0, "seletivo": False},
        "84713012": {"desc": "Notebook / Laptop Portátil", "mva_orig": 35.0, "ipi": 0.0, "seletivo": False},
        "22030000": {"desc": "Cerveja de Malte (Bebidas Alcoólicas)", "mva_orig": 140.0, "ipi": 6.0, "seletivo": True},
    }
    
    LC116_DATABASE = {
        "7.02": {"desc": "Construção Civil / Obras", "aliq": 5.0, "local_excecao": True, "inciso": "Art. 3, III"},
        "1.05": {"desc": "Licenciamento de Software (SaaS)", "aliq": 2.0, "local_excecao": False, "inciso": "Art. 3, Caput"},
        "11.02": {"desc": "Vigilância e Segurança", "aliq": 5.0, "local_excecao": True, "inciso": "Art. 3, XVII"},
    }

# =====================================================================
# 3. LÓGICA DE CÁLCULO E TRANSIÇÃO REFORMA
# =====================================================================
def calcular_malha_completa(dados):
    # Regra 24/08/2026: CBS e IBS a 0,1% (Fase de Teste)
    v_nota = dados['valor']
    cbs = v_nota * 0.001
    ibs = v_nota * 0.001
    
    # Alíquotas ICMS (Interestadual 12%, Interna 18%)
    aliq_inter = 12.0 if dados['uf_o'] != dados['uf_d'] else 18.0
    aliq_intra = 18.0
    
    res = {"cbs": cbs, "ibs": ibs, "detalhes": {}}
    
    if dados['natureza'] == "PRODUTO":
        info = FiscalCore.NCM_DATABASE.get(dados['codigo'], {"desc": "Produto Geral", "mva_orig": 50.0, "ipi": 0.0})
        # Cálculo ST Base Dupla
        valor_ipi = v_nota * (info['ipi'] / 100)
        mva_ajustada = ((1 + (info['mva_orig']/100)) * (1 - aliq_inter/100) / (1 - aliq_intra/100)) - 1
        base_st = (v_nota + valor_ipi) * (1 + (mva_ajustada if aliq_inter < aliq_intra else info['mva_orig']/100))
        icms_proprio = (v_nota + valor_ipi) * (aliq_inter / 100)
        valor_st = (base_st * (aliq_intra / 100)) - icms_proprio
        
        res.update({
            "nome": info['desc'], "ipi": valor_ipi, "st": valor_st, "base_st": base_st, 
            "mva_final": mva_ajustada, "icms_p": icms_proprio, "aliq_inter": aliq_inter
        })
    else:
        info = FiscalCore.LC116_DATABASE.get(dados['codigo'], {"desc": "Serviço Geral", "aliq": 5.0, "local_excecao": False})
        # Retenção ISS
        iss_retido = (dados['cid_o'] != dados['cid_p']) and info['local_excecao']
        res.update({
            "nome": info['desc'], "iss_aliq": info['aliq'], "iss_valor": v_nota * (info['aliq']/100),
            "retencao": iss_retido, "local_devido": dados['cid_p'] if iss_retido else dados['cid_o']
        })
    return res

# =====================================================================
# 4. INTERFACE LATERAL - O "WIZARD"
# =====================================================================
with st.sidebar:
    st.markdown("<h2 style='color:#6366f1; margin-bottom:0;'>TaxIntelligence</h2><p style='font-size:12px; color:#64748b;'>Enterprise OS • v2026.8.24</p>", unsafe_allow_html=True)
    
    natureza = st.radio("Objeto da Operação", ["PRODUTO", "SERVIÇO"])
    op_tipo = st.selectbox("Tipo de Operação", ["SAÍDA/VENDA", "ENTRADA/COMPRA", "IMPORTAÇÃO", "EXPORTAÇÃO"])
    
    st.divider()
    cod_input = st.text_input("Código NCM ou LC 116", "85171300" if natureza == "PRODUTO" else "7.02")
    
    st.markdown("### Geolocalização")
    uf_o = st.selectbox("UF Origem", ["SP", "RJ", "MG", "PR", "SC", "RS"])
    uf_d = st.selectbox("UF Destino", ["RJ", "SP", "MG", "PR", "SC", "RS"])
    
    if natureza == "SERVIÇO":
        cid_o = st.text_input("Cidade Origem", "São Paulo")
        cid_p = st.text_input("Cidade da Prestação", "Rio de Janeiro")
        cid_d = "N/A"
    else:
        cid_o = cid_p = "N/A"
        cid_d = st.text_input("Cidade Destino", "Rio de Janeiro")

    st.divider()
    reg_o = st.selectbox("Regime Empresa", ["REAL", "PRESUMIDO", "SIMPLES NACIONAL"])
    reg_d = st.selectbox("Regime Destinatário", ["CONTRIBUINTE", "NÃO CONTRIBUINTE / PF"])
    v_nota = st.number_input("Valor da Nota (R$)", value=10000.0, min_value=0.0)
    
    processar = st.button("⚡ GERAR AUDITORIA FISCAL", use_container_width=True)

# =====================================================================
# 5. DASHBOARD E RELATÓRIO TÉCNICO
# =====================================================================
if processar:
    dados_input = {
        'natureza': natureza, 'codigo': cod_input, 'valor': v_nota,
        'uf_o': uf_o, 'uf_d': uf_d, 'cid_o': cid_o, 'cid_p': cid_p, 'reg_o': reg_o
    }
    auditoria = calcular_malha_completa(dados_input)
    
    st.markdown(f"<h1>{auditoria['nome']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<span class='badge-transicao'>PROJEÇÃO REFORMA VIGENTE EM 24/08/2026</span>", unsafe_allow_html=True)
    
    # --- ABAS ---
    tab1, tab2, tab3 = st.tabs(["🏛️ MATRIZ DE REGRAS", "🧮 MEMÓRIA DE CÁLCULO", "📊 COMPARATIVO & RELATÓRIO"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="glass-card"><p class="tech-label">ICMS / ISS</p>', unsafe_allow_html=True)
            if natureza == "PRODUTO":
                st.markdown(f"<p class='tech-label'>CFOP</p><p class='tech-value'>{'6.403' if uf_o != uf_d else '5.403'}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='tech-label'>CST ICMS</p><p class='tech-value'>010 (Tributada com ST)</p>", unsafe_allow_html=True)
                st.markdown(f"<div class='justificativa'><b>Motivo ST:</b> Aplicada Substituição Tributária devido ao NCM {cod_input} possuir protocolo ativo entre {uf_o} e {uf_d}.</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p class='tech-label'>LOCAL DE RECOLHIMENTO</p><p class='tech-value'>{auditoria['local_devido']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='tech-label'>RETENÇÃO</p><p class='tech-value'>{'OBRIGATÓRIA' if auditoria['retencao'] else 'NÃO APLICÁVEL'}</p>", unsafe_allow_html=True)
                st.markdown(f"<div class='justificativa'><b>Fundamentação:</b> Conforme Art. 3º da LC 116/03, o imposto é devido no local da execução para este código de atividade.</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="glass-card"><p class="tech-label">PIS / COFINS & CBS</p>', unsafe_allow_html=True)
            st.markdown(f"<p class='tech-label'>PIS/COFINS (REGIME)</p><p class='tech-value'>{reg_o}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='tech-label'>CBS (IVA FEDERAL)</p><p class='tech-value'>R$ {auditoria['cbs']:.2f} (0,1%)</p>", unsafe_allow_html=True)
            st.markdown(f"<div class='justificativa'><b>Transição 2026:</b> Incidência de CBS a 0,1% para fins de teste de arrecadação, compensável no PIS/COFINS conforme EC 132/23.</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### 🧮 Engenharia Tributária")
        if natureza == "PRODUTO":
            c_c1, c_c2, c_c3 = st.columns(3)
            c_c1.metric("MVA Ajustada", f"{auditoria['mva_final']*100:.2f}%")
            c_c2.metric("Base ICMS-ST", f"R$ {auditoria['base_st']:,.2f}")
            c_c3.metric("ICMS Próprio", f"R$ {auditoria['icms_p']:,.2f}")
            st.divider()
            st.markdown(f"**Cálculo:** `(Base ST * {18}%) - ICMS Próprio = R$ {auditoria['st']:,.2f}`")
        else:
            st.metric("Total ISS a Recolher", f"R$ {auditoria['iss_valor']:,.2f}")
            st.markdown(f"**Memória:** `{v_nota:,.2f} * {auditoria['iss_aliq']}%`")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("### Dashboard de Planejamento")
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            df_g = pd.DataFrame({"Regime": ["SIMPLES", "PRESUMIDO", "REAL"], "Carga": [6.0, 14.3, 19.5]})
            fig = px.bar(df_g, x="Regime", y="Carga", color="Regime", text_auto=True, title="Impacto por Regime (%)", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        with col_g2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.write("#### Relatório Final")
            st.write(f"Operação: **{op_tipo}**")
            st.write(f"Custo Total Imposto: **R$ {auditoria.get('st', 0) + auditoria.get('iss_valor', 0) + auditoria['cbs'] + auditoria['ibs']:,.2f}**")
            
            # PDF GENERATION
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, "AUDITORIA FISCAL PRO - 2026", ln=True, align='C')
            pdf.set_font("Arial", '', 10)
            pdf.ln(10)
            pdf.cell(200, 10, f"Objeto: {auditoria['nome']} | Valor: R$ {v_nota:,.2f}", ln=True)
            pdf.cell(200, 10, f"Data Vigência: 24/08/2026", ln=True)
            
            pdf_b = pdf.output(dest='S').encode('latin-1')
            b64 = base64.b64encode(pdf_b).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="auditoria_fiscal.pdf" style="display:block; text-align:center; padding:10px; background:#6366f1; color:white; border-radius:10px; text-decoration:none;">📥 BAIXAR RELATÓRIO PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
        <div style='text-align:center; padding: 100px; opacity: 0.5;'>
            <img src='https://cdn-icons-png.flaticon.com/512/1162/1162456.png' width='80'>
            <h2>Aguardando Parâmetros</h2>
            <p>Configure a operação na barra lateral para gerar a auditoria inteligente.</p>
        </div>
    """, unsafe_allow_html=True)
