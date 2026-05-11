# Cenários de ativação

Use estes cenários para calibrar quando aplicar a skill.

## Deve ativar

- "qual estrutura react ajuda a ia consumir menos tokens?"
- "revise este frontend para ficar melhor para agentes de ia manterem"
- "crie um AI_CONTEXT.md para meu projeto react"
- "vite ou next.js para um backoffice de onboarding?"
- "como evitar vazamento de token no frontend?"
- "avalie se esta feature deveria ir para shared ou ficar duplicada"
- "gere um checklist de pr frontend para ia"

## Não deve ativar

- "corrija este endpoint c#"
- "crie uma skill nova"
- "faça um layout visual no figma"
- "configure terraform de cloudfront"
- "explique react do zero sem foco em arquitetura, ia ou manutenção"

## Ambíguo

- "melhore meu projeto" -> perguntar ou inferir se é frontend react e se o foco é arquitetura, manutenção, segurança ou ia.
- "crie uma tela" -> usar somente se houver foco em padrões de frontend; caso seja design visual puro, não ativar.
- "revisa segurança" -> usar se o alvo for frontend; caso seja infraestrutura, backend ou cloud, encaminhar para revisão adequada.


- deve ativar: "revise este formulário de abertura de conta para reduzir fricção, mantendo compliance" -> usar `ux-flow-review` com contratos, segurança e métricas.
- deve ativar: "crie um AGENTS.md para separar implementação frontend, QA browser e acessibilidade" -> usar `ai-context-docs` e `runtime-validation`.
- deve ativar: "como validar esse modal no Playwright?" -> usar `runtime-validation`.
- ambíguo: "deixe essa tela mais bonita" -> se houver código/projeto, aplicar padrões existentes e qualidade visual; se for design visual puro sem código, não ativar.
