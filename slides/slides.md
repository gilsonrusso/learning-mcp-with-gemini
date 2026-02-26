# Treinamento: Introdução ao MCP em Produção com FastMCP

**Duração:** 30 minutos  
**Público-Alvo:** Desenvolvedores e Engenheiros de Software Sênior  
**Objetivo:** Demonstrar como expor APIs corporativas existentes para Agentes de IA de forma segura, escalável e automatizada usando o Model Context Protocol (MCP).

---

## 1. Estrutura dos Slides e Roteiro de Fala (10 a 15 minutos)

### Slide 1: O Problema e o Model Context Protocol (MCP)
* **Tópicos:**
  * LLMs nascem isolados do contexto corporativo.
  * Integrações customizadas (plugins) criam dívida técnica e fragmentação.
  * O MCP é o padrão aberto (criado pela Anthropic) para padronizar essa comunicação.
  * O **FastMCP** é o framework Python definitivo (o "FastAPI dos Agentes de IA").

> **Roteiro de Fala (Speaker Track):** > "Bom dia, pessoal. Hoje vamos resolver um dos maiores problemas na adoção de IA corporativa: como conectar nossos modelos de linguagem aos nossos bancos de dados e APIs privadas sem criar um pesadelo de segurança e manutenção. Para isso, usamos o Model Context Protocol (MCP). Em vez de escrever integrações específicas para o LangChain, outra para o Claude, outra para o Copilot, nós criamos um único Servidor MCP. Hoje vamos focar no FastMCP, um framework em Python que torna a criação desses servidores tão simples quanto criar uma API em FastAPI."



---

### Slide 2: Geração Automática com OpenAPI
* **Tópicos:**
  * Reaproveitamento de infraestrutura existente.
  * `FastMCP.from_openapi`: De Swagger para Ferramentas (Tools) de IA instantaneamente.
  * Mapeamento semântico de rotas REST para intenções do LLM.

> **Roteiro de Fala (Speaker Track):** > "Como desenvolvedores experientes, vocês não querem reescrever a camada de negócios que já existe nas nossas APIs REST. A grande vantagem do FastMCP para ambientes enterprise é a capacidade de ler uma especificação OpenAPI (o nosso bom e velho Swagger) e, dinamicamente, transformar cada endpoint em uma ferramenta que a IA sabe como e quando chamar. A validação de payload, as descrições e os parâmetros já vêm todos prontos a partir da sua documentação OpenAPI."

---

### Slide 3: Autenticação Dinâmica e Segurança
* **Tópicos:**
  * O problema do *Token Passthrough* (Vazamento de credenciais via LLM).
  * Autenticação Estática (Bearer) vs Autenticação Dinâmica (Fábrica de Tokens via OAuthProxy).
  * Interceptação de cabeçalhos (Middlewares/Auth Customizado).

> **Roteiro de Fala (Speaker Track):** > "O maior desafio de colocar isso em produção é a segurança. Como o LLM chama a API de RH sem ter acesso de super admin? A regra de ouro é: o LLM não deve conhecer o token real da sua API. No ecossistema MCP, usamos um padrão de 'Fábrica de Tokens' ou repassamos o token do usuário final (via LangChain ou interface cliente) no momento da requisição. O FastMCP atua como um cofre e um proxy, interceptando a chamada da IA, injetando o Bearer Token do usuário que está logado naquele momento, e só então fazendo a requisição para a nossa API real. Isso garante governança e evita o perigoso *Token Passthrough*."



---

### Slide 4: Elevando o FastMCP para Produção
* **Tópicos:**
  * **Transporte HTTP (ASGI):** Pronto para Uvicorn, Gunicorn e Kubernetes.
  * **Observabilidade:** Rastreamento distribuído nativo com OpenTelemetry.
  * **Estado e Escala:** Substituição do estado em memória por Redis para múltiplas réplicas.

> **Roteiro de Fala (Speaker Track):** > "Para fechar a parte conceitual: como isso roda de fato no nosso Kubernetes? Primeiro, não usamos o transporte padrão por terminal (STDIO). O FastMCP expõe uma aplicação ASGI nativa, pronta para rodar em containers atrás de um Load Balancer. Para escalabilidade horizontal com múltiplas réplicas, conectamos ele a um cluster Redis para gerenciamento de sessão e tokens OAuth. E para fechar com governança, ele possui instrumentação nativa com OpenTelemetry. Toda ferramenta que a IA invoca gera um *trace* padronizado direto no nosso Datadog ou Grafana. Não é apenas um script, é um microsserviço de produção."



---

## 2. Demonstração Prática (15 a 20 minutos)

> **Roteiro de Fala (Speaker Track):** > "Vamos ver isso funcionando na prática. Vou levantar um servidor FastMCP que consome o OpenAPI de uma API existente e configura uma classe de segurança para garantir que cada chamada da IA utilize o token do usuário atual, sem fixar senhas globais no código."

### Passo 1: Instalação
Mostre no terminal os pacotes necessários:
```bash
pip install fastmcp httpx