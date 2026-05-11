# Arquitetura frontend para baixo consumo de contexto

Use esta referência para estrutura de projeto, regras de dependência, duplicidade, nomes e documentação de feature.

## Estrutura base

```txt
src/
  app/
    main.tsx
    router.tsx
    providers.tsx
    query-client.ts
    env.ts

  features/
    account-opening/
      README.md
      routes/
      components/
      hooks/
      api/
      model/
      tests/
      index.ts

  entities/
    company/
      components/
      api/
      model/

  shared/
    ui/
    api/
    lib/
    types/

  pages/
  assets/
  test/
```

Adapte nomes de domínio ao projeto. A regra é que uma demanda comum caiba mentalmente dentro de uma feature mais contratos compartilhados pequenos.

## Responsabilidade por pasta

| pasta | responsabilidade |
|---|---|
| `app/` | bootstrap, providers, rotas, configuração global |
| `pages/` | composição de rotas quando o framework separar pages de features |
| `features/` | fluxos de negócio e casos de uso |
| `entities/` | entidades reutilizáveis de domínio sem fluxo específico |
| `shared/` | código genérico sem regra de negócio |
| `test/` | setup global e helpers de teste |

## Regras de dependência

```txt
app      -> pages, features, entities, shared
pages    -> features, entities, shared
features -> entities, shared
entities -> shared
shared   -> bibliotecas externas
```

Proibido:

```txt
shared -> features
entities -> features
feature a -> feature b diretamente
```

Se duas features precisam compartilhar algo, extraia para `entities` ou `shared` somente quando a regra for estável e sem dependência do fluxo.

## Duplicidade controlada

Aceite duplicidade local quando ela preserva isolamento de contexto.

Regra prática:

```txt
1ª ocorrência: manter local
2ª ocorrência: observar diferenças
3ª ocorrência: avaliar extração
```

Extraia para `shared/ui` apenas componentes visuais sem regra de negócio, como botão, input, modal, tabela, empty state e loading state.

Extraia para `entities` quando o componente representa uma entidade de domínio reutilizável, como `CompanyCard`, `UserAvatar` ou `CompanyDocumentBadge`.

Evite extrair formulários de negócio cedo demais. Dois formulários parecidos podem ter regras diferentes de criação, atualização, auditoria, elegibilidade, permissões e payload.

## README por feature

Cada feature relevante deve ter `README.md` curto com:

- responsabilidade;
- entradas e saídas;
- arquivos principais;
- regras do fluxo;
- dependências externas;
- testes importantes;
- decisões não óbvias.

Exemplo:

```md
# account-opening

fluxo responsável pela abertura de conta pj.

## responsabilidades
- coletar dados da empresa
- validar sócios e representantes
- enviar solicitação de abertura
- exibir status inicial

## arquivos principais
- routes/AccountOpeningPage.tsx: tela principal
- components/CompanyForm.tsx: formulário de empresa
- model/account-opening.schema.ts: validações
- api/account-opening.api.ts: chamadas http

## regras
- componentes não chamam api diretamente
- validação fica em model/*.schema.ts
- conversão backend/frontend fica em mappers
```

## Nomes que economizam contexto

Prefira nomes específicos:

```txt
AccountOpeningPage.tsx
CompanyForm.tsx
PartnerList.tsx
account-opening.api.ts
account-opening.schema.ts
account-opening.mappers.ts
useCreateAccountOpening.ts
```

Evite nomes que exigem abrir o arquivo para entender:

```txt
Page.tsx
Form.tsx
List.tsx
api.ts
helpers.ts
useData.ts
manager.ts
processor.ts
```

## Tamanho de arquivos

Use como alerta, não como dogma:

```txt
até 150 linhas: saudável
150-300: aceitável
300-500: atenção
500+: quebrar ou justificar
```

Quando crescer, extraia subcomponentes, hooks específicos, schemas, mappers, funções puras ou testes.
