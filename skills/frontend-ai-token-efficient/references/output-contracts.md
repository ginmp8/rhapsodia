# Contratos de saída

Use estes formatos para manter respostas auditáveis e úteis.

## Recomendação de arquitetura

```md
## suposições
- ...

## recomendação
[decisão objetiva]

## estrutura proposta
```txt
...
```

## regras principais
- ...

## validação
- executado: ...
- recomendado: ...

## riscos
- ...
```

## Plano de implementação

```md
## suposições
- ...

## menor contexto necessário
- feature: ...
- arquivos prováveis: ...
- contratos: ...

## plano
1. alterar ... -> verificar ...
2. alterar ... -> verificar ...
3. ajustar testes ... -> verificar ...

## validação
- executar: ...
- revisar manualmente: ...

## riscos
- ...
```

## Revisão de código ou pr

```md
## achados

1. [severidade] problema - evidência - impacto - menor correção

## lacunas de validação
- ...

## próximo passo
- ...
```

## Revisão de segurança frontend

```md
## postura geral
[resumo curto]

## achados

1. [severidade] risco - evidência - impacto - menor correção - validação

## controles recomendados
- ...

## validação
- executado: ...
- não executado: ...

## limitações
- ...
```

## Documentação para agentes

```md
## arquivos sugeridos
- arquivo: motivo

## conteúdo
[conteúdo pronto ou patch conceitual]

## regras protegidas
- ...

## validação
- links locais
- ausência de contradições
- alinhamento com estrutura real
```


## Revisão UX/flow

```md
## objetivo do fluxo
[usuário, tarefa e resultado esperado]

## achados
1. [impacto] problema - evidência - impacto no usuário/métrica - menor ajuste

## hipótese de melhoria
se [mudança] para [segmento], esperamos [métrica] porque [mecanismo].

## validação
- executado: ...
- recomendado: analytics, teste usuário, playwright, screenshot, revisão a11y
```

## Validação runtime/browser

```md
## escopo validado
- rota/feature:
- viewports:
- fluxo:

## evidência
- comando:
- resultado:
- logs/screenshot/teste:

## lacunas
- não executado:
- bloqueios:

## riscos restantes
- ...
```
