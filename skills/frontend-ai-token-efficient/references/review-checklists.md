# Checklists de revisão frontend para ia

Use estes checklists em revisões de pr, arquitetura, segurança e manutenibilidade.

## Checklist de arquitetura

- a alteração ficou restrita à feature correta?
- a demanda pode ser entendida lendo poucos arquivos?
- alguma regra de negócio foi colocada em `shared`?
- feature está importando outra feature diretamente?
- `shared` ou `entities` importam `features`?
- nomes de arquivos e funções explicam o domínio?
- há abstração global criada antes de uso repetido e estável?
- duplicidade local foi mantida quando a extração pioraria clareza?
- arquivos com mais de 300 linhas foram justificados ou quebrados?
- o README da feature precisa ser atualizado?

## Checklist de implementação

- componentes chamam hooks ou handlers, não `fetch`/`axios` direto?
- tipos, schemas, mappers e fixtures foram atualizados juntos?
- contrato de api foi lido ou marcado como suposição?
- loading, empty, error, success e permission denied foram considerados?
- estado de servidor usa cache apropriado em vez de store manual?
- estado derivado foi calculado em vez de armazenado?
- testes cobrem comportamento relevante?
- acessibilidade básica foi preservada?

## Checklist de UX, forms e onboarding

- o componente respeita design system, tokens e padrões visuais existentes?
- há direção visual clara quando a UI é nova?
- a hierarquia visual deixa a ação principal evidente?
- o formulário pede apenas campos necessários agora?
- labels continuam visíveis e placeholders não substituem labels?
- erros são específicos, próximos ao campo e preservam input?
- mobile usa teclado e touch targets adequados?
- empty state explica valor e oferece próxima ação?
- onboarding reduz time-to-value e foca uma meta por sessão?
- checklist/tour pode ser dispensado e não bloqueia valor principal sem motivo?
- métricas de fricção, ativação ou conversão foram consideradas quando relevantes?

## Checklist de validação runtime

- fluxo principal foi validado no browser ou há justificativa para não executar?
- console errors e failed requests foram verificados?
- modal/popover/dropdown tratam foco, Escape e retorno de foco?
- submit inválido foca primeiro erro?
- mobile e desktop foram considerados?
- screenshot ou teste visual foi usado quando layout era parte do risco?
- performance foi medida antes de qualquer claim?
- validação executada foi separada de recomendada?

## Checklist de segurança

- alguma variável pública contém segredo?
- algum token foi salvo em localStorage, sessionStorage ou indexedDB?
- algum dado sensível foi colocado em url?
- algum payload completo foi logado?
- algum dado sensível foi enviado para analytics ou observabilidade?
- foi usado `dangerouslySetInnerHTML`?
- urls externas foram validadas?
- permissões são revalidadas no backend?
- csp e headers continuam compatíveis?
- source maps estão controlados em produção?
- cache local não persiste dados sensíveis?
- nova dependência é realmente necessária?

## Checklist para pr feito por ia

- a ia declarou suposições relevantes?
- a ia listou arquivos alterados e por quê?
- a ia evitou alterações fora do escopo?
- a ia separou validação executada de validação sugerida?
- a ia não alegou performance, segurança ou readiness sem evidência?
- a ia não adicionou abstração global por conveniência?
- a ia atualizou documentação curta quando o comportamento da feature mudou?

## Severidade em revisão

| severidade | critério |
|---|---|
| crítica | vazamento de segredo, bypass de autorização, xss provável, perda de dados sensíveis |
| alta | acoplamento estrutural grave, token em storage, payload sensível em logs, contrato inventado |
| média | abstração prematura, teste ausente em regra crítica, duplicidade técnica clara, estado global indevido |
| baixa | nome ruim, docs desatualizadas, pequenas inconsistências de organização |
| nota | melhoria opcional sem impacto direto |
