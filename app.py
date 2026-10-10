import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Horizon OS — Simulador Estratégico",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BANCO DE DADOS (SQLite) ---
conn = sqlite3.connect("horizon.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS configuracoes (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    patrimonio_atual REAL DEFAULT 0.0,
    aporte_mensal REAL DEFAULT 1500.0,
    renda_mensal REAL DEFAULT 8000.0
)
""")
cursor.execute("INSERT OR IGNORE INTO configuracoes (id, patrimonio_atual, aporte_mensal, renda_mensal) VALUES (1, 0.0, 1500.0, 8000.0)")

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS simulacoes_bens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_bem TEXT,
    tipo_bem TEXT,
    valor_aquisicao REAL,
    parcela_mensal REAL DEFAULT 0.0,
    seguro_anual REAL DEFAULT 0.0,
    impostos_anual REAL DEFAULT 0.0,
    manutencao_mensal REAL DEFAULT 0.0,
    consumo_mensal REAL DEFAULT 0.0
)
""")
conn.commit()

# --- RECUPERAÇÃO DE CONFIGURAÇÕES ---
cursor.execute("SELECT patrimonio_atual, aporte_mensal, renda_mensal FROM configuracoes WHERE id = 1")
cfg_row = cursor.fetchone()
patrimonio_base = cfg_row[0] if cfg_row else 0.0
aporte_base = cfg_row[1] if cfg_row else 1500.0
renda_base = cfg_row[2] if cfg_row else 8000.0

df_metas = pd.read_sql_query("SELECT id, titulo, categoria, valor_alvo, valor_acumulado, prioridade FROM metas ORDER BY id ASC", conn)

# --- BARRA LATERAL (NAVEGAÇÃO) ---
st.sidebar.title("🌌 Horizon OS")
st.sidebar.caption("Cockpit Financeiro Estratégico")

menu = st.sidebar.radio(
    "Módulos:",
    [
        "🚀 Cockpit & Linha do Tempo",
        "🚗 Simulador de Custo de Posse (TCO)",
        "🔮 Simulador de Cenários de Renda",
        "🎯 Gestão de Metas & Parâmetros"
    ]
)

