# Validação runtime, browser e agentes especializados

Use esta referência quando a tarefa envolve comportamento que não é confiável por leitura estática: fluxo real no browser, layout responsivo, foco, modal, dropdown, erro de formulário, loading, navegação, regressão visual, performance percebida ou acessibilidade runtime.

## Quando pedir validação runtime

Validação estática é insuficiente quando a mudança altera:

- fluxo de formulário, submit, erro ou navegação;
- modal, popover, tooltip, combobox, tabs, menu ou focus trap;
- responsividade ou layout acima/abaixo de breakpoints;
- carregamento assíncrono, retry, cache, suspense ou skeleton;
- autenticação, permissão, redirecionamento ou rota protegida;
- acessibilidade de teclado/screen reader;
- performance percebida, layout shift, long task ou bundle.

## Playwright/browser como evidência

Quando houver repo e ambiente executável, preferir scripts/testes Playwright ou equivalente para:

- abrir a rota local;
- capturar console errors e failed requests;
- validar fluxo feliz e principal erro;
- verificar foco no primeiro erro de formulário;
- testar teclado: Tab, Enter, Escape;
- testar viewport mobile e desktop;
- capturar screenshot somente quando ajuda a validar layout;
- registrar comando, status e evidência.

Não afirmar que a UI funciona visualmente sem screenshot, teste browser ou evidência fornecida quando a tarefa depende disso.

## Plano mínimo de validação por tipo

| tipo de mudança | validação mínima |
|---|---|
| formulário | submit válido, primeiro erro, preservação de input, loading, success/error |
| modal/popover | abrir, fechar, Escape, click outside, foco inicial, foco preso, retorno de foco |
| tabela/lista | loading, empty, paginação, erro, mobile overflow |
| onboarding | primeiro passo, progresso, dismiss/back, estado de retorno |
| rota protegida | permitido, negado, redirect e estado sem permissão |
| performance | bundle/route impact quando disponível, lighthouse/core web vitals se aplicável |

## Agentes e separação de papéis

Quando o ambiente suporta agentes especializados, prefira separar responsabilidades em vez de pedir a um único agente para tudo:

- engenheiro frontend: implementação React/TypeScript e integração com design system;
- acessibilidade runtime: teclado, foco, labels, WCAG e validação no browser;
- performance investigator: Core Web Vitals, Lighthouse, layout shift, long tasks e rede lenta;
- tester/playwright: testes E2E, screenshots, logs e regressão visual;
- qa/produtor: bug report, checklist de aceite, coordenação e sign-off sem alterar código.

A skill deve recomendar esses papéis como padrão de trabalho quando útil, mas não depender deles para responder.

## Evidência e relatório

Sempre separar:

- executado: comandos reais, screenshots, logs, testes e status;
- estático: inferências de código, estrutura ou padrões;
- recomendado: validações que ainda precisam rodar;
- bloqueado: dependência de ambiente, credencial, backend, dados ou browser.

Modelo de fechamento:

```md
## validação runtime
- executado: ...
- evidência: ...
- não executado: ...
- riscos restantes: ...
```
