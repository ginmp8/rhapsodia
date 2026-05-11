---
name: frontend-ai-token-efficient
description: use quando o usuário pedir arquitetura, revisão, implementação, refatoração, checklist, padrões, scaffolding, ux/cro, validação runtime ou segurança de frontend react/typescript para que ia ou agentes codem com baixo consumo de tokens e manutenção humana. cobre vite, next.js, react router, estrutura por feature, contratos, forms, onboarding, estado, api, design system, testes, acessibilidade, observabilidade e prevenção de vazamentos. não use para backend puro, mobile nativo, design visual isolado sem código, ou criação de skills.
---

# Frontend AI Token Efficient

## Missão

Ajudar a projetar, revisar e orientar frontends react/typescript que sejam fáceis para agentes de ia modificarem com baixo contexto e seguros para manutenção humana. Priorizar estruturas locais, contratos explícitos, regras de dependência, validação verificável e prevenção de vazamentos.

## Escopo

Use para:

- escolher stack ou framework frontend com foco em manutenção por ia;
- propor estrutura de projeto react/typescript, vite, next.js ou react router;
- revisar arquitetura, pastas, dependências, componentes, formulários, estado, api, testes e documentação para ia;
- revisar qualidade de ux quando ligada a implementação: formulários, onboarding, empty states, ctas, fricção, responsividade e coerência com design system;
- orientar validação runtime com browser/playwright quando a tarefa envolver interação real, foco, modal, erro de formulário, responsividade ou regressão visual;
- gerar guias como AI_CONTEXT.md, ARCHITECTURE.md, CONVENTIONS.md, DEPENDENCY_RULES.md, TESTING_GUIDE.md, API_GUIDE.md, UI_GUIDE.md e SECURITY_FRONTEND.md;
- revisar riscos de vazamento no frontend: secrets, tokens, logs, analytics, storage, urls, source maps, xss, csp e cache;
- orientar implementação ou refatoração mantendo o menor conjunto de arquivos necessário.

Não use para backend puro, mobile nativo, design visual sem código, skill creation, auditoria de segurança de infraestrutura, ou implementação em repositório sem escopo frontend claro.

## Regras centrais

- Reduza contexto antes de reduzir linhas: uma mudança deve exigir ler poucos arquivos da feature e contratos compartilhados.
- Organize por feature e domínio; use pastas técnicas apenas dentro de uma feature ou em camadas realmente compartilhadas.
- Prefira duplicidade local pequena a abstração global prematura.
- Não coloque regra de negócio em `shared`.
- Não permita chamada http direta em componentes; use camada `api/`, hooks de orquestração e mappers.
- Nunca invente contrato de api; peça, leia ou marque como suposição explícita.
- Nunca trate frontend como fronteira de segurança. Autorizações reais pertencem ao backend.
- Nunca sugerir segredo no bundle, token sensível em storage web ou payload sensível em logs/analytics.
- Em projeto existente, preserve linguagem visual, biblioteca de ui, tokens, padrões de css e componentes antes de propor estética nova.
- Em interface nova sem design system, escolha direção visual intencional e tokens explícitos; evite aparência genérica gerada por ia.
- Separe validação executada, validação recomendada e raciocínio estático.

## Entradas esperadas

Inferir e seguir com suposições quando possível:

1. tipo de projeto: spa interna, backoffice, dashboard, produto público, site de conteúdo ou app full-stack;
2. stack atual ou pretendida: react, vite, next.js, react router, tanstack, astro;
3. artefato alvo: estrutura de pastas, feature, componente, diff, pr, guia, checklist ou política de segurança;
4. restrições: design system, autenticação, compliance, dados sensíveis, padrões do time, ferramenta de ia, testes e deploy;
5. saída esperada: recomendação, plano, checklist, arquivos markdown, revisão, patch conceitual ou comandos de validação.

## Modos

Escolha um modo principal:

