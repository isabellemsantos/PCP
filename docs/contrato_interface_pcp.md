# Contrato de interface do PCP (back-end ↔ front-end)

> **Este documento é o contrato estável.** Qualquer front-end — a interface
> provisória atual (`cadastros_admin.html`) ou um design final futuro,
> qualquer que seja a ferramenta usada para produzi-lo — deve conseguir
> consumir exatamente estas rotas, com exatamente estes campos, sem exigir
> mudança nenhuma em `servidor_pcp.py`,
> `db_manutencao.py` ou `scripts/migrar_clientes_cpds.py`. Se um campo daqui
> precisar mudar, este documento muda primeiro, e a mudança é deliberada —
> nunca um efeito colateral de mexer no HTML.
>
> Convenções gerais:
> - Todas as rotas abaixo (exceto login, quando existir — ver seção 8) são
>   **somente leitura** nesta fase. Não existe `POST`/`PUT`/`PATCH`/`DELETE`
>   em nenhuma delas hoje.
> - Toda rota nova (`/api/admin/*` e `/cadastros`) exige a variável de
>   ambiente `PCP_HABILITAR_CADASTROS_NOVOS=1` — sem ela, `404` (a rota se
>   comporta como se não existisse). Ver `require_cadastros_novos_habilitados()`
>   em `servidor_pcp.py`.
> - Toda rota `/api/admin/*` também exige `schema_version >= 5` no banco —
>   caso contrário, `503` com corpo padronizado (ver seção 0.2). O banco
>   real está em `schema_version=3`; a migração para v4/v5 nunca é aplicada
>   automaticamente (`PCP_APLICAR_MIGRACOES` precisa ser `1` explicitamente).
> - Paginação é sempre `pagina` (>=1, padrão 1) e `por_pagina` (1-100,
>   padrão 25) — valores inválidos (0, negativo, texto) caem no padrão;
>   acima de 100 é limitado a 100.
> - Filtros de texto (`busca`, `cliente`, `grupo`, `codigo`) são
>   case-insensitive e ignoram acentos dos dois lados (função `NOACENTO()`
>   no SQLite).
> - Nenhuma dessas rotas grava em `audit_log`, `orders`, `sections` ou
>   `manual_cpd` — são todas seguras de chamar em qualquer volume durante
>   testes/demonstração.

---

## 0. Respostas comuns a todos os ambientes

### 0.1 Envelope de listagem

```json
{
  "itens": [ /* ... */ ],
  "paginacao": {
    "pagina": 1,
    "por_pagina": 25,
    "total_itens": 263,
    "total_paginas": 11
  }
}
```

### 0.2 Erro — feature flag desligada

```
HTTP 404
```
Corpo texto simples (`"Não encontrado."`), sem JSON estruturado — a rota se
comporta como se não existisse. Front-end deve tratar `404` em qualquer rota
`/api/admin/*` como "ambiente sem os novos cadastros habilitados" e nunca
mostrar isso como um erro de dado (ex.: "item não encontrado").

### 0.3 Erro — schema do banco ainda não migrado

```
HTTP 503
{
  "ok": false,
  "codigo": "CADASTROS_NOVOS_INDISPONIVEIS",
  "mensagem": "Os novos cadastros ainda não foram habilitados neste banco."
}
```
Nunca contém traceback nem detalhe interno do banco. Front-end deve mostrar
essa `mensagem` como aviso amigável (não como erro técnico).

### 0.4 Erro — registro não encontrado

