import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import base64

# =====================================================================
# 1. ARQUITETURA DE DESIGN (UI/UX PREMIUM)
# =====================================================================
st.set_page_config(page_title="TAX INTELLIGENCE OS | 2026", layout="wide")

def local_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        
        :root { --primary: #007AFF; --accent: #34C759; --warning: #FF9500; --danger: #FF3B30; }
        
        .main { background: #f5f5f7; font-family: 'Inter', sans-serif; }
        
        /* Glassmorphism Card */
        .glass-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            margin-bottom: 20px;
        }
        
        .section-header {
            font-size: 14px; font-weight: 700; color: var(--primary);
            text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 15px;
        }
        
        .tech-label { font-size: 12px; color: #86868b; margin-bottom: 5px; }
        .tech-value { font-size: 18px; font-weight: 600; color: #1d1d1f; }
        
        .justificativa-tecnica {
            background: #ffffff; border-left: 4px solid var(--primary);
            padding: 15px; border-radius: 8px; font-size: 13px; line-height: 1.6; color: #424245;
        }
        
        /* Badge Dinâmico */
        .badge {
            padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: 700;
        }
        .badge-blue { background: #E5F1FF; color: #007AFF; }
        </style>
    """, unsafe_allow_html=True)

local_css()

# =====================================================================
# 2. MÓDULO DE INTELIGÊNCIA FISCAL (DATA ENGINE)
# =====================================================================
class FiscalEngine:
    @staticmethod
    def get_legal_ncm(ncm):
        base = {
            "85171300": {"desc": "Smartphone", "mva_orig": 40.0, "aliq_ipi": 15.0, "seletivo": False},
            "22030000": {"desc": "Cerveja", "mva_orig": 140.0, "aliq_ipi": 6.0, "seletivo": True},
        }
        return base.get(ncm, {"desc": "Outros Produtos", "mva_orig": 50.0, "aliq_ipi": 0.0, "seletivo": False})

    @staticmethod
    def get_legal_iss(code):
        services = {
            "7.02": {"desc": "Construção Civil", "excecao": True, "art": "Art. 3, III LC 116"},
            "1.05": {"desc": "Software/SaaS", "excecao": False, "art": "Art. 3, Caput LC 116"},
            "11.02": {"desc": "Vigilância", "excecao": True, "art": "Art. 3, XVII LC 116"},
        }
        return services.get(code, {"desc": "Serviços Gerais", "excecao": False, "art": "Art. 3 LC 116"})

# =====================================================================
# 3. MÓDULO DE CÁLCULO (TAX CALC ENGINE)
# =====================================================================
class TaxCalculator:
    def __init__(self, valor, uf_o, uf_d, reg_o):
        self.valor = valor
        self.uf_o = uf_o
        self.uf_d = uf_d
        self.reg_o = reg_o
        self.aliq_inter = 12.0 if uf_o in ["SP", "RJ", "MG", "PR", "SC", "RS"] else 7.0
        self.aliq_intra = 18.0 # Média Brasil 2026

    def calcular_transicao_2026(self):
        # Regra de 24/08/2026: CBS e IBS a 0,1% cada
        cbs = self.valor * 0.001
        ibs = self.valor * 0.001
        return cbs, ibs

    def calcular_st_base_dupla(self, mva_orig, ipi_percent):
        mva_decimal = mva_orig / 100
        valor_ipi = self.valor * (ipi_percent / 100)
        # MVA Ajustada: [(1 + MVA-ST original) x (1 - ALQ-inter) / (1 - ALQ-intra)] - 1
        mva_ajustada = ((1 + mva_decimal) * (1 - self.aliq_inter/100) / (1 - self.aliq_intra/100)) - 1
        
        base_st = (self.valor + valor_ipi) * (1 + mva_ajustada)
        icms_proprio = (self.valor + valor_ipi) * (self.aliq_inter / 100)
        valor_st = (base_st * (self.aliq_intra / 100)) - icms_proprio
        return valor_st, base_st, mva_ajustada

# =====================================================================
# 4. EXPORTAÇÃO DE RELATÓRIO (PDF ENGINE)
# =====================================================================
def generate_pdf(data_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RELATÓRIO TÉCNICO DE AUDITORIA FISCAL 2026", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    for key, value in data_dict.items():
        pdf.multi_cell(0, 10, f"{key}: {value}")
    return pdf.output(dest='S').encode('latin-1')

# =====================================================================
# 5. INTERFACE DINÂMICA
# =====================================================================
with st.sidebar:
    st.markdown("### 🛠️ CONFIGURAÇÃO DE MALHA")
    natureza = st.segmented_control("Natureza", ["📦 PRODUTO", "🛠️ SERVIÇO"], default="📦 PRODUTO")
    
    st.divider()
    op_tipo = st.selectbox("Operação", ["SAÍDA/VENDA", "ENTRADA/COMPRA", "IMPORTAÇÃO", "EXPORTAÇÃO"])
    uf_o = st.selectbox("Origem", ["SP", "RJ", "MG", "PR", "SC", "RS", "ES", "GO", "BA", "MT"])
    uf_d = st.selectbox("Destino", ["RJ", "SP", "MG", "PR", "SC", "RS", "ES", "GO", "BA", "MT"])
    
    if natureza == "🛠️ SERVIÇO":
        cod_ref = st.text_input("Código LC 116", "7.02")
        cid_prest = st.text_input("Cidade Prestação", "Rio de Janeiro")
    else:
        cod_ref = st.text_input("NCM", "85171300")
        
    st.divider()
    reg_o = st.selectbox("Regime Empresa", ["LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL"])
    reg_d = st.selectbox("Regime Comprador", ["CONTRIBUINTE", "NÃO CONTRIBUINTE / PF"])
    v_operacao = st.number_input("Valor da Operação (R$)", value=10000.0, step=500.0)
    
    run = st.button("🚀 EXECUTAR AUDITORIA", use_container_width=True)

# =====================================================================
# 6. EXECUÇÃO E DASHBOARD
# =====================================================================
if run:
    calc = TaxCalculator(v_operacao, uf_o, uf_d, reg_o)
    cbs, ibs = calc.calcular_transicao_2026()
    
    st.markdown(f"## ⚙️ AUDITORIA TÉCNICA: {cod_ref}")
    st.markdown(f"**Vigência Analisada:** 24/08/2026 | **Status da Malha:** <span class='badge badge-blue'>Validado</span>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏛️ MATRIZ TRIBUTÁRIA", "🧮 ENGENHARIA DE CÁLCULO", "📊 IMPACTO REFORMA"])

    with tab1:
        c1, c2 = st.columns(2)
        if natureza == "📦 PRODUTO":
            p_data = FiscalEngine.get_legal_ncm(cod_ref)
            with c1:
                st.markdown('<div class="glass-card"><p class="section-header">ICMS & IPI</p>', unsafe_allow_html=True)
                st.markdown(f"<p class='tech-label'>CFOP Sugerido</p><p class='tech-value'>{'6.403' if uf_o != uf_d else '5.403'}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='tech-label'>CST ICMS</p><p class='tech-value'>010 (Tributada com ST)</p>", unsafe_allow_html=True)
                st.markdown(f"<div class='justificativa-tecnica'><b>Justificativa:</b> Produto sujeito a Substituição Tributária conforme Convênio ICMS. Incidência de IPI de {p_data['aliq_ipi']}% conforme TIPI 2026.</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="glass-card"><p class="section-header">PIS & COFINS</p>', unsafe_allow_html=True)
                st.markdown(f"<p class='tech-label'>Regime</p><p class='tech-value'>{reg_o}</p>", unsafe_allow_html=True)
                st.markdown(f"<div class='justificativa-tecnica'><b>Nota 2026:</b> O valor da CBS ({cbs:.2f}) será deduzido da base de cálculo do PIS/COFINS para evitar bitributação durante a transição.</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            s_data = FiscalEngine.get_legal_iss(cod_ref)
            with c1:
                st.markdown('<div class="glass-card"><p class="section-header">ISS & RETENÇÃO</p>', unsafe_allow_html=True)
                retencao = "SIM" if (uf_o != uf_d and s_data['excecao']) else "NÃO"
                st.write(f"**Retenção no Destino:** {retencao}")
                st.markdown(f"<div class='justificativa-tecnica'><b>Base Legal:</b> {s_data['art']}. O serviço de {s_data['desc']} {'exige' if retencao == 'SIM' else 'não exige'} recolhimento na cidade de {uf_d}.</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### Memória de Cálculo - Metodologia Base Dupla")
        if natureza == "📦 PRODUTO":
            v_st, b_st, mva_a = calc.calcular_st_base_dupla(p_data['mva_orig'], p_data['aliq_ipi'])
            col_calc1, col_calc2 = st.columns(2)
            col_calc1.metric("MVA Ajustada", f"{mva_a*100:.2f}%")
            col_calc1.metric("Base de Cálculo ST", f"R$ {b_st:,.2f}")
            col_calc2.metric("Valor ICMS-ST", f"R$ {v_st:,.2f}")
            col_calc2.metric("IPI Calculado", f"R$ {v_operacao*(p_data['aliq_ipi']/100):,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.write("### Transição Reforma Tributária (Em vigor 24/08/2026)")
        c_r1, c_r2 = st.columns(2)
        c_r1.metric("CBS (IVA Federal) - 0,1%", f"R$ {cbs:,.2f}")
        c_r2.metric("IBS (IVA Estadual) - 0,1%", f"R$ {ibs:,.2f}")
        
        # Gráfico Dinâmico
        fig = go.Figure(data=[go.Bar(name='Carga Atual', x=['Tributos'], y=[v_operacao*0.25]),
                             go.Bar(name='Transição 2026', x=['Tributos'], y=[cbs+ibs])])
        fig.update_layout(barmode='group', title="Impacto Financeiro da Transição", template="simple_white")
        st.plotly_chart(fig, use_container_width=True)

    # Botão de Download PDF
    report_data = {
        "Data": "24/08/2026",
        "Operação": op_tipo,
        "Origem": uf_o,
        "Destino": uf_d,
        "Valor": f"R$ {v_operacao:,.2f}",
        "CBS": f"R$ {cbs:,.2f}",
        "IBS": f"R$ {ibs:,.2f}"
    }
    pdf_bytes = generate_pdf(report_data)
    st.download_button("📥 BAIXAR RELATÓRIO COMPLETO (PDF)", data=pdf_bytes, file_name="auditoria_fiscal_2026.pdf", mime="application/pdf")

else:
    st.markdown("""
        <div style='text-align:center; padding: 100px;'>
            <h2 style='color:#d2d2d7;'>Tax Intelligence Engine v2.0</h2>
            <p style='color:#86868b;'>Selecione os parâmetros e execute a auditoria para ver os dados.</p>
        </div>
    """, unsafe_allow_html=True)
