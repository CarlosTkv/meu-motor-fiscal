import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px  # CORREÇÃO: Importação necessária para o gráfico
import base64
from datetime import datetime
from fpdf import FPDF

# =====================================================================
# 1. SISTEMA DE DESIGN (MODERNO & EXECUTIVO)
# =====================================================================
st.set_page_config(page_title="TaxWizard Master 2026", layout="wide", page_icon="⚡")

def aplicar_design_premium():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #1e293b; }
        .stApp { background: #f8fafc; }

        /* Bento Grid Style */
        .bento-card {
            background: white; border-radius: 20px; padding: 25px;
            border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.02);
            transition: all 0.3s ease; margin-bottom: 20px;
        }
        .bento-card:hover { border-color: #6366f1; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }

        .label-tech { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
        .value-tech { font-size: 20px; font-weight: 800; color: #0f172a; }
        
        .justificativa-box { 
            font-size: 13px; line-height: 1.6; color: #334155; background: #f1f5f9; 
            padding: 15px; border-radius: 12px; border-left: 5px solid #6366f1; margin-top: 10px;
        }
        
        .status-badge {
            background: #e0e7ff; color: #4338ca; padding: 4px 12px; border-radius: 99px;
            font-size: 11px; font-weight: 700; border: 1px solid #c7d2fe;
        }
        </style>
    """, unsafe_allow_html=True)

aplicar_design_premium()

# =====================================================================
# 2. MOTOR DE INTELIGÊNCIA (BASES LEGAIS VIGENTES EM 2026)
# =====================================================================
class TaxIntelligence:
    # Simulação de Base de Dados Robusta
    NCM_DATABASE = {
        "85171300": {"desc": "Smartphone / Terminal Celular", "mva_orig": 40.0, "ipi": 15.0},
        "84713012": {"desc": "Notebook / Computador Portátil", "mva_orig": 35.0, "ipi": 0.0},
        "22030000": {"desc": "Cerveja de Malte", "mva_orig": 140.0, "ipi": 6.0},
    }
    
    LC116_DATABASE = {
        "7.02": {"desc": "Construção Civil / Obras", "aliq": 5.0, "retencao_local": True, "base": "Art. 3, III LC 116"},
        "1.05": {"desc": "Licenciamento de Software (SaaS)", "aliq": 2.0, "retencao_local": False, "base": "Art. 3, Caput LC 116"},
        "11.02": {"desc": "Vigilância e Segurança", "aliq": 5.0, "retencao_local": True, "base": "Art. 3, XVII LC 116"},
    }

# =====================================================================
# 3. LÓGICA DE CÁLCULO TÉCNICO (MVA, ST, DIFAL, CBS, IBS)
# =====================================================================
def executar_calculo_fiscal(d):
    v = d['valor']
    # REGRAS VIGENTES EM 24/08/2026 (Transição Reforma Tributária)
    cbs_2026 = v * 0.001 # Alíquota de teste 0,1%
    ibs_2026 = v * 0.001 # Alíquota de teste 0,1%
    
    aliq_inter = 12.0 if d['uf_o'] != d['uf_d'] else 18.0
    aliq_intra = 18.0 # Média Brasil em 2026

    if d['natureza'] == "PRODUTO":
        info = TaxIntelligence.NCM_DATABASE.get(d['codigo'], {"desc": "Produto Geral", "mva_orig": 50.0, "ipi": 0.0})
        v_ipi = v * (info['ipi'] / 100)
        
        # MVA Ajustada: [ (1+MVA_orig) * (1-AliqInter) / (1-AliqIntra) ] - 1
        mva_ajustada = ((1 + (info['mva_orig']/100)) * (1 - aliq_inter/100) / (1 - aliq_intra/100)) - 1
        mva_f = mva_ajustada if d['uf_o'] != d['uf_d'] else info['mva_orig']/100
        
        # Cálculo ST Base Dupla
        base_st = (v + v_ipi) * (1 + mva_f)
        icms_prop = (v + v_ipi) * (aliq_inter / 100)
        v_st = max(0, (base_st * (aliq_intra / 100)) - icms_prop)
        
        # Cálculo DIFAL (EC 87/15)
        v_difal = (v + v_ipi) * ((aliq_intra - aliq_inter) / 100)

        return {
            "nome": info['desc'], "ipi": v_ipi, "st": v_st, "difal": v_difal, "cbs": cbs_2026, "ibs": ibs_2026,
            "mva_f": mva_f, "base_st": base_st, "icms_p": icms_prop, "aliq_inter": aliq_inter, "aliq_intra": aliq_intra,
            "justificativa_icms": f"CST 010 aplicado. MVA Ajustada de {mva_f*100:.2f}% calculada sobre a base composta por Valor + IPI.",
            "justificativa_pis": "CST 01. Alíquota mantida durante a transição para a CBS conforme EC 132/23."
        }
    else:
        info = TaxIntelligence.LC116_DATABASE.get(d['codigo'], {"desc": "Serviço Especializado", "aliq": 5.0, "retencao_local": False})
        iss_retido = (d['cid_o'] != d['cid_p']) and info['retencao_local']
        iss_v = v * (info['aliq'] / 100)
        
        return {
            "nome": info['desc'], "iss_v": iss_v, "cbs": cbs_2026, "ibs": ibs_2026, "retencao": iss_retido,
            "local_recolhimento": d['cid_p'] if iss_retido else d['cid_o'],
            "justificativa_iss": f"ISS devido em {d['cid_p'] if iss_retido else d['cid_o']} conforme {info.get('base', 'LC 116/03')}.",
            "justificativa_pis": "Regime de transição. CBS a 0,1% compensável no PIS/COFINS."
        }

# =====================================================================
# 4. INTERFACE DO USUÁRIO (WIZARD)
# =====================================================================
with st.sidebar:
    st.markdown("<h2 style='color:#6366f1;'>TaxWizard Pro</h2>", unsafe_allow_html=True)
    st.markdown(f"<span class='status-badge'>VIGÊNCIA: 24/08/2026</span>", unsafe_allow_html=True)
    
    natureza = st.radio("Natureza da Operação", ["PRODUTO (ICMS/IPI)", "SERVIÇO (ISS)"])
    
    st.divider()
    cod_input = st.text_input("NCM ou Código Atividade (LC 116)", value="85171300" if "PRODUTO" in natureza else "7.02")
    v_nota = st.number_input("Valor da Nota (R$)", value=10000.0)
    
    st.markdown("### Geografia")
    uf_o = st.selectbox("UF Origem", ["SP", "RJ", "MG", "PR", "SC", "RS"])
    uf_d = st.selectbox("UF Destino", ["RJ", "SP", "MG", "PR", "SC", "RS"])
    
    if "SERVIÇO" in natureza:
        cid_o = st.text_input("Cidade Sede Empresa", "São Paulo")
        cid_d = st.text_input("Cidade Tomador (Cliente)", "Rio de Janeiro")
        cid_p = st.text_input("Cidade Local da Prestação", "Rio de Janeiro")
    else:
        cid_o = cid_d = cid_p = "N/A"

    st.divider()
    reg_o = st.selectbox("Regime Empresa", ["LUCRO REAL", "LUCRO PRESUMIDO", "SIMPLES NACIONAL"])
    reg_d = st.selectbox("Regime Destinatário", ["CONTRIBUINTE", "NÃO CONTRIBUINTE / PF"])
    
    btn_analisar = st.button("🚀 EXECUTAR AUDITORIA FISCAL", use_container_width=True)

# =====================================================================
# 5. RESULTADOS E DASHBOARDS
# =====================================================================
if btn_analisar:
    inputs = {
        'natureza': "PRODUTO" if "PRODUTO" in natureza else "SERVICO",
        'codigo': cod_input, 'valor': v_nota, 'uf_o': uf_o, 'uf_d': uf_d,
        'cid_o': cid_o, 'cid_p': cid_p, 'reg_o': reg_o, 'reg_d': reg_d
    }
    
    res = executar_calculo_fiscal(inputs)
    
    st.markdown(f"# {res['nome']}")
    st.markdown("---")

    tab_analise, tab_calculo, tab_relatorio = st.tabs(["📋 ANÁLISE TÉCNICA", "🧮 MEMÓRIA DE CÁLCULO", "📊 DASHBOARD & PDF"])

    with tab_analise:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="bento-card">', unsafe_allow_html=True)
            st.markdown('<p class="label-tech">Principal (ICMS / ISS)</p>', unsafe_allow_html=True)
            if inputs['natureza'] == "PRODUTO":
                st.write(f"**CFOP Sugerido:** {'6.403' if uf_o != uf_d else '5.403'}")
                st.write(f"**CST Sugerido:** 010")
                st.markdown(f'<div class="justificativa-box">{res["justificativa_icms"]}</div>', unsafe_allow_html=True)
            else:
                st.write(f"**Local Devido:** {res['local_recolhimento']}")
                st.write(f"**Retenção ISS:** {'SIM' if res['retencao'] else 'NÃO'}")
                st.markdown(f'<div class="justificativa-box">{res["justificativa_iss"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="bento-card">', unsafe_allow_html=True)
            st.markdown('<p class="label-tech">PIS / COFINS & CBS</p>', unsafe_allow_html=True)
            st.write(f"**CBS (Transição):** R$ {res['cbs']:,.2f}")
            st.write(f"**IBS (Transição):** R$ {res['ibs']:,.2f}")
            st.markdown(f'<div class="justificativa-box">{res["justificativa_pis"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_calculo:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        st.write("### Detalhamento Matemático")
        if inputs['natureza'] == "PRODUTO":
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Base de Cálculo ST", f"R$ {res['base_st']:,.2f}")
            cc2.metric("MVA Utilizada", f"{res['mva_f']*100:.2f}%")
            cc3.metric("Valor ICMS-ST", f"R$ {res['st']:,.2f}")
            
            if "NÃO CONTRIBUINTE" in reg_d:
                st.info(f"DIFAL Estimado (EC 87/15): R$ {res['difal']:,.2f}")
        else:
            st.metric("Total ISS a Recolher", f"R$ {res['iss_v']:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_relatorio:
        # Gráfico Corrigido
        st.subheader("Composição da Carga Tributária")
        
        # Preparação de dados para o gráfico
        labels = ['Imposto Principal', 'CBS (Reforma)', 'IBS (Reforma)']
        valores = [res.get('st', res.get('iss_v', 0)), res['cbs'], res['ibs']]
        
        fig = px.pie(names=labels, values=valores, hole=0.5, color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig, use_container_width=True)
        
        # PDF EXPORT
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "RELATORIO DE AUDITORIA FISCAL 2026", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, f"Objeto: {res['nome']} | Valor: R$ {v_nota:,.2f}", ln=True)
        pdf.cell(200, 10, f"Origem: {uf_o} | Destino: {uf_d}", ln=True)
        
        pdf_out = pdf.output(dest='S').encode('latin-1')
        b64_pdf = base64.b64encode(pdf_out).decode()
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="auditoria_fiscal_2026.pdf" style="display:inline-block; padding:12px 24px; background-color:#6366f1; color:white; text-decoration:none; border-radius:10px; font-weight:bold;">📥 BAIXAR RELATÓRIO COMPLETO (PDF)</a>'
        st.markdown(href, unsafe_allow_html=True)

else:
    st.markdown("""
        <div style='text-align:center; padding: 100px; opacity:0.3;'>
            <img src='https://cdn-icons-png.flaticon.com/512/1162/1162456.png' width='100'>
            <h2>Motor Fiscal Pronto para Auditoria</h2>
            <p>Selecione os parâmetros e clique em Executar.</p>
        </div>
    """, unsafe_allow_html=True)
