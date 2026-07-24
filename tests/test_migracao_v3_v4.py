"""Testes da migração de schema_version 3 -> 4 (rastreabilidade de
descrições e pendências de revisão: cpd_descricoes_fontes e
cpd_pendencias_revisao).

Nenhum teste aqui toca no pcp.sqlite3 real. Cada teste trabalha sobre uma
cópia isolada, feita com sqlite3.Connection.backup(), de uma base sintética
já em schema_version 3 (via servidor_pcp.init_db() + migrar_v1_para_v2 +
migrar_v2_para_v3).

Rodar com:  py -m unittest tests.test_migracao_v3_v4 -v
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


class MigracaoV3V4TestCase(unittest.TestCase):
    tmp_dir: Path
    db_v3_base: Path
    servidor = None
    dbm = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_migracao_v3v4_"))
        cls.db_v3_base = cls.tmp_dir / "base_v3.sqlite3"

        os.environ["PCP_DB_FILE"] = str(cls.db_v3_base)
        os.environ["PCP_EXCEL_FILE"] = str(cls.tmp_dir / "dados_pcp_teste.xlsx")
        os.environ["PCP_EXCEL_PENDING_FILE"] = str(cls.tmp_dir / "dados_pcp_pendente_teste.xlsx")
        os.environ["PCP_LOG_FILE"] = str(cls.tmp_dir / "servidor_pcp_teste.log")
        os.environ["PCP_BACKUP_DIR"] = str(cls.tmp_dir / "backups")

        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        cls.servidor = importlib.import_module("servidor_pcp")
        cls.dbm = importlib.import_module("db_manutencao")
        cls.servidor.init_db()

        with sqlite3.connect(str(cls.db_v3_base)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            cls.dbm.migrar_v1_para_v2(c)
            cls.dbm.migrar_v2_para_v3(c)
            cls.dbm.set_schema_version(c, 3)
            c.commit()

    @classmethod
    def tearDownClass(cls):
        for var in ("PCP_DB_FILE", "PCP_EXCEL_FILE", "PCP_EXCEL_PENDING_FILE", "PCP_LOG_FILE", "PCP_BACKUP_DIR"):
            os.environ.pop(var, None)
        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def _copia(self, nome: str) -> Path:
        destino = self.tmp_dir / f"{nome}.sqlite3"
        _copiar_via_backup(self.db_v3_base, destino)
        return destino

    def _migrar(self, db_path: Path, backup_dir: Path | None = None) -> dict:
        # Este arquivo testa isoladamente o degrau v3->v4. Como v4->v5
        # (arruelas) também está registrada em MIGRATIONS agora, escondemos
        # temporariamente qualquer migração >= 4 pra run_migrations() parar
        # exatamente em v4, preservando o comportamento original destes
        # testes (ver tests/test_migracao_v4_v5.py pro degrau seguinte).
        backup_dir = backup_dir or (self.tmp_dir / f"backups_{db_path.stem}")
        conexao = sqlite3.connect(str(db_path))
        conexao.execute("PRAGMA foreign_keys=ON")
        migracoes_futuras = {v: f for v, f in self.dbm.MIGRATIONS.items() if v >= 4}
        for v in migracoes_futuras:
            del self.dbm.MIGRATIONS[v]
        try:
            resultado = self.dbm.run_migrations(conexao, db_path, backup_dir, log=lambda _msg: None)
        finally:
            conexao.close()
            self.dbm.MIGRATIONS.update(migracoes_futuras)
        return resultado

    def _cpd_ficticio(self, conn, codigo_pai="9990"):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO cpds(codigo_pai, ativo, criado_em, atualizado_em) VALUES (?,1,?,?)",
            (codigo_pai, agora, agora),
        )
        return conn.execute("SELECT id FROM cpds WHERE codigo_pai=?", (codigo_pai,)).fetchone()[0]

    # ------------------------------------------------------------------
    # Transição de versão e idempotência
    # ------------------------------------------------------------------

    def test_migracao_registrada_em_migrations_3(self):
        self.assertIn(3, self.dbm.MIGRATIONS)
        self.assertIs(self.dbm.MIGRATIONS[3], self.dbm.migrar_v3_para_v4)

    def test_latest_schema_version_e_pelo_menos_4(self):
        # Não é mais necessariamente a última (v4->v5 de arruelas pode ter
        # sido registrada depois) -- só garante que o degrau testado aqui existe.
        self.assertGreaterEqual(self.dbm.LATEST_SCHEMA_VERSION, 4)

    def test_migracoes_pendentes_de_3_inclui_4(self):
        self.assertIn(4, self.dbm.migracoes_pendentes(3))

    def test_banco_v3_termina_em_v4(self):
        db = self._copia("v3_para_v4")
        resultado = self._migrar(db)
        self.assertEqual(resultado["versao_final"], 4)
        self.assertEqual(resultado["migracoes_aplicadas"], [4])

    def test_segunda_execucao_e_no_op(self):
        db = self._copia("idempotencia")
        primeiro = self._migrar(db, self.tmp_dir / "backups_idem1")
        segundo = self._migrar(db, self.tmp_dir / "backups_idem2")
        self.assertEqual(primeiro["migracoes_aplicadas"], [4])
        self.assertEqual(segundo["migracoes_aplicadas"], [])
        self.assertEqual(segundo["versao_final"], 4)

    def test_backup_pre_migracao_e_criado_e_valido(self):
        db = self._copia("backup_v3v4")
        backup_dir = self.tmp_dir / "backups_validacao_v3v4"
        self._migrar(db, backup_dir)
        arquivos = list(backup_dir.glob("pcp_pre_migracao_v3_para_v4_*.sqlite3"))
        self.assertEqual(len(arquivos), 1)
        self.assertEqual(self.dbm.verificar_integridade(arquivos[0]), "ok")

    def test_falha_simulada_mantem_versao_3_sem_tabelas_orfas(self):
        db = self._copia("falha_v3v4")
        original = self.dbm.MIGRATIONS[3]

        def migracao_quebrada(c):
            c.execute("CREATE TABLE cpd_descricoes_fontes (id INTEGER PRIMARY KEY)")
            raise RuntimeError("falha simulada proposital")

        self.dbm.MIGRATIONS[3] = migracao_quebrada
        try:
            resultado = self._migrar(db, self.tmp_dir / "backups_falha_v3v4")
        finally:
            self.dbm.MIGRATIONS[3] = original

        self.assertEqual(resultado["versao_final"], 3)
        self.assertEqual(resultado["migracoes_aplicadas"], [])
        with sqlite3.connect(str(db)) as c:
            self.assertEqual(self.dbm.get_schema_version(c), 3)
            existe = c.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='cpd_descricoes_fontes'"
            ).fetchone()[0]
        self.assertEqual(existe, 0)

    # ------------------------------------------------------------------
    # Estrutura criada
    # ------------------------------------------------------------------

    def test_tabelas_e_indices_criados(self):
        db = self._copia("estrutura")
        self._migrar(db)
        with sqlite3.connect(str(db)) as c:
            tabelas = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
            indices = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
        self.assertIn("cpd_descricoes_fontes", tabelas)
        self.assertIn("cpd_pendencias_revisao", tabelas)
        for idx in (
            "idx_descricao_canonica_unica", "idx_descricoes_fontes_codigo", "idx_descricoes_fontes_cpd",
            "idx_pendencias_codigo", "idx_pendencias_tipo", "idx_pendencias_status",
            "idx_pendencias_cpd", "idx_pendencias_variacao",
        ):
            self.assertIn(idx, indices, f"Índice {idx} não foi criado")

    def test_integrity_e_foreign_key_check_ok_apos_migracao(self):
        db = self._copia("integridade")
        self._migrar(db)
        self.assertEqual(self.dbm.verificar_integridade(db), "ok")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            violacoes = c.execute("PRAGMA foreign_key_check").fetchall()
        self.assertEqual(violacoes, [])

    # ------------------------------------------------------------------
    # Regras de negócio das tabelas novas
    # ------------------------------------------------------------------

    def test_apenas_uma_descricao_canonica_por_codigo(self):
        db = self._copia("canonica_unica")
        self._migrar(db)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            cpd_id = self._cpd_ficticio(c)
            c.execute(
                "INSERT INTO cpd_descricoes_fontes(cpd_id, codigo_completo, descricao, fonte, descricao_canonica, criado_em) "
                "VALUES (?,?,?,?,1,?)",
                (cpd_id, "9990", "Descrição A", "LISTA_OFICIAL", agora),
            )
            c.commit()
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute(
                    "INSERT INTO cpd_descricoes_fontes(cpd_id, codigo_completo, descricao, fonte, descricao_canonica, criado_em) "
                    "VALUES (?,?,?,?,1,?)",
                    (cpd_id, "9990", "Descrição B", "MANUAL_CPD", agora),
                )

    def test_segunda_descricao_nao_canonica_e_permitida(self):
        db = self._copia("nao_canonica_ok")
        self._migrar(db)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            cpd_id = self._cpd_ficticio(c)
            c.execute(
                "INSERT INTO cpd_descricoes_fontes(cpd_id, codigo_completo, descricao, fonte, descricao_canonica, criado_em) "
                "VALUES (?,?,?,?,1,?)", (cpd_id, "9990", "Descrição A", "LISTA_OFICIAL", agora),
            )
            c.execute(
                "INSERT INTO cpd_descricoes_fontes(cpd_id, codigo_completo, descricao, fonte, descricao_canonica, criado_em) "
                "VALUES (?,?,?,?,0,?)", (cpd_id, "9990", "Descrição B", "MANUAL_CPD", agora),
            )
            c.commit()
            total = c.execute("SELECT COUNT(*) FROM cpd_descricoes_fontes WHERE codigo_completo='9990'").fetchone()[0]
        self.assertEqual(total, 2)

    def test_fonte_invalida_e_rejeitada(self):
        db = self._copia("fonte_invalida")
        self._migrar(db)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            cpd_id = self._cpd_ficticio(c)
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute(
                    "INSERT INTO cpd_descricoes_fontes(cpd_id, codigo_completo, descricao, fonte, criado_em) "
                    "VALUES (?,?,?,?,?)", (cpd_id, "9990", "X", "ORIGEM_INVALIDA", agora),
                )

    def test_tipo_pendencia_invalido_e_rejeitado(self):
        db = self._copia("tipo_invalido")
        self._migrar(db)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute(
                    "INSERT INTO cpd_pendencias_revisao(codigo_completo, tipo, status, criado_em) "
                    "VALUES (?,?,?,?)", ("9990", "TIPO_QUE_NAO_EXISTE", "PENDENTE", agora),
                )

    def test_pendencia_sem_cpd_e_permitida(self):
        db = self._copia("pendencia_sem_cpd")
        self._migrar(db)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            c.execute(
                "INSERT INTO cpd_pendencias_revisao(codigo_completo, tipo, status, criado_em) "
                "VALUES (?,?,?,?)", ("", "CLIENTE_INDEFINIDO", "PENDENTE", agora),
            )
            c.commit()
            total = c.execute("SELECT COUNT(*) FROM cpd_pendencias_revisao").fetchone()[0]
        self.assertEqual(total, 1)


if __name__ == "__main__":
    unittest.main()
