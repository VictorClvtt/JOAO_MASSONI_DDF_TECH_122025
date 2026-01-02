import streamlit as st
import pandas as pd
import plotly.express as px
import pyarrow.dataset as ds

# ======================================================
# Configuração do App
# ======================================================
st.set_page_config(
    page_title="E-commerce Analytics",
    layout="wide"
)

st.title("📊 E-commerce Analytics – Data Exploration App")

# ======================================================
# Função utilitária – leitura de diretórios parquet
# ======================================================
def read_parquet_dir(path: str) -> pd.DataFrame:
    dataset = ds.dataset(path, format="parquet")
    return dataset.to_table().to_pandas()

# ======================================================
# Load data
# ======================================================
@st.cache_data(show_spinner=True)
def load_data():
    base_path = "./data/analytics"

    fact = read_parquet_dir(f"{base_path}/fact_order")
    dim_date = read_parquet_dir(f"{base_path}/dim_date")
    dim_status = read_parquet_dir(f"{base_path}/dim_order_status")
    dim_payment = read_parquet_dir(f"{base_path}/dim_payment_method")
    dim_product = read_parquet_dir(f"{base_path}/dim_product")
    dim_customer = read_parquet_dir(f"{base_path}/dim_customer")
    dim_location = read_parquet_dir(f"{base_path}/dim_location")

    df = (
        fact
        .merge(dim_date, left_on="order_date_sk", right_on="date_sk", how="left")
        .merge(dim_status, on="order_status_sk", how="left")
        .merge(dim_payment, on="payment_method_sk", how="left")
        .merge(dim_product, on="product_sk", how="left")
        .merge(dim_customer, on="customer_sk", how="left")
        .merge(dim_location, on="location_sk", how="left")
    )

    return df

# ======================================================
# Execução
# ======================================================
df = load_data()

# ======================================================
# Sidebar – Filtros
# ======================================================
st.sidebar.header("🎛️ Filtros")

years = sorted(df["year"].dropna().unique())
selected_years = st.sidebar.multiselect("Ano", years, default=years)

statuses = sorted(df["status"].dropna().unique())
selected_statuses = st.sidebar.multiselect(
    "Status do Pedido", statuses, default=statuses
)

df = df[
    (df["year"].isin(selected_years)) &
    (df["status"].isin(selected_statuses))
]

# ======================================================
# KPIs
# ======================================================
total_revenue = df["total_amount"].sum()
total_orders = df["order_id"].nunique()
cancelled_orders = df[df["status"].str.lower() == "cancelado"]["order_id"].nunique()
cancel_rate = cancelled_orders / total_orders if total_orders else 0
avg_ticket = df["total_amount"].mean()
avg_items = df["quantity"].mean()

# ======================================================
# Abas principais
# ======================================================
tab_overview, tab_time, tab_products, tab_customers, tab_categorical, tab_numeric = st.tabs([
    "📊 Visão Geral",
    "📈 Temporal",
    "🏭 Produtos & Fornecedores",
    "👥 Clientes",
    "🧩 Categórico",
    "🔢 Numérico"
])

# ======================================================
# 📊 VISÃO GERAL
# ======================================================
with tab_overview:
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("💰 Faturamento", f"R$ {total_revenue:,.2f}")
    col2.metric("📦 Pedidos", total_orders)
    col3.metric("❌ Cancelados", cancelled_orders)
    col4.metric("📉 Taxa Cancelamento", f"{cancel_rate:.2%}")
    col5.metric("🧾 Ticket Médio", f"R$ {avg_ticket:,.2f}")
    col6.metric("📦 Itens/Pedido", f"{avg_items:.2f}")

    st.divider()

    fig_dist = px.histogram(
        df,
        x="total_amount",
        nbins=30,
        title="Distribuição do Valor dos Pedidos"
    )
    st.plotly_chart(fig_dist, use_container_width=True)

# ======================================================
# 📈 TEMPORAL
# ======================================================
with tab_time:
    revenue_time = (
        df.groupby("full_date", as_index=False)["total_amount"]
        .sum()
        .sort_values("full_date")
    )

    fig_time = px.line(
        revenue_time,
        x="full_date",
        y="total_amount",
        title="Faturamento ao longo do tempo"
    )
    st.plotly_chart(fig_time, use_container_width=True)

    st.divider()

    monthly_revenue = (
        df.groupby(["year", "month"], as_index=False)["total_amount"]
        .sum()
    )

    fig_month = px.line(
        monthly_revenue,
        x="month",
        y="total_amount",
        color="year",
        title="Sazonalidade mensal por ano"
    )
    st.plotly_chart(fig_month, use_container_width=True)

