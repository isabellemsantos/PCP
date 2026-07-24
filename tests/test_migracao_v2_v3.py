"""Testes da migração de schema_version 2 -> 3 (retroaplica CHECKs faltantes
em processos, regras_urgencia e niveis_urgencia).

Importante: nenhum teste aqui toca no pcp.sqlite3 real. Cada teste trabalha
sobre uma cópia isolada, feita com sqlite3.Connection.backup(), de uma das
duas bases sintéticas montadas em setUpClass:

- `db_v1_base`: schema v1 puro (servidor_pcp.init_db()).
- `db_v2_base`: schema v2 reconstruído para bater exatamente com a produção
  real de hoje — ou seja, com processos/regras_urgencia/niveis_urgencia
  SEM os CHECK (que só existem em db_manutencao._V2_TABELAS desde depois
  que a migração v1->v2 já tinha rodado no banco real). Isso é montado
  chamando migrar_v1_para_v2() (que já cria essas 3 tabelas com CHECK, na
  versão atual do código) e em seguida substituindo essas 3 tabelas por
  versões "legadas" sem CHECK, preservando os 5 níveis de urgência
  seedados. É essa base que exercita de verdade o objetivo da migração
  v2->v3: adicionar CHECK a tabelas que já existem sem eles.

Rodar com:  py -m unittest tests.test_migracao_v2_v3 -v
(a partir de C:\\Sites\\PCP)
"""

from __future__ import annotations

import importlib
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _copiar_via_backup(origem: Path, destino: Path) -> None:
    origem_conn = sqlite3.connect(str(origem))
    destino_conn = sqlite3.connect(str(destino))
    try:
        with destino_conn:
            origem_conn.backup(destino_conn)
    finally:
        destino_conn.close()
        origem_conn.close()


# Definições "legadas" (sem CHECK) das 3 tabelas, exatamente como existiam em
# produção antes de qualquer CHECK ter sido adicionado ao código-fonte —
# usadas só para montar a base de teste db_v2_base, nunca no código real.
_PROCESSOS_LEGADO_SQL = """
    CREATE TABLE processos (
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
        atualizado_em TEXT NOT NULL
    )
"""
_REGRAS_URGENCIA_LEGADO_SQL = """
    CREATE TABLE regras_urgencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        processo_id INTEGER REFERENCES processos(id) ON DELETE SET NULL,
        dias_minimos INTEGER,
        dias_maximos INTEGER,
        nivel_urgencia_id INTEGER NOT NULL REFERENCES niveis_urgencia(id) ON DELETE RESTRICT,
        prioridade INTEGER NOT NULL DEFAULT 0,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL
    )
"""
_NIVEIS_URGENCIA_LEGADO_SQL = """
    CREATE TABLE niveis_urgencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nome TEXT NOT NULL,
        prioridade INTEGER NOT NULL,
        cor_fundo TEXT,
        cor_texto TEXT,
        cor_borda TEXT,
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL,
        atualizado_em TEXT NOT NULL
    )
"""


def _rebaixar_para_schema_legado_sem_check(conexao: sqlite3.Connection) -> None:
    """Substitui as 3 tabelas (já criadas com CHECK por migrar_v1_para_v2)
    por versões sem CHECK, preservando os dados (os 5 níveis seedados),
    para simular fielmente o estado do pcp.sqlite3 real antes da v2->v3."""
    niveis = conexao.execute(
        "SELECT id, codigo, nome, prioridade, cor_fundo, cor_texto, cor_borda, ativo, criado_em, atualizado_em "
        "FROM niveis_urgencia"
    ).fetchall()

    conexao.execute("DROP TABLE regras_urgencia")
    conexao.execute("DROP TABLE processos")
    conexao.execute("DROP TABLE niveis_urgencia")

    conexao.execute(_NIVEIS_URGENCIA_LEGADO_SQL)
    conexao.executemany(
        "INSERT INTO niveis_urgencia (id, codigo, nome, prioridade, cor_fundo, cor_texto, cor_borda, ativo, criado_em, atualizado_em) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        niveis,
    )
    conexao.execute(_PROCESSOS_LEGADO_SQL)
    conexao.execute(_REGRAS_URGENCIA_LEGADO_SQL)
    conexao.execute("CREATE INDEX IF NOT EXISTS idx_processos_nome ON processos(nome)")
    conexao.execute("CREATE INDEX IF NOT EXISTS idx_regras_urgencia_processo ON regras_urgencia(processo_id)")
    conexao.execute("CREATE INDEX IF NOT EXISTS idx_regras_urgencia_nivel ON regras_urgencia(nivel_urgencia_id)")


