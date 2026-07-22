"""Segurança, backup, versão de schema e validação do banco pcp.sqlite3.

Este módulo concentra as rotinas de manutenção introduzidas na etapa de
"segurança e preparação de migrações":

- Backup oficial do SQLite via sqlite3.Connection.backup() (funciona com o
  banco em modo WAL, ao contrário de uma simples cópia de arquivo).
- Controle de versão de schema, guardado na tabela `meta` já existente.
- Backup obrigatório e validado antes de qualquer migração futura.
- Relatório de validação dos dados existentes (totais + integrity_check).

Nesta etapa NENHUMA tabela existente é alterada. O dicionário MIGRATIONS
está vazio de propósito: só prepara a estrutura para migrações futuras.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable
import json
import sqlite3
import traceback

SCHEMA_VERSION_KEY = "schema_version"


def _log_default(msg: str) -> None:
    print(msg)


def _remover_arquivo_seguro(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 1) Backup oficial via API do SQLite (funciona com o banco em modo WAL)
# ---------------------------------------------------------------------------

def verificar_integridade(db_path: Path) -> str:
    """Abre o banco e roda PRAGMA integrity_check. Retorna 'ok' se estiver íntegro."""
    try:
        c = sqlite3.connect(str(db_path))
        try:
            row = c.execute("PRAGMA integrity_check").fetchone()
            return str(row[0]) if row else "erro: sem resultado do integrity_check"
        finally:
            c.close()
    except Exception:
        return "erro: " + traceback.format_exc(limit=1).strip().splitlines()[-1]


def criar_backup_sqlite(db_path: Path, backup_dir: Path, prefixo: str = "pcp_backup", log: Callable[[str], None] = _log_default) -> Path | None:
    """Cria um backup consistente do banco usando sqlite3.Connection.backup().

    Diferente de shutil.copy2 (que pode copiar o .sqlite3 sem as páginas que
    ainda só existem no -wal), o backup API do SQLite lê o estado consolidado
    do banco corretamente mesmo com journal_mode=WAL.

    O backup só é considerado válido se abrir e o PRAGMA integrity_check
    retornar "ok"; caso contrário o arquivo de backup é descartado e a
    função retorna None. Nada dos backups já existentes é apagado.
    """
    db_path = Path(db_path)
    backup_dir = Path(backup_dir)
    if not db_path.exists():
        log(f"[backup] Banco {db_path} não encontrado; backup não foi gerado.")
        return None

    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destino = backup_dir / f"{prefixo}_{stamp}.sqlite3"

    origem_conn = None
    destino_conn = None
    try:
        origem_conn = sqlite3.connect(str(db_path))
        destino_conn = sqlite3.connect(str(destino))
        with destino_conn:
            origem_conn.backup(destino_conn)
    except Exception:
        log(f"[backup] Erro ao criar backup de {db_path.name}:\n" + traceback.format_exc())
        _remover_arquivo_seguro(destino)
        return None
    finally:
        if destino_conn is not None:
            destino_conn.close()
        if origem_conn is not None:
            origem_conn.close()

    resultado = verificar_integridade(destino)
    if resultado != "ok":
        log(f"[backup] Integrity check falhou para {destino.name}: {resultado}. Backup descartado.")
        _remover_arquivo_seguro(destino)
        return None

    log(f"[backup] Backup válido criado: {destino.name} (integrity_check=ok)")
    return destino


# ---------------------------------------------------------------------------
# 2) Sistema de versão do banco (tabela meta, chave schema_version)
# ---------------------------------------------------------------------------

def get_schema_version(c: sqlite3.Connection) -> int:
    """Lê schema_version da tabela meta, criando-a como 1 se ainda não existir."""
    c.execute("INSERT OR IGNORE INTO meta(key,value) VALUES(?,?)", (SCHEMA_VERSION_KEY, "1"))
    row = c.execute("SELECT value FROM meta WHERE key=?", (SCHEMA_VERSION_KEY,)).fetchone()
    try:
        return int(row[0]) if row is not None else 1
    except (TypeError, ValueError):
        return 1


def set_schema_version(c: sqlite3.Connection, version: int) -> None:
    c.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)",
        (SCHEMA_VERSION_KEY, str(int(version))),
    )


# Migrações futuras entram aqui: {versao_origem: funcao(conn) -> None}.
# Cada função deve ser idempotente e só mexer no schema, nunca apagar dados.
# Ex.: MIGRATIONS[2] = migrar_v2_para_v3
MIGRATIONS: dict[int, Callable[[sqlite3.Connection], None]] = {}


def criar_backup_pre_migracao(db_path: Path, backup_dir: Path, de: int, para: int, log: Callable[[str], None] = _log_default) -> Path | None:
    """Backup obrigatório antes de aplicar uma migração de versão `de` para `para`.

    Nome do arquivo: pcp_pre_migracao_v{de}_para_v{para}_AAAA-MM-DD_HH-MM-SS.sqlite3
    """
    prefixo = f"pcp_pre_migracao_v{de}_para_v{para}"
    return criar_backup_sqlite(db_path, backup_dir, prefixo=prefixo, log=log)


def run_migrations(c: sqlite3.Connection, db_path: Path, backup_dir: Path, log: Callable[[str], None] = _log_default) -> dict:
    """Executa migrações pendentes, sequencialmente, cada uma com backup prévio.

    Regras:
    - Sequencial: só aplica v -> v+1 se v+1 estiver registrada em MIGRATIONS.
    - Idempotente: se a versão atual já é a mais recente, não faz nada.
    - Nunca migra sem um backup válido (integrity_check == "ok") imediatamente
      antes; se o backup falhar, a migração é cancelada e nada é alterado.
    """
    aplicadas: list[int] = []
    versao = get_schema_version(c)

    while versao in MIGRATIONS:
        alvo = versao + 1
        backup = criar_backup_pre_migracao(db_path, backup_dir, versao, alvo, log=log)
        if backup is None:
            log(f"[migracao] Backup pré-migração v{versao}->v{alvo} falhou ou é inválido. Migração cancelada, nada foi alterado.")
            break
        try:
            MIGRATIONS[versao](c)
            set_schema_version(c, alvo)
            c.commit()
            aplicadas.append(alvo)
            log(f"[migracao] Migração v{versao} -> v{alvo} aplicada com sucesso. Backup: {backup.name}")
            versao = alvo
        except Exception:
            c.rollback()
            log(f"[migracao] Erro ao aplicar migração v{versao}->v{alvo}, migração cancelada:\n" + traceback.format_exc())
            break

    return {"versao_final": get_schema_version(c), "migracoes_aplicadas": aplicadas}


# ---------------------------------------------------------------------------
# 4) Validação dos dados existentes
# ---------------------------------------------------------------------------

_FINALIZADOS = {"concluído", "concluido", "cancelado", "cancelada"}


def gerar_relatorio_validacao(db_path: Path, salvar_em: Path | None = None) -> dict:
    """Gera um resumo somente-leitura dos dados existentes no banco.

    Não altera nenhum dado. Se `salvar_em` for informado, grava o relatório
    como JSON nesse caminho (ex.: backups/validacao_banco_AAAA-MM-DD_HH-MM-SS.json).
    """
    db_path = Path(db_path)
    relatorio = {
        "gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "banco": str(db_path),
        "integrity_check": verificar_integridade(db_path),
    }

    c = sqlite3.connect(str(db_path))
    c.row_factory = sqlite3.Row
    try:
        pedidos = c.execute("SELECT payload FROM orders").fetchall()
        ativos = finalizados = lixeira_pedidos = 0
        for row in pedidos:
            try:
                payload = json.loads(row["payload"]) if row["payload"] else {}
            except Exception:
                payload = {}
            if payload.get("deleted"):
                lixeira_pedidos += 1
                continue
            setor = str(payload.get("setor") or "").strip().lower()
            if setor in _FINALIZADOS:
                finalizados += 1
            else:
                ativos += 1

        secoes = c.execute("SELECT payload FROM sections").fetchall()
        lixeira_secoes = 0
        for row in secoes:
            try:
                payload = json.loads(row["payload"]) if row["payload"] else {}
            except Exception:
                payload = {}
            if payload.get("deleted"):
                lixeira_secoes += 1

        total_auditoria = c.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        total_cpds = c.execute("SELECT COUNT(*) FROM manual_cpd").fetchone()[0]

        relatorio.update(
            {
                "total_pedidos": len(pedidos),
                "total_datas_secoes": len(secoes),
                "total_pedidos_ativos": ativos,
                "total_pedidos_finalizados": finalizados,
                "total_pedidos_lixeira": lixeira_pedidos,
                "total_datas_lixeira": lixeira_secoes,
                "total_registros_auditoria": total_auditoria,
                "total_cpds_cadastrados": total_cpds,
            }
        )
    finally:
        c.close()

    if salvar_em is not None:
        salvar_em = Path(salvar_em)
        salvar_em.parent.mkdir(parents=True, exist_ok=True)
        salvar_em.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")

    return relatorio
