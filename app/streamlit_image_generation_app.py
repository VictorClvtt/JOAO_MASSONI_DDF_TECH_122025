import streamlit as st
from gradio_client import Client
from PIL import Image
import io
import pandas as pd

# ---------------------------------------------------------
# Configuração do App
# ---------------------------------------------------------
st.set_page_config(
    page_title="Gerador de Imagem de Produto (GenAI)",
    page_icon="🖼️",
    layout="centered"
)

st.title("🖼️ Gerador de Imagem de Produto (GenAI)")
st.write(
    "Selecione um produto e gere automaticamente uma imagem promocional "
    "utilizando Inteligência Artificial."
)

# ---------------------------------------------------------
# Carregamento dos dados
# ---------------------------------------------------------
@st.cache_data
def load_products():
    return pd.read_parquet("./data/analytics/dim_product")

df_products = load_products()

# ---------------------------------------------------------
# UI - Seleção de Produto
# ---------------------------------------------------------
selected_product = st.selectbox(
    "📦 Selecione um produto",
    df_products["product_name"].unique()
)

product_data = df_products[
    df_products["product_name"] == selected_product
].iloc[0]

# ---------------------------------------------------------
# Função de geração de imagem (HF Space)
# ---------------------------------------------------------
def generate_product_image(product_name, category, supplier):
    prompt = f"""
    Professional studio product photo for e-commerce.

    Product: {product_name}
    Category: {category}
    Brand: {supplier}

    White background, soft studio lighting,
    centered composition, ultra realistic,
    high detail, 4k quality.
    """

    client = Client("hysts/SDXL")

    result = client.predict(
        prompt,
        api_name="/predict"
    )

    image = Image.open(result)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue(), prompt

# ---------------------------------------------------------
# Geração da imagem
# ---------------------------------------------------------
if st.button("✨ Gerar imagem do produto"):
    with st.spinner("Gerando imagem com IA..."):
        try:
            image_bytes, image_prompt = generate_product_image(
                product_name=product_data["product_name"],
                category=product_data["category"],
                supplier=product_data["supplier"]
            )

            st.image(
                image_bytes,
                caption=f"Imagem gerada para {selected_product}",
                use_container_width=True
            )

            st.subheader("🧠 Prompt utilizado")
            st.code(image_prompt)

        except Exception as e:
            st.error(f"Erro ao gerar imagem: {e}")