| modo | use quando | saída principal |
|---|---|---|
| `framework-selection` | escolher vite, next.js, react router, tanstack start, astro ou stack auxiliar | matriz de decisão e recomendação |
| `architecture-plan` | desenhar estrutura, dependências, features, shared, entities, docs para ia | proposta de arquitetura e regras |
| `implementation-guidance` | orientar alteração frontend específica sem editar repo diretamente | passos mínimos, arquivos prováveis, validação |
| `code-review` | revisar estrutura, componente, hook, feature, diff ou pr frontend | achados por severidade e menor correção |
| `ux-flow-review` | revisar formulários, onboarding, empty states, ctas, acessibilidade visual e fricção | achados de ux, hipótese e menor ajuste |
| `runtime-validation` | planejar ou interpretar testes browser/playwright, screenshots, logs e fluxos reais | plano de validação e evidência esperada |
| `security-review` | revisar risco de vazamento frontend | achados, controles, checklist e gates |
| `ai-context-docs` | criar ou revisar guias para agentes de ia no repo | arquivos markdown sugeridos ou conteúdo pronto |
| `repo-scan` | há um repositório local e vale executar checagem leve | relatório do script e leitura crítica |

## Carregamento progressivo

Leia somente o necessário:

- `references/framework-selection.md`: escolha de framework e stack.
- `references/architecture.md`: estrutura por feature, duplicidade, imports e documentação de contexto.
- `references/implementation-patterns.md`: formulários, estado, api, mappers, design system, testes, acessibilidade, performance e observabilidade.
- `references/ux-quality.md`: design adaptado ao projeto, qualidade visual, cro de formulários, onboarding, empty states, métricas e experimentos.
- `references/runtime-validation.md`: validação browser/playwright, evidência visual, logs, acessibilidade runtime, performance e agentes especializados.
- `references/security.md`: prevenção de vazamento e controles defensivos frontend.
- `references/review-checklists.md`: checklists de arquitetura, pr, segurança e manutenção por ia.
- `references/ai-context-docs.md`: modelos de arquivos markdown para orientar agentes.
- `references/output-contracts.md`: formatos de resposta para recomendações, revisão, segurança e documentação.
- `examples/activation-scenarios.md`: calibração de ativação e fronteiras.
- `evals/activation-scenarios.json`: cenários planejados, não métricas executadas.
- `scripts/check_frontend_ai_package.py`: inspeção local opcional de estrutura e riscos comuns.

## Workflow

1. Classifique a demanda e escolha o modo.
2. Declare suposições que afetam a resposta, especialmente tipo de app, sensibilidade dos dados e framework.
3. Se houver arquivos, diff ou repo, inspecione antes de concluir; não generalize sem evidência.
4. Defina o menor contexto útil: feature, entity, shared/api, shared/ui, docs, testes e, quando houver ui real, screenshots ou validação browser.
5. Em projeto existente, analise padrões visuais e componentes antes de criar novos.
6. Aplique a referência do modo escolhido.
7. Produza a resposta no contrato apropriado.
8. Inclua validação: comandos executados, checagens estáticas, testes recomendados e riscos não verificados.

## Uso do script opcional

Quando houver acesso ao repositório local e o usuário pedir auditoria rápida, rode:

```bash
python scripts/check_frontend_ai_package.py --target <frontend-root> --format markdown --output <report.md>
```

Use o resultado como triagem. O script não substitui revisão humana: confirme falsos positivos, leia arquivos relevantes e explique limitações.

## Output contract

Este é o contrato de saída principal da skill.

## Saída esperada

Use `references/output-contracts.md` para formatos. Por padrão inclua:

1. suposições;
2. recomendação ou achados;
3. estrutura, arquivos ou mudanças mínimas;
4. validação executada e recomendada;
5. riscos, dependências e próximo passo de maior valor.

## Stop conditions

Pare, reduza o escopo ou sinalize bloqueio quando:

- a mudança exige contrato de api inexistente e seria necessário inventar payload;
- o usuário pede para colocar segredo, client secret, token de serviço, chave privada ou senha no frontend;
- a resposta dependeria de política interna, compliance ou autorização que não foi fornecida;
- o repositório ou diff não está disponível e a pergunta exige evidência sobre arquivos reais;
- a alteração proposta criaria abstração global sem caso de uso repetido e estável;
- a solução dependeria de segurança apenas no frontend;
- validação, benchmark ou readiness seriam alegados sem execução ou evidência.
