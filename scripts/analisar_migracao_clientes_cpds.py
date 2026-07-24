"""Análise somente-leitura para preparar a migração de clientes e CPDs
existentes (orders.payload / manual_cpd) para as tabelas novas (clientes,
cliente_aliases, cliente_grupos, cpds, cpd_variacoes, cliente_cpds,
grupo_cpds).

NÃO migra nada, NÃO grava nada no banco analisado, NÃO importa Excel, NÃO
inicia Flask, NÃO roda migrações de schema. Gera relatórios (JSON e/ou XLSX)
para decisão humana em `relatorios_migracao/`.

Fonte dos dados (confirmada pelo schema, não assumida):
- orders(id, payload, updated_at): payload é um JSON com, entre outros
  campos, "cliente" (nome do cliente), "cpd" (código do CPD) e "descricao"
  (descrição do item). Ver normalize_order() em servidor_pcp.py.
- manual_cpd(codigo, descricao, updated_at): cadastro de CPDs conhecidos,
  independente dos pedidos.
Não há nenhuma outra tabela ou arquivo que armazene cliente/CPD de pedidos.

Uso:
    .venv\\Scripts\\python.exe scripts\\analisar_migracao_clientes_cpds.py
    .venv\\Scripts\\python.exe scripts\\analisar_migracao_clientes_cpds.py --banco caminho\\copia.sqlite3 --usar-copia
    .venv\\Scripts\\python.exe scripts\\analisar_migracao_clientes_cpds.py --formato json

Por padrão (sem --usar-copia), o script SEMPRE cria sua própria cópia do
--banco informado via sqlite3.Connection.backup() antes de analisar --
nunca abre o --banco original para escrita, e se --banco for o
pcp.sqlite3 real, ele nunca é tocado além dessa cópia inicial (que também
é feita em modo leitura da origem).
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import db_manutencao as dbm  # reaproveita normalizar_cpd(), já revisada e testada
import scripts.config_clientes_migracao as config_clientes

DEFAULT_DB = ROOT / "pcp.sqlite3"
DEFAULT_SAIDA = ROOT / "relatorios_migracao"

# O grupo Honda (mesma regra usada hoje em grupo_cliente() em servidor_pcp.py,
# usada nos KPIs do Excel) nunca fica hardcoded aqui -- vem sempre da
# configuração local de clientes (--config-clientes / carregar_config_clientes()).
# É um match EXATO (case-sensitive) contra esse conjunto; variações de
# caixa/espaço no nome do cliente não são reconhecidas por essa regra hoje.

_FINALIZADOS = {"concluído", "concluido", "cancelado", "cancelada"}


# ---------------------------------------------------------------------------
# Cópia segura da origem
# ---------------------------------------------------------------------------

def criar_copia_segura(origem: Path, pasta_saida: Path) -> Path:
    pasta_saida.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destino = pasta_saida / f"copia_analise_{stamp}.sqlite3"
    origem_conn = sqlite3.connect(str(origem))
    destino_conn = sqlite3.connect(str(destino))
    try:
        with destino_conn:
            origem_conn.backup(destino_conn)
    finally:
        destino_conn.close()
        origem_conn.close()
    return destino


def abrir_somente_leitura(caminho: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# Normalização de nome de cliente (só para comparação/sugestão, nunca gravada)
# ---------------------------------------------------------------------------

def normalizar_cliente_para_comparacao(nome: str) -> str:
    txt = str(nome or "").strip()
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("ascii")
    txt = re.sub(r"[^\w\s]", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip().upper()
    return txt


def similaridade(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def eh_possivel_abreviacao(curto: str, longo: str) -> bool:
    """Heurística simples: 'curto' pode ser abreviação de 'longo' se todas as
    letras de 'curto' aparecem em 'longo' na mesma ordem (ex.: 'HDA' dentro
    de 'HONDA') E 'longo' não é longo demais perto de 'curto'. Sem esse
    segundo limite, qualquer string curta acaba "cabendo" como subsequência
    de nomes bem compridos sem relação nenhuma (ex.: 'SMRC' "cabe" dentro de
    'PLASTICOMP INDUSTRIA E CO' só por coincidência de letras comuns). Não
    decide nada sozinho -- só sinaliza para revisão humana.
    """
    if not curto or not longo or len(curto) < 2 or len(curto) >= len(longo):
        return False
    if len(longo) / len(curto) > 3:
        return False
    it = iter(longo)
    return all(ch in it for ch in curto)


# ---------------------------------------------------------------------------
# Carregamento dos dados de origem
# ---------------------------------------------------------------------------

def carregar_orders(conn: sqlite3.Connection) -> list[dict]:
    orders = []
    for row in conn.execute("SELECT id, payload, updated_at FROM orders"):
        try:
            payload = json.loads(row["payload"]) if row["payload"] else {}
        except Exception:
            payload = {}
        payload["_id"] = row["id"]
        payload["_updated_at"] = row["updated_at"]
        orders.append(payload)
    return orders


def carregar_manual_cpd(conn: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT codigo, descricao, updated_at FROM manual_cpd")]


# ---------------------------------------------------------------------------
# 3) Análise de clientes
# ---------------------------------------------------------------------------

def analisar_clientes(orders: list[dict]) -> dict:
    por_cliente_raw: dict[str, list[dict]] = defaultdict(list)
    em_branco = []
    for o in orders:
        nome = o.get("cliente")
        if nome is None or str(nome).strip() == "":
            em_branco.append(o)
            continue
        por_cliente_raw[str(nome)].append(o)

    detalhado = {}
    for nome_original, pedidos in por_cliente_raw.items():
        trimado = nome_original.strip()
        normalizado = normalizar_cliente_para_comparacao(nome_original)
        cpds = sorted({str(p.get("cpd") or "").strip() for p in pedidos if p.get("cpd")})
        criados = sorted(str(p.get("criadoEm") or p.get("_updated_at") or "") for p in pedidos)
        atualizados = sorted(str(p.get("alteradoEm") or p.get("_updated_at") or "") for p in pedidos)
        ativos = [p for p in pedidos if not p.get("deleted")]
        so_lixeira = len(ativos) == 0

        detalhado[nome_original] = {
            "valor_original": nome_original,
            "valor_sem_espacos": trimado,
            "normalizado_para_comparacao": normalizado,
            "quantidade_pedidos": len(pedidos),
            "quantidade_pedidos_ativos": len(ativos),
            "quantidade_pedidos_lixeira": len(pedidos) - len(ativos),
            "primeiro_uso": criados[0] if criados else None,
            "ultimo_uso": atualizados[-1] if atualizados else None,
            "cpds_distintos": cpds,
            "somente_lixeira": so_lixeira,
        }

    # Agrupa por forma normalizada para achar possíveis aliases.
    por_normalizado: dict[str, list[str]] = defaultdict(list)
    for nome_original, info in detalhado.items():
        por_normalizado[info["normalizado_para_comparacao"]].append(nome_original)

    aliases_alta_confianca = []  # mesma forma normalizada, grafias diferentes
    for normalizado, variantes in por_normalizado.items():
        if len(variantes) > 1:
            aliases_alta_confianca.append({
                "forma_normalizada": normalizado,
                "variantes_originais": variantes,
                "justificativa": "Diferem só por espaços/maiúsculas/acentuação/pontuação após normalizar.",
            })

    # Candidatos de média/baixa confiança entre formas normalizadas DIFERENTES
    # (abreviação ou nomes muito parecidos) -- sempre para decisão humana.
    formas_unicas = sorted(por_normalizado.keys())
    precisam_decisao = []
    for i, a in enumerate(formas_unicas):
        for b in formas_unicas[i + 1:]:
            if a == b:
                continue
            score = similaridade(a, b)
            abreviacao = eh_possivel_abreviacao(a, b) or eh_possivel_abreviacao(b, a)
            if abreviacao or score >= 0.72:
                precisam_decisao.append({
                    "cliente_a": por_normalizado[a][0],
                    "cliente_b": por_normalizado[b][0],
                    "similaridade": round(score, 3),
                    "possivel_abreviacao": abreviacao,
                    "motivo": "possivel_abreviacao" if abreviacao else "nomes_semelhantes",
                })

    sem_duplicidade = [
        nome for nome, info in detalhado.items()
        if len(por_normalizado[info["normalizado_para_comparacao"]]) == 1
        and not any(nome in (item["cliente_a"], item["cliente_b"]) for item in precisam_decisao)
    ]

    usados_so_lixeira = [nome for nome, info in detalhado.items() if info["somente_lixeira"]]
    usados_ativos_e_historico = [nome for nome, info in detalhado.items() if not info["somente_lixeira"]]

    return {
        "detalhado_por_cliente": detalhado,
        "total_clientes_distintos_raw": len(detalhado),
        "clientes_sem_possivel_duplicidade": sem_duplicidade,
        "possiveis_aliases_alta_confianca": aliases_alta_confianca,
        "possiveis_aliases_para_decisao_humana": precisam_decisao,
        "pedidos_sem_cliente": len(em_branco),
        "ids_pedidos_sem_cliente": [p.get("_id") for p in em_branco],
        "clientes_usados_somente_em_lixeira": usados_so_lixeira,
        "clientes_usados_em_pedidos_ativos_ou_historicos": usados_ativos_e_historico,
    }


# ---------------------------------------------------------------------------
# 4) Sugestão de grupos (nunca grava, só sugere)
# ---------------------------------------------------------------------------

def sugerir_grupos(analise_clientes: dict, grupo_honda: set[str]) -> dict:
    sugestoes = {}
    for nome, info in analise_clientes["detalhado_por_cliente"].items():
        normalizado = info["normalizado_para_comparacao"]
        if nome in grupo_honda:
            sugestoes[nome] = {
                "grupo_sugerido": "Honda",
                "justificativa": "Corresponde exatamente à regra já existente grupo_cliente() em servidor_pcp.py.",
                "confianca": "alta",
                "revisao_humana": False,
            }
            continue
        # Nome normalizado é parecido com um dos nomes do grupo Honda
        # configurado, mas não bate exatamente -- não decide sozinho, só
        # sinaliza média confiança.
        parecido_honda = None
        for referencia in grupo_honda:
            if normalizado == normalizar_cliente_para_comparacao(referencia):
                parecido_honda = referencia
                break
        if parecido_honda:
            sugestoes[nome] = {
                "grupo_sugerido": "Honda",
                "justificativa": (
                    f"Nome normalizado é idêntico ao de '{parecido_honda}' (que hoje conta como Honda em "
                    "grupo_cliente()), mas a grafia original é diferente -- pode ser o mesmo cliente com "
                    "variação de escrita, ou pode não ser."
                ),
                "confianca": "media",
                "revisao_humana": True,
            }
            continue
        sugestoes[nome] = {
            "grupo_sugerido": "Diversos",
            "justificativa": "Não corresponde a nenhum nome do grupo Honda conhecido hoje (nem exato nem por semelhança).",
            "confianca": "baixa" if info["quantidade_pedidos"] <= 1 else "media",
            "revisao_humana": True,
        }
    return sugestoes


# ---------------------------------------------------------------------------
# 5) Análise de CPDs em manual_cpd (pai + variações via normalizar_cpd)
# ---------------------------------------------------------------------------

def analisar_cpds(manual_cpd_rows: list[dict]) -> dict:
    pais: dict[str, list[dict]] = defaultdict(list)
    vazios_ou_invalidos = []
    com_espacos = []
    vistos_apos_trim: dict[str, list[str]] = defaultdict(list)

    for row in manual_cpd_rows:
        codigo_original = row["codigo"]
        if codigo_original is None or str(codigo_original).strip() == "":
            vazios_ou_invalidos.append(row)
            continue
        if str(codigo_original) != str(codigo_original).strip():
            com_espacos.append(codigo_original)

        info = dbm.normalizar_cpd(codigo_original)
        vistos_apos_trim[info["codigo_original"]].append(codigo_original)
        pais[info["codigo_pai"]].append({
            "codigo_original": codigo_original,
            "extensao": info["extensao"],
            "descricao": row["descricao"],
            "updated_at": row["updated_at"],
        })

    duplicidades_apos_trim = {k: v for k, v in vistos_apos_trim.items() if len(v) > 1}

    pais_unica_variacao = {p: v for p, v in pais.items() if len(v) == 1}
    pais_varias_variacoes = {p: v for p, v in pais.items() if len(v) > 1}
    sem_extensao = [item for variacoes in pais.values() for item in variacoes if item["extensao"] is None]
    com_sufixo_nao_numerico = [
        item for variacoes in pais.values() for item in variacoes
        if item["extensao"] is None and "." in item["codigo_original"]
    ]

    return {
        "total_codigos_originais": len(manual_cpd_rows),
        "total_pais_estimado": len(pais),
        "total_variacoes": sum(len(v) for v in pais.values()),
        "pais_com_unica_variacao": len(pais_unica_variacao),
        "pais_com_varias_variacoes": len(pais_varias_variacoes),
        "codigos_sem_extensao": len(sem_extensao),
        "codigos_com_sufixo_nao_numerico": len(com_sufixo_nao_numerico),
        "exemplos_sufixo_nao_numerico": [i["codigo_original"] for i in com_sufixo_nao_numerico[:20]],
        "codigos_vazios_ou_invalidos": len(vazios_ou_invalidos),
        "codigos_com_espacos": com_espacos,
        "duplicidades_apos_trim": duplicidades_apos_trim,
        "duplicidades_apos_normalizacao_de_pai": {p: len(v) for p, v in pais_varias_variacoes.items()},
        "pais": pais,
    }


# ---------------------------------------------------------------------------
# 6) Conflitos de descrição por CPD-pai
# ---------------------------------------------------------------------------

def classificar_conflitos_descricao(analise_cpds: dict, orders: list[dict]) -> dict:
    descricoes_pedidos_por_pai: dict[str, set[str]] = defaultdict(set)
    for o in orders:
        cpd = str(o.get("cpd") or "").strip()
        if not cpd:
            continue
        info = dbm.normalizar_cpd(cpd)
        desc = str(o.get("descricao") or "").strip()
        if desc:
            descricoes_pedidos_por_pai[info["codigo_pai"]].add(desc)

    classificacao = {}
    for pai, variacoes in analise_cpds["pais"].items():
        tem_pai_sem_extensao = any(v["extensao"] is None for v in variacoes)
        descricoes_manual = {str(v["descricao"] or "").strip() for v in variacoes if v["descricao"]}
        descricoes_pedidos = descricoes_pedidos_por_pai.get(pai, set())
        todas_descricoes = descricoes_manual | descricoes_pedidos

        if not todas_descricoes:
            categoria = "E"  # descrição ausente
            detalhe = "Nenhuma descrição utilizável em manual_cpd nem em pedidos."
        elif not tem_pai_sem_extensao and any(v["extensao"] is not None for v in variacoes):
            categoria = "D"  # pai ausente
            detalhe = f"Existem variações ({[v['codigo_original'] for v in variacoes]}) mas não existe o código '{pai}' sem extensão."
        elif len(descricoes_manual) <= 1 and len(descricoes_pedidos - descricoes_manual) == 0:
            categoria = "A"  # sem conflito
            detalhe = "Todas as descrições encontradas são equivalentes."
        elif len(variacoes) > 1 and len({v["descricao"] for v in variacoes if v["extensao"] is not None}) == len(
            [v for v in variacoes if v["extensao"] is not None]
        ) and len(descricoes_manual) > 1:
            categoria = "B"  # variação legítima: cada extensão tem descrição própria e diferente
            detalhe = "Cada variação (extensão) tem sua própria descrição específica."
        else:
            categoria = "C"  # conflito provável
            detalhe = f"Descrições divergentes para o mesmo código: {sorted(todas_descricoes)}"

        classificacao[pai] = {
            "categoria": categoria,
            "detalhe": detalhe,
            "descricoes_manual_cpd": sorted(descricoes_manual),
            "descricoes_em_pedidos": sorted(descricoes_pedidos),
            "pai_ausente": categoria == "D",
            "descricao_padrao_sugerida": None if categoria in ("C", "D", "E") else (sorted(todas_descricoes)[0] if todas_descricoes else None),
        }
    return classificacao


# ---------------------------------------------------------------------------
# 7) Cruzamento pedidos x manual_cpd
# ---------------------------------------------------------------------------

def cruzar_pedidos_manual_cpd(orders: list[dict], manual_cpd_rows: list[dict]) -> dict:
    codigos_manual = {row["codigo"]: row["descricao"] for row in manual_cpd_rows}

    usados_e_existentes = set()
    usados_e_ausentes = set()
    descricao_diferente = []
    pedidos_sem_cpd = []
    pedidos_cpd_invalido = []
    codigos_em_lixeira = set()
    codigos_em_visiveis = set()

    for o in orders:
        cpd = o.get("cpd")
        cpd_str = str(cpd or "").strip()
        if not cpd_str:
            pedidos_sem_cpd.append(o.get("_id"))
            continue
        if cpd is not None and str(cpd) != cpd_str and cpd_str == "":
            pedidos_cpd_invalido.append(o.get("_id"))
            continue

        if o.get("deleted"):
            codigos_em_lixeira.add(cpd_str)
        else:
            codigos_em_visiveis.add(cpd_str)

        if cpd_str in codigos_manual:
            usados_e_existentes.add(cpd_str)
            desc_pedido = str(o.get("descricao") or "").strip()
            desc_manual = str(codigos_manual[cpd_str] or "").strip()
            if desc_pedido and desc_manual and desc_pedido != desc_manual:
                descricao_diferente.append({
                    "codigo": cpd_str,
                    "descricao_pedido": desc_pedido,
                    "descricao_manual_cpd": desc_manual,
                    "pedido_id": o.get("_id"),
                })
        else:
            usados_e_ausentes.add(cpd_str)

    nunca_usados = set(codigos_manual.keys()) - codigos_em_visiveis - codigos_em_lixeira
    apenas_lixeira = codigos_em_lixeira - codigos_em_visiveis

    return {
        "cpds_usados_e_existentes_em_manual_cpd": sorted(usados_e_existentes),
        "cpds_usados_e_ausentes_em_manual_cpd": sorted(usados_e_ausentes),
        "cpds_em_manual_cpd_nunca_usados_em_pedidos": sorted(nunca_usados),
        "codigos_com_descricao_diferente_pedido_vs_manual": descricao_diferente,
        "pedidos_sem_cpd": pedidos_sem_cpd,
        "pedidos_com_cpd_invalido": pedidos_cpd_invalido,
        "cpds_presentes_apenas_em_pedidos_na_lixeira": sorted(apenas_lixeira),
    }


# ---------------------------------------------------------------------------
# 8) Vínculos cliente x CPD-pai (sugestão, nada é inserido)
# ---------------------------------------------------------------------------

def sugerir_vinculos_cliente_cpd(orders: list[dict], sugestao_grupos: dict) -> dict:
    vinculos: dict[tuple[str, str], dict] = {}
    for o in orders:
        cliente = str(o.get("cliente") or "").strip()
        cpd = str(o.get("cpd") or "").strip()
        if not cliente or not cpd:
            continue
        info_cpd = dbm.normalizar_cpd(cpd)
        chave = (cliente, info_cpd["codigo_pai"])
        item = vinculos.setdefault(chave, {
            "cliente_original": cliente,
            "cliente_canonico_sugerido": cliente,  # nesta etapa, 1:1 -- decisão de unir fica pra revisão humana
            "cpd_informado_exemplos": set(),
            "cpd_pai": info_cpd["codigo_pai"],
            "quantidade_pedidos": 0,
            "primeiro_uso": None,
            "ultimo_uso": None,
            "somente_lixeira": True,
        })
        item["cpd_informado_exemplos"].add(cpd)
        item["quantidade_pedidos"] += 1
        criado = str(o.get("criadoEm") or o.get("_updated_at") or "")
        atualizado = str(o.get("alteradoEm") or o.get("_updated_at") or "")
        if criado and (item["primeiro_uso"] is None or criado < item["primeiro_uso"]):
            item["primeiro_uso"] = criado
        if atualizado and (item["ultimo_uso"] is None or atualizado > item["ultimo_uso"]):
            item["ultimo_uso"] = atualizado
        if not o.get("deleted"):
            item["somente_lixeira"] = False

    vinculos_lista = []
    cpd_para_clientes: dict[str, set[str]] = defaultdict(set)
    for (cliente, cpd_pai), item in vinculos.items():
        item["cpd_informado_exemplos"] = sorted(item["cpd_informado_exemplos"])
        vinculos_lista.append(item)
        cpd_para_clientes[cpd_pai].add(cliente)

    cpds_unico_cliente = {p: list(c)[0] for p, c in cpd_para_clientes.items() if len(c) == 1}
    cpds_varios_clientes = {p: sorted(c) for p, c in cpd_para_clientes.items() if len(c) > 1}

    cpds_grupos_mistos = {}
    for cpd_pai, clientes in cpds_varios_clientes.items():
        grupos = {sugestao_grupos.get(c, {}).get("grupo_sugerido", "Diversos") for c in clientes}
        if len(grupos) > 1:
            cpds_grupos_mistos[cpd_pai] = {"clientes": clientes, "grupos_sugeridos": sorted(grupos)}

    cpds_apenas_lixeira = [v for v in vinculos_lista if v["somente_lixeira"]]

    return {
        "vinculos_sugeridos": vinculos_lista,
        "cpds_pai_ligados_a_um_unico_cliente": cpds_unico_cliente,
        "cpds_pai_ligados_a_varios_clientes": cpds_varios_clientes,
        "cpds_pai_compartilhados_entre_grupos_sugeridos_diferentes": cpds_grupos_mistos,
        "vinculos_presentes_apenas_em_pedidos_na_lixeira": len(cpds_apenas_lixeira),
    }


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------

def executar_analise(conn: sqlite3.Connection, grupo_honda: set[str]) -> dict:
    orders = carregar_orders(conn)
    manual_cpd_rows = carregar_manual_cpd(conn)

    analise_clientes = analisar_clientes(orders)
    sugestao_grupos = sugerir_grupos(analise_clientes, grupo_honda)
    analise_cpds = analisar_cpds(manual_cpd_rows)
    conflitos = classificar_conflitos_descricao(analise_cpds, orders)
    cruzamento = cruzar_pedidos_manual_cpd(orders, manual_cpd_rows)
    vinculos = sugerir_vinculos_cliente_cpd(orders, sugestao_grupos)

    itens_para_decisao_humana = []
    for item in analise_clientes["possiveis_aliases_alta_confianca"]:
        itens_para_decisao_humana.append({"tipo": "alias_cliente_alta_confianca", **item})
    for item in analise_clientes["possiveis_aliases_para_decisao_humana"]:
        itens_para_decisao_humana.append({"tipo": "alias_cliente_para_revisar", **item})
    for nome, sugestao in sugestao_grupos.items():
        if sugestao["revisao_humana"]:
            itens_para_decisao_humana.append({"tipo": "grupo_cliente_para_revisar", "cliente": nome, **sugestao})
    for pai, info in conflitos.items():
        if info["categoria"] in ("C", "D", "E"):
            itens_para_decisao_humana.append({"tipo": "conflito_descricao_cpd", "cpd_pai": pai, **info})
    for cpd_pai, info in vinculos["cpds_pai_compartilhados_entre_grupos_sugeridos_diferentes"].items():
        itens_para_decisao_humana.append({"tipo": "cpd_compartilhado_entre_grupos", "cpd_pai": cpd_pai, **info})

    return {
        "orders": orders,
        "manual_cpd_rows": manual_cpd_rows,
        "analise_clientes": analise_clientes,
        "sugestao_grupos": sugestao_grupos,
        "analise_cpds": analise_cpds,
        "conflitos_descricao": conflitos,
        "cruzamento_pedidos_manual_cpd": cruzamento,
        "vinculos_sugeridos": vinculos,
        "itens_para_decisao_humana": itens_para_decisao_humana,
    }


# ---------------------------------------------------------------------------
# Relatórios
# ---------------------------------------------------------------------------

def _resumo_serializavel(resultado: dict, metadados: dict) -> dict:
    def sem_pais_completo(analise_cpds):
        # "pais" pode ser grande; no resumo json, só as contagens (o detalhe
        # completo vai pro xlsx cpds_pais_e_variacoes).
        copia = dict(analise_cpds)
        copia.pop("pais", None)
        return copia

    return {
        "metadados": metadados,
        "analise_clientes": {k: v for k, v in resultado["analise_clientes"].items() if k != "detalhado_por_cliente"},
        "total_clientes_com_sugestao_de_grupo": len(resultado["sugestao_grupos"]),
        "analise_cpds": sem_pais_completo(resultado["analise_cpds"]),
        "cruzamento_pedidos_manual_cpd": {
            k: (len(v) if isinstance(v, list) else v)
            for k, v in resultado["cruzamento_pedidos_manual_cpd"].items()
        },
        "vinculos_resumo": {
            "total_vinculos_sugeridos": len(resultado["vinculos_sugeridos"]["vinculos_sugeridos"]),
            "cpds_pai_unico_cliente": len(resultado["vinculos_sugeridos"]["cpds_pai_ligados_a_um_unico_cliente"]),
            "cpds_pai_varios_clientes": len(resultado["vinculos_sugeridos"]["cpds_pai_ligados_a_varios_clientes"]),
            "cpds_pai_grupos_mistos": len(resultado["vinculos_sugeridos"]["cpds_pai_compartilhados_entre_grupos_sugeridos_diferentes"]),
        },
        "total_itens_para_decisao_humana": len(resultado["itens_para_decisao_humana"]),
    }


def gravar_json(resultado: dict, metadados: dict, pasta_saida: Path) -> Path:
    caminho = pasta_saida / "resumo_migracao_clientes_cpds.json"
    with caminho.open("w", encoding="utf-8") as f:
        json.dump(_resumo_serializavel(resultado, metadados), f, ensure_ascii=False, indent=2, default=str)
    return caminho


def gravar_xlsx(resultado: dict, metadados: dict, pasta_saida: Path) -> list[Path]:
    from openpyxl import Workbook

    arquivos = []

    def nova_planilha(nome_arquivo: str, cabecalho: list[str], linhas: list[list]) -> Path:
        wb = Workbook()
        ws = wb.active
        ws.title = "Dados"
        ws.append([f"Cópia analisada em: {metadados['copia_criada_em']}"])
        ws.append([f"Arquivo de origem: {metadados['banco_origem']}"])
        ws.append([])
        ws.append(cabecalho)
        for linha in linhas:
            ws.append(linha)
        caminho = pasta_saida / nome_arquivo
        wb.save(caminho)
        arquivos.append(caminho)
        return caminho

    ac = resultado["analise_clientes"]
    nova_planilha(
        "clientes_encontrados.xlsx",
        ["Cliente", "Sem espaços", "Normalizado", "Qtd pedidos", "Qtd ativos", "Qtd lixeira", "1º uso", "Último uso", "CPDs distintos", "Somente lixeira"],
        [
            [nome, i["valor_sem_espacos"], i["normalizado_para_comparacao"], i["quantidade_pedidos"],
             i["quantidade_pedidos_ativos"], i["quantidade_pedidos_lixeira"], i["primeiro_uso"], i["ultimo_uso"],
             ", ".join(i["cpds_distintos"]), i["somente_lixeira"]]
            for nome, i in ac["detalhado_por_cliente"].items()
        ],
    )

    linhas_aliases = []
    for item in ac["possiveis_aliases_alta_confianca"]:
        linhas_aliases.append(["alta", ", ".join(item["variantes_originais"]), item["forma_normalizada"], item["justificativa"], ""])
    for item in ac["possiveis_aliases_para_decisao_humana"]:
        linhas_aliases.append([
            "media/baixa", f"{item['cliente_a']} | {item['cliente_b']}", "", item["motivo"], item["similaridade"],
        ])
    nova_planilha(
        "possiveis_aliases_clientes.xlsx",
        ["Confiança", "Clientes envolvidos", "Forma normalizada", "Motivo", "Similaridade"],
        linhas_aliases,
    )

    sg = resultado["sugestao_grupos"]
    linhas_grupos = [
        [nome, s["grupo_sugerido"], s["confianca"], s["revisao_humana"], s["justificativa"]]
        for nome, s in sg.items()
    ]
    nova_planilha(
        "sugestao_grupos_clientes.xlsx",
        ["Cliente", "Grupo sugerido", "Confiança", "Revisão humana?", "Justificativa"],
        linhas_grupos,
    )

    acpd = resultado["analise_cpds"]
    linhas_cpds = []
    for pai, variacoes in acpd["pais"].items():
        for v in variacoes:
            linhas_cpds.append([pai, v["codigo_original"], v["extensao"], v["descricao"], v["updated_at"]])
    nova_planilha(
        "cpds_pais_e_variacoes.xlsx",
        ["CPD pai", "Código original", "Extensão", "Descrição", "Atualizado em"],
        linhas_cpds,
    )

    conf = resultado["conflitos_descricao"]
    linhas_conf = [
        [pai, info["categoria"], info["detalhe"], "; ".join(info["descricoes_manual_cpd"]), "; ".join(info["descricoes_em_pedidos"])]
        for pai, info in conf.items()
        if info["categoria"] != "A"
    ]
    nova_planilha(
        "conflitos_descricoes_cpds.xlsx",
        ["CPD pai", "Categoria", "Detalhe", "Descrições em manual_cpd", "Descrições em pedidos"],
        linhas_conf,
    )

    cruz = resultado["cruzamento_pedidos_manual_cpd"]
    nova_planilha(
        "cpds_pedidos_ausentes_manual.xlsx",
        ["CPD usado em pedido, ausente de manual_cpd"],
        [[c] for c in cruz["cpds_usados_e_ausentes_em_manual_cpd"]],
    )
    nova_planilha(
        "cpds_manual_sem_uso.xlsx",
        ["CPD cadastrado em manual_cpd, nunca usado em pedidos"],
        [[c] for c in cruz["cpds_em_manual_cpd_nunca_usados_em_pedidos"]],
    )

    vinc = resultado["vinculos_sugeridos"]
    nova_planilha(
        "vinculos_sugeridos_cliente_cpd.xlsx",
        ["Cliente original", "Cliente canônico sugerido", "CPDs informados", "CPD pai", "Qtd pedidos", "1º uso", "Último uso", "Somente lixeira"],
        [
            [v["cliente_original"], v["cliente_canonico_sugerido"], ", ".join(v["cpd_informado_exemplos"]),
             v["cpd_pai"], v["quantidade_pedidos"], v["primeiro_uso"], v["ultimo_uso"], v["somente_lixeira"]]
            for v in vinc["vinculos_sugeridos"]
        ],
    )

    linhas_decisao = [
        [item.get("tipo"), json.dumps({k: v for k, v in item.items() if k != "tipo"}, ensure_ascii=False, default=str)]
        for item in resultado["itens_para_decisao_humana"]
    ]
    nova_planilha(
        "itens_para_decisao_humana.xlsx",
        ["Tipo", "Detalhe (JSON)"],
        linhas_decisao,
    )

    return arquivos


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Análise somente-leitura para migração de clientes e CPDs.")
    parser.add_argument("--banco", type=Path, default=DEFAULT_DB, help="Banco de origem (padrão: pcp.sqlite3 real).")
    parser.add_argument("--saida", type=Path, default=DEFAULT_SAIDA, help="Pasta de saída dos relatórios.")
    parser.add_argument(
        "--usar-copia", action="store_true",
        help="Trata --banco como já sendo uma cópia segura (ex.: já criada por sqlite3.Connection.backup()) e analisa direto, sem copiar de novo.",
    )
    parser.add_argument("--formato", choices=["json", "xlsx", "ambos"], default="ambos")
    parser.add_argument(
        "--config-clientes", type=Path, required=True,
        help="Caminho do JSON local com as regras de clientes (grupo_honda/aliases/placeholders_invalidos). "
             "Ver config_local/regras_clientes_migracao.example.json.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.saida.mkdir(parents=True, exist_ok=True)

    try:
        config = config_clientes.carregar_config_clientes(args.config_clientes)
    except (FileNotFoundError, config_clientes.ConfigClientesInvalida) as exc:
        print(f"ERRO: {exc}")
        return 1

    if args.usar_copia:
        if not args.banco.exists():
            print(f"ERRO: --usar-copia informado, mas {args.banco} não existe.")
            return 1
        copia = args.banco
        copia_criada_agora = False
    else:
        if not args.banco.exists():
            print(f"ERRO: banco de origem não encontrado: {args.banco}")
            return 1
        copia = criar_copia_segura(args.banco, args.saida / "_copias_temporarias")
        copia_criada_agora = True

    horario_copia = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = abrir_somente_leitura(copia)
    try:
        resultado = executar_analise(conn, config.grupo_honda)
    finally:
        conn.close()

    metadados = {
        "banco_origem": str(args.banco),
        "copia_analisada": str(copia),
        "copia_criada_nesta_execucao": copia_criada_agora,
        "copia_criada_em": horario_copia,
        "gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "config_clientes_caminho": config.caminho,
        "config_clientes_hash_sha256": config.hash_sha256,
    }

    arquivos_gerados = []
    if args.formato in ("json", "ambos"):
        arquivos_gerados.append(gravar_json(resultado, metadados, args.saida))
    if args.formato in ("xlsx", "ambos"):
        arquivos_gerados.extend(gravar_xlsx(resultado, metadados, args.saida))

    print(f"Cópia analisada: {copia} (criada em {horario_copia})")
    print(f"Clientes distintos: {resultado['analise_clientes']['total_clientes_distintos_raw']}")
    print(f"CPDs-pai estimados: {resultado['analise_cpds']['total_pais_estimado']}")
    print(f"Itens para decisão humana: {len(resultado['itens_para_decisao_humana'])}")
    print("Arquivos gerados:")
    for arq in arquivos_gerados:
        print(f"  {arq}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