```
HTTP 404
{"ok": false, "codigo": "NAO_ENCONTRADO", "mensagem": "Cliente não encontrado."}
```
(mensagem varia por entidade: "CPD não encontrado.", "Arruela não
encontrada.", "Pendência não encontrada.")

### 0.5 Erro — método não permitido

```
HTTP 405
```
Qualquer `POST`/`PUT`/`PATCH`/`DELETE` numa rota `/api/admin/*` hoje.

### 0.6 Erro genérico de rede/servidor

Qualquer outro status non-2xx: front-end usa `mensagem` do corpo se houver
JSON, senão mostra `"Erro ao consultar o servidor (HTTP {status})."`
(mesma lógica já implementada em `apiGet()` no front provisório).

### 0.7 Permissões

Nesta fase, **nenhuma rota `/api/admin/*` exige autenticação** (mesmo
comportamento de `/api/state`, que também é aberto). Isso muda na Etapa A
(ver seção 8) — quando a autenticação real existir, este documento será
atualizado com o cabeçalho/token exigido por rota antes de qualquer rota de
escrita ser criada.

---

## 1. Visão Geral

| | |
|---|---|
| **Endpoint** | `GET /api/admin/resumo` |
| **Parâmetros** | nenhum (a rota ignora qualquer query string) |
| **Paginação** | não se aplica |
| **Permissões** | nenhuma (fase atual) |

**Resposta:**
```json
{
  "ok": true,
  "total_clientes_ativos": 263,
  "total_clientes_inativos": 0,
  "total_itens": 2730,
  "total_cpds": 2700,
  "total_arruelas": 30,
  "total_pendencias_abertas": 438,
  "pendencias_por_tipo": {"CONFLITO_DESCRICAO": 289, "CLIENTE_INDEFINIDO": 146, "DUPLICIDADE_LISTA": 3}
}
```
`total_itens = total_cpds + total_arruelas`. `pendencias_por_tipo` só conta
`status='PENDENTE'` (pendências já resolvidas/ignoradas não aparecem aqui).
Chaves possíveis em `pendencias_por_tipo`: `ZERO_ESQUERDA`,
`CONFLITO_DESCRICAO`, `DUPLICIDADE_LISTA`, `PAI_AUSENTE`,
`CLIENTE_INDEFINIDO`, `FORMATO_AMBIGUO`, `CODIGO_INVALIDO` (só aparecem as
que tiverem count > 0).

**Não existem mais** (removidos deliberadamente): `total_codigos_completos`,
`total_variacoes`. CPDs não têm variações — não recriar esses campos.

**Ações disponíveis:** nenhuma (somente leitura). Botão "Atualizar" no
front provisório só re-chama esta rota e as de consulta rápida.

**Estados:**
- Carregamento: mostrar placeholder nos 5 cards enquanto a promise não resolve.
- Vazio: não existe estado vazio real (resumo sempre retorna números, mesmo que 0).
- Erro: banner de erro com a `mensagem` (ver 0.3/0.6).

**KPIs rápidos / Consulta rápida / Pendências recentes** (painéis da Visão
Geral) não têm rota própria — são montados combinando `GET /api/admin/itens`
(ver seção 3), `GET /api/admin/clientes` (seção 4) e `GET
/api/admin/pendencias` (seção 5) com `por_pagina` pequeno (5-8). Ver seção 2
para os KPIs que também dependem dessas mesmas rotas.

---

## 2. KPIs

Não existe uma rota `/api/admin/kpis` dedicada nesta fase — os indicadores
são compostos no front a partir das rotas já existentes. Isto é
**deliberadamente instável** e candidato a virar uma rota própria
(`GET /api/admin/kpis`) numa etapa futura (provavelmente Etapa F, "KPIs,
relatórios, integração com pedidos legados") para parar de depender de
`Promise.all` com múltiplas chamadas no cliente.

| Indicador | Fonte hoje | Status |
|---|---|---|
| Pendências por tipo | `GET /api/admin/resumo` → `pendencias_por_tipo` | ✅ real |
| Clientes por grupo | `GET /api/admin/clientes?grupo=X&por_pagina=1` → `paginacao.total_itens`, uma chamada por grupo | ✅ real, mas O(n) chamadas (n = nº de grupos) |
| Itens por cliente (top N) | `GET /api/admin/clientes?por_pagina=100`, ordenado no cliente por `total_cpds+total_arruelas` | ⚠️ real mas parcial — só considera os primeiros 100 clientes retornados, não o dataset inteiro |
| Pedidos ativos/atrasados/críticos | nenhuma | ❌ não implementado — front mostra "Indicador ainda não disponível". Depende da lógica de urgência do sistema legado (`/api/state` + cálculo de prazo), nunca replicado nas APIs novas. |
| Itens sem cliente | nenhuma | ❌ não implementado — precisaria de um filtro novo (`sem_cliente=1`) em `/api/admin/itens` |
| Itens sem descrição válida | nenhuma | ❌ não implementado — precisaria de um filtro novo (`sem_descricao=1`) |

**Ação recomendada para quem for construir o design final:** tratar esta
seção como a lista de contratos que **ainda faltam** — o design pode já
prever o espaço visual pros indicadores "não disponível", mas não deve
assumir que a API vai entregar um número (o front precisa checar
explicitamente e mostrar o aviso, nunca inventar/calcular no cliente algo
que pareça vir do servidor).

**Estados:** carregamento por indicador (cada um resolve independente),
vazio = "Indicador ainda não disponível" (texto fixo, não é erro), erro =
mesmo banner global de erro se qualquer uma das chamadas falhar.

---

## 3. Consulta de Itens

| | |
|---|---|
| **Endpoint (lista)** | `GET /api/admin/itens` |
| **Endpoint (detalhe CPD)** | `GET /api/admin/cpds/<id>` |
| **Endpoint (detalhe Arruela)** | `GET /api/admin/arruelas/<id>` |
| **Permissões** | nenhuma (fase atual) |

Itens reúne CPDs e Arruelas na mesma listagem (categorias distintas no
banco, nunca misturadas — `tipo` no item resultante diz qual é qual).

**Filtros (`GET /api/admin/itens`):**

| Parâmetro | Tipo | Efeito |
|---|---|---|
| `busca` | texto | procura em código e descrição (CPD: `codigo_pai`+`descricao_padrao`; Arruela: `codigo`+`descricao_padrao`) |
| `tipo` | `CPD` \| `ARRUELA` \| vazio | filtra por categoria; vazio = ambas |
| `cliente` | texto (nome exato, sem acento/caixa) | só itens vinculados a esse cliente |
| `grupo` | texto (nome exato, sem acento/caixa) | só itens vinculados a esse grupo |
| `ativo` | `1` \| `0` \| vazio | filtra por status |
| `possui_pendencia` | `1` \| `0` \| vazio | `1` = só itens com pendência `PENDENTE`; arruelas nunca aparecem aqui (arruelas não têm pendência própria neste schema) |
| `pagina`, `por_pagina` | inteiro | paginação padrão (ver seção 0) |

**Resposta (cada item da lista):**
```json
{
  "id": 1897, "tipo": "CPD", "codigo": "27859", "descricao": "(SL) (ST) MFF 3X8 ZINKLAD 8.8",
  "ativo": true, "clientes": [".VITESCO"], "grupos": ["Diversos"], "total_pendencias": 0
}
```
Para `tipo="ARRUELA"`, os mesmos campos existem; `total_pendencias` é sempre
`0` (arruelas não referenciam `cpd_pendencias_revisao`).

**Detalhe de CPD** (`GET /api/admin/cpds/<id>`):
```json
{
  "id": 1897, "codigo": "27859", "descricao_padrao": "...", "descricao_canonica": "...",
  "observacoes": null, "ativo": true, "criado_em": "...", "atualizado_em": "...", "desativado_em": null,
  "codigos_originais_historicos": ["27859"],
  "descricoes_fontes": [
    {"id": 1633, "codigo_completo": "27859", "descricao": "...", "fonte": "LISTA_OFICIAL", "referencia_origem": "linha 1896", "cliente_origem": "...", "descricao_canonica": 1, "criado_em": "..."}
  ],
  "clientes": ["...VITESCO"], "grupos": ["Diversos"], "pendencias": []
}
```
- `codigo`: **sempre 5 dígitos numéricos**. CPDs não têm variações —
  `codigos_originais_historicos` é só rastreabilidade (pode conter formas
  como `"31947.1"`, `"31947/2"` de fontes históricas que colapsaram no
  mesmo CPD); nunca use esse campo para montar sub-linhas de cadastro.
- `descricoes_fontes`: todas as descrições encontradas em todas as fontes
  (LISTA_OFICIAL, MANUAL_CPD, PEDIDO, MIGRACAO), com no máximo uma
  `descricao_canonica=1` **por CPD** (não por código histórico).
- `pendencias`: mesma forma da seção 5, já filtrada para este CPD.

**Detalhe de Arruela** (`GET /api/admin/arruelas/<id>`): mesma ideia, sem
`codigos_originais_historicos`/`descricao_canonica` (arruelas não têm
conflito de descrição neste schema); campo `codigo_original` em vez de
`codigo_completo` dentro de `descricoes_fontes`.

**Ações disponíveis:** nenhuma. Não existe "editar", "ativar/inativar" nem
"excluir" nesta fase — isso é Etapa C.

**Estados:** carregamento = linha "Carregando..." na tabela; vazio =
"Nenhum registro encontrado."; erro = banner global.

---

## 4. Consulta de Clientes

| | |
|---|---|
| **Endpoint (lista)** | `GET /api/admin/clientes` |
| **Endpoint (detalhe)** | `GET /api/admin/clientes/<id>` |
| **Permissões** | nenhuma (fase atual) |

**Filtros:** `busca` (nome ou alias), `grupo`, `ativo`, `pagina`, `por_pagina`.

**Resposta (item da lista):**
```json
{
  "id": 1, "nome": ".VITESCO", "grupos": ["Diversos"], "aliases": [],
  "ativo": true, "total_cpds": 1, "total_arruelas": 0, "total_pedidos": 0
}
```
`total_pedidos` é **best-effort**: conta pedidos legados (`orders`) cujo
campo `cliente` (texto livre, não FK) bate com o nome canônico ou algum
alias do cliente, ignorando lixeira. Nunca é garantia de 100% de precisão —
é um vínculo textual herdado do sistema antigo.

**Detalhe:**
```json
{
  "id": 1, "nome": "...", "codigo_interno": null, "observacoes": null, "ativo": true,
  "criado_em": "...", "atualizado_em": "...", "desativado_em": null,
  "grupos": ["Diversos"], "aliases": [],
  "cpds": [{"id": 1897, "codigo": "27859", "descricao_padrao": "...", "ativo": 1}],
  "arruelas": [{"id": ..., "codigo": "...", "descricao_padrao": "...", "ativo": 1}],
  "total_pedidos": 0
}
```

**Ações disponíveis:** nenhuma (Etapa B implementa CRUD).

**Estados:** iguais à seção 3.

---

## 5. Pendências

| | |
|---|---|
| **Endpoint (lista)** | `GET /api/admin/pendencias` |
| **Endpoint (detalhe)** | `GET /api/admin/pendencias/<id>` |
| **Permissões** | nenhuma (fase atual) |

**Filtros:** `tipo`, `status` (`PENDENTE`\|`RESOLVIDO`\|`IGNORADO`),
`nivel_confianca`, `codigo` (busca em `codigo_completo`), `pagina`,
`por_pagina`.

**Resposta (item da lista):**
```json
{
  "id": 1, "tipo": "CONFLITO_DESCRICAO", "status": "PENDENTE", "nivel_confianca": null,
  "codigo_completo": "31467", "cpd_id": 2212, "cpd_variacao_id": null,
  "detalhes": {"categoria": "C", "descricoes_por_fonte": {"...": ["..."]}, "pares_comparados": [{"...": "..."}]},
  "criado_em": "...", "resolvido_em": null
}
```
- `cpd_variacao_id` é **sempre `null`** (CPDs não têm variações — o campo
  existe no schema por compatibilidade histórica, nunca é preenchido).
- `detalhes` é o `detalhes_json` já parseado; se o JSON salvo estiver
  corrompido, vem `null` (nunca derruba a API, nunca lança exceção pro
  front).
- Tipos possíveis: `ZERO_ESQUERDA`, `CONFLITO_DESCRICAO`,
  `DUPLICIDADE_LISTA`, `PAI_AUSENTE`, `CLIENTE_INDEFINIDO`,
  `FORMATO_AMBIGUO`, `CODIGO_INVALIDO`.

**Detalhe:** mesmos campos + `cpd_codigo_pai` (código de 5 dígitos do CPD
relacionado, ou `null`) e `variacao_codigo_completo` (sempre `null` hoje).

**Ações disponíveis:** nenhuma. **Resolver/editar/ignorar pendência é
Etapa D** — não existe `POST`/`PATCH` para isso ainda. O botão "Visualizar"
do front provisório só abre o painel de leitura.

**Estados:** iguais à seção 3.

---

## 6. Cadastros

| | |
|---|---|
| **Endpoint** | nenhum |
| **Status** | placeholder ("Em desenvolvimento") |

Não existe nenhuma API de escrita para clientes/CPDs/arruelas ainda.
Etapas B e C constroem isso. Quando existir, este documento ganha uma
seção 6 real com os contratos de `POST`/`PUT`/`DELETE`, os campos
obrigatórios de cada formulário, e as mensagens de validação — hoje a tela
só mostra um aviso estático.

---

## 7. Configurações

| | |
|---|---|
| **Endpoint** | nenhum |
| **Status** | placeholder ("Em desenvolvimento") |

Schema já existe (`configuracoes_sistema`, `historico_configuracoes`,
criadas desde a migração v1→v2, já aplicada no banco real) mas vazio e sem
nenhuma rota. Etapa E.

---

## 8. Usuários e Permissões

| | |
|---|---|
| **Endpoint** | nenhum |
| **Status** | não implementado — schema pronto, zero lógica |

O schema completo já existe (`areas`, `perfis`, `permissoes`,
`perfil_permissoes`, `usuarios`, `usuario_permissoes`), criado desde a
migração v1→v2 (já aplicada no banco real, então **não precisa de nova
migração de schema** para começar a Etapa A). Todas as tabelas estão
**vazias** — nenhum perfil, nenhuma permissão, nenhum usuário cadastrado.

A autenticação real (login com senha, sessão/token, controle de
permissão por rota) é o objeto da **Etapa A** (ver plano técnico
apresentado separadamente). Até lá:

- A tela operacional atual (`pcp_prototype.html`) continua usando o
  esquema antigo: header `X-PCP-Login` sem senha, contra o dicionário fixo
  `AUTH_USERS` em `servidor_pcp.py` (`VENDAS`/`EXPEDICAO`=leitura,
  `PCP`=edição). **Isso não muda nesta fase.**
- As rotas `/api/admin/*` (admin novo) não exigem autenticação nenhuma
  ainda — qualquer um na rede interna acessa. Isso é aceitável só enquanto
  as rotas continuarem 100% somente-leitura; a Etapa A precisa resolver
  isso **antes** da primeira rota de escrita ser criada (Etapa B).

Quando a Etapa A for implementada, esta seção passa a documentar:
endpoint de login, formato do token/sessão, cabeçalho exigido em cada rota
protegida, formato do erro `401`/`403`, e o catálogo de permissões por
módulo.

---

## Referência rápida de arquivos

| Arquivo | Papel |
|---|---|
| `servidor_pcp.py` | Único ponto que implementa as rotas `/api/admin/*` e serve `/cadastros`. Fonte de verdade do contrato. |
| `db_manutencao.py` | Schema (todas as tabelas, inclusive as ainda não usadas por nenhuma rota). |
| `scripts/migrar_clientes_cpds.py` | Popula `clientes`/`cpds`/`arruelas`/`cpd_descricoes_fontes`/`cpd_pendencias_revisao` a partir das fontes legadas. Nunca roda automaticamente. |
| `cadastros_admin.html` | Front-end **provisório** — consome exatamente este contrato. Ver `docs/guia_integracao_frontend.md` para como substituí-lo. |
