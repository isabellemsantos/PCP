# Guia de integração de frontend

## Contexto

`cadastros_admin.html` é uma interface **técnica provisória**, criada para
desenvolver e testar a lógica de back-end enquanto o design definitivo não
existe. Ela não deve ser tratada como referência visual — cores, ícones,
espaçamento, quantidade de cards e estrutura de menu são todos
provisórios e serão descartados.

Quando um novo frontend (ou uma evolução visual da interface atual)
estiver pronto, o objetivo é trocar **só a camada visual**, sem tocar em
`servidor_pcp.py`, `db_manutencao.py` ou `scripts/migrar_clientes_cpds.py`.
Este documento existe pra isso dar certo — independente de qual
ferramenta, referência visual ou processo de design for usado para
produzir esse frontend.

## 1. O que pode ser substituído livremente

| Arquivo | Pode substituir? |
|---|---|
| `cadastros_admin.html` | **Sim, inteiro.** É a interface provisória. O único requisito é continuar consumindo o contrato em `docs/contrato_interface_pcp.md` (mesmos endpoints, mesmos campos) e continuar sendo servido pela mesma rota `/cadastros` (ver seção 3). |
| CSS/cores/ícones/layout | Sim, sem restrição — nada disso está acoplado a regra de negócio. |
| Estrutura do menu lateral, nomes de aba, quantidade/ordem dos cards | Sim — tudo isso é só apresentação. O código JS provisório já foi organizado (ver `cadastros_admin.html`, comentário no topo do `<script>`) em camadas — Estado / API / Render / Controladores — exatamente para que a camada de Render e a estrutura de HTML possam ser jogadas fora sem mexer na camada de API (ver seção 4 abaixo). |

## 2. O que NÃO deve ser alterado sem análise

| Arquivo | Por quê |
|---|---|
| `servidor_pcp.py` | Contém toda a lógica de negócio, rotas, feature flag, gate de schema. Qualquer novo frontend consome as rotas que já existem; não deve exigir mudança de contrato sem atualizar `docs/contrato_interface_pcp.md` primeiro. |
| `db_manutencao.py` | Schema e migrações. Nunca alterar pra "encaixar" um design. |
| `scripts/migrar_clientes_cpds.py` | Lógica de migração de dados (regra dos 5 dígitos, colapso de extensões, regra PARAF/PARAFUSO). Puramente back-end, zero relação com a tela. |
| `pcp_prototype.html` | Interface **operacional** atual (pedidos/seções) — sistema em produção, fora do escopo desta reforma de design. Não mexer (ver seção 10, compatibilidade). |
| Nomes de rota (`/api/admin/*`, `/cadastros`) e formato de resposta | Mudar isso quebra o contrato documentado. Se um novo frontend precisar de um campo/endpoint que não existe, a resposta é **estender o contrato** (nova rota ou novo campo, documentado primeiro em `docs/contrato_interface_pcp.md`), nunca redefinir o que já existe. |

## 3. Como a substituição acontece na prática

`servidor_pcp.py` serve o arquivo através de:
```python
CADASTROS_HTML_FILE = ROOT / "cadastros_admin.html"

@app.get("/cadastros")
def pagina_cadastros():
    ...
    html = CADASTROS_HTML_FILE.read_text(encoding="utf-8")
    aviso_demo = os.environ.get("PCP_DEMO_BANNER", "").strip()
    if aviso_demo:
        html = html.replace("<!--DEMO_BANNER-->", f'<div class="demo-banner">{aviso_demo}</div>')
    return Response(html, mimetype="text/html; charset=utf-8")
```
Trocar o design definitivo significa **substituir o conteúdo de
`cadastros_admin.html`** (ou apontar `CADASTROS_HTML_FILE` para outro
arquivo, se for mais conveniente ter os dois lado a lado durante a
transição — é assim, por exemplo, que uma demonstração visual isolada,
rodando em outra porta/diretório fora deste repositório, pode ser avaliada
sem afetar `/cadastros`). Nenhuma outra mudança de código é necessária só
por causa da troca visual.

Se o novo frontend vier como múltiplos arquivos (HTML separado de
CSS/JS), está tudo bem servir estáticos adicionais — só não voltar a
acoplar lógica de negócio num arquivo de front-end.

## 4. Separação em camadas (Estado / Api / Render / Controladores)

O JS de `cadastros_admin.html` está organizado em 4 camadas (ver
comentário no topo do `<script>` do arquivo) exatamente para que qualquer
novo frontend possa reaproveitar a parte que já funciona e descartar só a
parte visual:

