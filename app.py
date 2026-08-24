import streamlit as st

# =====================================================================
# 1. CONFIGURAÇÃO DE DESIGN (LAYOUT DELICADO & PREMIUM)
# =====================================================================
st.set_page_config(page_title="Fiscal Pro | Intelligence", page_icon="❄️", layout="wide")

# CSS para tornar a interface mais limpa e moderna
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #444; }
    .main { background-color: #fdfdfd; }
    div.stButton > button {
        background-color: #000; color: white; border-radius: 8px; border: none;
        padding: 10px 20px; transition: 0.3s; width: 100%;
    }
    div.stButton > button:hover { background-color: #333; color: white; }
    .card {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #f0f0f0; margin-bottom: 20px;
    }
    .tag {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 12px; font-weight: 600; margin-bottom: 10px;
    }
    .tag-vigente { background: #e3f2fd; color: #1976d2; }
    .tag-reforma { background: #e8f5e9; color: #2e7d32; }
    .tag-resp { background: #fff3e0; color: #e65100; }
    h1, h2, h3 { font-weight: 600; letter-spacing: -0.5px; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. LOGICA TRIBUTÁRIA E RESPONSABILIDADES
# =====================================================================
def identificar_produto(ncm):
    base = {
        "85171300": "Smartphone", "84713012": "Notebook", "85285200": "Monitor",
        "22030000": "Cerveja", "30049099": "Medicamento", "87032310": "Veículo"
    }
    return base.get(ncm, "Produto Não Especificado")

def analisar_fiscal(ncm, uf_o, uf_d, reg_o, reg_d, operacao):
    produto = identificar_produto(ncm)
    is_interestadual = uf_o != uf_d
    tem_st = True if ncm.startswith(("8517", "2203", "8703")) else False
    is_nao_contribuinte = "NÃO CONTRIBUINTE" in reg_d
    
    # Responsabilidades
    resp_st = "NÃO APLICÁVEL"
    resp_difal = "NÃO APLICÁVEL"
    
    # Regra de ST
    if tem_st:
        resp_st = "REMETENTE (SUBSTITUTO)" if operacao == "SAÍDA" else "DESTINATÁRIO (ANTECIPAÇÃO)"
        
    # Regra de DIFAL (EC 87/2015)
    if is_interestadual and operacao == "SAÍDA":
        if is_nao_contribuinte:
            resp_difal = "REMETENTE (ESTADO DE ORIGEM)"
        else:
            resp_difal = "DESTINATÁRIO (ESTADO DE DESTINO)"

    # CFOP
    if operacao == "EXPORTAÇÃO": cfop = "7101"
    elif operacao == "IMPORTAÇÃO": cfop = "3101"
    else:
        pref = "6" if is_interestadual else "5"
        cfop = f"{pref}403" if tem_st else f"{pref}102"

    # Justificativas
    just = []
    if operacao == "EXPORTAÇÃO": just.append("Imunidade conforme Art. 149 da CF/88.")
    if is_nao_contribuinte: just.append("Destinatário final não contribuinte: Incidência de DIFAL total para a origem (EC 87/15).")
    if tem_st: just.append(f"Produto na lista de ST do convênio ICMS vigente para {ncm}.")

    return {
        "produto": produto, "cfop": cfop, "st": "SIM" if tem_st else "NÃO",
        "resp_st": resp_st, "resp_difal": resp_difal,
        "cbs": "8.8%", "ibs": "17.7%", "just": just
    }

# =====================================================================
# 3. INTERFACE (UI)
# =====================================================================
st.title("❄️ Fiscal Intelligence Pro")
st.write("Análise tributária delicada para operações complexas.")

with st.sidebar:
    st.markdown("### 🛠 Configuração")
    ncm_in = st.text_input("NCM do Produto", "85171300")
    tipo_op = st.selectbox("Operação", ["SAÍDA", "ENTRADA", "IMPORTAÇÃO", "EXPORTAÇÃO"])
    
    st.divider()
    c1, c2 = st.columns(2)
    uf_o = c1.selectbox("UF Origem", ["SP", "RJ", "MG", "PR", "SC", "RS"])
    uf_d = c2.selectbox("UF Destino", ["RJ", "SP", "MG", "PR", "SC", "RS", "EXTERIOR"])
    
    reg_o = st.selectbox("Regime Empresa", ["LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL"])
    reg_d = st.selectbox("Regime Destinatário", [
        "LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL", 
        "NÃO CONTRIBUINTE (PESSOA FÍSICA)", "NÃO CONTRIBUINTE (PESSOA JURÍDICA)"
    ])
    
    analisar = st.button("GERAR ANÁLISE")

if analisar:
    res = analisar_fiscal(ncm_in, uf_o, uf_d, reg_o, reg_d, tipo_op)
    
    # Header do Resultado
    st.markdown(f"## {res['produto']} <span style='font-size:18px; color:gray;'>(NCM {ncm_in})</span>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CFOP SUGERIDO", res['cfop'])
    with col2:
        st.metric("ST APLICÁVEL", res['st'])
    with col3:
        st.metric("PROJEÇÃO IVA 2026", f"{res['cbs']} + {res['ibs']}")

    st.divider()

    # Cards de Responsabilidade e Detalhes
    c_vig, c_resp = st.columns(2)
    
    with c_vig:
        st.markdown(f"""
        <div class="card">
            <span class="tag tag-vigente">REGRAS VIGENTES</span>
            <h3>Operação de {tipo_op}</h3>
            <p><b>Rota:</b> {uf_o} para {uf_d}</p>
            <p><b>Regime Destino:</b> {reg_d}</p>
            <hr style="border:0; border-top:1px solid #eee">
            <p style="font-size: 14px; color: #666;">Dados processados com base no RICMS do Estado de {uf_o}.</p>
        </div>
        """, unsafe_allow_html=True)

    with c_resp:
        st.markdown(f"""
        <div class="card">
            <span class="tag tag-resp">RESPONSABILIDADES</span>
            <h3>Quem recolhe as guias?</h3>
            <p><b>Responsável ST:</b> {res['resp_st']}</p>
            <p><b>Responsável DIFAL:</b> {res['resp_difal']}</p>
            <hr style="border:0; border-top:1px solid #eee">
            <p style="font-size: 14px; color: #666;">Atenção: Verifique se há protocolo de ST entre {uf_o} e {uf_d}.</p>
        </div>
        """, unsafe_allow_html=True)

    # Justificativa Técnica
    st.markdown(f"""
    <div class="card">
        <span class="tag tag-reforma">JUSTIFICATIVA TÉCNICO-LEGAL</span>
        <h3>Fundamentação</h3>
        <ul style="color: #555; line-height: 1.8;">
            {"".join([f"<li>{item}</li>" for item in res['just']])}
            <li>CBS e IBS calculados com alíquotas padrão de transição da Reforma Tributária (EC 132).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("Nota: Este sistema é um simulador. Sempre consulte seu contador antes de emitir a nota fiscal.")

else:
    st.markdown("""
        <div style="text-align:center; margin-top: 100px; color: #bbb;">
            <p>Preencha os parâmetros na barra lateral para gerar a inteligência fiscal.</p>
        </div>
    """, unsafe_allow_html=True)
