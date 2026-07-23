"""Segurança, backup, versão de schema e validação do banco pcp.sqlite3.

Este módulo concentra as rotinas de manutenção introduzidas na etapa de
"segurança e preparação de migrações":

- Backup oficial do SQLite via sqlite3.Connection.backup() (funciona com o
  banco em modo WAL, ao contrário de uma simples cópia de arquivo).
- Controle de versão de schema, guardado na tabela `meta` já existente.
- Backup obrigatório e validado antes de qualquer migração futura.
- Relatório de validação dos dados existentes (totais + integrity_check).

E, na etapa "estrutura e configurações" (schema_version 1 -> 2):

- Tabelas novas de áreas, perfis, permissões e usuários (sem criar nenhum
  usuário real ainda).
- Tabelas novas de clientes, grupos de clientes e CPDs (pai + variações),
  sem migrar nenhum dado real ainda.
- Tabelas novas de processos, fornecedores, rotas e níveis/regras de
  urgência, sem conectar nada à tela atual ainda.
- Tabelas novas de configurações do sistema e histórico de configurações.
- Utilitários puros: normalizar_cpd() (separa código pai/extensão sem
  nunca converter para número) e hash_senha()/verificar_senha() (nenhuma
  senha é armazenada em texto puro).

NENHUMA tabela existente (meta, orders, sections, manual_cpd, audit_log)
é alterada, apagada ou renomeada por nenhuma migração deste módulo.

E, na etapa schema_version 2 -> 3 (retroaplica validações que não
retroagiram na migração anterior, já que CREATE TABLE IF NOT EXISTS não
altera tabelas já criadas):

- Reconstrói só as tabelas `processos`, `regras_urgencia` e
  `niveis_urgencia` com os CHECK que faltavam, preservando IDs, timestamps
  e todos os dados existentes. Nenhuma outra tabela é tocada.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable
import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import traceback

SCHEMA_VERSION_KEY = "schema_version"

# Versão de schema mais recente conhecida por este módulo. Mantida em sincronia
# com MIGRATIONS por um assert logo após o registro da última migração —
# nunca espalhar o número "3" (ou o que vier depois) por outros arquivos.
LATEST_SCHEMA_VERSION = 3


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


# Migrações registradas aqui: {versao_origem: funcao(conn) -> None}.
# Cada função deve ser idempotente e só mexer no schema, nunca apagar dados.
MIGRATIONS: dict[int, Callable[[sqlite3.Connection], None]] = {}


def migracoes_pendentes(versao_atual: int) -> list[int]:
    """Lista, em ordem, as versões-alvo ainda pendentes a partir de `versao_atual`.

    Ex.: com MIGRATIONS = {1: ..., 2: ...}, migracoes_pendentes(1) == [2, 3],
    migracoes_pendentes(2) == [3], migracoes_pendentes(3) == []. Não altera
    nada — só espelha, de forma pura e testável, a mesma sequência que
    run_migrations() aplicaria.
    """
    pendentes: list[int] = []
    versao = versao_atual
    while versao in MIGRATIONS:
        versao += 1
        pendentes.append(versao)
    return pendentes


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


# ---------------------------------------------------------------------------
# 5) Hash de senha (nunca armazenar em texto puro)
# ---------------------------------------------------------------------------

_HASH_ALGO = "pbkdf2_sha256"
_HASH_ITERACOES = 200_000


def hash_senha(senha: str) -> str:
    """Gera um hash salgado (PBKDF2-HMAC-SHA256) para gravar em usuarios.senha_hash.

    A senha em si nunca é armazenada, só este hash. Formato do resultado:
    'pbkdf2_sha256$<iteracoes>$<salt_hex>$<hash_hex>'.
    """
    if not senha:
        raise ValueError("Senha não pode ser vazia")
    salt = secrets.token_hex(16)
    derivado = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), bytes.fromhex(salt), _HASH_ITERACOES)
    return f"{_HASH_ALGO}${_HASH_ITERACOES}${salt}${derivado.hex()}"


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Confere uma senha em texto contra o hash salvo, em tempo constante."""
    try:
        algo, iteracoes, salt, hash_hex = (hash_armazenado or "").split("$")
        if algo != _HASH_ALGO:
            return False
        derivado = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), bytes.fromhex(salt), int(iteracoes))
        return hmac.compare_digest(derivado.hex(), hash_hex)
    except (ValueError, AttributeError):
        return False


# ---------------------------------------------------------------------------
# 6) Normalização de código de CPD (código pai + extensão)
# ---------------------------------------------------------------------------

