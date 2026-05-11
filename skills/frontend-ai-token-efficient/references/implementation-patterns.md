# Padrões de implementação frontend

Use esta referência para orientar mudanças em formulários, estado, api, design system, testes, acessibilidade, performance e observabilidade.

## Contratos de api

A ia não deve inventar payload. Prefira contrato explícito:

- openapi ou tipos gerados;
- tipos request/response versionados;
- fixtures canônicas;
- mappers entre backend e frontend;
- schemas de validação quando resposta for crítica.

Padrão de feature:

```txt
api/account-opening.api.ts
model/account-opening.types.ts
model/account-opening.schema.ts
model/account-opening.mappers.ts
tests/account-opening.fixtures.ts
```

Componentes não chamam `fetch` ou `axios` diretamente. Eles chamam hooks de fluxo ou handlers recebidos por props.

## Formulários

Padrão preferido:

```txt
react hook form + zod
schema em model/*.schema.ts
mapper para request em model/*.mappers.ts
api em api/*.api.ts
estado visual no componente
```

Fluxo:

```txt
ui do formulário -> schema validation -> mapper -> api request -> tratamento padronizado de erro
```

Evite montar payload manualmente no `onSubmit` dentro do componente quando houver regra de transformação.

## Estado

Classifique antes de escolher ferramenta:

| tipo | ferramenta preferida |
|---|---|
| estado local de ui | `useState` ou `useReducer` |
| estado de formulário | react hook form |
| estado de servidor | tanstack query |
| estado global transversal | store/context com parcimônia |
| estado derivado | calcular, não armazenar |

Não coloque tudo em store global. Estado global deve cobrir sessão, usuário autenticado, permissões, tema, flags ou preferências realmente transversais.

## Permissões

Frontend pode esconder ações e rotas, mas backend deve revalidar tudo. Prefira funções nomeadas:

```ts
canCreateAccountOpening(user)
canApproveCompanyUpdate(user)
canViewPartnerDetails(user)
```

Evite espalhar strings mágicas de roles em componentes.

## Design system

Em projeto existente, use primeiro os componentes e tokens já adotados. Antes de criar componente visual novo, procure equivalente no design system ou em features próximas. Só crie variação nova quando houver lacuna real e documente o motivo.

Tenha um conjunto limitado de blocos reutilizáveis:

```txt
shared/ui/Button
shared/ui/Input
shared/ui/Select
shared/ui/Modal
shared/ui/DataTable
shared/ui/Alert
shared/ui/FormField
shared/ui/EmptyState
shared/ui/ErrorState
shared/ui/LoadingState
```

A ia deve montar telas com blocos existentes antes de criar variações novas.

## Qualidade visual sem design solto

Para novas interfaces sem design system claro, defina direção visual, tokens e hierarquia antes de implementar. Para sistemas internos, prefira precisão, legibilidade, contraste, densidade controlada e feedback explícito a estética chamativa. Para produto público, a identidade pode ser mais expressiva, mas precisa preservar acessibilidade, performance e responsividade.

Evite padrões genéricos de IA: cards repetitivos sem hierarquia, roxo-gradiente por padrão, animações decorativas demais, fontes/paletas aleatórias e layouts sem relação com o domínio.

## Loading, empty, error e success

Toda tela de dados deve considerar:

```txt
loading
empty
error
success
permission denied
partial data
retry
```

Padrão:

```tsx
if (isLoading) return <LoadingState />;
if (error) return <ErrorState error={error} onRetry={refetch} />;
if (!data.length) return <EmptyState title="nenhum registro encontrado" />;
```

## Formulários de alta qualidade

Além de schema e mapper, revisar UX do formulário:

- remover ou adiar campos sem uso comprovado;
- labels sempre visíveis; placeholder apenas como exemplo;
- campos fáceis antes de campos sensíveis;
- uma coluna por padrão, especialmente mobile;
- teclado mobile correto;
- inline validation sem punir enquanto digita;
- erro específico, próximo ao campo e sem limpar input;
- no submit inválido, focar primeiro erro;
- CTA deve comunicar ação e resultado quando fizer sentido;
- medir form start, completion, field drop-off e error rate quando otimização for objetivo.

## Onboarding e empty states

Para primeiro uso, onboarding ou ativação:

- identifique o evento de ativação ou `aha moment`;
- reduza passos até primeiro valor;
- uma meta principal por sessão;
- empty state deve explicar valor, mostrar exemplo/preview e oferecer ação primária;
- checklist deve ter poucos itens, quick wins e opção de dismiss;
- tours devem ser curtos, contextuais e não repetitivos;
- medir activation rate, time-to-activation e feature adoption.

## Testes

Priorize testes de comportamento:

- schemas;
- mappers;
- regras de permissão;
- hooks de fluxo;
- componentes com regra relevante;
- fluxos críticos;
- regressões de bug.

Evite testes frágeis de classe css ou estrutura visual sem comportamento.

Fixtures devem ser nomeadas por intenção:

```ts
validAccountOpeningRequest
companyWithoutRequiredPartner
userWithoutApprovalPermission
```

## Acessibilidade

Regras mínimas:

- cada input tem label;
- botão é `button`, não `div` clicável;
- erros são associados aos campos;
- modal gerencia foco;
- não depender apenas de cor;
- estados loading/error são anunciáveis quando relevante;
- links e botões têm nomes acessíveis.

## Validação browser

Quando comportamento depende do navegador, complemente testes unitários com Playwright ou ferramenta equivalente. Priorize fluxos reais: formulário, modal, foco, teclado, responsividade, console errors, failed requests, loading/error/empty states e screenshots quando layout importar.

## Performance

Priorize clareza. Otimize após sinal concreto.

Boas práticas:

- paginação para listas grandes;
- virtualização para tabelas muito grandes;
- code splitting por rota quando útil;
- evitar estado global que re-renderiza tudo;
- não adicionar `useMemo`, `useCallback` e `React.memo` por reflexo;
- medir antes de declarar ganho de performance.

## Observabilidade

Crie wrapper central:

```txt
shared/observability/track-event.ts
shared/observability/report-error.ts
shared/observability/sanitize-event.ts
```

Não logue payload completo, headers ou dados pessoais. Eventos devem usar códigos, etapas e metadados mínimos.