| Camada | Responsabilidade | Pode descartar num novo frontend? |
|---|---|---|
| **Estado** (`ESTADO`, `TITULOS`, `viewAtual`) | Dados de sessão de navegação (página atual, filtros ativos, view aberta). Sem qualquer referência a HTML/CSS. | Conceito deve ser mantido (algum lugar precisa guardar isso), mas a forma é livre. |
| **Api** (objeto `Api`, mais `apiGet`/`montarQuery`) | Único ponto que conhece as rotas `/api/admin/*`. Nenhuma outra camada monta URL diretamente. Contrato completo em `docs/contrato_interface_pcp.md`. | **Não** — é a camada que qualquer novo frontend deveria reaproveitar quase sem mudança, já que ela não sabe nada de layout. |
| **Render** (`escapeHtml`, `TIPO_LABELS`, `STATUS_BADGE`, ícones) | Funções puras de formatação — não sabem nada de estado nem de rede. | **Sim, inteira.** É exatamente a parte que muda quando o visual muda. |
| **Controladores** (`carregarX`) | Leem `ESTADO` + filtros do DOM, chamam `Api.*`, passam o resultado pro Render, atualizam o DOM. | Sim, mas a lógica de "quais dados buscar, com quais filtros" deve ser preservada — só a forma de exibir muda. |

Nenhum desses controladores deve ser tratado como definitivo quanto a
posição de elementos, cores, ícones, menu ou quantidade de cards — isso é
sempre provisório, independente da camada de Render escolhida.

## 5. Contratos de API

Ver `docs/contrato_interface_pcp.md` — é o documento que descreve, endpoint
por endpoint, o que o front pode assumir: envelope de listagem, paginação,
filtros e formatos de erro (resumidos abaixo, seções 6 a 9). Antes de
plugar qualquer novo frontend, confirmar que ele só chama rotas de lá, com
os parâmetros de lá.

## 6. Paginação

Todas as rotas de listagem usam `pagina` (>=1, padrão 1) e `por_pagina`
(1-100, padrão 25) — valores inválidos caem no padrão, acima de 100 é
limitado a 100. Qualquer novo frontend deve respeitar esse contrato em vez
de assumir paginação diferente (cursor, offset livre, etc.) — ver
`docs/contrato_interface_pcp.md`, seção 0.1.

## 7. Filtros

Filtros de texto (`busca`, `cliente`, `grupo`, `codigo`) são
case-insensitive e ignoram acentos dos dois lados. Cada rota tem seu
próprio conjunto de filtros documentado por seção em
`docs/contrato_interface_pcp.md` (seções 3-5) — um novo frontend não deve
inventar filtro que a API não suporta sem antes estender o contrato.

## 8. Autenticação

**Hoje:** nenhuma rota `/api/admin/*` exige autenticação (mesmo padrão
aberto de `/api/state`). Um novo frontend pode ser plugado sem se
preocupar com login ainda.

**Depois da Etapa A:** rotas de escrita (Etapas B em diante) vão exigir
autenticação. Quando isso existir, este guia ganha uma seção com o fluxo
exato (tela de login, onde o token fica armazenado no cliente, como
expira, como o front detecta "sessão expirada" vs "sem permissão"). Até
lá, o novo frontend não precisa prever tela de login funcional — só
reservar o espaço, se quiser.

## 9. Controle de permissões

Ainda não existe (ver `docs/contrato_interface_pcp.md`, seção 8). Quando a
Etapa A estiver pronta, cada ação (visível ou não) vai depender de uma
permissão específica retornada pelo backend — qualquer novo frontend deve
prever estados "ação desabilitada/oculta por falta de permissão" nos
botões de escrita (cadastrar, editar, excluir, resolver pendência), mesmo
que hoje nenhum desses botões exista.

## 10. Compatibilidade com a interface operacional

`pcp_prototype.html` (pedidos/seções) é o sistema **em produção** hoje,
rodando na porta operacional real. Nenhuma mudança de frontend feita neste
guia — provisório ou definitivo — deve alterar esse arquivo, seu contrato
(`/api/state` e demais rotas legadas) ou a autenticação por
`X-PCP-Login`/`AUTH_USERS` que ele usa. Qualquer avaliação visual nova
(demonstração isolada, protótipo, referência externa) deve rodar separada
desse sistema (porta e/ou diretório próprios) até ser formalmente adotada
— ver seção 3.

