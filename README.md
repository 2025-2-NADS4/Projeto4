# FECAP - Fundação Escola de Comércio Álvares Penteado

<p align="center">
<a href= "https://www.fecap.br/"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhZPrRa89Kma0ZZogxm0pi-tCn_TLKeHGVxywp-LXAFGR3B1DPouAJYHgKZGV0XTEf4AE&usqp=CAU" alt="FECAP - Fundação de Comércio Álvares Penteado" border="0"></a>
</p>

---

# Fidelize

## Projeto 4 | Equipe Rocket 🚀

## Integrantes:  
- [Gustavo de Souza Castro](https://www.linkedin.com/in/gustavocastro01/)
- [João Pedro Brosselin de Albuquerque Souza](https://www.linkedin.com/in/brosselindev//)
- [Marcella Santana Gonçalves Diniz Rocha](https://www.linkedin.com/in/marcella-santana-b76883262/)  
- [Thays Helyda da Silva Pontes](https://www.linkedin.com/in/thays-pontes-14663822b/)  

## Professores orientadores: 
- [Aimar Martins Lopes](https://www.linkedin.com/in/aimarlopes/)
- [Ronaldo Araujo Pinto](https://br.linkedin.com/in/ronaldo-araujo-pinto-3542811a)
- [Eduardo Savino Gomes](https://br.linkedin.com/in/eduardo-savino)
- [Edson Ricardo Barbero](https://br.linkedin.com/in/edsonbarbero)
- [Lucy Mari Tabuti](https://br.linkedin.com/in/lucymari)

## Descrição

  <p align="center">
  <img src="https://i.imgur.com/MnT1i81.png" alt="Fidelize" border="0">
  
  <br></br>
  Fidelize é um projeto acadêmico desenvolvido por alunos do Grupo 4 do curso de Análise e Desenvolvimento de Sistemas (ADS) da FECAP, no 4º semestre de 2025, em parceria com a startup foodtech Cannoli. O projeto tem como objetivo criar um dashboard interativo, responsivo e inteligente voltado à análise de dados operacionais e estratégicos da plataforma Cannoli.
<br></br>
A proposta do Fidelize é unir tecnologia e gestão de relacionamento para melhorar a experiência de administradores e parceiros comerciais, como restaurantes e negócios integrados à plataforma.
<br></br>
Com o dashboard Fidelize, os usuários poderão:

- Visualizar métricas de desempenho e indicadores estratégicos de forma clara e dinâmica.
- Acompanhar o engajamento de clientes e resultados de campanhas de fidelização.
- Gerenciar campanhas, pedidos e interações em tempo real, com foco em eficiência operacional.
- Tomar decisões baseadas em dados, com painéis personalizados e intuitivos.

Assim, o Fidelize reforça o propósito central da Cannoli: fidelizar clientes por meio da inteligência de dados, oferecendo uma solução tecnológica moderna, acessível e alinhada às necessidades do mercado de foodtech.

## 🛠 Estrutura de pastas

<b>README.MD</b>: Arquivo que serve como guia e explicação geral sobre seu projeto. O mesmo que você está lendo agora.

Há 3 pastas que seguem da seguinte forma:

<b>documentos</b>: Toda a documentação estará nesta pasta.

<b>imagens</b>: Imagens do sistema.

<b>src</b>: Pasta que contém o código fonte.

## 🔗 URL e Credenciais

Acesse a aplicação de demonstração:

**URL do site:** [fidelize.onrender.com](https://fidelize.onrender.com)

### 🔐 Credenciais de teste

#### Admin

email: admin@cannoli.com

senha: admin

#### Cliente

email: cliente@restaurante.com

senha: cliente

### ☑️ Como usar
1. Acesse a URL acima.  
2. Faça login com uma das credenciais de teste conforme sua necessidade (Admin ou Cliente).


## 🖥 Tecnologias Utilizadas

O núcleo do projeto é construído em Python, utilizando um ecossistema robusto para análise e visualização de dados:

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Dash](https://img.shields.io/badge/Dash-Plotly-blue?logo=plotly)
![Plotly Express](https://img.shields.io/badge/Plotly_Express-blue?logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-blue?logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-blue?logo=matplotlib)
![Jupyter](https://img.shields.io/badge/Jupyter-Colab-orange?logo=jupyter)

- **Python:** Linguagem principal para todo o projeto.
- **Dash (Plotly):** Framework principal para a construção do dashboard web interativo.
- **Plotly Express:** Biblioteca de alto nível para a criação dos gráficos interativos.
- **Pandas:** Ferramenta essencial para a limpeza, tratamento e análise dos dados.
- **Matplotlib:** Usada na fase de Análise Exploratória de Dados (AED) inicial.
- **Google Colab/Jupyter:** Utilizado para a prototipação e validação das análises.


## 📋 Pré-requisitos

Antes de iniciar a execução do Fidelize, é importante garantir que o ambiente de desenvolvimento esteja configurado com as ferramentas e dependências adequadas.
O projeto foi desenvolvido em Python e utiliza bibliotecas específicas para análise de dados, visualização interativa e execução de notebooks.

- [Python 3.10+](https://www.python.org/downloads/), a linguagem principal do projeto, usada para análise, tratamento de dados e execução do dashboard interativo..
- Um banco de dados PostgreSQL:
  - Caso utilize localmente, baixe e instale o [PostgreSQL](https://www.postgresql.org/download/).
  - Caso utilize um banco online, tenha as credenciais de acesso configuradas.
- [Pip](https://pip.pypa.io/en/stable/), o gerenciador de pacotes do Python, utilizado para instalar todas as dependências listadas em requirements.txt..
- Um editor de código como [VSCode](https://code.visualstudio.com/) (opcional, mas recomendado para editar o backend).
- [Git](https://git-scm.com/) para clonar o repositório do projeto e gerenciar versões do código.
- O dashboard é alimentado pelos seguintes arquivos .csv, que devem estar presentes na pasta src/data/: CampaignQueue.csv, Campaign.csv, Customer.csv, Order.csv.

## 🛠 Instalação e Configuração

O Fidelize é um projeto acadêmico desenvolvido em Python, voltado à análise e visualização interativa de dados da plataforma Cannoli, uma startup foodtech. O sistema utiliza Dash (Plotly) para criar um dashboard web responsivo e dinâmico, permitindo que administradores e parceiros da Cannoli explorem indicadores operacionais, campanhas e comportamento de clientes.

### 1. Estrutura e diretório do projeto

Após clonar o repositório do Fidelize a partir do GitHub, verifique a estrutura inicial do diretório:

```bash
|--> fidelize
 |--> src
  |--> documento/           # documentação e relatórios do projeto
  |--> imagens/             # recursos visuais utilizados
  |--> src/                 # código-fonte principal, arquivos CSV e notebooks colab
 requirements.txt
 README.md
```
Esses arquivos representam os dados de campanhas, clientes e pedidos utilizados para alimentar os gráficos e relatórios interativos do projeto.

### 2. Configuração do ambiente python

O projeto utiliza Python 3.10+ e as principais bibliotecas científicas para tratamento e visualização de dados.
Antes de rodar o dashboard, configure o ambiente conforme abaixo:

```bash
python --version
pip install --upgrade pip
```

Em um ambiente virtual, instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

### 3. Execução em Jupyter Notebook ou Google Colab

Durante o desenvolvimento, parte das análises do Fidelize (como segmentação, funil de campanhas e coortes) pode ser visualizada em notebooks Jupyter caso a execução seja local.

```bash
jupyter notebook
```
Com a execução no Google Colab, segue: upload de notebooks localizados em src/ e execução das células sequencialmente.

### 4. Inicializando o dashboard

A aplicação web está centralizada dentro da pasta src/, onde se encontra o arquivo principal.
Esse script faz a leitura dos dados, aplica os tratamentos necessários e gera as visualizações dinâmicas por meio do Dash.

```bash
cd src
python app.py
```
E o terminal exibirá algo como:
```bash
Dash is running on http://127.0.0.1:8050/
```
Esse enderço dará acesso ao dashboard interativo.

### 5. Configuração dos dados

Os arquivos de dados utilizados no projeto devem estar presentes em src/:
```bash
data/
 ├── CampaignQueue.csv
 ├── Campaign.csv
 ├── Customer.csv
 └── Order.csv
```
Esses arquivos são responsáveis por alimentar os gráficos e métricas do dashboard.

### 6. Hospedagem via GitHub

Como o Fidelize é um projeto em Python, o GitHub serve como repositório de código e documentação, e não executa o dashboard interativo diretamente.
Ainda assim, é possível hospedar o projeto e permitir que outros usuários o executem localmente.

```bash
python src/app.py
```

Com isso, o projeto é executado localmente e disponibilizado.

## 📋 Licença/License

<a href="https://github.com/2025-2-NADS4/Projeto4/">Fidelize</a> © 2025 by <a href="https://creativecommons.org">FECAP, Gustavo de Souza Castro, João Pedro Brosselin de Albuquerque Souza, Marcella Santana Gonçalves Diniz Rocha, Thays Helyda da Silva Pontes</a> is licensed under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a><img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;"><img src="https://mirrors.creativecommons.org/presskit/icons/by.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;">

## 🎓 Referências

Aqui estão as referências usadas no projeto.

1. [Cannoli Foodtech](https://www.cannoli.food/)
2. [Dash](https://plotly.com/dash/)
3. [Google Colab](https://colab.google/)
   
