# Segurança frontend e prevenção de vazamento

Use esta referência quando a demanda envolver secrets, tokens, storage, logs, analytics, urls, xss, csp, headers, source maps, permissões ou dados sensíveis.

## Princípio central

Não existe segredo seguro no frontend. Tudo que chega ao browser pode ser inspecionado: bundle, variáveis públicas, source maps, storage, requests, headers, payloads e logs.

## Secrets e variáveis públicas

Nunca coloque no frontend:

```txt
client_secret
api key privada
senha
connection string
token de serviço
chave de assinatura
credencial de backend
segredo de oauth
chave privada
```

Variáveis como `vite_*` e `next_public_*` são públicas quando entram no bundle. Integrações com segredo devem passar por backend ou bff.

Arquitetura correta:

```txt
frontend -> backend/bff -> serviço externo com segredo
```

## Tokens e storage

Evite armazenar access token, refresh token ou dados sensíveis em:

```txt
localStorage
sessionStorage
indexedDB
cookies acessíveis por javascript
window.__INITIAL_STATE__
```

Quando aplicável para sessão web, prefira cookie `HttpOnly`, `Secure` e `SameSite`, emitido pelo backend.

## XSS

Trate xss como principal risco de vazamento. Evite:

```tsx
<div dangerouslySetInnerHTML={{ __html: htmlFromApi }} />
```

Se renderizar html externo for inevitável, sanitize com biblioteca aprovada e mantenha exceção documentada. Valide urls vindas de usuário ou backend e bloqueie protocolos como `javascript:` e `data:` quando não forem explicitamente permitidos.

## Content security policy

Use csp como defesa em profundidade. Base inicial para spa sensível:

```http
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'; img-src 'self' data: https:; connect-src 'self' https://api.suaempresa.com
```

Quando houver ssr/bff capaz de emitir nonce por resposta, preferir csp com nonce e sem `unsafe-inline` para scripts.

## Logs, analytics e observabilidade

Não envie para console, analytics ou rum:

```txt
token
authorization header
payload completo
cpf/cnpj completo
e-mail pessoal
telefone
nome completo quando não necessário
dados bancários
documentos
dados cadastrais completos
motivo sensível de reprovação
```

Eventos devem passar por sanitização central. Use códigos e etapas em vez de payloads.

## Urls

Não colocar dados sensíveis em query string, hash ou path params:

```txt
ruim: /onboarding?documentNumber=12345678000199&email=user@email.com
bom:  /onboarding/:requestId
```

URLs aparecem em histórico, logs, analytics, referer, prints e proxies.

## Source maps

Em produção sensível, não publicar `.map` publicamente. Envie source maps apenas para observabilidade autorizada, se necessário.

## Autorização

Frontend pode melhorar ux escondendo ações. Segurança real exige validação no backend:

- autenticação;
- autorização;
- ownership;
- escopo;
- regra transacional.

Nunca aceitar solução cuja única proteção é botão escondido, rota escondida ou role check no cliente.

## Headers recomendados

Use quando compatível com a aplicação:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Content-Security-Policy: frame-ancestors 'none'
```

## CORS

Restrinja origens, mas não trate cors como autenticação. A api ainda deve validar sessão, token, permissão e escopo.

## Dependências

Antes de adicionar dependência:

- verificar se código local simples resolve;
- evitar pacotes minúsculos para funções triviais;
- manter lockfile;
- revisar scripts de instalação;
- usar audit, dependabot ou renovate quando disponível;
- remover dependências não usadas.

## Cache

Para dados sensíveis, respostas autenticadas e páginas com dados pessoais, considerar:

```http
Cache-Control: no-store
```

Não persistir cache de tanstack query em storage web para dados sensíveis sem decisão de segurança.
