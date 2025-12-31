# Case Técnico Dadosfera - Data Engineer Jr
Case desenvolvido por **João Victor Clivatti Massoni**

## Sumário
- [Item 0 - Agilidade e Planejamento](#item-0---agilidade-e-planejamento)
- [Item 1 - Base de Dados](#item-1---base-de-dados)
- [Item 2 - Integração](#item-2---integração)
- [Item 3 - Exploração](#item-3---exploração)
- [Item 4 - Data Quality](#item-4---data-quality)
- [Item 5 - Processamento](#item-5---processamento)
- [Item 6 - Modelagem](#item-6---modelagem)
- [Item 7 - Análise](#item-7---análise)
- [Item 8 - Pipelines](#item-8---pipelines)
- [Item 9 - Data Apps](#item-9---data-apps)
- [Item 10 - Apresentação](#item-10---apresentação)
- [Item Bonus - GenAI + Data Apps](#item-bonus---genai--data-apps)

## Item 0 - Agilidade e Planejamento
Abaixo está o diagrama de todo o case representando o meu entendimento e planejamento do case como todo:
![](./docs/diagrams/item_0/fluxograma_case.png)

## Item 1 - Base de Dados
Na escolha do conjunto de dados optei por criar um script Python que gera e salva localmente uma base de dados sintéticos sobre vendas, que seriam vendas da empresa de e-commerce a qual a definição do case se refere.

O script gera 125 mil linhas de dados que apesar de sintéticos seguem uma coerência entre si, estanto de acordo com os requisitos definidos pelo case.

O arquivo do script esta localizado em [./scripts/bronze/generate_data.py](./scripts/bronze/generate_data.py) e os arquivos de dados em CSV que ele grava estão localizados em [./data/raw/synthetic_data_full.csv](./data/raw/synthetic_data_full.csv)(sendo o conjunto de dados completo) e [./data/raw/synthetic_data_sample.csv](./data/raw/synthetic_data_sample.csv)(sendo uma amostra de mil linhas do conjunto completo).

## Item 2 - Integração
Na etapa de integração e ingestão da base de dados gerada na plataforma da Dadosfera, inicialmente criei um script([./scripts/ingest.py](./scripts/ingest.py)) que grava os dados que estão armazenados localmente em uma planilha do Google Sheets no meu Google Drive pessoal para poder conectar a Dadosfera à essa planilha mais facilmente por estar na nuvem.

Antes mesmo de criar o script, comecei configurando a minha conta do Google para poder me comunicar com a API do Google, comecei ativando as APIs do Google Drive e do Google Sheets na seção "APIs e serviços" do Google Cloud Console:
![](./docs/prints/item_2/01_ativar_apis.png)

Ainda na seção "APIs e serviços", segui criando e posteriormente baixando credenciais pessoais para poder me comunicar com a API:
![](./docs/prints/item_2/02_opcao_criar_credencial_oauth.png)
![](./docs/prints/item_2/03_criar_credencial_oauth.png)
![](./docs/prints/item_2/04_baixar_credenciais.png)

Para finalmente poder me comunicar com as APIs, movi o arquivo baixado de credenciais para a raiz do diretório do projeto e o renomeei para [client_secret.json](./client_secret.json)

![](./docs/prints/item_2/05_renomear_e_mover_credenciais.png)

Com isso pude finalmente executar o script que move os dados para o Google Sheets, precisando apenas autorizar o script a manipular arquivos no meu Google Drive para que fosse criado o arquivo [token.json](./token.json) e não fosse necessária essa confirmação em execuções futuras. Para executar o script deve-se executa-lo como módulo: ```python -m scripts.bronze.generate_data``` dentro do diretório raiz do projeto (lembrando que o venv deve ter sido criado e ativado) com os seguintes parametros
```python
if __name__ == "__main__":
    ingest_data_to_sheets(
        csv_file="./data/raw/synthetic_data_full.csv",
        secret_path="client_secret.json",
        env_path=".env",
        spreadsheet_name="raw_orders"
    )
```
![](./docs/prints/item_2/06_autorizar_execucao.png)
![](./docs/prints/item_2/07_execucao_autorizada.png)

Após o script ser executado com sucesso, pude verificar no meu Google Drive que a planilha com os dados havia sido gravada com sucesso.
![](./docs/prints/item_2/08_dados_salvos_no_google_drive.png)

Até esse ponto minha idéia era poder criar scripts que executassem toda a etapa de integração, desde os dados locais até os dados ingeridos na plataforma, porém infelizmente enfrentei muitas dificuldades utilizando a API da Dadosfera, senti que faltou uma melhor descrição e talvez exemplos de como consumir os endpoints da API e que tipo de valores deveriam ser colocados em cada campo(o máximo que consegui foi criar uma função para logar na API). Por isso optei por criar a conexão com o Google Sheets e executar a pipeline de integração manualmente pelo site.

Para terminar a integração dos dados, primeiro criei uma conexão com o Google Sheets manualmente na seção de conexões da plataforma da Dadosfera:

Comecei clicando em "Nova fonte"
![](./docs/prints/item_2/09_opcao_nova_fonte.png)

Em seguida selecionei o Google Sheets como fonte
![](./docs/prints/item_2/10_selecionar_google_sheets.png)

E preenchi as informações da conexão
![](./docs/prints/item_2/11_informacoes_gerais_da_fonte.png)
![](./docs/prints/item_2/12_autorizar_google_na_fonte.png)

Depois de preencher as informações da conexão consegui cria-la com sucesso
![](./docs/prints/item_2/13_conexao_criada.png)

Com a conexão criada parti para a criação da pipeline que foi a última etapa da integração:

Comecei clicando em "Nova pipeline" e depois em "Criar pipeline" no modal que o primeiro botão abriu
![](./docs/prints/item_2/14_opcao_criar_pipeline.png)

E preenchi as informações da pipeline
![](./docs/prints/item_2/15_informacoes_gerais_da_pipeline.png)
![](./docs/prints/item_2/16_inserir_link_dos_dados.png)
![](./docs/prints/item_2/17_preencher_abas.png)
![](./docs/prints/item_2/18_definir_agendamento.png)

Depois de preencher as informações da pipeline, fazer outras tentativas trocando algumas configurações e esperar um pouco finalmente a pipeline foi executada e os dados foram integrados com sucesso
![](./docs/prints/item_2/19_pipeline_executada.png)

## Item 3 - Exploração
Pelo que pude perceber, os dados foram automaticamente catalogados na plataforma da Dadosfera após a integração, a unica coisa que fiz foi alterar o nome da tabela no catálogo para "orders_landing_zone".

Com os dados já catalogados, pude explora-los através da plataforma da Dadosfera que me trouxe algumas estatísticas sobre cada coluna do conjunto e uma visualização de uma amostra dos dados em formato de tabela:
![](./docs/prints/item_3/01_estatisticas_basicas.png)
![](./docs/prints/item_3/02_visualizacao_em_tabela.png)

Explorando os dados, pude ver os defeitos que eu mesmo inseri propositalmente neles já que eu fiz o script que os gera. Entre os defeitos inseridos estão valores nulos, valores fora de um alcance de valores lógico, linhas duplicadas, endereços de e-mail fora do padrão e nomes com espaços em branco antes e depois do nome.

Tendo conhecimento sobre os defeitos da base de dados eu estava pronto para explora-los melhor com outras ferramentas.

## Item 4 - Data Quality
Para a etapa de verificação de qualidade de dados desenvolvi o script [data_quality_report.py](./scripts/silver/data_quality_report.py) que lê o conjunto de dados gerados pelo script [generate_data.py](./scripts/bronze/generate_data.py) em CSV com Pandas e faz validações de qualidade de dados com Great Expectations.

Para executar o script deve-se executa-lo como módulo: ```python -m scripts.silver.data_quality_report``` dentro do diretório raiz do projeto (lembrando que o venv deve ter sido criado e ativado)

As validações foram definidas com base em um Common Data Model (CDM) orientado a entidades de negócio, cobrindo regras de integridade, consistência e semântica dos dados.

Foram realizadas as seguintes verificações sobre o conjunto de dados:

**Customer:**
- Verificação de valores nulos nos campos customer_id, customer_name e customer_email.
- Validação de higiene de strings, garantindo que o campo customer_name não contenha espaços em branco no início ou no final.
- Validação do formato de e-mail, assegurando que os valores em customer_email sigam o padrão esperado.
- Validação de domínio, garantindo que o estado do cliente (customer_state) pertença ao conjunto de estados válidos.

**Order:**
- Verificação de unicidade do identificador do pedido (order_id), evitando registros duplicados.
- Verificação de valores nulos nos campos order_id e order_date.
- Validação de domínio do status do pedido (status), restringindo os valores a um conjunto previamente definido.
- Validação de integridade referencial, garantindo a presença de customer_id associado ao pedido.

**Order Item:**
- Verificação de valores nulos nos campos product_id, order_id, quantity e unit_price.
- Validação de intervalos lógicos, garantindo que:
- A quantidade (quantity) seja maior ou igual a 1.
- O preço unitário (unit_price) seja maior que zero, com tolerância controlada.

**Payment:**
- Validação de domínio do método de pagamento (payment_method), restringindo os valores aos meios aceitos.
- Verificação de integridade referencial, garantindo a associação do pagamento a um pedido (order_id).

**Shipping:**
- Validação de regras de negócio, assegurando que pedidos cancelados não possuam data de envio (shipping_date).
- Verificação de consistência temporal, garantindo que a data de envio seja posterior à data do pedido para pedidos não cancelados.

**Review:**
- Validação de regras de negócio, garantindo que pedidos cancelados não possuam avaliações (review).

Ao final da execução, o script gera um relatório de validação no console, informando o status geral da qualidade dos dados, o total de expectativas avaliadas e o detalhamento das validações que apresentaram falhas:

![](./docs/prints/item_4/01_relatorio_de_qualidade_de_dados.png)

O pipeline de Data Quality foi executado com sucesso e identificou cinco violações relevantes nos dados de entrada:

- Nomes de clientes com espaços em branco antes e/ou depois do nome
- Endereços de e-mail fora do padrão
- Id de compra duplicados
- Valores fora de uma faixa de valores lógica no campo 'quantity'
- Valores nulos de valor unitário
- Valores de data de compra antes de valores de data de entrega e vice versa

Para tratar esses defeitos nos dados optei por utilizar PySpark(Spark) por ser uma ferramenta muito adequada para cenários de produção e de grandes volumes de dados, e também por ser uma ferramenta que já uso há alguns anos(apesar de também trabalhar com Pandas, R, etc).

Desenvolvi um script com PysPark que lê os dados crus, corrige da forma mais adequada possível(procurando recuperar dados) cada um dos defeitos que encontrei com o Great Expectations e grava o dataset limpo localmente em [data/clean/clean_orders/](./data/clean/clean_orders/). O script pode ser executado como módulo com o comando ```python -m scripts.silver.clean``` dentro do diretório raiz do projeto (lembrando que o venv deve ter sido criado e ativado e é necessário ter um JDK insatalado para executar Spark, de preferência o 17).

Agora se mudarmos os parametros da funcao de data quality para que ela verifique a qualidade de dados sobre os dados limpos pelo script PySpark ser;a possível observar que o conjunto de dados limpos passa em todas as condições de qualidade de dados definidas no script as quais os dados crus não passavam:
```python
if __name__ == "__main__":
    # data_quality_report(dataset="raw", dataset_path="./data/raw/synthetic_data_full.csv")
    data_quality_report(dataset="clean", dataset_path="./data/clean/clean_orders/*.csv")
```
![](./docs/prints/item_4/03_relatorio_de_qualidade_de_dados_limpos.png)

Após isso fiz o mesmo procedimento do [Item 2](#item-2---integração), primeiro executei o script que carrega os dados([scripts/ingest.py](./scripts/ingest.py)) no Google Sheets com outros parâmetros como mostrado abaixo e depois fiz as etapas manuais na plataforma para integrar e catalogar também os dados limpos na plataforma da Dadosfera.
```python
if __name__ == "__main__":
    ingest_data_to_sheets(
        csv_folder="./data/clean/clean_orders",
        secret_path="client_secret.json",
        env_path=".env",
        spreadsheet_name="clean_orders"
    )
```

## Item 5 - Processamento
O dataset que escolhi para esse item é o dataset que baixei para o diretório [./data/raw/](./data/raw/) e que se encontra para download [nesse link](https://raw.githubusercontent.com/octaprice/ecommerce-product-dataset/main/data/mercadolivre_com_br/reviews_mercadolivre_com_br_1.json), o dataset se trata de um pouco mais de 100 mil registros em JSON de avaliações de produtos do Mercado Livre, cada registro contendo a data da avaliação, uma nota numérica, uma avaliação textual e o link original produto avaliado, sendo possível extrair features dos campos de avaliação textual e do link.

Para executar o código de extração de features optei por utilizar o Google Colab como indicado pela documentação do case por ser um ambiente mais preparado para esse tipo de código.

Por estar trabalhando com IA, utilizei modelos do HuggingFace, o que me fez precisar criar uma conta no HuggingFace, criar um token e registrar esse token com o nome 'HF_TOKEN' no Colab para que eu pudesse utilizar os modelos.

Criei um diretório chamado 'data' e dentro dele outro diretório chamado 'raw' e copiei o [arquivo JSON](./data/raw/reviews_mercadolivre_com_br_1.json) para dentro desse diretório manualmente.

Em seguida, desenvolvi um [script](./scripts/bronze/extract_features.py) que utiliza inteligência artificial para extrair informações adicionais de forma programática a partir dos campos content e product_url do JSON original. Entre essas informações, estão: uma lista de tópicos relacionados ao produto, um campo que indica se o usuário recomenda ou não o produto, e uma análise de sentimento que classifica a avaliação como muito negativa, negativa, neutra, positiva ou muito positiva.""Em seguida, desenvolvi um script que utiliza duas inteligências artificiais para enriquecer os dados extraídos do JSON original (content e product_url).

- A primeira IA, ```tabularisai/multilingual-sentiment-analysis```, foi utilizada para análise de sentimento, classificando cada avaliação como muito negativa, negativa, neutra, positiva ou muito positiva.
Além disso, o script gera um campo que indica se o usuário recomenda ou não o produto, com base no sentimento detectado.

- A segunda IA, ```MoritzLaurer/mDeBERTa-v3-base-mnli-xnli```, foi aplicada em uma tarefa de zero-shot classification para identificar tópicos relevantes mencionados pelo usuário no review e no nome do produto.

Por fim o script grava esse novo JSON com as features dentro do mesmo diretório do original.

Neste repositório é possível acessar apenas uma [amostra dos dados](./data/raw/reviews_with_features_sample.json) com features pois infelizmente o processamento que o Colab me disponibilizou não me possibilitou processar os 100 mil registros.

## Item 6 - Modelagem
Para definir um modelo de dados sobre o conjunto de dados de vendas optei por começar desenvolvendo um script PySpark que modela os dados posteriormente limpos por outro script PySpark pois estou mais acostumado a olhar o schema dos dados por meio do código e a partir disso modelar as tabelas.

### Modelagem definida:
Durante o desenvolvimento do [script de modelagem](./scripts/gold/data_modeling.py) eu desenvolvi o seguinte modelo:
```
fact_order schema:
root
 |-- order_id: integer (nullable = true)
 |-- order_date_sk: string (nullable = true)
 |-- shipping_date_sk: string (nullable = true)
 |-- customer_sk: string (nullable = true)
 |-- product_sk: string (nullable = true)
 |-- payment_method_sk: string (nullable = true)
 |-- order_status_sk: string (nullable = true)
 |-- quantity: integer (nullable = true)
 |-- unit_price: double (nullable = true)
 |-- total_amount: double (nullable = true)

dim_date schema:
root
 |-- full_date: date (nullable = true)
 |-- day: integer (nullable = true)
 |-- month: integer (nullable = true)
 |-- month_name: string (nullable = true)
 |-- quarter: integer (nullable = true)
 |-- year: integer (nullable = true)
 |-- day_of_week: string (nullable = true)
 |-- is_weekend: boolean (nullable = false)
 |-- date_sk: string (nullable = true)

dim_order_status schema:
root
 |-- status: string (nullable = true)
 |-- order_status_sk: string (nullable = true)

dim_payment_method schema:
root
 |-- payment_method: string (nullable = true)
 |-- payment_method_sk: string (nullable = true)

dim_product schema:
root
 |-- product_id: integer (nullable = true)
 |-- product_name: string (nullable = true)
 |-- category: string (nullable = true)
 |-- supplier: string (nullable = true)
 |-- product_sk: string (nullable = true)

dim_customer schema:
root
 |-- customer_id: integer (nullable = true)
 |-- customer_name: string (nullable = true)
 |-- customer_email: string (nullable = true)
 |-- customer_sk: string (nullable = true)
 |-- location_sk: string (nullable = true)

dim_location schema:
root
 |-- city: string (nullable = true)
 |-- state: string (nullable = true)
 |-- location_sk: string (nullable = true)
```
Estes são os schemas de cada tabela definida para o modelo dimensional de dados que visa identificar cada entidade de dados e suas variáveis e tornar consultas analíticas mais eficientes.

A modelagem proposta segue os princípios de Dimensional Modeling (Kimball), adotando um Snowflake Schema, com uma tabela fato central (fact_order) e dimensões descritivas ao redor.
Essa abordagem foi escolhida por favorecer simplicidade, performance analítica e facilidade de consumo por ferramentas de BI, sendo adequada ao cenário de pedidos e vendas do cliente.

### Visões finais dos dados:
- 📊 Visão 1 – Vendas por período e produto
```SQL
SELECT
    d.year,
    d.month,
    p.category,
    p.product_name,
    SUM(f.quantity) AS total_quantity,
    SUM(f.total_amount) AS total_revenue
FROM fact_order f
JOIN dim_date d ON f.order_date_sk = d.date_sk
JOIN dim_product p ON f.product_sk = p.product_sk
GROUP BY d.year, d.month, p.category, p.product_name;
```
Vendas por período e produto permite analisar o desempenho comercial ao longo do tempo, detalhando vendas e receita por produto e categoria, apoiando decisões relacionadas a planejamento, estoque e estratégia de vendas.

- 👤 Visão 2 – Comportamento do cliente
```SQL
SELECT
    c.customer_name,
    l.city,
    l.state,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.total_amount) AS total_spent
FROM fact_order f
JOIN dim_customer c ON f.customer_sk = c.customer_sk
JOIN dim_location l ON c.location_sk = l.location_sk
GROUP BY c.customer_name, l.city, l.state;
```
Comportamento do cliente possibilita analisar padrões de consumo dos clientes, considerando volume de pedidos, valor gasto e localização geográfica, sendo útil para segmentação, marketing e identificação de clientes estratégicos.

### Diagrama da Modelagem Diomensional:
Baseado no modelo que desenvolvi no script, criei um diagrama relacional do modelo de dados:
![](./docs/diagrams/item_6/diagrama_dw.png)

## Item 7 - Análise
## Item 8 - Pipelines
## Item 9 - Data Apps
## Item 10 - Apresentação
## Item Bonus - GenAI + Data Apps