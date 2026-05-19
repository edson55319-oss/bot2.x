import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Dashboard Financeiro",
    layout="wide"
)

st.title("💰 Dashboard Financeiro")

# =========================
# CONECTAR SQLITE
# =========================
conn = sqlite3.connect("finance_v2.db")

# =========================
# CARREGAR DADOS
# =========================
query = """
SELECT
    data,
    tipo,
    valor,
    descricao,
    pagamento,
    user_id
FROM transactions
"""

df = pd.read_sql_query(query, conn)

conn.close()

# =========================
# SE NÃO EXISTIR DADOS
# =========================
if df.empty:

    st.warning("Nenhuma transação encontrada.")

    st.stop()

# =========================
# AJUSTAR SAIDAS NEGATIVAS
# =========================
df["valor_ajustado"] = df.apply(
    lambda row: -row["valor"]
    if row["tipo"] == "saida"
    else row["valor"],
    axis=1
)

# =========================
# FILTRO USUARIO
# =========================
usuarios = df["user_id"].unique()

usuario = st.sidebar.selectbox(
    "Usuário",
    usuarios
)

df = df[df["user_id"] == usuario]

# =========================
# KPIs
# =========================
entradas = df[df["tipo"] == "entrada"]["valor"].sum()

saidas = df[df["tipo"] == "saida"]["valor"].sum()

saldo = entradas - saidas

col1, col2, col3 = st.columns(3)

col1.metric(
    "Entradas",
    f"R$ {entradas:.2f}"
)

col2.metric(
    "Saídas",
    f"R$ {saidas:.2f}"
)

col3.metric(
    "Saldo",
    f"R$ {saldo:.2f}"
)

# =========================
# GRAFICO ENTRADA X SAIDA
# =========================
grafico_tipo = (
    df.groupby("tipo")["valor"]
    .sum()
    .reset_index()
)

fig1 = px.pie(
    grafico_tipo,
    names="tipo",
    values="valor",
    title="Entradas vs Saídas"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =========================
# GRAFICO POR DESCRICAO
# =========================
grafico_categoria = (
    df.groupby("descricao")["valor"]
    .sum()
    .reset_index()
)

fig2 = px.bar(
    grafico_categoria,
    x="descricao",
    y="valor",
    title="Gastos por Descrição"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================
# TABELA
# =========================
st.subheader("📋 Transações")

st.dataframe(
    df[
        [
            "data",
            "tipo",
            "valor",
            "descricao",
            "pagamento"
        ]
    ],
    use_container_width=True
)