class MigracaoV2V3TestCase(unittest.TestCase):
    tmp_dir: Path
    db_v1_base: Path
    db_v2_base: Path
    servidor = None
    dbm = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_migracao_v2v3_"))
        cls.db_v1_base = cls.tmp_dir / "base_v1.sqlite3"
        cls.db_v2_base = cls.tmp_dir / "base_v2_sem_check.sqlite3"

        os.environ["PCP_DB_FILE"] = str(cls.db_v1_base)
        os.environ["PCP_EXCEL_FILE"] = str(cls.tmp_dir / "dados_pcp_teste.xlsx")
        os.environ["PCP_EXCEL_PENDING_FILE"] = str(cls.tmp_dir / "dados_pcp_pendente_teste.xlsx")
        os.environ["PCP_LOG_FILE"] = str(cls.tmp_dir / "servidor_pcp_teste.log")
        os.environ["PCP_BACKUP_DIR"] = str(cls.tmp_dir / "backups")

        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)

        cls.servidor = importlib.import_module("servidor_pcp")
        cls.dbm = importlib.import_module("db_manutencao")

        assert cls.servidor.DB_FILE == cls.db_v1_base
        cls.servidor.init_db()  # schema v1

        with sqlite3.connect(str(cls.db_v1_base)) as c:
            assert cls.dbm.get_schema_version(c) == 1

        # Monta db_v2_base: v1 -> migrar_v1_para_v2() -> rebaixa as 3 tabelas
        # pra versão sem CHECK (reproduz fielmente a produção real de hoje).
        _copiar_via_backup(cls.db_v1_base, cls.db_v2_base)
        with sqlite3.connect(str(cls.db_v2_base)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            cls.dbm.migrar_v1_para_v2(c)
            _rebaixar_para_schema_legado_sem_check(c)
            cls.dbm.set_schema_version(c, 2)
            c.commit()

        with sqlite3.connect(str(cls.db_v2_base)) as c:
            assert cls.dbm.get_schema_version(c) == 2
            cols = {r[1] for r in c.execute("PRAGMA table_info(processos)").fetchall()}
            assert "interno" in cols

    @classmethod
    def tearDownClass(cls):
        for var in ("PCP_DB_FILE", "PCP_EXCEL_FILE", "PCP_EXCEL_PENDING_FILE", "PCP_LOG_FILE", "PCP_BACKUP_DIR"):
            os.environ.pop(var, None)
        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def _copia_v1(self, nome: str) -> Path:
        destino = self.tmp_dir / f"{nome}.sqlite3"
        _copiar_via_backup(self.db_v1_base, destino)
        return destino

    def _copia_v2(self, nome: str) -> Path:
        destino = self.tmp_dir / f"{nome}.sqlite3"
        _copiar_via_backup(self.db_v2_base, destino)
        return destino

    def _migrar(self, db_path: Path, backup_dir: Path | None = None) -> dict:
        backup_dir = backup_dir or (self.tmp_dir / f"backups_{db_path.stem}")
        conexao = sqlite3.connect(str(db_path))
        conexao.execute("PRAGMA foreign_keys=ON")
        try:
            resultado = self.dbm.run_migrations(conexao, db_path, backup_dir, log=lambda _msg: None)
        finally:
            conexao.close()
        return resultado


# ---------------------------------------------------------------------------
# 1) Transições de versão
# ---------------------------------------------------------------------------

class TransicaoVersaoTest(MigracaoV2V3TestCase):

    def test_migracao_registrada_em_migrations_2(self):
        self.assertIn(2, self.dbm.MIGRATIONS)
        self.assertIs(self.dbm.MIGRATIONS[2], self.dbm.migrar_v2_para_v3)

    def test_latest_schema_version_e_pelo_menos_3(self):
        # Não fixamos um valor exato: outras migrações (v3->v4 etc.) podem
        # ter sido registradas depois que este arquivo foi escrito. O que
        # importa aqui é que, com migrar_v2_para_v3 registrada, a versão
        # mais recente nunca pode ser menor que 3.
        self.assertGreaterEqual(self.dbm.LATEST_SCHEMA_VERSION, 3)

    def test_migracoes_pendentes_de_2_inclui_3(self):
        # Idem: não fixamos a cauda completa (pode incluir 4, 5... depois),
        # só que migrar de 2 sempre passa por 3 primeiro.
        self.assertEqual(self.dbm.migracoes_pendentes(2)[0], 3)

    def test_banco_v2_termina_em_v3(self):
        # Chama migrar_v2_para_v3() diretamente (não via run_migrations):
        # como outras migrações podem existir depois desta (v3->v4 etc.),
        # run_migrations() encadearia além da v3, o que não é o que este
        # teste específico verifica (isso é coberto em
        # tests.test_migracao_v3_v4 e em qualquer migração futura).
        db = self._copia_v2("v2_para_v3")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            self.dbm.migrar_v2_para_v3(c)
            self.dbm.set_schema_version(c, 3)
            c.commit()
        with sqlite3.connect(str(db)) as c:
            self.assertEqual(self.dbm.get_schema_version(c), 3)

    def test_banco_v3_executado_novamente_e_no_op(self):
        db = self._copia_v2("v3_no_op")
        primeiro = self._migrar(db, self.tmp_dir / "backups_noop1")
        segundo = self._migrar(db, self.tmp_dir / "backups_noop2")
        self.assertEqual(primeiro["versao_final"], self.dbm.LATEST_SCHEMA_VERSION)
        self.assertEqual(segundo["migracoes_aplicadas"], [])
        self.assertEqual(segundo["versao_final"], self.dbm.LATEST_SCHEMA_VERSION)

    def test_banco_v1_executa_1_2_3_corretamente(self):
        db = self._copia_v1("v1_para_v3")
        resultado = self._migrar(db)
        self.assertEqual(resultado["versao_final"], self.dbm.LATEST_SCHEMA_VERSION)
        self.assertIn(3, resultado["migracoes_aplicadas"])
        with sqlite3.connect(str(db)) as c:
            self.assertEqual(self.dbm.get_schema_version(c), self.dbm.LATEST_SCHEMA_VERSION)
            tabelas = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        for antiga in ("meta", "orders", "sections", "manual_cpd", "audit_log"):
            self.assertIn(antiga, tabelas, f"Tabela antiga {antiga} deveria continuar existindo")


# ---------------------------------------------------------------------------
# 2) Backup obrigatório, falha simulada, rollback sem tabelas órfãs
# ---------------------------------------------------------------------------

class BackupEFalhaTest(MigracaoV2V3TestCase):

    def test_backup_pre_migracao_v2_para_v3_e_criado_e_valido(self):
        db = self._copia_v2("backup_v2v3")
        backup_dir = self.tmp_dir / "backups_validacao_v2v3"
        self._migrar(db, backup_dir)
        arquivos = list(backup_dir.glob("pcp_pre_migracao_v2_para_v3_*.sqlite3"))
        self.assertEqual(len(arquivos), 1)
        self.assertEqual(self.dbm.verificar_integridade(arquivos[0]), "ok")

    def test_falha_simulada_mantem_versao_2(self):
        db = self._copia_v2("falha_v2v3")
        original = self.dbm.MIGRATIONS[2]

        def migracao_quebrada(c):
            c.execute("CREATE TABLE processos_v3_novo (id INTEGER PRIMARY KEY)")
            raise RuntimeError("falha simulada proposital")

        self.dbm.MIGRATIONS[2] = migracao_quebrada
        try:
            resultado = self._migrar(db, self.tmp_dir / "backups_falha_v2v3")
        finally:
            self.dbm.MIGRATIONS[2] = original

        self.assertEqual(resultado["versao_final"], 2)
        self.assertEqual(resultado["migracoes_aplicadas"], [])
        with sqlite3.connect(str(db)) as c:
            self.assertEqual(self.dbm.get_schema_version(c), 2)

    def test_rollback_nao_deixa_tabelas_temporarias_orfas(self):
        db = self._copia_v2("rollback_sem_orfas")
        original = self.dbm.MIGRATIONS[2]

        def migracao_quebrada(c):
            c.execute("CREATE TABLE regras_urgencia_v3_novo (id INTEGER PRIMARY KEY)")
            c.execute("CREATE TABLE niveis_urgencia_v3_novo (id INTEGER PRIMARY KEY)")
            c.execute("CREATE TABLE processos_v3_novo (id INTEGER PRIMARY KEY)")
            raise RuntimeError("falha simulada proposital")

        self.dbm.MIGRATIONS[2] = migracao_quebrada
        try:
            self._migrar(db, self.tmp_dir / "backups_rollback_orfas")
        finally:
            self.dbm.MIGRATIONS[2] = original

        with sqlite3.connect(str(db)) as c:
            orfas = c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_v3_novo'"
            ).fetchall()
        self.assertEqual(orfas, [], f"Tabelas temporárias órfãs após rollback: {orfas}")

    def test_guard_dinamico_aborta_se_processos_referenciado(self):
        """Se rota_etapas já tiver uma linha apontando pra processos, a
        reconstrução automática de processos não é segura -- a migração deve
        abortar (RuntimeError -> rollback), não arriscar um DROP que falharia
        de qualquer forma por causa do RESTRICT."""
        db = self._copia_v2("guard_processos")
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            c.execute("INSERT INTO processos(nome, interno, externo, criado_em, atualizado_em) VALUES ('P',1,0,?,?)", (agora, agora))
            c.execute("INSERT INTO rotas_processo(nome, ativo, criado_em, atualizado_em) VALUES ('R',1,?,?)", (agora, agora))
            c.execute(
                "INSERT INTO rota_etapas(rota_id, processo_id, ordem, criado_em) VALUES (1,1,1,?)", (agora,)
            )
            c.commit()

        resultado = self._migrar(db, self.tmp_dir / "backups_guard_processos")
        self.assertEqual(resultado["versao_final"], 2, "Guard deveria ter abortado a migração, mantendo v2")
        self.assertEqual(resultado["migracoes_aplicadas"], [])
        with sqlite3.connect(str(db)) as c:
            orfas = c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_v3_novo'"
            ).fetchall()
        self.assertEqual(orfas, [])


