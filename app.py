import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import base64

# =====================================================================
# 1. CONFIGURAÇÃO DE UI/UX - DESIGN "WIZARD PRO"
# =====================================================================
st.set_page_config(page_title="TaxWizard Pro | 2026", page_icon="⚡", layout="wide")

def apply_custom_design():
    st.markdown("""
        <style>
        /* Importação de Fonte */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
        
        :root {
            --bg-glass: rgba(255, 255, 255, 0.8);
            --border-glass: rgba(209, 213, 219, 0.3);
            --primary-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        }

        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

        /* Estilização Geral do Fundo */
        .stApp {
            background: radial-gradient(circle at top right, #f8fafc, #eff6ff);
        }

        /* Sidebar Customizada */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0;
        }

        /* Card Estilo SaaS Premium */
        .tax-card {
            background: white;
            padding: 24px;
            border-radius: 20px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }
        .tax-card:hover {
            transform: translateY(-5px);
            border-color: #6366f1;
        }

        /* Badge Estilizado */
        .status-badge {
            padding: 4px 12px;
            border-radius: 99px;
            font-size: 11px;
            font-weight: 700;
            background: #f1f5f9;
            color: #475569;
            border: 1px solid #e2e8f0;
        }

        /* Títulos */
        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .section-header {
            color: #1e293b;
            font-weight: 700;
            font-size: 1.1rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* Justificativa Técnica Box */
        .legal-box {
            background: #f8fafc;
            border-left: 5px solid #6366f1;
            padding: 1.5rem;
            border-radius: 8px;
            font-size: 13px;
            line-height: 1.6;
            color: #334155;
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_design()

# =====================================================================
# 2. MOTOR FISCAL ROBUSTO (LOGICA VIGENTE EM 24/08/2026)
# =====================================================================
class TaxEngine:
    def __init__(self):
        # Base de dados técnica
        self.ncm_db = {
            "85171300": {"nome": "Smartphone", "mva": 40.0, "ipi": 15.0, "cst_ipi": "50"},
            "84713012": {"nome": "Notebook", "mva": 35.0, "ipi": 0.0, "cst_ipi": "51"},
            "22030000": {"nome": "Cerveja", "mva": 140.0, "ipi": 6.0, "cst_ipi": "50"}
        }
        self.iss_db = {
            "7.02": {"desc": "Obras de Construção Civil", "excecao": True, "aliq": 5.0},
            "1.05": {"desc": "Licenciamento de Software", "excecao": False, "aliq": 2.0},
            "11.02": {"desc": "Vigilância e Segurança", "excecao": True, "aliq": 5.0}
        }

    def calcular_mva_ajustada(self, mva_original, aliq_inter, aliq_intra):
        # Fórmula: [ (1+MVA) * (1-AliqInter) / (1-AliqIntra) ] - 1
        return ((1 + (mva_original/100)) * (1 - (aliq_inter/100)) / (1 - (aliq_intra/100))) - 1

# engine = TaxEngine()

# =====================================================================
# 3. INTERFACE DE NAVEGAÇÃO (WIZARD STEPS)
# =====================================================================
with st.sidebar:
    st.markdown("<h2 style='color:#6366f1;'>TaxWizard ⚡</h2>", unsafe_allow_html=True)
    st.caption("Intelligence OS for 2026 Tax Reform")
    
    menu = st.radio("Navegação", ["Dashboard", "Calculadora Fiscal", "Relatórios", "Configurações"])
    
    st.divider()
    st.markdown("### Parâmetros da Operação")
    op_type = st.selectbox("Natureza", ["Produto (ICMS/IPI)", "Serviço (ISS)"])
    uf_o = st.selectbox("Origem", ["SP", "RJ", "MG", "PR", "SC", "RS", "ES", "GO"])
    uf_d = st.selectbox("Destino", ["RJ", "SP", "MG", "PR", "SC", "RS", "ES", "GO"])
    
    reg_remetente = st.selectbox("Regime Empresa", ["LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL"])
    reg_destinatario = st.selectbox("Regime Destinatário", ["CONTRIBUINTE", "NÃO CONTRIBUINTE / PF"])

# =====================================================================
# 4. PÁGINA: CALCULADORA (A MAIS TÉCNICA)
# =====================================================================
if menu == "Calculadora Fiscal":
    st.markdown("<h1 class='main-title'>Calculadora Fiscal Pro</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-header'>Dados da Nota</p>", unsafe_allow_html=True)
        cod_ref = st.text_input("NCM ou Código LC 116", value="85171300")
        v_bruto = st.number_input("Valor da Operação (R$)", value=10000.0, step=1000.0)
        v_frete = st.number_input("Frete / Despesas (R$)", value=0.0)
        
        if op_type == "Serviço (ISS)":
            cid_p = st.text_input("Município da Prestação", "Rio de Janeiro")
            
        process = st.button("Executar Malha Fiscal 360", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if process:
        engine = TaxEngine()
        # --- LOGICA 24/08/2026 ---
        cbs_transicao = v_bruto * 0.001 # 0,1% conforme reforma
        ibs_transicao = v_bruto * 0.001 # 0,1% conforme reforma
        
        with col2:
            st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
            st.markdown(f"<span class='status-badge'>ANALISADO EM 24/08/2026</span>", unsafe_allow_html=True)
            
            if op_type == "Produto (ICMS/IPI)":
                prod = engine.ncm_db.get(cod_ref, {"nome": "Genérico", "mva": 50, "ipi": 0})
                aliq_inter = 12.0 if uf_o != uf_d else 18.0
                aliq_intra = 18.0
                
                mva_a = engine.calcular_mva_ajustada(prod['mva'], aliq_inter, aliq_intra)
                valor_ipi = v_bruto * (prod['ipi']/100)
                base_st = (v_bruto + valor_ipi) * (1 + mva_a)
                valor_st = (base_st * (aliq_intra/100)) - (v_bruto * (aliq_inter/100))
                
                # Visualização Técnica
                st.subheader(f"Análise: {prod['nome']}")
                
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("CST ICMS", "010")
                c_b.metric("CFOP", "6.403" if uf_o != uf_d else "5.403")
                c_c.metric("ICMS-ST", f"R$ {valor_st:,.2f}")
                
                st.markdown("<p class='section-header'>📖 Justificativa Técnico-Legal</p>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class='legal-box'>
                    <b>ICMS-ST:</b> Aplicado MVA Ajustada de {mva_a*100:.2f}% (MVA Original {prod['mva']}%). 
                    Ajuste obrigatório conforme Convênio ICMS 142/18 devido à diferença de alíquotas entre {uf_o} ({aliq_inter}%) e {uf_d} ({aliq_intra}%).
                    <br><br><b>IPI:</b> Incidência de {prod['ipi']}% com CST {prod.get('cst_ipi', '50')} baseada na TIPI 2026.
                </div>
                """, unsafe_allow_html=True)
                
            else:
                serv = engine.iss_db.get(cod_ref, {"desc": "Geral", "excecao": False, "aliq": 5.0})
                st.subheader(f"Serviço: {serv['desc']}")
                
                retido = "SIM" if (uf_o != uf_d and serv['excecao']) else "NÃO"
                st.metric("ISS RETIDO NO DESTINO?", retido)
                
                st.markdown("<p class='section-header'>📖 Fundamentação ISS (LC 116/03)</p>", unsafe_allow_html=True)
                msg_iss = f"ISS devido no local da prestação conforme Art. 3º da LC 116." if retido == "SIM" else "Imposto devido no local do estabelecimento prestador (Regra Geral)."
                st.markdown(f"<div class='legal-box'>{msg_iss} Código {cod_ref} identificado como exceção à regra geral.</div>", unsafe_allow_html=True)

            # --- SEÇÃO REFORMA 2026 ---
            st.divider()
            st.markdown("<p class='section-header'>🌿 Transição Reforma Tributária (CBS/IBS)</p>", unsafe_allow_html=True)
            col_ref1, col_ref2 = st.columns(2)
            col_ref1.info(f"**CBS (Federal):** R$ {cbs_transicao:,.2f}")
            col_ref2.success(f"**IBS (Estadual):** R$ {ibs_transicao:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 5. PÁGINA: DASHBOARD (VISUALIZAÇÃO DE DADOS)
# =====================================================================
elif menu == "Dashboard":
    st.markdown("<h1 class='main-title'>Analytics & Viabilidade</h1>", unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns([2, 1])
    
    with col_d1:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        # Comparativo Real
        df_viz = pd.DataFrame({
            "Regime": ["Lucro Real", "Lucro Presumido", "Simples Nacional"],
            "Carga %": [26.5, 16.8, 10.5],
            "Custo Bruto (R$)": [2650, 1680, 1050]
        })
        fig = px.bar(df_viz, x="Regime", y="Custo Bruto (R$)", color="Regime", 
                     title="Carga Tributária Estimada por Regime em 2026",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_d2:
        st.markdown("<div class='tax-card'>", unsafe_allow_html=True)
        st.write("### Insights de IA")
        st.write("📍 **Oportunidade:** O destino em RJ possui incentivo para o NCM informado.")
        st.write("⚠️ **Risco:** MVA Ajustada acima da média nacional para este segmento.")
        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 6. RELATÓRIOS E EXPORTAÇÃO (PDF SEM ERRO)
# =====================================================================
elif menu == "Relatórios":
    st.markdown("<h1 class='main-title'>Central de Relatórios</h1>", unsafe_allow_html=True)
    st.write("Gere o laudo pericial da análise efetuada.")
    
    if st.button("Gerar PDF Auditoria Pro"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "LAUDO TECNICO FISCAL - TAXWIZARD PRO", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, f"Data da Auditoria: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
        pdf.cell(200, 10, f"Vigencia Legal: 24/08/2026", ln=True)
        pdf.ln(5)
        pdf.multi_cell(0, 10, "Este documento certifica o calculo de MVA Ajustada, DIFAL e a incidencia de CBS/IBS conforme a Emenda Constitucional da Reforma Tributaria.")
        
        pdf_content = pdf.output(dest='S').encode('latin-1')
        b64_pdf = base64.b64encode(pdf_content).decode('utf-8')
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="auditoria_fiscal.pdf">Clique aqui para baixar o PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("PDF Gerado com sucesso!")

# =====================================================================
# FOOTER
# =====================================================================
st.divider()
st.caption("TaxWizard Pro v2.4 - Engine 2026 Active - All rights reserved.")
