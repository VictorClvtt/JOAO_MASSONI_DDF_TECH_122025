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

## Item 1 - Base de Dados
Na escolha do conjunto de dados optei por criar um script Python que gera e salva localmente uma base de dados sintéticos sobre vendas, que seriam vendas da empresa de e-commerce a qual a definição do case se refere.

O script gera 125 mil linhas de dados que apesar de sintéticos seguem uma coerência entre si, estanto de acordo com os requisitos definidos pelo case.

O arquivo do script esta localizado em [./scripts/bronze/generate_data.py](./scripts/bronze/generate_data.py) e os arquivos de dados em CSV que ele grava estão localizados em [./data/raw/synthetic_data_full.csv](./data/raw/synthetic_data_full.csv)(sendo o conjunto de dados completo) e [./data/raw/synthetic_data_sample.csv](./data/raw/synthetic_data_sample.csv)(sendo uma amostra de mil linhas do conjunto completo).

## Item 2 - Integração
Na etapa de integração e ingestão da base de dados gerada na plataforma da Dadosfera, inicialmente criei um script([./scripts/bronze/ingest.py](./scripts/bronze/ingest.py)) que grava os dados que estão armazenados localmente em uma planilha do Google Sheets no meu Google Drive pessoal para poder conectar a Dadosfera à essa planilha mais facilmente por estar na nuvem.

Antes mesmo de criar o script, comecei configurando a minha conta do Google para poder me comunicar com a API do Google, comecei ativando as APIs do Google Drive e do Google Sheets na seção "APIs e serviços" do Google Cloud Console:
![](./docs/prints/item_2/01_ativar_apis.png)

Ainda na seção "APIs e serviços", segui criando e posteriormente baixando credenciais pessoais para poder me comunicar com a API:
![](./docs/prints/item_2/02_opcao_criar_credencial_oauth.png)
![](./docs/prints/item_2/03_criar_credencial_oauth.png)
![](./docs/prints/item_2/04_baixar_credenciais.png)

Para finalmente poder me comunicar com as APIs, movi o arquivo baixado de credenciais para a raiz do diretório do projeto e o renomeei para [client_secret.json](./client_secret.json)

![](./docs/prints/item_2/05_renomear_e_mover_credenciais.png)

Com isso pude finalmente executar o script que move os dados para o Google Sheets, precisando apenas autorizar o script a manipular arquivos no meu Google Drive para que fosse criado o arquivo [token.json](./token.json) e não fosse necessária essa confirmação em execuções futuras.
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


## Item 4 - Data Quality
## Item 5 - Processamento
## Item 6 - Modelagem
## Item 7 - Análise
## Item 8 - Pipelines
## Item 9 - Data Apps
## Item 10 - Apresentação
## Item Bonus - GenAI + Data Apps