# ---------------------------------------------------------------------------
# 3) Preservação de dados: IDs, contagens, índices, FKs, integridade
# ---------------------------------------------------------------------------

class PreservacaoDeDadosTest(MigracaoV2V3TestCase):

    def setUp(self):
        self.db = self._copia_v2(f"preservacao_{self._testMethodName}")

    def test_confirma_dinamicamente_que_processos_e_regras_estao_vazias_antes(self):
        with sqlite3.connect(str(self.db)) as c:
            self.assertEqual(c.execute("SELECT COUNT(*) FROM processos").fetchone()[0], 0)
            self.assertEqual(c.execute("SELECT COUNT(*) FROM regras_urgencia").fetchone()[0], 0)
            self.assertEqual(c.execute("SELECT COUNT(*) FROM niveis_urgencia").fetchone()[0], 5)

    def test_ids_dos_cinco_niveis_sao_preservados(self):
        with sqlite3.connect(str(self.db)) as c:
            antes = {r[0]: r[1] for r in c.execute("SELECT id, codigo FROM niveis_urgencia ORDER BY id").fetchall()}
        self._migrar(self.db)
        with sqlite3.connect(str(self.db)) as c:
            depois = {r[0]: r[1] for r in c.execute("SELECT id, codigo FROM niveis_urgencia ORDER BY id").fetchall()}
        self.assertEqual(antes, depois)
        self.assertEqual(set(antes.values()), {"ATRASADO", "CRITICO", "ALTO", "ATENCAO", "NORMAL"})

    def test_processo_e_regra_validos_pre_existentes_preservam_id_e_timestamps(self):
        agora = "2026-01-01 10:00:00"
        with sqlite3.connect(str(self.db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            c.execute(
                "INSERT INTO processos(nome, interno, externo, criado_em, atualizado_em) VALUES ('Solda',1,0,?,?)",
                (agora, agora),
            )
            processo_id = c.execute("SELECT id FROM processos WHERE nome='Solda'").fetchone()[0]
            nivel_id = c.execute("SELECT id FROM niveis_urgencia WHERE codigo='NORMAL'").fetchone()[0]
            c.execute(
                "INSERT INTO regras_urgencia(nome, processo_id, dias_minimos, dias_maximos, nivel_urgencia_id, criado_em, atualizado_em) "
                "VALUES ('Regra1', ?, 1, 5, ?, ?, ?)",
                (processo_id, nivel_id, agora, agora),
            )
            regra_id = c.execute("SELECT id FROM regras_urgencia WHERE nome='Regra1'").fetchone()[0]
            c.commit()

        self._migrar(self.db)

        with sqlite3.connect(str(self.db)) as c:
            c.row_factory = sqlite3.Row
            processo = c.execute("SELECT * FROM processos WHERE id=?", (processo_id,)).fetchone()
            regra = c.execute("SELECT * FROM regras_urgencia WHERE id=?", (regra_id,)).fetchone()
        self.assertIsNotNone(processo)
        self.assertEqual(processo["nome"], "Solda")
        self.assertEqual(processo["criado_em"], agora)
        self.assertEqual(processo["atualizado_em"], agora)
        self.assertIsNotNone(regra)
        self.assertEqual(regra["processo_id"], processo_id)
        self.assertEqual(regra["nivel_urgencia_id"], nivel_id)
        self.assertEqual(regra["criado_em"], agora)

    def test_contagens_de_todas_as_tabelas_sao_preservadas(self):
        with sqlite3.connect(str(self.db)) as c:
            antes = {
                t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("processos", "regras_urgencia", "niveis_urgencia", "grupos_clientes", "orders", "audit_log")
            }
        self._migrar(self.db)
        with sqlite3.connect(str(self.db)) as c:
            depois = {
                t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("processos", "regras_urgencia", "niveis_urgencia", "grupos_clientes", "orders", "audit_log")
            }
        self.assertEqual(antes, depois)

    def test_indices_sao_preservados(self):
        self._migrar(self.db)
        with sqlite3.connect(str(self.db)) as c:
            indices = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
        for esperado in ("idx_processos_nome", "idx_regras_urgencia_processo", "idx_regras_urgencia_nivel"):
            self.assertIn(esperado, indices)

    def test_chaves_estrangeiras_sao_preservadas(self):
        self._migrar(self.db)
        with sqlite3.connect(str(self.db)) as c:
            c.row_factory = sqlite3.Row
            fks_regras = {r["table"]: r["on_delete"] for r in c.execute("PRAGMA foreign_key_list(regras_urgencia)").fetchall()}
            fks_rota = {r["table"]: r["on_delete"] for r in c.execute("PRAGMA foreign_key_list(rota_etapas)").fetchall()}
        self.assertEqual(fks_regras, {"processos": "SET NULL", "niveis_urgencia": "RESTRICT"})
        self.assertEqual(fks_rota, {"rotas_processo": "RESTRICT", "processos": "RESTRICT", "fornecedores": "SET NULL"})

    def test_integrity_check_ok_apos_migracao(self):
        self._migrar(self.db)
        self.assertEqual(self.dbm.verificar_integridade(self.db), "ok")

    def test_foreign_key_check_sem_violacoes_apos_migracao(self):
        self._migrar(self.db)
        with sqlite3.connect(str(self.db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            violacoes = c.execute("PRAGMA foreign_key_check").fetchall()
        self.assertEqual(violacoes, [])


# ---------------------------------------------------------------------------
# 4) CHECK constraints passam a valer depois da migração
# ---------------------------------------------------------------------------

class ChecksAposMigracaoTest(MigracaoV2V3TestCase):

    def setUp(self):
        self.db = self._copia_v2(f"checks_{self._testMethodName}")
        self._migrar(self.db)
        self.conn = sqlite3.connect(str(self.db))
        self.conn.execute("PRAGMA foreign_keys=ON")

    def tearDown(self):
        self.conn.close()

    def _inserir_processo(self, nome, interno, externo):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "INSERT INTO processos(nome, interno, externo, criado_em, atualizado_em) VALUES (?,?,?,?,?)",
            (nome, interno, externo, agora, agora),
        )

    def test_processo_interno_0_externo_0_e_rejeitado(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._inserir_processo("Nulo", 0, 0)

    def test_processo_interno_2_e_rejeitado(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._inserir_processo("InternoInvalido", 2, 0)

    def test_processo_externo_negativo_e_rejeitado(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._inserir_processo("ExternoInvalido", 1, -1)

    def test_processo_interno_1_externo_0_e_aceito(self):
        self._inserir_processo("SoInterno", 1, 0)
        self.conn.commit()

    def test_processo_interno_0_externo_1_e_aceito(self):
        self._inserir_processo("SoExterno", 0, 1)
        self.conn.commit()

    def test_processo_interno_1_externo_1_e_aceito(self):
        self._inserir_processo("Ambos", 1, 1)
        self.conn.commit()

    def _inserir_regra(self, nome, dias_minimos, dias_maximos):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nivel_id = self.conn.execute("SELECT id FROM niveis_urgencia WHERE codigo='NORMAL'").fetchone()[0]
        self.conn.execute(
            "INSERT INTO regras_urgencia(nome, dias_minimos, dias_maximos, nivel_urgencia_id, criado_em, atualizado_em) "
            "VALUES (?,?,?,?,?,?)",
            (nome, dias_minimos, dias_maximos, nivel_id, agora, agora),
        )

    def test_regra_dias_minimos_10_maximos_5_e_rejeitada(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._inserir_regra("Invalida", 10, 5)

    def test_regra_dias_nulos_e_aceita(self):
        self._inserir_regra("SemLimite", None, None)
        self.conn.commit()

    def test_regra_dias_minimos_5_maximos_10_e_aceita(self):
        self._inserir_regra("Valida", 5, 10)
        self.conn.commit()

    def _inserir_nivel(self, codigo, prioridade):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "INSERT INTO niveis_urgencia(codigo, nome, prioridade, ativo, criado_em, atualizado_em) VALUES (?,?,?,1,?,?)",
            (codigo, codigo, prioridade, agora, agora),
        )

    def test_nivel_prioridade_0_e_rejeitado(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._inserir_nivel("TESTE_ZERO", 0)

    def test_nivel_prioridade_negativa_e_rejeitada(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._inserir_nivel("TESTE_NEGATIVO", -1)

    def test_nivel_prioridade_positiva_e_aceita(self):
        self._inserir_nivel("TESTE_POSITIVO", 99)
        self.conn.commit()


# ---------------------------------------------------------------------------
# 5) Gatilho de migração automática
# ---------------------------------------------------------------------------

class GatilhoTest(MigracaoV2V3TestCase):

    def test_sem_variavel_nao_aplica(self):
        os.environ.pop("PCP_APLICAR_MIGRACOES", None)
        self.assertFalse(self.servidor.deve_aplicar_migracoes_automaticamente())

    def test_com_variavel_0_nao_aplica(self):
        os.environ["PCP_APLICAR_MIGRACOES"] = "0"
        try:
            self.assertFalse(self.servidor.deve_aplicar_migracoes_automaticamente())
        finally:
            os.environ.pop("PCP_APLICAR_MIGRACOES", None)

    def test_com_variavel_1_aplica(self):
        os.environ["PCP_APLICAR_MIGRACOES"] = "1"
        try:
            self.assertTrue(self.servidor.deve_aplicar_migracoes_automaticamente())
        finally:
            os.environ.pop("PCP_APLICAR_MIGRACOES", None)

    def test_iniciar_servidor_normalmente_detecta_pendencia_e_nao_altera_banco(self):
        # Aponta o servidor pra uma cópia em v2 (migração v2->v3 pendente) e
        # confirma que só detectar-e-avisar não muda o schema_version.
        db = self._copia_v2("gatilho_v2_pendente")
        os.environ["PCP_DB_FILE"] = str(db)
        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        servidor_isolado = importlib.import_module("servidor_pcp")
        dbm_isolado = importlib.import_module("db_manutencao")
        try:
            os.environ.pop("PCP_APLICAR_MIGRACOES", None)
            self.assertFalse(servidor_isolado.deve_aplicar_migracoes_automaticamente())
            resultado = servidor_isolado.verificar_e_avisar_migracao_pendente()
            self.assertTrue(resultado["pendente"])
            self.assertEqual(resultado["versao_atual"], 2)
            with sqlite3.connect(str(db)) as c:
                self.assertEqual(dbm_isolado.get_schema_version(c), 2, "Banco não pode ser alterado só por avisar")
        finally:
            os.environ["PCP_DB_FILE"] = str(self.db_v1_base)

    def test_banco_ja_em_v3_nao_tem_pendencia(self):
        db = self._copia_v2("gatilho_v3_sem_pendencia")
        self._migrar(db)
        with sqlite3.connect(str(db)) as c:
            versao = self.dbm.get_schema_version(c)
        self.assertEqual(self.dbm.migracoes_pendentes(versao), [])


if __name__ == "__main__":
    unittest.main()