# ======================================================
# 🏭 PRODUTOS & FORNECEDORES
# ======================================================
with tab_products:
    top_products = (
        df.groupby("product_name", as_index=False)["total_amount"]
        .sum()
        .sort_values("total_amount", ascending=False)
        .head(10)
    )

    fig_top_products = px.bar(
        top_products,
        x="product_name",
        y="total_amount",
        title="Top 10 Produtos por Faturamento"
    )
    st.plotly_chart(fig_top_products, use_container_width=True)

    st.divider()

    top_products_qty = (
        df.groupby("product_name", as_index=False)
        .agg(
            quantidade_total=("quantity", "sum"),
            faturamento=("total_amount", "sum")
        )
        .sort_values("quantidade_total", ascending=False)
        .head(20)
    )

    st.dataframe(top_products_qty, use_container_width=True)

    st.divider()

    cancel_supplier = (
        df.assign(is_cancelled=df["status"].str.lower() == "cancelado")
        .groupby("supplier", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            cancelled_orders=("is_cancelled", "sum")
        )
    )

    cancel_supplier["cancel_rate"] = (
        cancel_supplier["cancelled_orders"] / cancel_supplier["total_orders"]
    )

    fig_cancel_supplier = px.bar(
        cancel_supplier.sort_values("cancel_rate", ascending=False),
        x="supplier",
        y="cancel_rate",
        title="Taxa de Cancelamento por Fornecedor"
    )

    st.plotly_chart(fig_cancel_supplier, use_container_width=True)

# ======================================================
# 👥 CLIENTES
# ======================================================
with tab_customers:
    top_customers = (
        df.groupby("customer_name", as_index=False)["total_amount"]
        .sum()
        .sort_values("total_amount", ascending=False)
        .head(10)
    )

    fig_top_customers = px.bar(
        top_customers,
        x="customer_name",
        y="total_amount",
        title="Top 10 Clientes por Faturamento"
    )
    st.plotly_chart(fig_top_customers, use_container_width=True)

    st.divider()

    top_customers_value = (
        df.groupby("customer_name", as_index=False)
        .agg(
            faturamento=("total_amount", "sum"),
            pedidos=("order_id", "nunique")
        )
        .sort_values("faturamento", ascending=False)
        .head(20)
    )

    st.dataframe(top_customers_value, use_container_width=True)

# ======================================================
# 🧩 CATEGÓRICO
# ======================================================
with tab_categorical:
    suppliers = df["supplier"].value_counts().reset_index(name="count")
    categories = df["category"].value_counts().reset_index(name="count")
    customers = df["customer_name"].value_counts().reset_index(name="count")
    states = df["state"].value_counts().reset_index(name="count")
    cities = df["city"].value_counts().reset_index(name="count")

    t1, t2, t3, t4, t5 = st.tabs(
        ["🏭 Fornecedores", "🗂️ Categorias", "👥 Clientes", "📍 Estados", "🗺️ Cidades"]
    )

    with t1: st.dataframe(suppliers, use_container_width=True)
    with t2: st.dataframe(categories, use_container_width=True)
    with t3: st.dataframe(customers, use_container_width=True)
    with t4: st.dataframe(states, use_container_width=True)
    with t5: st.dataframe(cities, use_container_width=True)

# ======================================================
# 🔢 NUMÉRICO
# ======================================================
with tab_numeric:
    numeric_cols = ["unit_price", "quantity", "total_amount"]

    t1, t2, t3, t4 = st.tabs([
        "📈 Estatísticas",
        "📊 Distribuição",
        "📦 Outliers",
        "🔗 Correlação"
    ])

    with t1:
        st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)

    with t2:
        metric = st.selectbox("Métrica", numeric_cols)
        st.plotly_chart(px.histogram(df, x=metric, nbins=50), use_container_width=True)

    with t3:
        metric = st.selectbox("Métrica ", numeric_cols)
        st.plotly_chart(px.box(df, y=metric), use_container_width=True)

    with t4:
        corr = df[numeric_cols].corr()
        st.plotly_chart(px.imshow(corr, text_auto=True), use_container_width=True)
