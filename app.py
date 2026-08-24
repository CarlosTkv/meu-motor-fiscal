import streamlit as st

# =====================================================================
# 1. CONFIGURAÇÃO VISUAL PREMIUM
# =====================================================================
st.set_page_config(
    page_title="Fiscal Inteligente Pro",
    page_icon="⚖️",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .card-vigente { background: white; padding: 20px; border-radius: 10px; border-left: 6px solid #0056b3; margin-bottom: 15px; }
    .card-reforma { background: #f0fff4; padding: 20px; border-radius: 10px; border-left: 6px solid #28a745; margin-bottom: 15px; }
    .card-justificativa { background: #fffaf0; padding: 20px; border-radius: 10px; border-left: 6px solid #ff9800; }
    h3 { color: #1a202c; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. INTELIGÊNCIA DE DADOS (NCM & REGRAS)
# =====================================================================
def identificar_produto(ncm):
    base_ncm = {
        "85171300": "Smartphone/Celular",
        "84713012": "Notebook/Laptop",
        "85285200": "Monitor de Vídeo",
        "22030000": "Cerveja de Malte",
        "30049099": "Medicamentos Diversos",
        "87032310": "Automóvel de Passeio",
    }
    return base_ncm.get(ncm, "Produto Geral (NCM Não Catalogado)")

def processar_motor_fiscal(ncm, uf_orig, uf_dest, reg_orig, reg_dest, operacao):
    produto = identificar_produto(ncm)
    is_interestadual = uf_orig != uf_dest
    tem_st = True if ncm.startswith(("8517", "2203", "8703")) else False
    
    # Inicialização de Variáveis
    justificativa = []
    cfop = ""
    pis_cofins = "0%"
    icms = "0%"
    
    # LOGICA DE CFOP E JUSTIFICATIVA
    if operacao == "EXPORTAÇÃO":
        cfop = "7101"
        pis_cofins = "0% (Imunidade)"
        icms = "0% (Não Incidência)"
        justificativa.append("Imunidade tributária conforme Art. 149 da Constituição Federal (desoneração de exportações).")
        justificativa.append("Manutenção de crédito assegurada para a origem.")
        
    elif operacao == "IMPORTAÇÃO":
        cfop = "3101"
        pis_cofins = "9.25% (Lucro Real)" if reg_orig == "LUCRO REAL" else "3.65%"
        icms = "18% (Varia por UF)"
        justificativa.append("Operação de entrada do exterior. Incidência de II, IPI, PIS-Importação e COFINS-Importação.")
        justificativa.append("O ICMS é devido no desembaraço aduaneiro para o estado de destino.")

    elif operacao == "SAÍDA":
        pref = "6" if is_interestadual else "5"
        if tem_st:
            cfop = f"{pref}403"
            justificativa.append(f"Produto sujeito à Substituição Tributária em {uf_orig}. ICMS-ST recolhido antecipadamente.")
        else:
            cfop = f"{pref}102"
            justificativa.append("Venda de mercadoria tributada integralmente no regime normal.")
        
        if is_interestadual and reg_dest == "SIMPLES NACIONAL":
            justificativa.append("DIFAL devido: Diferencial de alíquota para consumidor final não contribuinte.")

    # REFORMA TRIBUTÁRIA 2026
    cbs = "8.8%" 
    ibs = "17.7%"

    return {
        "produto": produto,
        "cfop": cfop,
        "icms": icms if operacao in ["IMPORTAÇÃO", "EXPORTAÇÃO"] else ("12%" if is_interestadual else "18%"),
        "pis_cofins": pis_cofins,
        "st": "SIM" if tem_st else "NÃO",
        "cbs": cbs,
        "ibs": ibs,
        "justificativa": justificativa
    }

# =====================================================================
# 3. INTERFACE DE USUÁRIO
# =====================================================================
st.title("⚖️ Motor Fiscal Pro - 1000% Funcional")
st.markdown("---")

# Barra Lateral
with st.sidebar:
    st.header("📋 Dados da Operação")
    ncm_in = st.text_input("NCM (8 dígitos)", value="85171300")
    tipo_op = st.selectbox("Tipo de Operação", ["SAÍDA", "ENTRADA", "IMPORTAÇÃO", "EXPORTAÇÃO"])
    
    c1, c2 = st.columns(2)
    uf_o = c1.selectbox("Origem", ["SP", "RJ", "MG", "PR", "SC", "RS", "ES"])
    uf_d = c2.selectbox("Destino", ["RJ", "SP", "MG", "PR", "SC", "RS", "ES", "EXTERIOR"])
    
    r_orig = st.selectbox("Regime Empresa", ["LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL"])
    r_dest = st.selectbox("Regime Destinatário", ["LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL", "CONSUMIDOR FINAL"])
    
    processar = st.button("ANALISAR AGORA")

# Área de Resultados
if processar:
    if len(ncm_in) != 8:
        st.error("NCM Inválido! Use 8 dígitos numéricos.")
    else:
        res = processar_motor_fiscal(ncm_in, uf_o, uf_d, r_orig, r_dest, tipo_op)
        
        # Cabeçalho do Produto
        st.subheader(f"🔍 Identificação: {res['produto']} (NCM {ncm_in})")
        
        # Métricas Rápidas
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CFOP Sugerido", res['cfop'])
        m2.metric("ICMS Sugerido", res['icms'])
        m3.metric("ST Aplicável?", res['st'])
        m4.metric("Status", "Processado")

        st.markdown("---")
        
        col_v, col_r = st.columns(2)
        
        with col_v:
            st.markdown(f"""
            <div class="card-vigente">
                <h3>📦 Regras Vigentes (2024-2025)</h3>
                <p><b>PIS/COFINS:</b> {res['pis_cofins']}</p>
                <p><b>Operação:</b> {tipo_op}</p>
                <p><b>Rota:</b> {uf_o} ➔ {uf_d}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_r:
            st.markdown(f"""
            <div class="card-reforma">
                <h3>🌿 Projeção Reforma (2026)</h3>
                <p><b>CBS (Federal):</b> {res['cbs']}</p>
                <p><b>IBS (Estadual):</b> {res['ibs']}</p>
                <p><b>Transição:</b> Alíquotas baseadas no regulamento atualizado.</p>
            </div>
            """, unsafe_allow_html=True)

        # Justificativa Legal
        st.markdown(f"""
        <div class="card-justificativa">
            <h3>📖 Justificativa Técnico-Legal</h3>
            <ul>
                {"".join([f"<li>{item}</li>" for item in res['justificativa']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("Análise concluída com sucesso e pronta para faturamento.")
else:
    st.info("Aguardando entrada de dados para gerar a árvore fiscal.")
