# VagaLens

**Automação de triagem de vagas de estágio e cartas de apresentação com RAG, rodando 100% local.**

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)
![License](https://img.shields.io/badge/license-MIT-green)
![Custo](https://img.shields.io/badge/custo-zero-brightgreen)

O VagaLens é uma ferramenta de linha de comando, executada de forma agendada, que **coleta vagas de estágio**, avalia o quanto cada uma combina com o meu perfil usando **RAG (Retrieval-Augmented Generation)** e, para as que valem a pena, gera um rascunho de carta de apresentação baseado **apenas em informações reais** da minha base pessoal. No fim, **avisa por Telegram ou e-mail** com um resumo das melhores vagas e oferece um **painel local em Streamlit** para revisar vagas, editar cartas e registrar decisões.

O projeto tem dois propósitos: ser usado de verdade nas minhas candidaturas e servir de laboratório para estudar RAG a fundo, com decisões de design **medidas** em vez de assumidas.

> **Status:** em desenvolvimento. Os comandos e telas descritos abaixo seguem o [roadmap](#roadmap); o que ainda não existe está marcado como *planejado*.

---

## Sumário

- [O que é](#o-que-é)
- [Objetivos](#objetivos)
- [Motivação](#motivação)
- [Custo zero](#custo-zero)
- [Como funciona](#como-funciona)
- [Stack](#stack)
- [Estrutura de arquivos](#estrutura-de-arquivos)
- [Como usar](#como-usar-planejado)
- [Avaliação](#avaliação)
- [Resultados](#resultados)
- [Roadmap](#roadmap)
- [Limitações conhecidas](#limitações-conhecidas)
- [Privacidade e uso responsável](#privacidade-e-uso-responsável)
- [Licença](#licença)

---

## O que é

O VagaLens automatiza quatro tarefas manuais e repetitivas:

1. **Busca:** checar periodicamente as fontes de vagas e separar o que é novo.
2. **Triagem:** ler descrições de vagas e decidir quais valem o esforço.
3. **Candidatura:** escrever uma carta (e ajustar o currículo) adaptada a cada vaga escolhida.
4. **Acompanhamento:** lembrar quais vagas já foram vistas, notificadas e decididas.

Meus documentos (currículo, projetos, READMEs de repositórios, certificados) são indexados em um banco vetorial. Para cada vaga, o sistema:

- extrai os **requisitos** da vaga;
- recupera os trechos do meu perfil que servem de evidência para cada requisito;
- classifica cada requisito como **atendido, parcialmente atendido ou não atendido**, citando o trecho usado;
- calcula uma **nota de compatibilidade** a partir dessa classificação;
- para vagas acima do limiar, **rascunha a carta**, com cada afirmação ligada a um trecho da base.

Todo esse fluxo roda de forma **agendada**: uma rodada diária coleta as vagas novas, descarta duplicadas e irrelevantes, tria, gera os rascunhos e envia o resumo. Eu só preciso revisar e decidir, pelo painel ou pela CLI.

**Toda carta passa por revisão humana. O sistema não envia candidaturas.**

## Objetivos

**Aprendizado (foco principal)**

- Construir um pipeline RAG de ponta a ponta, escrevendo cada etapa (sem esconder a lógica atrás de frameworks), com decisões justificadas.
- **Avaliar quantitativamente**, em vez de concluir que "parece bom":
  - precisão, recall e F1 da triagem contra vagas rotuladas manualmente;
  - hit rate da recuperação (o trecho certo aparece no top-k?);
  - fidelidade das cartas (as afirmações têm sustentação na base?).
- Comparar **RAG contra um baseline sem RAG** (perfil inteiro no prompt) e documentar quando cada abordagem vence.
- Fazer experimentos controlados: tamanho de chunk, sobreposição, modelo de embedding, valor de k, reranking e formato da consulta.
- Praticar boas práticas de engenharia: testes, configuração, prompts versionados e registro reprodutível de cada experimento.

**Automação (uso real)**

- Ter uma ferramenta que eu use nas candidaturas desde as primeiras versões, mesmo que simples.
- Fazer a rodada diária funcionar **sozinha**: coletar, deduplicar, filtrar, triar, gerar rascunhos e notificar, sem intervenção manual.
- Ser **confiável**: execução idempotente, falha de uma fonte sem derrubar a rodada, logs por rodada e aviso quando algo quebrar.
- Ser **econômica**: filtros baratos antes de usar o LLM e limite de vagas triadas por rodada, para caber no hardware local.
- Fechar o ciclo: as decisões que eu registro (candidatei / ignorei) viram rótulos para a avaliação.
- Ter uma **interface simples** (painel Streamlit) para acompanhar as vagas, revisar evidências e cartas, e ver a saúde da automação.

**Fora do escopo (por enquanto)**

- Envio automático de candidaturas.
- API REST e frontend separado (FastAPI + React): a interface é um painel local em Streamlit, mais a CLI e as notificações.
- Deploy online e serviços pagos.

## Motivação

Candidatar-se a estágios exige repetir um ciclo cansativo: procurar vagas, comparar requisitos com o que já fiz e escrever uma carta. Grande parte desse trabalho é recuperar a informação certa do meu próprio histórico e reorganizá-la para um contexto específico, que é o problema que o RAG se propõe a resolver. Além disso, o valor prático só aparece quando o processo roda sozinho: o que mais custa é lembrar de checar as fontes todo dia, e isso a automação elimina.

Há também uma questão técnica interessante: minha base pessoal é **pequena** (dezenas de trechos, não milhares de documentos). Em escalas assim, RAG nem sempre supera simplesmente colocar tudo no prompt. Em vez de assumir que ajuda, o projeto mede.

## Custo zero

| Item | Solução gratuita |
|---|---|
| LLM | Ollama rodando localmente (modelos de 3B a 8B parâmetros) |
| Embeddings | `sentence-transformers`, local |
| Banco vetorial | ChromaDB, local |
| Registro de experimentos | SQLite e CSV |
| Testes e CI | `pytest`, `ruff`, GitHub Actions (repositório público) |
| Coleta | `requests`, `BeautifulSoup4`, `feedparser` |
| Agendamento | `cron` ou `systemd timer` (ou `APScheduler`) |
| Painel | Streamlit, rodando localmente |
| Notificações | Telegram Bot API e `smtplib` (e-mail) |

API externa de LLM é **opcional**, configurável por `.env`, com limite de tokens por execução, e nunca usada em testes automatizados. Um exemplo é a Groq, que tem plano gratuito com limites por organização que mudam com o tempo (confira os atuais antes de depender deles); nesse caso os trechos recuperados saem da máquina.

**Limitação:** modelos locais pequenos escrevem pior em português do que modelos grandes, e a velocidade depende do hardware. Por isso o projeto avalia mais de um modelo logo no início e permite trocá-lo por configuração.

## Como funciona

### Ciclo diário

```
 Agendador (cron / systemd timer / APScheduler), uma vez por dia
        │
        ▼
 [Coletores]       RSS e páginas de carreira (definidos em sources.yaml)
        │
        ▼
 [Deduplicação]    a mesma vaga em fontes diferentes só entra uma vez
        │
        ▼
 [Pré-filtro]      palavras-chave, tipo e local, sem gastar LLM
        │
        ▼
 [Pipeline de triagem e carta]   (detalhado abaixo)
        │
        ▼
 [Notificação]     resumo no Telegram ou e-mail com as melhores vagas
        │
        ▼
 Eu reviso e decido no painel (vagalens ui)
        ou pela CLI:  vagalens mark <id> applied | ignored
```

### Pipeline de uma vaga

```
  Base pessoal (currículo, projetos, certificados)        Vaga (texto)
                    │                                          │
                    ▼                                          ▼
          [Ingestão + chunking]                     [Extração de requisitos]
                    │                                          │
                    ▼                                          │
        [Embeddings → ChromaDB]                                │
                    │                                          │
                    └───────► [Recuperação top-k] ◄────────────┘
                                      │      (uma consulta por requisito)
                                      ▼
                    [LLM: classifica cada requisito + cita evidência]
                                      │
                                      ▼
                      [Nota calculada a partir dos requisitos]
                                      │
                              nota ≥ limiar?
                                      │
                                      ▼
                  [LLM: carta com citações dos trechos usados]
                                      │
                                      ▼
                       [Checagem de fidelidade da carta]
                                      │
                                      ▼
                          Rascunho para revisão humana
```

**Por que a nota vem dos requisitos?** Pedir a um modelo pequeno uma nota de 0 a 10 diretamente costuma gerar números mal calibrados. Classificar requisito por requisito, com evidência citada, é mais verificável, e a nota passa a ser uma consequência auditável.

### Automação

- **Estado das vagas:** uma tabela em SQLite guarda URL, hash do texto, fonte, datas e status (`nova`, `filtrada`, `triada`, `notificada`, `candidatada`, `ignorada`). É a memória do sistema entre uma rodada e outra.
- **Deduplicação:** por URL normalizada e por hash do texto, então uma vaga repetida em várias fontes não é triada duas vezes.
- **Pré-filtro barato:** palavras-chave, tipo de vaga e local eliminam o que claramente não interessa antes de gastar tempo de LLM. Há também um limite de vagas triadas por rodada.
- **Idempotência e recuperação:** rodar duas vezes não duplica nada, e uma rodada atrasada (por exemplo, com o computador desligado no horário) processa só o que falta. Com `systemd timer` (`Persistent=true`) ou `anacron`, a rodada perdida roda ao ligar.
- **Resiliência:** se uma fonte falha, as outras seguem. Há retries com espera crescente, log por rodada e aviso no Telegram quando uma fonte falha vários dias seguidos (provável mudança no site).
- **Notificação:** mensagem curta com empresa, nota, requisitos que faltam e link, mais o caminho local do rascunho. A carta completa não é enviada pelo Telegram por padrão.
- **Decisão e feedback:** `vagalens mark` registra se me candidatei ou ignorei, e isso vira rótulo para a avaliação.
- **Fontes:** configuradas em `sources.yaml`. Começo pelas mais simples (RSS e páginas estáticas) e só adiciono outra se os termos de uso permitirem. Os testes dos coletores usam HTML salvo, sem rede.

### Painel (Streamlit)

Uma camada fina de visualização que lê o **mesmo SQLite** da automação. Não há API separada nem build de frontend: o painel é um processo Python local (`vagalens ui`, em `http://localhost:8501`).

| Tela | O que mostra |
|---|---|
| **Vagas** | Tabela ordenada por nota, com filtros por status (nova, notificada, candidatada, ignorada), fonte e data |
| **Detalhe da vaga** | Requisitos atendidos, parciais e não atendidos, com o trecho do meu perfil usado como evidência |
| **Carta** | Rascunho editável, com as frases de baixa fidelidade destacadas e botões *candidatei* e *ignorar* (o mesmo que `vagalens mark`) |
| **Saúde da automação** | Última rodada, vagas novas por dia, fontes com falha e tempo por rodada |
| **Avaliação** | Tabela de resultados dos experimentos (F1, hit rate, fidelidade, RAG contra baseline) |

**Decisões de design**

- O painel só **escreve** o status da vaga e a carta editada; todo o resto é leitura. A automação e o painel nunca disputam os mesmos dados.
- Como dois processos acessam o SQLite (agendador e painel), o banco usa o modo **WAL**.
- O painel é para uso local e não deve ser exposto na internet.
- Se um dia eu quiser estudar full stack, o painel pode ser substituído por FastAPI + React sem mexer na automação, já que a base de dados é a mesma.

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11+ |
| Embeddings | `sentence-transformers` (modelo multilíngue, ex.: `paraphrase-multilingual-MiniLM-L12-v2`) |
| Banco vetorial | ChromaDB |
| LLM | Ollama (local, padrão); API externa opcional |
| Orquestração do RAG | Implementação própria (para entender cada etapa) |
| Saídas estruturadas | Pydantic (validação do JSON do LLM) |
| Cartas | Templates `Jinja2` |
| CLI | `typer` |
| Coleta | `requests`, `BeautifulSoup4`, `feedparser` |
| Agendamento | `cron` ou `systemd timer` (alternativa em Python: `APScheduler`) |
| Estado das vagas | SQLite |
| Notificações | Telegram Bot API e `smtplib` (e-mail) |
| Currículo por vaga | Template LaTeX com `Jinja2` |
| Painel | Streamlit (lê o mesmo SQLite) |
| Registro de execuções | SQLite |
| Qualidade | `pytest`, `ruff`, `mypy`, `pre-commit` |
| CI | GitHub Actions (lint e testes) |
| Configuração | `.env` + `config.yaml` |
| Automação local | `Makefile` |

## Estrutura de arquivos

```
vagalens/
├── README.md
├── pyproject.toml
├── .env.example
├── config.yaml                  # modelos, k, tamanho de chunk, limiar de nota, idioma
├── Makefile                     # atalhos: install, lint, test, eval
├── .pre-commit-config.yaml
├── sources.yaml                 # fontes de vagas, palavras-chave e filtros
├── .github/workflows/ci.yml     # lint e testes
│
├── prompts/                     # prompts versionados (a versão é registrada em cada execução)
│   ├── extract_requirements.v1.md
│   ├── screening.v1.md
│   └── cover_letter.v1.md
│
├── data/
│   ├── profile/                 # base pessoal (NÃO versionar)
│   │   ├── curriculo.md
│   │   ├── projetos/
│   │   └── certificados/
│   ├── vagalens.db              # SQLite: estado das vagas e registro de execuções
│   ├── jobs/                    # vagas (texto) para triagem
│   ├── vectorstore/             # índice do ChromaDB
│   ├── demo/                    # perfil e vagas fictícias para quem clonar o repo
│   └── eval/
│       ├── jobs_labeled.csv     # vagas rotuladas (candidatar / ignorar)
│       └── retrieval_gold.csv   # requisito → trecho que deveria ser recuperado
│
├── templates/
│   ├── cover_letter.md.j2
│   ├── resume.tex.j2            # currículo em LaTeX com variáveis por vaga
│   └── notification.md.j2       # formato do resumo enviado
│
├── src/vagalens/
│   ├── config.py                # leitura de config e variáveis de ambiente
│   ├── ingestion/
│   │   ├── loader.py            # leitura de md, pdf e tex
│   │   ├── chunking.py          # estratégias de chunking comparáveis
│   │   └── indexer.py           # embeddings e escrita no ChromaDB
│   ├── retrieval/
│   │   └── retriever.py         # top-k e reranking opcional
│   ├── collectors/
│   │   ├── base.py              # interface comum dos coletores
│   │   ├── rss.py
│   │   └── careers_page.py      # páginas de carreira (HTML)
│   ├── automation/
│   │   ├── jobs_store.py        # estado das vagas (nova, triada, notificada, candidatada, ignorada)
│   │   ├── dedup.py             # deduplicação por URL e hash do texto
│   │   ├── prefilter.py         # filtro barato por palavras-chave, antes do LLM
│   │   └── run_daily.py         # orquestra a rodada: coleta, filtro, triagem, carta, notificação
│   ├── notify/
│   │   ├── telegram.py
│   │   └── email.py
│   ├── ui/
│   │   ├── app.py               # entrada do Streamlit (vagalens ui)
│   │   ├── data.py              # acesso ao SQLite (leitura; escrita só de status e carta editada)
│   │   └── pages/
│   │       ├── 1_Vagas.py
│   │       ├── 2_Detalhe.py
│   │       ├── 3_Carta.py
│   │       ├── 4_Automacao.py
│   │       └── 5_Avaliacao.py
│   ├── llm/
│   │   ├── client.py            # abstração Ollama / API
│   │   └── prompts.py           # carrega e renderiza os prompts de prompts/
│   ├── pipeline/
│   │   ├── requirements.py      # extração de requisitos da vaga
│   │   ├── screening.py         # classificação por requisito e nota
│   │   ├── generation.py        # carta com citações
│   │   ├── resume_variant.py    # variante do currículo em LaTeX por vaga
│   │   └── faithfulness.py      # checagem de fidelidade
│   ├── runs.py                  # registro de execuções em SQLite
│   └── cli.py                   # index, collect, run, screen, generate, notify, mark, ui, eval, compare
│
├── scripts/
│   ├── run_daily.sh             # chamado pelo cron ou systemd timer
│   └── evaluate.py              # métricas e comparação de configurações
│
├── experiments/                 # resultados dos experimentos (CSV) e notas de análise
├── docs/
│   └── img/                     # prints do painel e da notificação, GIF da rodada
├── logs/                        # logs das rodadas automáticas
├── outputs/                     # rascunhos de cartas gerados, por vaga
│
└── tests/
    ├── test_chunking.py
    ├── test_retrieval.py
    ├── test_screening.py
    ├── test_faithfulness.py
    ├── test_collectors.py       # com HTML salvo, sem rede
    ├── test_dedup.py
    ├── test_notify.py
    └── test_ui_data.py          # camada de dados do painel
```

## Como usar (planejado)

### Pré-requisitos

- Python 3.11 ou superior
- [Ollama](https://ollama.com) instalado, com ao menos um modelo baixado (por exemplo, `ollama pull qwen2.5:7b`)

### Núcleo

```bash
# 1. Instalar
git clone https://github.com/<seu-usuario>/vagalens.git
cd vagalens
pip install -e .

# 2. Configurar
cp .env.example .env
# edite config.yaml e coloque seus documentos em data/profile/
# (para testar sem dados pessoais, use data/demo/)

# 3. Indexar a base pessoal
vagalens index

# 4. Triar uma vaga (texto colado em um arquivo)
vagalens screen --job data/jobs/vaga_123.txt

# 5. Gerar o rascunho da carta
vagalens generate --job data/jobs/vaga_123.txt

# 6. Avaliar e comparar configurações
vagalens eval
vagalens compare --config config.yaml --baseline full-context
```

### Automação

```bash
# Coletar as vagas das fontes de sources.yaml (sem triar)
vagalens collect

# Rodada completa: coleta → deduplicação → pré-filtro → triagem → cartas → notificação
vagalens run

# Registrar a decisão sobre uma vaga (alimenta os rótulos de avaliação)
vagalens mark 123 applied     # applied | ignored

# Abrir o painel local (http://localhost:8501)
vagalens ui

# Agendar a rodada todo dia às 8h (cron)
0 8 * * * cd /caminho/vagalens && ./scripts/run_daily.sh >> logs/cron.log 2>&1
```

Para o Telegram: criar um bot com o BotFather e colocar o token e o `chat_id` no `.env`. Se o computador nem sempre estiver ligado no horário, prefira um `systemd timer` com `Persistent=true` ou `anacron`; como a rodada é idempotente, executar atrasado não duplica nada.

Atalhos: `make install`, `make lint`, `make test`, `make eval`, `make run`, `make ui`.

## Avaliação

Esta é a parte central do projeto. A avaliação fica em `scripts/evaluate.py` e usa dois conjuntos rotulados à mão.

**Conjuntos de dados**

- `jobs_labeled.csv`: de 40 a 60 vagas que realmente avaliei, rotuladas como *candidatar* ou *ignorar*. As marcações feitas com `vagalens mark` durante o uso diário alimentam esse conjunto.
- `retrieval_gold.csv`: para um subconjunto de requisitos, quais trechos da minha base deveriam ser recuperados.

**Métricas**

| O que mede | Métrica |
|---|---|
| Triagem | Precisão, recall e F1 da decisão candidatar / ignorar |
| Recuperação | Hit rate@k e MRR do trecho correto |
| Fidelidade da carta | % de afirmações sustentadas pelos trechos citados |
| Automação | Vagas novas por rodada, taxa de falha por fonte, tempo por rodada e % das vagas notificadas em que acabei me candidatando |

**Experimentos planejados**

| Variável | Valores |
|---|---|
| Baseline | Perfil inteiro no prompt (sem RAG) vs. RAG |
| Tamanho de chunk | por exemplo 200, 400 e 800 tokens |
| Sobreposição | 0%, 10% e 20% |
| Modelo de embedding | Multilíngue pequeno vs. maior |
| k | 3, 5 e 8 |
| Reranking | Com e sem |
| Consulta | Vaga inteira vs. um requisito por vez |
| Modelo de LLM | 2 a 3 modelos do Ollama |

**Cuidados metodológicos**

- Com conjuntos pequenos, as métricas oscilam. Cada configuração é rodada mais de uma vez e reporta média e variação, não um número único.
- A checagem de fidelidade usa um LLM como juiz, que pode errar. Uma amostra das avaliações é auditada manualmente para estimar a confiabilidade do juiz.
- Cada execução é registrada (prompt e versão, modelo de LLM, modelo de embedding, parâmetros, hash do índice e métricas), então qualquer resultado é reproduzível.

## Resultados

> A preencher conforme os experimentos forem concluídos. Esta seção é o principal entregável de aprendizado do projeto.

| Configuração | F1 triagem | Hit rate@5 | Fidelidade |
|---|---|---|---|
| Baseline (sem RAG) | – | – | – |
| RAG (configuração padrão) | – | – | – |
| RAG (melhor configuração) | – | – | – |

Análise, gráficos e lições aprendidas ficarão em `experiments/`.

## Roadmap

**Núcleo**

- [ ] **v0.1:** indexar a base pessoal e triar uma vaga colada manualmente (requisitos, evidências e nota)
- [ ] **v0.1+:** repositório com `pre-commit`, `Makefile` e CI de lint e testes
- [ ] **v0.2:** teste de 2 a 3 modelos do Ollama gerando em PT-BR, para decidir o modelo padrão
- [ ] **v0.3:** geração de carta com citações e checagem de fidelidade

**Automação (foco do projeto)**

- [ ] **v0.4:** primeiro coletor (RSS ou uma página de carreira), deduplicação, pré-filtro por palavras-chave e estado das vagas em SQLite
- [ ] **v0.5:** agendamento diário e notificação por Telegram com o resumo das melhores vagas, fechando o **primeiro ciclo automático completo**
- [ ] **v0.5+:** painel Streamlit com as telas *Vagas* e *Detalhe da vaga* (evidências por requisito) e registro de decisões, lendo o mesmo SQLite
- [ ] **v0.6:** mais fontes, resiliência (retries, logs por rodada, aviso quando uma fonte falha) e registro de decisões com `vagalens mark`
- [ ] **v0.6+:** telas *Carta* (com fidelidade destacada) e *Saúde da automação* no painel
- [ ] **v0.7:** variante do currículo em LaTeX por vaga

**Qualidade e experimentos**

- [ ] **v0.8:** conjuntos rotulados (aproveitando as marcações do uso diário), métricas e baseline sem RAG
- [ ] **v0.9:** experimentos de chunking, embeddings, k, reranking e consulta, com registro de execuções em SQLite
- [ ] **v1.0:** modo demo com dados fictícios, tela de avaliação no painel, prints e GIF no README, relatório de resultados e documentação final

**Futuro (opcional)**

- [ ] Botões de resposta no Telegram para marcar a decisão direto da notificação
- [ ] Tracing de chamadas ao LLM (Langfuse auto-hospedado)
- [ ] Empacotar o agendador e o painel com Docker Compose
- [ ] Substituir o painel por FastAPI + React, caso eu queira estudar full stack

## Limitações conhecidas

- Base pessoal pequena: o RAG pode não superar o baseline sem RAG, e isso é um resultado válido do projeto.
- Modelos locais pequenos têm qualidade limitada em português e podem errar tanto na classificação quanto no julgamento de fidelidade.
- Conjuntos rotulados pequenos geram métricas ruidosas.
- Coleta automática depende de fontes acessíveis e dos termos de uso de cada uma. Muitos sites exigem login ou JavaScript, e coletores quebram quando o site muda; por isso o modo manual (colar a vaga) continua disponível.
- O agendador precisa de uma máquina ligada no horário; a idempotência reduz o problema, mas não o elimina.
- Agendador e painel compartilham o mesmo SQLite; o modo WAL evita a maior parte dos conflitos, mas escritas simultâneas continuam sendo um ponto a testar.
- O pré-filtro por palavras-chave pode descartar vagas boas com descrição fora do padrão, então vale revisar de vez em quando o que foi filtrado.

## Privacidade e uso responsável

- Meus documentos pessoais ficam em `data/profile/`, que está no `.gitignore` e nunca entra no repositório.
- Com LLM local (Ollama), nenhum dado sai da máquina. Com API externa, os trechos recuperados são enviados ao provedor.
- Respeitar os termos de uso e o `robots.txt` das fontes de vagas.
- O sistema **não envia candidaturas**: toda carta é um rascunho e deve ser revisada.
- O painel roda apenas em `localhost` e não deve ser exposto na internet: ele mostra minha base pessoal e minhas cartas.
- Tokens do Telegram e credenciais de e-mail ficam no `.env`, fora do repositório. Mensagens de bots no Telegram não têm criptografia de ponta a ponta, por isso a notificação leva só um resumo e o caminho local do rascunho, não a carta completa nem dados pessoais.

## Licença

Distribuído sob a licença [MIT](LICENSE).
