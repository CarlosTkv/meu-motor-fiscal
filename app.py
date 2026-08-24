import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from datetime import datetime
from fpdf import FPDF

# =====================================================================
# 1. CORE CONFIGURATION & LUXURY DESIGN SYSTEM
# =====================================================================
st.set_page_config(page_title="TaxWizard Ultra | Enterprise 2026", layout="wide", page_icon="💎")

def inject_ultra_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        
        :root {
            --primary: #6366f1; --primary-light: #e0e7ff;
            --success: #10b981; --warning: #f59e0b; --error: #ef4444;
            --slate-900: #0f172a; --slate-700: #334155; --slate-100: #f1f5f9;
        }

        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; color: var(--slate-900); }
        .stApp { background: #fafafa; }

        /* Bento Grid Style Cards */
        .bento-card {
            background: white; border-radius: 24px; padding: 1.8rem;
            border: 1px solid #eef2f6; box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            transition: all 0.3s ease; height: 100%;
        }
        .bento-card:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0,0,0,0.06); border-color: var(--primary); }

        /* Status & Badges */
        .status-pill {
            display: inline-flex; align-items: center; padding: 4px 12px;
            border-radius: 99px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
        }
        .pill-blue { background: var(--primary-light); color: var(--primary); border: 1px solid #c7d2fe; }
        
        /* Typography */
        .label-tech { font-size: 11px; font-weight: 700; color: var(--slate-700); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
        .value-tech { font-size: 20px; font-weight: 800; color: var(--slate-900); }
        .legal-box { 
            font-size: 13px; line-height: 1.6; color: #475569; background: #f8fafc; 
            padding: 1.2rem; border-radius: 16px; border-left: 6px solid var(--primary);
        }
        </style>
    """, unsafe_allow_html=True)

inject_ultra_css()

# =====================================================================
# 2. INTELLIGENCE ENGINE (DATABASE & LAWS 2026)
# =====================================================================
class TaxIntelligence:
    NCM_DATA = {
        "85171300": {"desc": "Smartphone / Terminal Celular", "mva": 40.0, "ipi": 15.0, "is": 0.0},
        "22030000": {"desc": "Cerveja de Malte", "mva": 140.0, "ipi": 6.0, "is": 15.0}, # Imposto Seletivo Ativo em 2026
        "84713012": {"desc": "Notebook / Laptop", "mva": 35.0, "ipi": 0.0, "is": 0.0}
    }
    
    LC116_DATA = {
        "7.02": {"desc": "Construção Civil / Obras", "aliq": 5.0, "ret": True, "art": "Art. 3, III"},
        "1.05": {"desc": "Software SaaS", "aliq": 2.0, "ret": False, "art": "Art. 3, Caput"},
        "11.02": {"desc": "Vigilância", "aliq": 5.0, "ret": True, "art": "Art. 3, XVII"}
    }

# =====================================================================
# 3. MÓDULO DE CÁLCULO E TRANSIÇÃO (MATEMÁTICA FISCAL)
# =====================================================================
def processar_malha(d):
    # Regras vigentes em 24/08/2026
    v = d['valor']
    res = {
        "cbs": v * 0.001, "ibs": v * 0.001, # Fase de teste transição
        "is": 0.0, "detalhes": {}
    }
    
    aliq_inter, aliq_intra = (12.0, 18.0) if d['uf_o'] != d['uf_d'] else (18.0, 18.0)

    if d['tipo'] == "PRODUTO":
        info = TaxIntelligence.NCM_DATA.get(d['cod'], {"desc": "Produto Geral", "mva": 50.0, "ipi": 0.0, "is": 0.0})
        # Cálculo ST com IPI compondo base
        v_ipi = v * (info['ipi'] / 100)
        v_is = v * (info['is'] / 100) if info['is'] > 0 else 0.0
        
        mva_ajust = ((1 + (info['mva']/100)) * (1 - aliq_inter/100) / (1 - aliq_intra/100)) - 1
        base_st = (v + v_ipi + v_is) * (1 + (mva_ajust if aliq_inter < aliq_intra else info['mva']/100))
        icms_prop = (v + v_ipi) * (aliq_inter / 100)
        v_st = max(0, (base_st * (aliq_intra / 100)) - icms_prop)
        
        res.update({
            "nome": info['desc'], "ipi": v_ipi, "st": v_st, "is": v_is, "icms_p": icms_prop,
            "base_st": base_st, "mva_ajust": mva_ajust, "aliq_inter": aliq_inter, "aliq_intra": aliq_intra
        })
    else:
        info = TaxIntelligence.LC116_DATA.get(d['cod'], {"desc": "Serviço Especializado", "aliq": 5.0, "ret": False})
        iss_r = (d['cid_o'] != d['cid_p']) and info['ret']
        res.update({
            "nome": info['desc'], "iss_v": v * (info['aliq']/100), "retencao": iss_r,
            "aliq_iss": info['aliq'], "local": d['cid_p'] if iss_r else d['cid_o']
        })
    return res

# =====================================================================
# 4. SIDEBAR - CONTROLE DE NAVEGAÇÃO E INPUTS
# =====================================================================
with st.sidebar:
    st.markdown("<h1 style='color:#6366f1;'>TaxWizard <span style='color:#0f172a'>Pro</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:11px; margin-top:-20px; font-weight:700; color:#94a3b8;'>SaaS ENTERPRISE • AUG 2026</p>", unsafe_allow_html=True)
    
    tab_op = st.radio("Selecione o Objeto", ["📦 PRODUTO (NCM)", "🛠️ SERVIÇO (LC116)"])
    
    st.divider()
    with st.expander("🌍 Geografia e Operação", expanded=True):
        uf_origem = st.selectbox("UF Origem", ["SP", "RJ", "MG", "PR", "SC", "RS"])
        uf_destino = st.selectbox("UF Destino", ["RJ", "SP", "MG", "PR", "SC", "RS"])
        if tab_op == "🛠️ SERVIÇO (LC116)":
            cid_orig = st.text_input("Município Sede", "São Paulo")
            cid_prest = st.text_input("Município Prestação", "Rio de Janeiro")
            cid_tomad = st.text_input("Município Tomador", "Belo Horizonte")
        else:
            cod_id = st.text_input("NCM (8 dígitos)", "85171300")
            cid_orig = cid_prest = cid_tomad = "N/A"

    with st.expander("💰 Valores e Regime", expanded=True):
        if tab_op == "🛠️ SERVIÇO (LC116)":
            cod_id = st.text_input("Código LC 116", "7.02")
        valor_nf = st.number_input("Valor Bruto (R$)", value=50000.0)
        regime = st.selectbox("Regime Empresa", ["LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL"])

    st.divider()
    gerar = st.button("⚡ ANALISAR AGORA", use_container_width=True)

# =====================================================================
# 5. DASHBOARD - O "PERFEITO" VISUAL
# =====================================================================
if gerar:
    params = {
        'tipo': "PRODUTO" if "📦" in tab_op else "SERVIÇO",
        'cod': cod_id, 'valor': valor_nf, 'uf_o': uf_origem, 'uf_d': uf_destino,
        'cid_o': cid_orig, 'cid_p': cid_prest, 'cid_t': cid_tomad
    }
    audit = processar_malha(params)

    # HEADER DINÂMICO
    st.markdown(f"<h1>{audit['nome']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<span class='status-pill pill-blue'>AUDITORIA EM 24/08/2026 • ID {datetime.now().strftime('%Y%m%d%H%M')}</span>", unsafe_allow_html=True)
    
    st.divider()

    # BENTO GRID - ROW 1
    col1, col2, col3 = st.columns([1.2, 1, 1])
    
    with col1:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<p class="label-tech">Principal (ICMS / ISS)</p>', unsafe_allow_html=True)
        if params['tipo'] == "PRODUTO":
            st.markdown(f"<p class='tech-value'>CFOP {'6403' if uf_origem != uf_destino else '5403'}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='label-tech'>ICMS Próprio: R$ {audit['icms_p']:,.2f}</p>", unsafe_allow_html=True)
            st.markdown(f"<div class='legal-box'><b>Fundamentação:</b> Mercadoria sujeita ao regime de ST conforme Convênio ICMS 142/18. Base de cálculo composta por IPI + IS conforme legislação de 2026.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p class='tech-value'>{audit['local']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='label-tech'>ISS Due To: {'LOCAL DA PRESTAÇÃO' if audit['retencao'] else 'SEDE DO PRESTADOR'}</p>", unsafe_allow_html=True)
            st.markdown(f"<div class='legal-box'><b>LC 116/03:</b> O serviço {cod_id} é exceção à regra geral. Imposto devido em {audit['local']} conforme Art. 3º.</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<p class="label-tech">Transição Reforma (CBS / IBS)</p>', unsafe_allow_html=True)
        st.markdown(f"<p class='tech-value' style='color:#6366f1'>R$ {audit['cbs'] + audit['ibs']:,.2f}</p>", unsafe_allow_html=True)
        st.write(f"🔹 CBS (0,1%): R$ {audit['cbs']:.2f}")
        st.write(f"🔹 IBS (0,1%): R$ {audit['ibs']:.2f}")
        st.markdown(f"<div class='legal-box' style='border-left-color:#10b981'><b>Status:</b> Alíquotas de teste vigentes para compensação futura.</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.markdown('<p class="label-tech">Imposto Seletivo (IS)</p>', unsafe_allow_html=True)
        st.markdown(f"<p class='tech-value' style='color:#ef4444'>R$ {audit['is']:,.2f}</p>", unsafe_allow_html=True)
        st.write(f"Incidência: {'Sim' if audit['is'] > 0 else 'Não'}")
        st.markdown(f"<div class='legal-box' style='border-left-color:#ef4444'><b>Impacto:</b> Seletivo incidindo sobre valor bruto para desestimular consumo.</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ROW 2 - MEMÓRIA DE CÁLCULO E GRÁFICO
    st.markdown("### 🧮 Memória de Cálculo & Planejamento")
    col_calc, col_viz = st.columns([1.5, 1])
    
    with col_calc:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        if params['tipo'] == "PRODUTO":
            st.write(f"**Base ST (Base Dupla):** R$ {audit['base_st']:,.2f}")
            st.write(f"**MVA Ajustada:** {audit['mva_ajust']*100:.2f}%")
            st.code(f"Step 1: (Valor + IPI + IS) * (1 + MVA) = Base ST\nStep 2: (Base ST * {audit['aliq_intra']}%) - ICMS Próprio = R$ {audit['st']:,.2f}")
        else:
            st.write(f"**Base de Cálculo ISS:** R$ {valor_nf:,.2f}")
            st.code(f"Step 1: Base * {audit['aliq_iss']}% = R$ {audit['iss_v']:,.2f}\nRetenção: {'Sim (Tomador recolhe)' if audit['retencao'] else 'Não (Prestador recolhe)'}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_viz:
        # Gráfico Comparativo 2026
        df_viz = pd.DataFrame({
            "Tributo": ["ICMS/ISS", "PIS/COF", "IPI/IS", "IBS/CBS"],
            "Valor (R$)": [audit.get('icms_p', audit.get('iss_v', 0)), valor_nf*0.09, audit.get('ipi', 0)+audit['is'], audit['cbs']+audit['ibs']]
        })
        fig = px.pie(df_viz, values='Valor (R$)', names='Tributo', hole=.6, color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=250)
        st.plotly_chart(fig, use_container_width=True)

    # DOWNLOAD REPORT (PDF ENGINE)
    st.divider()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "AUDITORIA TÉCNICA TAXWIZARD ULTRA", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Operação: {params['tipo']} - {audit['nome']}\nData: 24/08/2026\nValor: R$ {valor_nf:,.2f}\nTotal Tributos: R$ {sum(df_viz['Valor (R$)']):,.2f}")
    
    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64_pdf = base64.b64encode(pdf_output).decode()
    st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="tax_audit_2026.pdf" style="text-decoration:none; background:var(--slate-900); color:white; padding:12px 30px; border-radius:12px; font-weight:700;">📥 BAIXAR RELATÓRIO PDF COMPLETO</a>', unsafe_allow_html=True)

else:
    st.markdown("""
        <div style='text-align:center; padding: 150px; opacity:0.4;'>
            <img src='https://cdn-icons-png.flaticon.com/512/1162/1162456.png' width='80'>
            <h2>Tax Engine Ready</h2>
            <p>Selecione os parâmetros técnicos e inicie o motor de auditoria.</p>
        </div>
    """, unsafe_allow_html=True)