# =========================================================
# MÓDULO 1: COCKPIT & LINHA DO TEMPO (TELA INICIAL)
# =========================================================
if menu == "🚀 Cockpit & Linha do Tempo":
    st.title("Cockpit Estratégico & Linha do Tempo")
    st.caption("Visão macro de médio e longo prazo do seu patrimônio e objetivos.")

    # 1. CARDS DE TOPO NATIVOS
    total_alvo_metas = df_metas["valor_alvo"].sum() if not df_metas.empty else 0.0
    total_acumulado_metas = df_metas["valor_acumulado"].sum() if not df_metas.empty else 0.0
    capital_total_disponivel = patrimonio_base + total_acumulado_metas

    proxima_meta_nome = "Nenhuma meta cadastrada"
    prazo_proxima = "-"
    if not df_metas.empty:
        # Pega a meta com maior progresso que ainda não foi concluída
        pendentes = df_metas[df_metas["valor_acumulado"] < df_metas["valor_alvo"]].copy()
        if not pendentes.empty:
            pendentes["falta"] = pendentes["valor_alvo"] - pendentes["valor_acumulado"]
            primeira = pendentes.sort_values(by="falta").iloc[0]
            proxima_meta_nome = primeira["titulo"]
            meses_prazo = max(1, int(primeira["falta"] / aporte_base)) if aporte_base > 0 else 0
            prazo_proxima = f"~{meses_prazo} meses"
        else:
            proxima_meta_nome = "Todas as metas atingidas! 🎉"
            prazo_proxima = "Concluído"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Patrimônio Base Alocado", f"R$ {capital_total_disponivel:,.2f}")
    c2.metric("Aporte Mensal Atual", f"R$ {aporte_base:,.2f}/mês")
    c3.metric("Próxima Meta no Radar", proxima_meta_nome, prazo_proxima)
    c4.metric("Total em Metas Planejadas", f"R$ {total_alvo_metas:,.2f}")

    st.write("")

    # 2. GRÁFICO DA LINHA DO TEMPO (HORIZON TIMELINE - 36 MESES)
    st.subheader("📈 Linha do Tempo do Patrimônio (Próximos 3 Anos)")
    
    meses_proj = list(range(1, 37))
    datas_proj = []
    hoje = datetime.now()
    curva_patrimonio = []
    
    acum_temp = capital_total_disponivel
    for m in meses_proj:
        acum_temp += aporte_base
        curva_patrimonio.append(acum_temp)
        # Calcula mês e ano futuro
        ano_f = hoje.year + (hoje.month + m - 1) // 12
        mes_f = (hoje.month + m - 1) % 12 + 1
        datas_proj.append(f"{mes_f:02d}/{ano_f}")

    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Scatter(
        x=datas_proj,
        y=curva_patrimonio,
        mode="lines",
        name="Patrimônio Projetado",
        line=dict(color="#10b981", width=3)
    ))

    # Plota as metas como linhas horizontais de conquista
    if not df_metas.empty:
        for _, rm in df_metas.iterrows():
            fig_timeline.add_hline(
                y=rm["valor_alvo"],
                line_dash="dot",
                line_color="#38bdf8",
                annotation_text=f"{rm['titulo']} (R$ {rm['valor_alvo']:,.0f})",
                annotation_position="bottom right"
            )

    fig_timeline.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(title="Linha do Tempo (Mês/Ano)", dtick=3),
        yaxis=dict(title="Reais (R$)", gridcolor="#1e2433"),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.write("")

    # 3. LISTA DE METAS ATIVAS
    st.subheader("🎯 Metas e Objetivos em Andamento")
    if not df_metas.empty:
        for _, row in df_metas.iterrows():
            with st.container(border=True):
                col_m1, col_m2 = st.columns([2.5, 1])
                val_alvo = row["valor_alvo"]
                val_acum = row["valor_acumulado"]
                pct = min(1.0, val_acum / val_alvo) if val_alvo > 0 else 0.0
                falta = max(0.0, val_alvo - val_acum)
                meses_estimados = int(falta / aporte_base) if aporte_base > 0 else 0

                col_m1.markdown(f"#### {row['categoria']} {row['titulo']}")
                col_m1.progress(pct)
                col_m1.caption(f"Progresso: **{pct * 100:.1f}%** • Guardado: **R$ {val_acum:,.2f}** de **R$ {val_alvo:,.2f}**")

                col_m2.metric("Falta Guardar", f"R$ {falta:,.2f}")
                if falta == 0:
                    col_m2.success("🎉 Meta Concluída!")
                else:
                    col_m2.info(f"⏳ Conclusão em ~**{meses_estimados} meses**")
    else:
        st.info("Nenhuma meta cadastrada ainda. Vá na aba '🎯 Gestão de Metas & Parâmetros' para registrar seus objetivos!")