# Extensão só é reconhecida quando o código termina em ".<dígitos>", usando
# o ÚLTIMO ponto do código (o ".+" guloso consome pontos anteriores).
_CPD_EXTENSAO_RE = re.compile(r"^(.+)\.(\d+)$")


def normalizar_cpd(codigo: str) -> dict:
    """Separa um código de CPD em código pai + extensão, sempre como texto.

    - '04772'    -> pai '04772', extensão None
    - '04772.1'  -> pai '04772', extensão '1'
    - '04772.10' -> pai '04772', extensão '10'
    - 'ABC.1'    -> pai 'ABC', extensão '1'
    - '01234.A'  -> não é extensão numérica; pai permanece '01234.A' inteiro
    - None ou '' (inclusive só espaços) -> pai '', extensão None; nunca
      levanta exceção. Regra explícita: entrada vazia/ausente é tratada como
      "sem código", não como erro — quem chama decide se isso é inválido
      para o contexto (ex.: rejeitar cadastro com código vazio).

    Nunca converte o código para número: zeros à esquerda (no pai ou na
    extensão) são sempre preservados como texto.
    """
    original = str(codigo or "").strip()
    match = _CPD_EXTENSAO_RE.match(original)
    if match:
        return {"codigo_original": original, "codigo_pai": match.group(1), "extensao": match.group(2)}
    return {"codigo_original": original, "codigo_pai": original, "extensao": None}


# ---------------------------------------------------------------------------
# 7) Migração schema_version 1 -> 2: estrutura e configurações
# ---------------------------------------------------------------------------
#
# Cria só tabelas/índices novos (todos com IF NOT EXISTS) e só dados padrão
# controlados (grupos Honda/Diversos, níveis de urgência), inseridos com
# INSERT OR IGNORE contra colunas UNIQUE — repetir a migração não duplica
# nada. Nenhuma tabela existente é tocada. Nenhum dado real (cliente, CPD,
# processo, usuário) é migrado nesta etapa.
#
# Importante: as instruções são executadas uma a uma via c.execute (nunca
# c.executescript, que força um COMMIT implícito antes de rodar e quebraria
# a transação/rollback que run_migrations() já garante em volta desta
# função).

