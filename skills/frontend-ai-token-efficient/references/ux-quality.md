# Qualidade de UX, design e conversão sem perder manutenibilidade

Use esta referência quando a mudança frontend envolve aparência, fluxo, formulário, onboarding, empty state, CTA, fricção, responsividade, ativação ou conversão. O objetivo não é transformar a skill em design visual puro; é garantir que a IA implemente interfaces úteis, coerentes e verificáveis.

## Projeto existente: adaptar primeiro

Antes de criar UI nova em um projeto existente, inspecione:

- design system e biblioteca de componentes;
- tokens de cor, espaçamento, tipografia, radius, sombra e motion;
- padrões de layout, grid, breakpoints e responsividade;
- componentes semelhantes já usados em outra feature;
- estados existentes de loading, empty, error, disabled, success e permission denied.

Preserve a linguagem visual estabelecida. Não introduza fonte, paleta, animação ou biblioteca nova apenas para parecer diferente.

## Interface nova: direção visual explícita

Quando não houver design system ou a tarefa for criar uma interface nova, defina antes de codar:

1. propósito: problema, usuário e tarefa principal;
2. tom: utilitário, editorial, institucional, premium, minimalista, denso, técnico, etc.;
3. restrições: framework, acessibilidade, performance, responsividade, dados sensíveis;
4. elemento memorável: o que torna a tela reconhecível sem prejudicar uso.

Use tokens explícitos para cores, spacing, radius, tipografia e motion. Evite aparência genérica de IA: layouts previsíveis sem contexto, roxo-gradiente por padrão, excesso de cards idênticos, microcopy vaga e animações decorativas sem função.

## Intensidade visual por contexto

| contexto | intensidade preferida |
|---|---|
| backoffice, dashboard, fluxo regulatório, cadastro | precisão refinada, hierarquia clara, baixa distração |
| landing page ou produto público | identidade visual mais expressiva, sem sacrificar performance e acessibilidade |
| onboarding ou primeiro uso | orientação clara, progressão e quick wins |
| tela crítica com dado sensível | sobriedade, confiança, feedback explícito e mínimo ruído |

## Formulários e fricção

Para cada campo, perguntar:

- é obrigatório antes de entregar valor?
- pode ser inferido, enriquecido ou pedido depois?
- há exigência legal/compliance para coletar agora?
- a informação é realmente usada no follow-up ou fluxo backend?

Boas práticas:

- um assunto por campo;
- labels sempre visíveis, placeholder como exemplo, não como label;
- campos fáceis primeiro; campos sensíveis ou difíceis depois;
- phone, documento, moeda e data com máscara/normalização clara;
- teclado mobile apropriado (`email`, `tel`, `numeric`);
- layout de uma coluna como default; múltiplas colunas só para campos curtos e relacionados;
- multi-step quando houver muitas seções, com progresso, back navigation e preservação dos dados;
- erros específicos, próximos ao campo, sem limpar input;
- no submit, focar primeiro erro e preservar dados;
- CTA com ação e resultado, não apenas `Enviar` quando houver benefício claro;
- microcopy de confiança perto de dados sensíveis, sem prometer privacidade que o produto não garante.

## Onboarding, ativação e primeiro uso

Antes de desenhar onboarding, identifique:

- qual é o `aha moment` ou evento de ativação;
- menor caminho até primeiro valor;
- onde usuários abandonam hoje;
- se o usuário precisa configurar algo antes de ver valor;
- quais passos são obrigatórios, opcionais ou adiáveis.

Princípios:

- reduzir time-to-value;
- uma meta principal por sessão;
- fazer o usuário executar a tarefa real em vez de apenas assistir tutorial;
- empty state deve explicar valor, mostrar exemplo ou preview e oferecer ação primária;
- checklists devem ter 3-7 itens, começar com quick wins, mostrar progresso e permitir dismiss;
- tours devem ser curtos, apontar para UI real, ser dispensáveis e não repetir para retornantes;
- progresso não deve bloquear valor principal sem motivo forte.

## Métricas e experimentos

Quando a decisão envolver conversão, ativação ou fricção, proponha hipótese testável, não certeza.

Métricas úteis:

- form start rate, completion rate, field drop-off, error rate e time-to-complete;
- activation rate, time-to-activation, onboarding completion e feature adoption;
- CTA click-through, dismiss rate, retry rate, task success, mobile vs desktop.

Formato de hipótese:

```txt
se reduzirmos [fricção] para [segmento], esperamos [métrica] melhorar porque [mecanismo]. validar por [teste/evidência].
```

## Acessibilidade visual e interação

Não trate estética como substituta de acessibilidade:

- contraste suficiente;
- foco visível;
- targets de toque adequados;
- navegação por teclado;
- leitura por screen reader em modais, erros e estados dinâmicos;
- animações com opção de redução quando aplicável;
- informação importante não depende apenas de cor.

## Saída para revisão UX

Para revisão, responder com:

1. objetivo do fluxo;
2. achados por impacto;
3. menor ajuste recomendado;
4. hipótese ou métrica associada;
5. validação necessária: teste de usuário, analytics, playwright, screenshot ou revisão manual.