# =========================================================
# MÓDULO 2: SIMULADOR DE CUSTO REAL DE POSSE (TCO)
# =========================================================
elif menu == "🚗 Simulador de Custo de Posse (TCO)":
    st.title("Simulador de Custo Real de Posse (TCO)")
    st.caption("Descubra quanto a compra e a manutenção de um bem (carro, moto, imóvel) vão custar todo mês no seu bolso.")

    with st.form("form_simular_bem"):
        c_b1, c_b2 = st.columns(2)
        with c_b1:
            nome_bem = st.text_input("Nome do Bem / Modelo", placeholder="Ex: Hyundai HB20 Semi-novo, Corolla, Moto")
            tipo_bem = st.selectbox("Tipo de Bem", ["🚗 Veículo / Carro", "🏍️ Moto", "🏡 Imóvel", "💻 Equipamento"])
            val_compra = st.number_input("Valor de Compra (R$)", min_value=1000.0, value=65000.0, step=1000.0)
            val_parcela = st.number_input("Parcela do Financiamento / Consórcio (R$/mês - 0 se à vista)", min_value=0.0, value=0.0, step=100.0)
        with c_b2:
            seguro_ano = st.number_input("Seguro Anual Estimado (R$)", min_value=0.0, value=3000.0, step=100.0)
            imposto_ano = st.number_input("IPVA / Impostos Anuais (R$)", min_value=0.0, value=2500.0, step=100.0)
            manut_mes = st.number_input("Manutenção Preventiva / Revisão Média (R$/mês)", min_value=0.0, value=250.0, step=50.0)
            consumo_mes = st.number_input("Combustível / Consumo Médio (R$/mês)", min_value=0.0, value=500.0, step=50.0)

        calcular = st.form_submit_button("Calcular Custo Mensal Real", type="primary")

    custo_recorrente_mes = (seguro_ano / 12) + (imposto_ano / 12) + manut_mes + consumo_mes
    custo_total_mes = custo_recorrente_mes + val_parcela
    peso_na_renda = (custo_total_mes / renda_base) * 100 if renda_base > 0 else 0.0

    st.write("")
    st.subheader("📊 Diagnóstico Financeiro de Posse")

    cd1, cd2, cd3 = st.columns(3)
    cd1.metric("Custo Total Mensal", f"R$ {custo_total_mes:,.2f}/mês")
    cd2.metric("Manutenção & Uso (Sem Parcela)", f"R$ {custo_recorrente_mes:,.2f}/mês")
    cd3.metric("Impacto na Renda Mensal", f"{peso_na_renda:.1f}% da Renda")

    if peso_na_renda <= 15:
        st.success(f"🟢 **Custo Confortável:** O custo de manter este bem representa {peso_na_renda:.1f}% da sua renda. Ele cabe de forma saudável no seu fluxo mensal sem sufocar seus aportes.")
    elif peso_na_renda <= 25:
        st.warning(f"🟡 **Atenção ao Fluxo:** Esse custo representará {peso_na_renda:.1f}% da sua renda mensal. É viável, mas exigirá disciplina para manter suas metas de poupança em dia.")
    else:
        st.error(f"🔴 **Custo Elevado:** Este bem consumirá {peso_na_renda:.1f}% da sua renda mensal. Pode comprometer sua capacidade de poupança e seu patrimônio no médio prazo.")