## 11. Comportamento de formulários (quando existirem — Etapas B/C/D)

Ainda não há formulário de escrita nesta fase. Quando a Etapa B (CRUD de
clientes) começar, este guia será atualizado com:
- quais campos são obrigatórios por entidade;
- formato esperado de erro de validação (provavelmente `422` com
  `{"ok": false, "codigo": "VALIDACAO", "erros": {"campo": "mensagem"}}`,
  a confirmar no plano técnico da Etapa B);
- se o campo `codigo` de CPD aceita entrada livre (com ponto/barra) e
  normaliza no servidor, ou se exige exatamente 5 dígitos na entrada — a
  decisão afeta a validação client-side que qualquer novo frontend precisa
  implementar.

## 12. Mensagens de erro

Já documentado por rota em `docs/contrato_interface_pcp.md`, seção 0. Em
resumo, o front deve tratar 3 categorias diferentes de forma diferente:
- `404` com corpo texto simples → funcionalidade indisponível (flag
  desligada), não é erro de dado;
- `503` com `codigo: CADASTROS_NOVOS_INDISPONIVEIS` → aviso amigável sobre
  o banco ainda não ter sido migrado;
- `404` com `codigo: NAO_ENCONTRADO` → registro específico não existe.

Nenhuma rota expõe traceback ou SQL bruto — se um novo frontend mostrar
mensagem de erro literal do servidor, ela é sempre uma dessas três formas
estruturadas, nunca uma exceção Python crua.

## 13. Responsividade

Sem exigência herdada do front provisório — `cadastros_admin.html` tem
rolagem horizontal nas tabelas em telas estreitas só como paliativo. Um
novo frontend pode (e deve) resolver isso do jeito que fizer mais sentido
para a ferramenta/framework escolhido, sem nenhuma restrição de
compatibilidade com o layout atual.

## 14. Preservação das regras de negócio

Nenhuma regra de negócio (validação de código de 5 dígitos, colapso de
variações/extensões, regra PARAF/PARAFUSO, cálculo de pendências, etc.)
vive no frontend — tudo isso está em `servidor_pcp.py`,
`db_manutencao.py` e `scripts/migrar_clientes_cpds.py` (ver seção 2). Um
novo frontend nunca deve reimplementar ou duplicar essas regras no
cliente (ex.: recalcular status de pendência em JS); ele só exibe o que a
API já decidiu. Se uma tela nova parecer precisar de uma regra que a API
não expõe, a resposta é estender o contrato documentado, não inferir a
regra no front.

## 15. Fluxo de auditoria

O sistema legado (`orders`/`sections`) grava em `audit_log` a cada escrita.
As tabelas novas (`clientes`, `cpds`, `arruelas`, etc.) **ainda não têm
nenhum mecanismo de auditoria** — isso precisa ser decidido antes da
Etapa B escrever a primeira linha nessas tabelas via API (reaproveitar
`audit_log` generalizando `entity`/`entity_id`, ou usar
`historico_configuracoes`, ou criar uma tabela nova). Um novo frontend não
precisa prever UI de auditoria agora, mas qualquer tela de "editar" deve
reservar espaço pra mostrar "quem alterou por último" depois, já que isso
é claramente parte do produto (o app inteiro já é sobre rastreabilidade).

## 16. Referências visuais externas

Referências visuais externas (mockups, exportações de ferramentas de
design, protótipos gerados por IA, imagens de layout) podem ser usadas
como fonte de inspiração/especificação visual para reconstruir
`cadastros_admin.html` (ou o arquivo que o substituir). Nenhuma ferramenta
específica é obrigatória ou parte fixa do processo — o que importa é que o
resultado final continue respeitando as seções 1-15 deste guia,
principalmente a separação em camadas (seção 4) e o contrato de API
(seção 5).

Se e quando esse material existir localmente, ele deve ficar em:
```
referencias_frontend/
  imagens/
  html_css/
  ...
```
Essa pasta já está no `.gitignore` (nunca versionada — é só referência
local de design, igual `referencias/`). Quando o material estiver lá,
reconstruir `cadastros_admin.html` (ou o arquivo que o substituir) usando
esse material como fonte visual e `docs/contrato_interface_pcp.md` como
fonte de dados — nunca inventar campo ou rota nova só porque o design pede
um dado que a API ainda não tem; nesse caso, primeiro atualizar o
contrato (e a rota), depois o front.
