💣 PARTE 2 — Perguntas Difíceis + Respostas Preparadas

Aqui estão as perguntas que um dev sênior realmente vai fazer.

❓1. “Por que não chamar a API direto do LangChain?”
Resposta:

Porque você cria:

Acoplamento com framework

Dependência de modelo

Repetição de lógica

Falta de governança central

O MCP:

Centraliza integração

Desacopla modelo de API

Permite trocar LLM sem alterar backend

❓2. “Isso não adiciona latência?”
Resposta técnica:

Sim, há uma camada extra.

Mas:

É apenas uma chamada HTTP adicional

O overhead é mínimo comparado ao tempo do LLM

Ganha-se governança e padronização

Latência típica extra: poucos milissegundos.

❓3. “E se o modelo chamar a tool errada?”
Resposta:

O MCP não decide.

A responsabilidade é:

Prompt engineering

Tool descriptions claras

Validação no backend

Sempre valide no backend.
Nunca confie na IA.

❓4. “Como controlar escopo de tools por usuário?”

Resposta madura:

Não esconda tools no MCP

Controle no backend via autorização

O backend é a fonte de verdade

Opcionalmente:

Gerar servidores MCP por domínio

Usar middleware para bloquear tools

❓5. “Como versionar isso?”

Boa pergunta sênior.

Resposta:

Versione o OpenAPI

Versione o servidor MCP

Use tags no Git

Deploy via CI/CD normal

O MCP é um microsserviço.

❓6. “Como escalar horizontalmente?”

Resposta:

Stateless por padrão

Rodar múltiplas réplicas

Redis se houver sessão

Load balancer na frente

❓7. “E se o Swagger mudar?”

Resposta:

Recarregar no startup

Ou implementar cache

Ideal: CI valida contrato antes de deploy

❓8. “Isso é seguro mesmo?”

Resposta profissional:

Seguro se:

Nunca usar token global super admin

Nunca deixar LLM ver token real

Sempre validar backend

Usar HTTPS

Monitorar chamadas

Inseguro se usado como atalho.

❓9. “Posso usar isso como API Gateway?”

Resposta:

Não completamente.

Ele é um gateway para IA.
Não substitui Kong, Apigee, etc.

Mas pode complementar.

❓10. “Isso é vendor lock-in da Anthropic?”

Resposta:

Não.

MCP é protocolo aberto.
Funciona com qualquer LLM que suporte tool calling.

🎯 Fechamento Forte para Devs

“O MCP não é moda.

É a padronização da camada de integração entre IA e sistemas.

Quem dominar isso vai definir como a empresa usa IA em produção.”