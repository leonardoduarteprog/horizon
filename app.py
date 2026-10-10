import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA (MOBILE APP CANVAS) ---
st.set_page_config(
    page_title="Horizon — Private Banking",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS BANCO DIGITAL (ESTILO NUBANK / REVOLUT / APPLE WALLET) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #08090d !important;
        color: #f8fafc;
    }

    /* Trava de formato mobile centralizado (App Canvas no smartphone ou desktop) */
    .block-container {
        max-width: 480px !important;
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: 0 auto !important;
    }

    /* Oculta barras padrão de site do Streamlit */
    #MainMenu, header, footer, div[data-testid="stToolbar"], section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Topo do App (Header de Banco) */
    .bank-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0 16px 0;
    }
    .user-profile {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .avatar-circle {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: linear-gradient(135deg, #10b981, #047857);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 15px;
        color: #ffffff;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
    }
    .greeting-text {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        line-height: 1.2;
    }
    .account-badge {
        font-size: 11px;
        color: #10b981;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    /* Cartão Principal de Patrimônio (Cartão Black / Ultravioleta) */
    .hero-card {
        background: linear-gradient(145deg, #151822, #0d0f16);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 22px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
    }
    .hero-label {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .hero-balance {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin: 6px 0;
        letter-spacing: -0.5px;
    }
    .hero-subtext {
        font-size: 12px;
        color: #10b981;
        font-weight: 600;
    }

    /* Cards de Caixinhas / Metas */
    .goal-card {
        background: #11141d;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 12px;
    }
    .goal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .goal-title-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .goal-icon-circle {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: #1a1f2c;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .goal-title {
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    .goal-values {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #94a3b8;
        margin-top: 8px;
    }
    .goal-highlight {
        color: #ffffff;
        font-weight: 700;
    }
    .goal-footer {
        margin-top: 6px;
        font-size: 11px;
        color: #38bdf8;
        font-weight: 500;
    }

    /* Abas em Pílula (Segmented Control de App) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #11141d;
        padding: 4px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #94a3b8;
        font-size: 12px;
        font-weight: 600;
        padding: 7px 12px;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e2433 !important;
        color: #ffffff !important;
    }

    /* Barra de Progresso Estilo Neobank */
    div[data-testid="stProgress"] > div > div > div > div {
        background: linear-gradient(90deg, #10b981, #38bdf8) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stProgress"] > div > div {
        background-color: #1e2330 !important;
        border-radius: 8px !important;
        height: 7px !important;
    }

    /* Botões estilo App */
    button[kind="primary"] {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 10px 18px !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.25) !important;
    }
    button[kind="secondary"] {
        background-color: #141722 !important;
        border: 1px solid #1e2330 !important;
        color: #cbd5e1 !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS (SQLite) ---
conn = sqlite3.connect("horizon.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS configuracoes (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    patrimonio_atual REAL DEFAULT 0.0,
    aporte_mensal REAL DEFAULT 1500.0,
    renda_mensal REAL DEFAULT 8000.0,
    nome_usuario TEXT DEFAULT 'Leonardo'
)
""")
cursor.execute("INSERT OR IGNORE INTO configuracoes (id, patrimonio_atual, aporte_mensal, renda_mensal, nome_usuario) VALUES (1, 0.0, 1500.0, 8000.0, 'Leonardo')")

cursor.execute("""
CREATE TABLE IF NOT EXISTS metas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    categoria TEXT,
    valor_alvo REAL,
    valor_acumulado REAL DEFAULT 0.0,
    prioridade TEXT DEFAULT 'Média'
)
""")
conn.commit()

# Session State para o Olho Mágico (Ocultar/Exibir Saldo)
if "mostrar_saldo" not in st.session_state:
    st.session_state.mostrar_saldo = True

def alternar_visibilidade():
    st.session_state.mostrar_saldo = not st.session_state.mostrar_saldo

# Recuperação de dados
cursor.execute("SELECT patrimonio_atual, aporte_mensal, renda_mensal, nome_usuario FROM configuracoes WHERE id = 1")
cfg_row = cursor.fetchone()
patrimonio_base = cfg_row[0] if cfg_row else 0.0
aporte_base = cfg_row[1] if cfg_row else 1500.0
renda_base = cfg_row[2] if cfg_row else 8000.0
nome_user = cfg_row[3] if cfg_row else "Leonardo"

df_metas = pd.read_sql_query("SELECT id, titulo, categoria, valor_alvo, valor_acumulado, prioridade FROM metas ORDER BY id ASC", conn)
total_acumulado_metas = df_metas["valor_acumulado"].sum() if not df_metas.empty else 0.0
capital_total = patrimonio_base + total_acumulado_metas

# Formatação condicional ao olho mágico
def fmt_dinheiro(valor):
    if st.session_state.mostrar_saldo:
        return f"R$ {valor:,.2f}"
    return "••••••••"

# =========================================================
# TOPO DO APLICATIVO (HEADER ESTILO NUBANK)
# =========================================================
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown(f"""
    <div class="user-profile">
        <div class="avatar-circle">{nome_user[:2].upper()}</div>
        <div>
            <div class="greeting-text">Olá, {nome_user} 👋</div>
            <div class="account-badge">Horizon Private</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    icone_olho = "👁️" if st.session_state.mostrar_saldo else "🙈"
    st.button(icone_olho, on_click=alternar_visibilidade, help="Ocultar ou mostrar valores")

# =========================================================
# CARTÃO HERO DE PATRIMÔNIO (BLACK CARD)
# =========================================================
st.markdown(f"""
<div class="hero-card">
    <div class="hero-label">Patrimônio Estratégico</div>
    <div class="hero-balance">{fmt_dinheiro(capital_total)}</div>
    <div class="hero-subtext">⚡ Aporte mensal: {fmt_dinheiro(aporte_base)}/mês</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# NAVEGAÇÃO PRINCIPAL (ABAS DE APP NATIVO)
# =========================================================
tab_metas, tab_timeline, tab_tco, tab_ajustes = st.tabs([
    "🎯 Caixinhas",
    "📈 Evolução",
    "🚗 Custo de Posse",
    "⚙️ Ajustes"
])

# ---------------------------------------------------------
# ABA 1: MINHAS CAIXINHAS & METAS (ESTILO NUBANK)
# ---------------------------------------------------------
with tab_metas:
    st.markdown("##### Minhas Metas & Objetivos")

    if not df_metas.empty:
        for _, row in df_metas.iterrows():
            m_id = row["id"]
            val_alvo = row["valor_alvo"]
            val_acum = row["valor_acumulado"]
            pct = min(1.0, val_acum / val_alvo) if val_alvo > 0 else 0.0
            falta = max(0.0, val_alvo - val_acum)

            # Previsão humanizada de data
            meses_faltam = max(1, int(falta / aporte_base)) if aporte_base > 0 else 0
            ano_alvo = datetime.now().year + (datetime.now().month + meses_faltam - 1) // 12
            mes_alvo = (datetime.now().month + meses_faltam - 1) % 12 + 1
            meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            previsao_str = f"{meses_pt[mes_alvo - 1]} de {ano_alvo}"

            st.markdown(f"""
            <div class="goal-card">
                <div class="goal-header">
                    <div class="goal-title-wrap">
                        <div class="goal-icon-circle">{row['categoria'].split()[0]}</div>
                        <div>
                            <div class="goal-title">{row['titulo']}</div>
                            <div style="font-size: 11px; color: #94a3b8;">Prioridade {row['prioridade']}</div>
                        </div>
                    </div>
                    <span style="font-size: 12px; font-weight: 700; color: #10b981;">{pct * 100:.0f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Barra de progresso nativa estilizada
            st.progress(pct)

            col_v1, col_v2 = st.columns(2)
            col_v1.caption(f"Guardado: **{fmt_dinheiro(val_acum)}**")
            col_v2.caption(f"Meta: **{fmt_dinheiro(val_alvo)}**")

            if falta == 0:
                st.success("🎉 Meta Concluída com Sucesso!")
            else:
                st.caption(f"⏳ Previsão de conquista: **{previsao_str}** (~{meses_faltam} meses)")

            # Aporte rápido direto na meta
            with st.expander(f"➕ Guardar dinheiro em '{row['titulo']}'"):
                c_ap1, c_ap2 = st.columns([2, 1])
                val_add = c_ap1.number_input("Valor a adicionar (R$)", min_value=10.0, value=200.0, step=50.0, key=f"inp_{m_id}")
                if c_ap2.button("Guardar", key=f"btn_add_{m_id}", type="primary"):
                    novo_val = val_acum + val_add
                    cursor.execute("UPDATE metas SET valor_acumulado = ? WHERE id = ?", (novo_val, m_id))
                    conn.commit()
                    st.rerun()

            st.write("")
    else:
        st.info("Você ainda não tem caixinhas ativas. Crie sua primeira meta logo abaixo!")

    st.divider()

    # FORMULÁRIO DE NOVA META ESTILO APP
    with st.expander("✨ Criar Nova Meta / Caixinha", expanded=df_metas.empty):
        with st.form("form_nova_meta_app", clear_on_submit=True):
            n_titulo = st.text_input("Qual é o seu objetivo?", placeholder="Ex: Entrada do HB20, Reserva, Viagem")
            n_cat = st.selectbox("Categoria", ["🚗 Veículo", "🛡️ Reserva", "✈️ Viagem", "🏡 Imóvel", "💻 Tech", "🎯 Outro"])
            c_val1, c_val2 = st.columns(2)
            n_alvo = c_val1.number_input("Valor Total (R$)", min_value=100.0, value=30000.0, step=500.0)
            n_ini = c_val2.number_input("Já tenho (R$)", min_value=0.0, value=0.0, step=100.0)
            n_prio = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])

            if st.form_submit_button("Criar Caixinha", type="primary"):
                if n_titulo.strip():
                    cursor.execute("""
                        INSERT INTO metas (titulo, categoria, valor_alvo, valor_acumulado, prioridade)
                        VALUES (?, ?, ?, ?, ?)
                    """, (n_titulo.strip(), n_cat, n_alvo, n_ini, n_prio))
                    conn.commit()
                    st.success("Caixinha criada com sucesso!")
                    st.rerun()
                else:
                    st.warning("Dê um nome para a sua meta.")

# ---------------------------------------------------------
# ABA 2: EVOLUÇÃO PATRIMONIAL (GRÁFICO FLUIDO DE BANCO)
# ---------------------------------------------------------
with tab_timeline:
    st.markdown("##### Projeção de Crescimento")
    st.caption("Evolução do seu patrimônio mantendo o aporte mensal:")

    meses_proj = list(range(1, 37))
    datas_proj = []
    hoje = datetime.now()
    curva_patrimonio = []

    acum_temp = capital_total
    for m in meses_proj:
        acum_temp += aporte_base
        curva_patrimonio.append(acum_temp)
        mes_f = (hoje.month + m - 1) % 12 + 1
        ano_f = hoje.year + (hoje.month + m - 1) // 12
        datas_proj.append(f"{mes_f:02d}/{str(ano_f)[2:]}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=datas_proj,
        y=curva_patrimonio,
        mode="lines",
        line=dict(color="#10b981", width=3, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.08)",
        hoverinfo="y+x"
    ))

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#08090d",
        paper_bgcolor="#08090d",
        height=280,
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(showgrid=False, dtick=4),
        yaxis=dict(showgrid=True, gridcolor="#161a24")
    )
    st.plotly_chart(fig, use_container_width=True)

    patr_1ano = curva_patrimonio[11]
    patr_3anos = curva_patrimonio[35]

    c_ev1, c_ev2 = st.columns(2)
    c_ev1.metric("Em 12 Meses", fmt_dinheiro(patr_1ano))
    c_ev2.metric("Em 36 Meses", fmt_dinheiro(patr_3anos))

# ---------------------------------------------------------
# ABA 3: SIMULADOR DE CUSTO DE POSSE (TCO)
# ---------------------------------------------------------
with tab_tco:
    st.markdown("##### Simulador de Posse de Bens")
    st.caption("Descubra o custo real para manter um carro ou bem por mês:")

    with st.form("form_tco_app"):
        bem_nome = st.text_input("Modelo ou Bem", value="Hyundai HB20")
        b_preco = st.number_input("Valor de Compra (R$)", min_value=1000.0, value=65000.0, step=1000.0)
        b_parc = st.number_input("Parcela (R$/mês - 0 se for à vista)", min_value=0.0, value=0.0, step=100.0)
        
        c_t1, c_t2 = st.columns(2)
        b_seguro = c_t1.number_input("Seguro Anual (R$)", min_value=0.0, value=3000.0, step=100.0)
        b_ipva = c_t2.number_input("IPVA Anual (R$)", min_value=0.0, value=2500.0, step=100.0)
        b_comb = c_t1.number_input("Combustível/Mês (R$)", min_value=0.0, value=500.0, step=50.0)
        b_manut = c_t2.number_input("Manutenção/Mês (R$)", min_value=0.0, value=250.0, step=50.0)

        st.form_submit_button("Analisar Viabilidade", type="primary")

    custo_manut_mes = (b_seguro / 12) + (b_ipva / 12) + b_comb + b_manut
    custo_total_mes = custo_manut_mes + b_parc
    impacto_renda = (custo_total_mes / renda_base) * 100 if renda_base > 0 else 0.0

    st.markdown("##### Veredito de Viabilidade")
    col_t1, col_t2 = st.columns(2)
    col_t1.metric("Custo Mensal Real", f"R$ {custo_total_mes:,.2f}")
    col_t2.metric("Peso no Salário", f"{impacto_renda:.1f}%")

    if impacto_renda <= 15:
        st.success("🟢 **Aprovado:** Custo totalmente saudável para o seu padrão de renda.")
    elif impacto_renda <= 25:
        st.warning("🟡 **Moderado:** Cabe no orçamento, mas exigirá atenção nos gastos livres.")
    else:
        st.error("🔴 **Pesado:** Este bem consumirá uma fatia muito grande da sua renda mensal.")

# ---------------------------------------------------------
# ABA 4: AJUSTES DO PERFIL & PARÂMETROS
# ---------------------------------------------------------
with tab_ajustes:
    st.markdown("##### Configurações do seu Perfil")

    with st.form("form_perfil_app"):
        novo_nome = st.text_input("Seu Primeiro Nome", value=nome_user)
        nova_renda = st.number_input("Sua Renda Líquida Mensal (R$)", min_value=0.0, value=float(renda_base), step=100.0)
        novo_aporte = st.number_input("Sua Capacidade de Aporte Mensal (R$)", min_value=50.0, value=float(aporte_base), step=50.0)
        novo_patr = st.number_input("Patrimônio Base Não Alocado (R$)", min_value=0.0, value=float(patrimonio_base), step=100.0)

        if st.form_submit_button("Salvar Perfil", type="primary"):
            cursor.execute("""
                UPDATE configuracoes SET patrimonio_atual = ?, aporte_mensal = ?, renda_mensal = ?, nome_usuario = ? WHERE id = 1
            """, (novo_patr, novo_aporte, nova_renda, novo_nome.strip()))
            conn.commit()
            st.success("Dados atualizados com sucesso!")
            st.rerun()

    if not df_metas.empty:
        st.divider()
        st.markdown("##### Excluir Caixinhas")
        opcoes_del = {f"{r['titulo']} (R$ {r['valor_alvo']:,.0f})": int(r['id']) for _, r in df_metas.iterrows()}
        meta_del = st.selectbox("Selecione para remover:", list(opcoes_del.keys()))
        if st.button("Excluir Meta", type="secondary"):
            cursor.execute("DELETE FROM metas WHERE id = ?", (opcoes_del[meta_del],))
            conn.commit()
            st.success("Meta excluída.")
            st.rerun()
