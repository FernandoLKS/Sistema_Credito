# Projeto de Simulação de Sistema de Crédito

## Objetivo do Projeto

Este projeto tem como objetivo desenvolver uma plataforma completa de simulação e análise de operações de crédito, utilizando dados macroeconômicos reais disponibilizados pela API do Banco Central do Brasil (BCB).

A proposta busca reproduzir um ambiente próximo ao de uma instituição financeira, contemplando desde a ingestão e armazenamento de dados até a geração de indicadores analíticos, dashboards e modelos estatísticos/ML aplicados ao contexto de crédito.

O sistema realiza a extração periódica de indicadores econômicos relacionados ao mercado de crédito, utilizando esses dados como base para gerar clientes e operações simuladas, mantendo consistência com cenários macroeconômicos reais.

Além disso, o projeto também serve como um ambiente prático para estudo e aplicação de diversas áreas da engenharia de dados, análise de dados e machine learning, integrando conceitos de:

- Engenharia de Dados
- ETL/ELT
- Orquestração de pipelines
- Modelagem de banco de dados
- Simulação de operações financeiras
- Business Intelligence
- Machine Learning
- Análise estatística

---

# Arquitetura Geral

O fluxo principal do projeto segue as seguintes etapas:

1. Extração mensal de indicadores de crédito através da API do Banco Central.
2. Persistência dos dados em banco PostgreSQL.
3. Execução automática de DAGs no Airflow para:
   - Atualização dos indicadores macroeconômicos;
   - Inserção de novos clientes;
   - Criação de novas operações de crédito;
   - Atualização do estado das operações existentes.
4. Construção de dashboards analíticos para acompanhamento das operações simuladas.
5. Desenvolvimento de modelos estatísticos e de machine learning utilizando os dados gerados pelo sistema.

---

# Funcionalidades Planejadas

## Engenharia de Dados

- Extração automatizada via API
- Pipelines ETL/ELT
- Orquestração com Airflow
- Persistência relacional com PostgreSQL
- Atualização incremental de dados
- Versionamento e automação de pipelines

## Simulação de Crédito

- Geração de clientes simulados
- Criação de operações de crédito
- Evolução temporal das operações
- Associação de operações a indicadores econômicos reais
- Controle de inadimplência e status das operações

## Analytics & BI

- Dashboards operacionais
- Indicadores de carteira
- Evolução temporal do crédito
- Métricas de inadimplência
- Indicadores de performance

## Machine Learning & Estatística

- Modelos preditivos
- Análise de risco
- Predição de inadimplência
- Estudos estatísticos sobre a carteira simulada
- Feature engineering baseada em indicadores econômicos

---

# Tecnologias Utilizadas

## Linguagem Principal

- Python

## Engenharia de Dados

- Apache Airflow
- PostgreSQL
- Pandas
- SQLAlchemy

## APIs e Dados

- API do Banco Central do Brasil (BCB)

## Visualização de Dados

- Power BI
- Matplotlib
- Seaborn
- Plotly

## Machine Learning

- Scikit-learn
- NumPy
- SciPy
- Statsmodels

## Versionamento

- Git
- GitHub