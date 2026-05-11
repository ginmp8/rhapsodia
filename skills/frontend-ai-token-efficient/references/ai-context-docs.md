# Documentação curta para agentes de ia

Use esta referência para criar ou revisar arquivos que orientam agentes no repositório. Mantenha guias curtos, objetivos e próximos das decisões reais do projeto.

## Arquivos recomendados

```txt
AI_CONTEXT.md
ARCHITECTURE.md
CONVENTIONS.md
DEPENDENCY_RULES.md
TESTING_GUIDE.md
API_GUIDE.md
UI_GUIDE.md
SECURITY_FRONTEND.md
UX_GUIDE.md
RUNTIME_VALIDATION.md
AGENTS.md ou .github/copilot-instructions.md quando a ferramenta do time suportar
*.agent.md quando houver agentes especializados versionados no repo
```

Crie apenas os arquivos que terão conteúdo útil. Um guia curto e lido vale mais que uma documentação longa e ignorada. Para ferramentas que suportam instruções/agentes por arquivo, mantenha esses arquivos versionados, pequenos e alinhados aos mesmos contratos da skill.

## Modelo de AI_CONTEXT.md

```md
# AI Context

## objetivo
este projeto prioriza alterações locais, baixo acoplamento e legibilidade.

## estrutura
- app/: bootstrap, providers e rotas
- features/: fluxos de negócio
- entities/: entidades reutilizáveis
- shared/: código genérico sem regra de negócio

## regras para alterações
1. antes de alterar uma feature, leia o readme dela.
2. não crie abstrações globais sem necessidade.
3. não mova código para shared se houver regra de negócio.
4. não chame api diretamente em componentes.
5. não use any sem justificativa local.
6. altere o menor número possível de arquivos.
7. adicione ou ajuste testes quando houver regra de negócio.
```

## Modelo de DEPENDENCY_RULES.md

```md
# Dependency Rules

permitido:
- app -> pages/features/entities/shared
- pages -> features/entities/shared
- features -> entities/shared
- entities -> shared
- shared -> bibliotecas externas

proibido:
- shared -> features
- entities -> features
- feature a -> feature b
```

## Modelo de SECURITY_FRONTEND.md

```md
# Frontend Security Rules

## segredos
- nunca colocar secrets no frontend.
- variáveis vite_* e next_public_* são públicas quando entram no bundle.
- integrações com segredo devem passar pelo backend ou bff.

## tokens
- não armazenar access token ou refresh token em localStorage.
- preferir cookie httponly + secure + samesite quando aplicável.
- não logar authorization header.

## dados sensíveis
- não colocar pii em url.
- não logar payload completo.
- não enviar pii para analytics sem aprovação.
- mascarar documento, telefone e e-mail quando possível.

## xss
- não usar dangerouslySetInnerHTML sem sanitização aprovada.
- validar urls externas.
- não usar eval ou new Function.
- não renderizar html vindo de usuário ou backend sem sanitizer.

## apis
- componentes não chamam fetch ou axios diretamente.
- usar camada api central.
- backend sempre revalida autorização.

## observabilidade
- eventos devem passar por sanitizeForTelemetry.
- erros enviados para observabilidade não devem conter payload sensível.
```

## Modelo de CONVENTIONS.md

```md
# Conventions

## nomenclatura
- componentes react: pascalcase
- hooks: useNomeDaCoisa
- arquivos de api: *.api.ts
- tipos: *.types.ts
- schemas: *.schema.ts
- mappers: *.mappers.ts

## componentes
- componentes não conhecem detalhes http.
- componentes de feature não são importados por outras features.
- componentes em shared/ui não contêm regra de negócio.

## estado
- server state: tanstack query
- estado local de ui: useState/useReducer
- estado global: apenas quando compartilhado entre áreas independentes
```

## Critério de qualidade

Cada arquivo deve responder a uma pergunta prática de desenvolvimento. Se um guia não muda decisões de implementação ou revisão, remova ou reduza.


## Modelo de UX_GUIDE.md

```md
# UX Guide

## princípios
- preservar design system existente antes de criar variações.
- formularios devem reduzir fricção e manter labels visíveis.
- empty states devem explicar valor e oferecer próxima ação.
- onboarding deve reduzir time-to-value e focar um objetivo por sessão.

## formulários
- validar inline sem punir enquanto digita.
- focar primeiro erro no submit inválido.
- preservar dados após erro.
- medir start, completion, drop-off e error rate quando otimização for objetivo.
```

## Modelo de RUNTIME_VALIDATION.md

```md
# Runtime Validation

## quando rodar browser/playwright
- mudança em formulário, modal, dropdown, popover, rota, loading/error/empty ou responsividade.
- alteração de foco, teclado ou acessibilidade.
- claim de performance ou layout.

## evidência mínima
- comando executado.
- rota/viewport testado.
- console errors e failed requests.
- fluxo feliz e principal erro.
- screenshots quando layout for parte da aceitação.
```

## Modelo de AGENTS.md

```md
# Agents

## papéis
- frontend: implementa mudança local seguindo features, contracts e design system.
- qa/browser: valida fluxo real, screenshots, console e failed requests.
- accessibility: revisa teclado, foco, labels, contraste e erros.
- performance: investiga core web vitals, layout shift, long tasks e bundle quando medido.

## regra
agentes não devem alterar escopo, criar abstrações globais ou alegar validação sem evidência.
```