_V2_TABELAS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS areas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS perfis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        perfil_sistema INTEGER NOT NULL DEFAULT 0,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS permissoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nome TEXT NOT NULL,
        descricao TEXT,
        modulo TEXT,
        criado_em TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS perfil_permissoes (
        perfil_id INTEGER NOT NULL REFERENCES perfis(id) ON DELETE CASCADE,
        permissao_id INTEGER NOT NULL REFERENCES permissoes(id) ON DELETE CASCADE,
        permitido INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        PRIMARY KEY (perfil_id, permissao_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_completo TEXT NOT NULL,
        area_id INTEGER NOT NULL REFERENCES areas(id) ON DELETE RESTRICT,
        login TEXT NOT NULL COLLATE NOCASE UNIQUE,
        senha_hash TEXT NOT NULL,
        perfil_id INTEGER NOT NULL REFERENCES perfis(id) ON DELETE RESTRICT,
        ativo INTEGER NOT NULL DEFAULT 1,
        bloqueado INTEGER NOT NULL DEFAULT 0,
        deve_trocar_senha INTEGER NOT NULL DEFAULT 0,
        tentativas_falhas INTEGER NOT NULL DEFAULT 0,
        bloqueado_ate TEXT,
        ultimo_acesso TEXT,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL,
        desativado_em TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuario_permissoes (
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        permissao_id INTEGER NOT NULL REFERENCES permissoes(id) ON DELETE CASCADE,
        permitido INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        PRIMARY KEY (usuario_id, permissao_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS grupos_clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        codigo_interno TEXT,
        observacoes TEXT,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL,
        desativado_em TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS cliente_aliases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
        alias TEXT NOT NULL,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS cliente_grupos (
        cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
        grupo_id INTEGER NOT NULL REFERENCES grupos_clientes(id) ON DELETE CASCADE,
        criado_em TEXT NOT NULL,
        PRIMARY KEY (cliente_id, grupo_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS cpds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_pai TEXT NOT NULL UNIQUE,
        descricao_padrao TEXT,
        observacoes TEXT,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL,
        desativado_em TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS cpd_variacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpd_id INTEGER NOT NULL REFERENCES cpds(id) ON DELETE RESTRICT,
        codigo_completo TEXT NOT NULL UNIQUE,
        extensao TEXT,
        descricao_especifica TEXT,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS cliente_cpds (
        cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
        cpd_id INTEGER NOT NULL REFERENCES cpds(id) ON DELETE CASCADE,
        criado_em TEXT NOT NULL,
        PRIMARY KEY (cliente_id, cpd_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS grupo_cpds (
        grupo_id INTEGER NOT NULL REFERENCES grupos_clientes(id) ON DELETE CASCADE,
        cpd_id INTEGER NOT NULL REFERENCES cpds(id) ON DELETE CASCADE,
        criado_em TEXT NOT NULL,
        PRIMARY KEY (grupo_id, cpd_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS processos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        grupo_processo TEXT,
        interno INTEGER NOT NULL DEFAULT 1,
        externo INTEGER NOT NULL DEFAULT 0,
        exige_previsao_retorno INTEGER NOT NULL DEFAULT 0,
        ordem_padrao INTEGER,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL,
        CHECK (interno IN (0, 1) AND externo IN (0, 1) AND (interno = 1 OR externo = 1))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS fornecedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        codigo_interno TEXT,
        tipo_servico TEXT,
        observacoes TEXT,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS processo_fornecedores (
        processo_id INTEGER NOT NULL REFERENCES processos(id) ON DELETE CASCADE,
        fornecedor_id INTEGER NOT NULL REFERENCES fornecedores(id) ON DELETE CASCADE,
        preferencial INTEGER NOT NULL DEFAULT 0,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        PRIMARY KEY (processo_id, fornecedor_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS rotas_processo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS rota_etapas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rota_id INTEGER NOT NULL REFERENCES rotas_processo(id) ON DELETE RESTRICT,
        processo_id INTEGER NOT NULL REFERENCES processos(id) ON DELETE RESTRICT,
        fornecedor_id INTEGER REFERENCES fornecedores(id) ON DELETE SET NULL,
        ordem INTEGER NOT NULL,
        obrigatoria INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS niveis_urgencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nome TEXT NOT NULL,
        prioridade INTEGER NOT NULL,
        cor_fundo TEXT,
        cor_texto TEXT,
        cor_borda TEXT,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL,
        CHECK (prioridade > 0)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS regras_urgencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        processo_id INTEGER REFERENCES processos(id) ON DELETE SET NULL,
        dias_minimos INTEGER,
        dias_maximos INTEGER,
        nivel_urgencia_id INTEGER NOT NULL REFERENCES niveis_urgencia(id) ON DELETE RESTRICT,
        prioridade INTEGER NOT NULL DEFAULT 0,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL,
        CHECK (dias_minimos IS NULL OR dias_maximos IS NULL OR dias_minimos <= dias_maximos)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS configuracoes_sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chave TEXT NOT NULL UNIQUE,
        valor TEXT,
        tipo TEXT,
        descricao TEXT,
        atualizado_por_usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS historico_configuracoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entidade TEXT NOT NULL,
        entidade_id TEXT,
        acao TEXT NOT NULL,
        valor_anterior_json TEXT,
        valor_novo_json TEXT,
        usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
        ator_texto TEXT,
        criado_em TEXT NOT NULL
    )
    """,
)

_V2_INDICES: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_usuarios_area ON usuarios(area_id)",
    "CREATE INDEX IF NOT EXISTS idx_usuarios_perfil ON usuarios(perfil_id)",
    "CREATE INDEX IF NOT EXISTS idx_perfil_permissoes_permissao ON perfil_permissoes(permissao_id)",
    "CREATE INDEX IF NOT EXISTS idx_usuario_permissoes_permissao ON usuario_permissoes(permissao_id)",
    "CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes(nome)",
    "CREATE INDEX IF NOT EXISTS idx_cliente_aliases_cliente ON cliente_aliases(cliente_id)",
    "CREATE INDEX IF NOT EXISTS idx_cliente_aliases_alias ON cliente_aliases(alias)",
    "CREATE INDEX IF NOT EXISTS idx_cliente_grupos_grupo ON cliente_grupos(grupo_id)",
    "CREATE INDEX IF NOT EXISTS idx_cpd_variacoes_cpd ON cpd_variacoes(cpd_id)",
    "CREATE INDEX IF NOT EXISTS idx_cliente_cpds_cpd ON cliente_cpds(cpd_id)",
    "CREATE INDEX IF NOT EXISTS idx_grupo_cpds_cpd ON grupo_cpds(cpd_id)",
    "CREATE INDEX IF NOT EXISTS idx_processos_nome ON processos(nome)",
    "CREATE INDEX IF NOT EXISTS idx_fornecedores_nome ON fornecedores(nome)",
    "CREATE INDEX IF NOT EXISTS idx_processo_fornecedores_fornecedor ON processo_fornecedores(fornecedor_id)",
    "CREATE INDEX IF NOT EXISTS idx_rota_etapas_rota ON rota_etapas(rota_id)",
    "CREATE INDEX IF NOT EXISTS idx_rota_etapas_processo ON rota_etapas(processo_id)",
    "CREATE INDEX IF NOT EXISTS idx_regras_urgencia_processo ON regras_urgencia(processo_id)",
    "CREATE INDEX IF NOT EXISTS idx_regras_urgencia_nivel ON regras_urgencia(nivel_urgencia_id)",
    "CREATE INDEX IF NOT EXISTS idx_historico_config_entidade ON historico_configuracoes(entidade, entidade_id)",
)

# codigo -> (nome, prioridade, cor_fundo, cor_texto, cor_borda); prioridade
# menor = mais urgente.
_V2_NIVEIS_URGENCIA_PADRAO: tuple[tuple[str, str, int, str, str, str], ...] = (
    ("ATRASADO", "Atrasado", 1, "#7f1d1d", "#ffffff", "#b91c1c"),
    ("CRITICO", "Crítico", 2, "#dc2626", "#ffffff", "#991b1b"),
    ("ALTO", "Alto", 3, "#f97316", "#ffffff", "#c2410c"),
    ("ATENCAO", "Atenção", 4, "#facc15", "#1f2937", "#ca8a04"),
    ("NORMAL", "Normal", 5, "#e5e7eb", "#1f2937", "#9ca3af"),
)

_V2_GRUPOS_CLIENTES_PADRAO: tuple[str, ...] = ("Honda", "Diversos")


def _seed_v2_dados_padrao(c: sqlite3.Connection) -> None:
    """Insere grupos de clientes e níveis de urgência padrão.

    Não contêm dados sensíveis/reais — são vocabulário fixo do sistema.
    INSERT OR IGNORE contra colunas UNIQUE garante que repetir a migração
    não duplica essas linhas.
    """
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for nome in _V2_GRUPOS_CLIENTES_PADRAO:
        c.execute(
            "INSERT OR IGNORE INTO grupos_clientes(nome, descricao, ativo, criado_em, atualizado_em) VALUES (?,?,?,?,?)",
            (nome, None, 1, agora, agora),
        )

    for codigo, nome, prioridade, cor_fundo, cor_texto, cor_borda in _V2_NIVEIS_URGENCIA_PADRAO:
        c.execute(
            """
            INSERT OR IGNORE INTO niveis_urgencia
                (codigo, nome, prioridade, cor_fundo, cor_texto, cor_borda, ativo, criado_em, atualizado_em)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (codigo, nome, prioridade, cor_fundo, cor_texto, cor_borda, 1, agora, agora),
        )


def migrar_v1_para_v2(c: sqlite3.Connection) -> None:
    """Migração de schema_version 1 -> 2: estrutura e configurações.

    Cria as tabelas de áreas, perfis, permissões, usuários, clientes,
    grupos de clientes, CPDs (pai + variações), processos, fornecedores,
    rotas, níveis/regras de urgência e configurações do sistema — só
    estruturas novas, nada existente é apagado/renomeado. Idempotente:
    chamar de novo não duplica tabelas nem os dados padrão (grupos
    Honda/Diversos, níveis de urgência). Roda dentro da transação e do
    backup pré-migração já garantidos por run_migrations().
    """
    for statement in _V2_TABELAS:
        c.execute(statement)
    for statement in _V2_INDICES:
        c.execute(statement)
    _seed_v2_dados_padrao(c)


MIGRATIONS[1] = migrar_v1_para_v2


# ---------------------------------------------------------------------------
# 8) Migração schema_version 2 -> 3: retroaplica CHECKs em tabelas existentes
# ---------------------------------------------------------------------------
#
# Os CHECK de processos.interno/externo, regras_urgencia.dias_minimos/
# dias_maximos e niveis_urgencia.prioridade foram adicionados em _V2_TABELAS
# depois que a migração v1->v2 já havia criado essas tabelas em produção.
# CREATE TABLE IF NOT EXISTS não altera uma tabela já existente, então essa
# migração reconstrói só essas 3 tabelas (nome_v3_novo -> copia linhas
# preservando id/timestamps/todos os campos -> confere contagem -> DROP da
# antiga -> RENAME), na ordem que respeita o grafo de chaves estrangeiras:
#
#   regras_urgencia (tabela-folha, nada a referencia) primeiro;
#   depois niveis_urgencia (referenciada por regras_urgencia.nivel_urgencia_id,
#   RESTRICT + NOT NULL — só seguro se a regras_urgencia recém-reconstruída
#   estiver vazia);
#   depois processos (referenciada por processo_fornecedores, rota_etapas e
#   regras_urgencia.processo_id — só seguro se essas três não tiverem
#   nenhuma linha apontando pra processos).
#
# PRAGMA foreign_keys=OFF não é usado aqui: testamos que a pragma não tem
# efeito no meio de uma transação já aberta (get_schema_version() já abre
# uma via INSERT OR IGNORE antes de qualquer migração rodar), então a
# estratégia é checar dinamicamente as tabelas dependentes antes de cada
# DROP e abortar com erro claro (RuntimeError -> rollback total via
# run_migrations()) se encontrar algo inesperado, em vez de arriscar.

_PROCESSOS_V3_SQL = """
    CREATE TABLE processos_v3_novo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        grupo_processo TEXT,
        interno INTEGER NOT NULL DEFAULT 1,
        externo INTEGER NOT NULL DEFAULT 0,
        exige_previsao_retorno INTEGER NOT NULL DEFAULT 0,
        ordem_padrao INTEGER,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL,
        CHECK (interno IN (0, 1) AND externo IN (0, 1) AND (interno = 1 OR externo = 1))
    )
"""
_PROCESSOS_COLUNAS = (
    "id", "nome", "descricao", "grupo_processo", "interno", "externo",
    "exige_previsao_retorno", "ordem_padrao", "ativo", "criado_em", "atualizado_em",
)

_NIVEIS_URGENCIA_V3_SQL = """
    CREATE TABLE niveis_urgencia_v3_novo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nome TEXT NOT NULL,
        prioridade INTEGER NOT NULL,
        cor_fundo TEXT,
        cor_texto TEXT,
        cor_borda TEXT,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL,
        CHECK (prioridade > 0)
    )
"""
_NIVEIS_URGENCIA_COLUNAS = (
    "id", "codigo", "nome", "prioridade", "cor_fundo", "cor_texto", "cor_borda",
    "ativo", "criado_em", "atualizado_em",
)

_REGRAS_URGENCIA_V3_SQL = """
    CREATE TABLE regras_urgencia_v3_novo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        processo_id INTEGER REFERENCES processos(id) ON DELETE SET NULL,
        dias_minimos INTEGER,
        dias_maximos INTEGER,
        nivel_urgencia_id INTEGER NOT NULL REFERENCES niveis_urgencia(id) ON DELETE RESTRICT,
        prioridade INTEGER NOT NULL DEFAULT 0,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL,
        CHECK (dias_minimos IS NULL OR dias_maximos IS NULL OR dias_minimos <= dias_maximos)
    )
"""
_REGRAS_URGENCIA_COLUNAS = (
    "id", "nome", "processo_id", "dias_minimos", "dias_maximos", "nivel_urgencia_id",
    "prioridade", "ativo", "criado_em", "atualizado_em",
)

_V3_INDICES_RECRIAR: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_processos_nome ON processos(nome)",
    "CREATE INDEX IF NOT EXISTS idx_regras_urgencia_processo ON regras_urgencia(processo_id)",
    "CREATE INDEX IF NOT EXISTS idx_regras_urgencia_nivel ON regras_urgencia(nivel_urgencia_id)",
)


def _substituir_tabela_reconstruida(
    c: sqlite3.Connection,
    tabela: str,
    tabela_temp: str,
    create_sql_temp: str,
    colunas: tuple[str, ...],
) -> None:
    """Reconstrói `tabela` com o schema de `create_sql_temp`, preservando dados.

    Cria `tabela_temp`, copia todas as linhas de `tabela` para `tabela_temp`
    listando explicitamente `colunas` (preserva id, timestamps e todo o
    resto exatamente como estavam — nada é gerado de novo), confere que a
    contagem bateu, e só então derruba `tabela` e renomeia `tabela_temp`
    para `tabela`. Levanta RuntimeError (sem alterar nada de fato visível
    fora da transação, já que run_migrations() faz rollback) se a contagem
    não bater.
    """
    c.execute(create_sql_temp)
    lista_colunas = ", ".join(colunas)
    c.execute(f"INSERT INTO {tabela_temp} ({lista_colunas}) SELECT {lista_colunas} FROM {tabela}")

    total_antigo = c.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
    total_novo = c.execute(f"SELECT COUNT(*) FROM {tabela_temp}").fetchone()[0]
    if total_novo != total_antigo:
        raise RuntimeError(
            f"Reconstrução de '{tabela}' abortada: contagem não bateu "
            f"({total_antigo} -> {total_novo})."
        )

    c.execute(f"DROP TABLE {tabela}")
    c.execute(f"ALTER TABLE {tabela_temp} RENAME TO {tabela}")


def migrar_v2_para_v3(c: sqlite3.Connection) -> None:
    """Migração de schema_version 2 -> 3: retroaplica CHECKs faltantes.

    Reconstrói processos, regras_urgencia e niveis_urgencia com os CHECK
    que a migração v1->v2 já deveria ter (mas CREATE TABLE IF NOT EXISTS
    não retroagiu em bancos onde essas tabelas já existiam). Preserva todo
    dado existente (IDs, timestamps, todos os campos) e não migra nenhum
    dado real novo. Idempotente: rodar de novo com os CHECK já presentes
    simplesmente reconstrói as mesmas tabelas com os mesmos dados (sem
    duplicar nada, já que DROP+RENAME substitui, não soma).
    """
    # 1) regras_urgencia primeiro: tabela-folha, nada a referencia, sempre seguro.
    _substituir_tabela_reconstruida(
        c, "regras_urgencia", "regras_urgencia_v3_novo", _REGRAS_URGENCIA_V3_SQL, _REGRAS_URGENCIA_COLUNAS
    )

    # 2) niveis_urgencia: só seguro se a regras_urgencia (recém-reconstruída,
    #    mesmos dados de antes) não tiver nenhuma linha — já que
    #    nivel_urgencia_id é NOT NULL + RESTRICT, qualquer linha ali
    #    impediria o DROP da niveis_urgencia antiga.
    total_regras = c.execute("SELECT COUNT(*) FROM regras_urgencia").fetchone()[0]
    if total_regras != 0:
        raise RuntimeError(
            "Migração v2->v3 abortada: reconstrução automática de niveis_urgencia "
            f"não é segura com regras_urgencia não-vazia ({total_regras} registro(s) "
            "referenciam niveis_urgencia via NOT NULL/RESTRICT). Precisa de uma "
            "migração dedicada para esse caso."
        )
    _substituir_tabela_reconstruida(
        c, "niveis_urgencia", "niveis_urgencia_v3_novo", _NIVEIS_URGENCIA_V3_SQL, _NIVEIS_URGENCIA_COLUNAS
    )

    # 3) processos: só seguro se nada nas tabelas que o referenciam tiver
    #    linhas apontando pra ele.
    total_rota_etapas = c.execute("SELECT COUNT(*) FROM rota_etapas").fetchone()[0]
    total_processo_fornecedores = c.execute("SELECT COUNT(*) FROM processo_fornecedores").fetchone()[0]
    total_regras_com_processo = c.execute(
        "SELECT COUNT(*) FROM regras_urgencia WHERE processo_id IS NOT NULL"
    ).fetchone()[0]
    if total_rota_etapas or total_processo_fornecedores or total_regras_com_processo:
        raise RuntimeError(
            "Migração v2->v3 abortada: reconstrução automática de processos não é "
            f"segura (rota_etapas={total_rota_etapas}, "
            f"processo_fornecedores={total_processo_fornecedores}, "
            f"regras_urgencia.processo_id preenchido={total_regras_com_processo}). "
            "Precisa de uma migração dedicada para esse caso."
        )
    _substituir_tabela_reconstruida(
        c, "processos", "processos_v3_novo", _PROCESSOS_V3_SQL, _PROCESSOS_COLUNAS
    )

    # Os índices das 3 tabelas foram derrubados junto com elas; recria.
    for statement in _V3_INDICES_RECRIAR:
        c.execute(statement)

    violacoes = c.execute("PRAGMA foreign_key_check").fetchall()
    if violacoes:
        raise RuntimeError(f"Migração v2->v3 abortada: foreign_key_check encontrou violações: {violacoes}")


MIGRATIONS[2] = migrar_v2_para_v3

assert LATEST_SCHEMA_VERSION == max(MIGRATIONS) + 1, (
    "LATEST_SCHEMA_VERSION desalinhada com MIGRATIONS: atualize a constante "
    "ao registrar uma nova migração."
)