# =========================================================
# MÓDULO 3: SIMULADOR DE CENÁRIOS ("E SE...?")
# =========================================================
elif menu == "🔮 Simulador de Cenários de Renda":
    st.title("Simulador de Cenários Futuros ('E se...?')")
    st.caption("Simule como um aumento de renda ou de aportes nos próximos anos antecipa a conquista dos seus objetivos.")

    col_cen1, col_cen2 = st.columns(2)
    with col_cen1:
        st.markdown("### 📌 Cenário Atual")
        st.write(f"Renda Base: **R$ {renda_base:,.2f}**")
        st.write(f"Aporte Atual: **R$ {aporte_base:,.2f}/mês**")

    with col_cen2:
        st.markdown("### 🚀 Cenário de Expansão (Futuro)")
        novo_aporte = st.number_input(
            "Novo Aporte Estimado (R$/mês)",
            min_value=float(aporte_base),
            value=float(aporte_base * 2),
            step=200.0
        )
        ganho_aporte = novo_aporte - aporte_base
        st.caption(f"Aumento de **+R$ {ganho_aporte:,.2f}** investidos por mês.")

    st.divider()

    st.subheader("⚡ Tempo Economizado por Meta")

    if not df_metas.empty:
        dados_comparativo = []
        for _, r in df_metas.iterrows():
            falta = max(0.0, r["valor_alvo"] - r["valor_acumulado"])
            if falta > 0:
                meses_atual = max(1, int(falta / aporte_base)) if aporte_base > 0 else 0
                meses_novo = max(1, int(falta / novo_aporte)) if novo_aporte > 0 else 0
                tempo_economizado = meses_atual - meses_novo

                dados_comparativo.append({
                    "Meta": r["titulo"],
                    "Meses (Cenário Atual)": meses_atual,
                    "Meses (Cenário Expansão)": meses_novo,
                    "Meses Economizados": tempo_economizado
                })

        if dados_comparativo:
            df_comp = pd.DataFrame(dados_comparativo)
            
            fig_comp = px.bar(
                df_comp,
                x="Meta",
                y=["Meses (Cenário Atual)", "Meses (Cenário Expansão)"],
                barmode="group",
                color_discrete_sequence=["#64748b", "#10b981"]
            )
            fig_comp.update_layout(
                template="plotly_dark",
                height=320,
                yaxis_title="Meses para Concluir",
                legend_title="Cenário"
            )
            st.plotly_chart(fig_comp, use_container_width=True)

            st.dataframe(
                df_comp.rename(columns={
                    "Meses (Cenário Atual)": "Prazo Atual (Meses)",
                    "Meses (Cenário Expansão)": "Novo Prazo (Meses)",
                    "Meses Economizados": "⚡ Meses Antecipados"
                }),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("Cadastre suas metas na aba 'Gestão de Metas' para ver o comparativo de cenários.")

# =========================================================
# MÓDULO 4: GESTÃO DE METAS & PARÂMETROS
# =========================================================
elif menu == "🎯 Gestão de Metas & Parâmetros":
    st.title("Gestão de Metas & Configurações")

    # 1. ATUALIZAR PARÂMETROS GERAIS
    with st.expander("⚙️ Parâmetros Financeiros Globais", expanded=False):
        with st.form("form_cfg_global"):
            nova_renda = st.number_input("Sua Renda Mensal Líquida (R$)", min_value=0.0, value=float(renda_base), step=100.0)
            novo_aporte_base = st.number_input("Sua Capacidade Mensal de Aporte (R$)", min_value=50.0, value=float(aporte_base), step=50.0)
            novo_patr = st.number_input("Patrimônio Inicial Não Alocado (R$)", min_value=0.0, value=float(patrimonio_base), step=100.0)

            if st.form_submit_button("Salvar Parâmetros", type="primary"):
                cursor.execute("""
                    UPDATE configuracoes SET patrimonio_atual = ?, aporte_mensal = ?, renda_mensal = ? WHERE id = 1
                """, (novo_patr, novo_aporte_base, nova_renda))
                conn.commit()
                st.success("Parâmetros globais salvos com sucesso!")
                st.rerun()

    st.write("")

    # 2. ADICIONAR NOVA META
    st.subheader("➕ Cadastrar Nova Meta")
    with st.form("form_nova_meta", clear_on_submit=True):
        f_titulo = st.text_input("Nome da Meta (ex: Troca de Carro, Reserva 6 Meses, Viagem Europa)")
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            f_cat = st.selectbox("Categoria", ["🚗 Veículo", "🛡️ Reserva de Emergência", "✈️ Viagem", "🏡 Imóvel", "💻 Equipamento", "🎯 Outro"])
            f_alvo = st.number_input("Valor Alvo (R$)", min_value=100.0, value=50000.0, step=500.0)
        with c_m2:
            f_acum = st.number_input("Valor Já Guardado Inicialmente (R$)", min_value=0.0, value=0.0, step=100.0)
            f_prio = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])

        if st.form_submit_button("Salvar Meta", type="primary"):
            if f_titulo.strip() == "":
                st.warning("Preencha o nome da meta.")
            else:
                cursor.execute("""
                    INSERT INTO metas (titulo, categoria, valor_alvo, valor_acumulado, prioridade)
                    VALUES (?, ?, ?, ?, ?)
                """, (f_titulo.strip(), f_cat, f_alvo, f_acum, f_prio))
                conn.commit()
                st.success(f"Meta '{f_titulo.strip()}' cadastrada com sucesso!")
                st.rerun()

    st.write("")

    # 3. METAS CADASTRADAS & EXCLUSÃO
    st.subheader("📋 Metas Cadastradas")
    if not df_metas.empty:
        st.dataframe(
            df_metas.rename(columns={
                "titulo": "Título",
                "categoria": "Categoria",
                "valor_alvo": "Valor Alvo (R$)",
                "valor_acumulado": "Acumulado (R$)",
                "prioridade": "Prioridade"
            })[["Título", "Categoria", "Valor Alvo (R$)", "Acumulado (R$)", "Prioridade"]].style.format({
                "Valor Alvo (R$)": "R$ {:,.2f}",
                "Acumulado (R$)": "R$ {:,.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### 🗑️ Excluir Meta")
        opcoes_del = {f"{r['titulo']} (R$ {r['valor_alvo']:,.2f})": int(r['id']) for _, r in df_metas.iterrows()}
        meta_del_sel = st.selectbox("Selecione a meta para remover:", list(opcoes_del.keys()))
        if st.button("Excluir Esta Meta", type="secondary"):
            id_del = opcoes_del[meta_del_sel]
            cursor.execute("DELETE FROM metas WHERE id = ?", (id_del,))
            conn.commit()
            st.success("Meta removida!")
            st.rerun()
    else:
        st.info("Nenhuma meta cadastrada.")
