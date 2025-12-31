import json
import re
from urllib.parse import urlparse
from transformers import pipeline

# ----------------------------
# Configurações
# ----------------------------
RAW_FILE = "./data/raw/reviews_mercadolivre_com_br_1.json"
CLEAN_FILE = "./data/raw/reviews_with_features.json"
NUM_TEST = 25  # primeiros registros para teste

# ----------------------------
# Lê o arquivo JSON
# ----------------------------
with open(RAW_FILE, "r", encoding="utf-8") as f:
    reviews = json.load(f)

# Limita para os primeiros registros apenas para teste
reviews = reviews[:NUM_TEST]

# ----------------------------
# Inicializa pipelines do Hugging Face
# ----------------------------
sentiment_analyzer = pipeline(
    "sentiment-analysis", model="tabularisai/multilingual-sentiment-analysis"
)
topic_extractor = pipeline(
    "zero-shot-classification",
    model="joeddav/xlm-roberta-large-xnli"
)

# Possíveis tópicos das reviews
CANDIDATE_TOPICS = [
    "qualidade do produto", "preço do produto", "embalagem", "entrega do produto",
    "fragância", "eficácia", "alergias", "modo de uso",
    "tecnologia", "cosmético ou produto de beleza", "higiene pessoal", "produto para casa",
    "conforto", "produto adulto", "produto infantil", "diversão ou entretenimento",
    "alimento ou bebida", "mobília", "produtos para animais"
]

# ----------------------------
# Funções auxiliares
# ----------------------------
def extract_product_info(url):
    path = urlparse(url).path
    match = re.match(r'/MLB-(\d+)-(.+)_JM', path)
    if match:
        product_code = match.group(1)
        product_name = match.group(2).replace("-", " ")
        return product_code, product_name
    return None, None

def classify_recommendation(content):
    """
    Classifica se o usuário recomenda ou não o produto
    a partir da análise de sentimento do texto.
    """
    result = sentiment_analyzer(content[:1024])[0]
    label = result["label"].lower()
    
    if label == "positive":
        return "recomenda"
    elif label == "negative":
        return "não recomenda"
    else:
        return "neutro"

def classify_sentiment(content):
    """
    Classifica o sentimento em:
    'muito positivo', 'positivo', 'neutro', 'negativo', 'muito negativo'
    """
    result = sentiment_analyzer(content[:512])[0]
    label = result["label"].lower()
    score = result["score"]
    
    if label == "positive":
        if score >= 0.9:
            return "muito positivo"
        else:
            return "positivo"
    elif label == "negative":
        if score >= 0.9:
            return "muito negativo"
        else:
            return "negativo"
    else:
        return "neutro"

def extract_topics(content, product_name):
    """
    Extrai tópicos a partir do conteúdo da review e do nome do produto.
    """
    # Combina texto da review com nome do produto
    combined_text = f"{product_name}. {content}"
    
    result = topic_extractor(combined_text[:512], CANDIDATE_TOPICS)
    
    # Filtra apenas tópicos com score > 0.3
    topics = [
        label for label, score in zip(result["labels"], result["scores"]) if score > 0.3
    ]
    return topics

# ----------------------------
# Processa as reviews
# ----------------------------
processed_reviews = []
total = len(reviews)

for i, review in enumerate(reviews, start=1):
    product_code, product_name = extract_product_info(review["product_url"])
    sentiment = classify_sentiment(review["content"])
    recommendation = classify_recommendation(review["content"])
    topics = extract_topics(review["content"], product_name)

    processed_reviews.append({
        "date": review["date"],
        "product_code": product_code,
        "product_name": product_name,
        "content": review["content"],
        "rating": review["rating"],
        "recommendation": recommendation,
        "sentiment": sentiment,
        "topics": topics,
        "product_url": review["product_url"]
    })

    # Log do progresso
    print(f"Processados {i}/{total} registros")

# ----------------------------
# Salva o resultado em JSON
# ----------------------------
with open(CLEAN_FILE, "w", encoding="utf-8") as f:
    json.dump(processed_reviews, f, ensure_ascii=False, indent=2)

print(f"Processamento concluído! Resultados salvos em {CLEAN_FILE}")
