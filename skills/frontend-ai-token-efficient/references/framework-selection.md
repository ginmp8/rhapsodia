# Seleção de framework e stack

Use esta referência quando a demanda envolver escolha de framework, stack base ou trade-off entre simplicidade, seo, ssr, full-stack e manutenção por ia.

## Recomendação padrão

Para spa corporativa, backoffice, dashboard, onboarding, cadastro, primeiro acesso, fluxos autenticados e sistemas internos, prefira:

```txt
react + typescript + vite
```

Stack auxiliar recomendada:

```txt
react router ou tanstack router
tanstack query
zod
react hook form
vitest
testing library
eslint
prettier
msw quando mocks de api forem relevantes
```

Motivo: menos convenção implícita, bootstrap enxuto, estrutura explícita e menor contexto obrigatório para ia.

## Matriz de escolha

| contexto | escolha preferida | motivo |
|---|---|---|
| spa interna consumindo api | react + vite + typescript | simplicidade e baixo contexto |
| backoffice, dashboard, onboarding, cadastro | react + vite + typescript | foco em fluxo e formulários |
| produto público com seo | next.js app router | ssr, ssg, rotas públicas |
| app full-stack react com loaders/actions | react router framework mode | boa separação sem a carga completa do next |
| time maduro em tanstack e aceita tecnologia mais nova | tanstack start | type safety forte e ecossistema tanstack |
| docs, site institucional, blog, landing page | astro + react | html estático com ilhas interativas |

## Quando escolher next.js

Escolha next.js quando pelo menos um ponto for real:

- seo ou indexação importa;
- ssr ou ssg melhora o produto;
- existem páginas públicas relevantes;
- autenticação server-side é necessária;
- bff ou route handlers no mesmo projeto reduzem acoplamento;
- o time domina app router e server/client components.

Em sistemas internos sem seo e com backend separado, next.js pode aumentar contexto e risco de uso incorreto de server/client boundaries.

## Quando escolher astro

Use astro quando a maior parte do produto é conteúdo estático, documentação, landing pages ou portal institucional. Evite como padrão para backoffice denso, formulários interdependentes e fluxos com muito estado autenticado.

## Critério final

Escolha o framework que minimiza a quantidade de regras implícitas que a ia precisa conhecer para alterar uma feature. Framework poderoso é vantagem apenas quando a necessidade dele é real.
