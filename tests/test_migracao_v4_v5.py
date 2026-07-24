"""Testes da migração de schema_version 4 -> 5 (cadastro separado de
arruelas: arruelas, cliente_arruelas, grupo_arruelas, arruela_descricoes_fontes).

Nenhum teste aqui toca no pcp.sqlite3 real. Cada teste trabalha sobre uma
cópia isolada, feita com sqlite3.Connection.backup(), de uma base sintética
já em schema_version 4 (via servidor_pcp.init_db() + migrar_v1_para_v2 +
migrar_v2_para_v3 + migrar_v3_para_v4).

Rodar com:  py -m unittest tests.test_migracao_v4_v5 -v
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


class MigracaoV4V5TestCase(unittest.TestCase):
    tmp_dir: Path
    db_v4_base: Path
    servidor = None
    dbm = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_migracao_v4v5_"))
        cls.db_v4_base = cls.tmp_dir / "base_v4.sqlite3"

        os.environ["PCP_DB_FILE"] = str(cls.db_v4_base)
        os.environ["PCP_EXCEL_FILE"] = str(cls.tmp_dir / "dados_pcp_teste.xlsx")
        os.environ["PCP_EXCEL_PENDING_FILE"] = str(cls.tmp_dir / "dados_pcp_pendente_teste.xlsx")
        os.environ["PCP_LOG_FILE"] = str(cls.tmp_dir / "servidor_pcp_teste.log")
        os.environ["PCP_BACKUP_DIR"] = str(cls.tmp_dir / "backups")

        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        cls.servidor = importlib.import_module("servidor_pcp")
        cls.dbm = importlib.import_module("db_manutencao")
        cls.servidor.init_db()

        with sqlite3.connect(str(cls.db_v4_base)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            cls.dbm.migrar_v1_para_v2(c)
            cls.dbm.migrar_v2_para_v3(c)
            cls.dbm.migrar_v3_para_v4(c)
            cls.dbm.set_schema_version(c, 4)
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
        _copiar_via_backup(self.db_v4_base, destino)
        return destino

    def _migrar(self, db_path: Path, backup_dir: Path | None = None) -> dict:
        # Isola o degrau v4->v5: esconde qualquer migração >= 5 (nenhuma
        # existe ainda, mas mantém o padrão usado em test_migracao_v3_v4.py
        # pra este teste continuar correto se um dia v5->v6 for registrada).
        backup_dir = backup_dir or (self.tmp_dir / f"backups_{db_path.stem}")
        conexao = sqlite3.connect(str(db_path))
        conexao.execute("PRAGMA foreign_keys=ON")
        migracoes_futuras = {v: f for v, f in self.dbm.MIGRATIONS.items() if v >= 5}
        for v in migracoes_futuras:
            del self.dbm.MIGRATIONS[v]
        try:
            resultado = self.dbm.run_migrations(conexao, db_path, backup_dir, log=lambda _msg: None)
        finally:
            conexao.close()
            self.dbm.MIGRATIONS.update(migracoes_futuras)
        return resultado

    def _cliente_ficticio(self, conn, nome="CLIENTE_TESTE_ARRUELA"):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO clientes(nome, ativo, criado_em, atualizado_em) VALUES (?,1,?,?)",
            (nome, agora, agora),
        )
        return conn.execute("SELECT id FROM clientes WHERE nome=?", (nome,)).fetchone()[0]

    def _grupo_ficticio(self, conn, nome="Diversos"):
        row = conn.execute("SELECT id FROM grupos_clientes WHERE nome=?", (nome,)).fetchone()
        if row:
            return row[0]
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO grupos_clientes(nome, ativo, criado_em, atualizado_em) VALUES (?,1,?,?)",
            (nome, agora, agora),
        )
        return conn.execute("SELECT id FROM grupos_clientes WHERE nome=?", (nome,)).fetchone()[0]

    def _arruela_ficticia(self, conn, codigo="AW-999"):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO arruelas(codigo, ativo, criado_em, atualizado_em) VALUES (?,1,?,?)",
            (codigo, agora, agora),
        )
        return conn.execute("SELECT id FROM arruelas WHERE codigo=?", (codigo,)).fetchone()[0]

    # ------------------------------------------------------------------
    # Transição de versão e idempotência
    # ------------------------------------------------------------------

    def test_migracao_registrada_em_migrations_4(self):
        self.assertIn(4, self.dbm.MIGRATIONS)
        self.assertIs(self.dbm.MIGRATIONS[4], self.dbm.migrar_v4_para_v5)

    def test_latest_schema_version_e_pelo_menos_5(self):
        self.assertGreaterEqual(self.dbm.LATEST_SCHEMA_VERSION, 5)

    def test_migracoes_pendentes_de_4_inclui_5(self):
        self.assertIn(5, self.dbm.migracoes_pendentes(4))

    def test_banco_v4_termina_em_v5(self):
        db = self._copia("v4_para_v5")
        resultado = self._migrar(db)
        self.assertEqual(resultado["versao_final"], 5)
        self.assertEqual(resultado["migracoes_aplicadas"], [5])

    def test_segunda_execucao_e_no_op(self):
        db = self._copia("idempotencia")
        primeiro = self._migrar(db, self.tmp_dir / "backups_idem1")
        segundo = self._migrar(db, self.tmp_dir / "backups_idem2")
        self.assertEqual(primeiro["migracoes_aplicadas"], [5])
        self.assertEqual(segundo["migracoes_aplicadas"], [])
        self.assertEqual(segundo["versao_final"], 5)

    def test_backup_pre_migracao_e_criado_e_valido(self):
        db = self._copia("backup_v4v5")
        backup_dir = self.tmp_dir / "backups_validacao_v4v5"
        self._migrar(db, backup_dir)
        arquivos = list(backup_dir.glob("pcp_pre_migracao_v4_para_v5_*.sqlite3"))
        self.assertEqual(len(arquivos), 1)
        self.assertEqual(self.dbm.verificar_integridade(arquivos[0]), "ok")

    def test_falha_simulada_mantem_versao_4_sem_tabelas_orfas(self):
        db = self._copia("falha_v4v5")
        original = self.dbm.MIGRATIONS[4]

        def migracao_quebrada(c):
            c.execute("CREATE TABLE arruelas (id INTEGER PRIMARY KEY)")
            raise RuntimeError("falha simulada proposital")

        self.dbm.MIGRATIONS[4] = migracao_quebrada
        try:
            resultado = self._migrar(db, self.tmp_dir / "backups_falha_v4v5")
        finally:
            self.dbm.MIGRATIONS[4] = original

        self.assertEqual(resultado["versao_final"], 4)
        self.assertEqual(resultado["migracoes_aplicadas"], [])
        with sqlite3.connect(str(db)) as c:
            self.assertEqual(self.dbm.get_schema_version(c), 4)
            existe = c.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='arruelas'"
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
        for tabela in ("arruelas", "cliente_arruelas", "grupo_arruelas", "arruela_descricoes_fontes"):
            self.assertIn(tabela, tabelas)
        for idx in (
            "idx_arruela_descricao_canonica_unica", "idx_arruela_descricoes_fontes_codigo",
            "idx_arruela_descricoes_fontes_arruela", "idx_cliente_arruelas_cliente",
            "idx_cliente_arruelas_arruela", "idx_grupo_arruelas_grupo", "idx_grupo_arruelas_arruela",
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

    def test_nao_mexe_em_cpds_existentes(self):
        # A migração de arruelas nunca deve tocar nas tabelas de CPD já
        # existentes -- só cria estruturas novas.
        db = self._copia("nao_mexe_cpds")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO cpds(codigo_pai, ativo, criado_em, atualizado_em) VALUES ('09999',1,?,?)", (agora, agora))
            c.commit()
            antes = c.execute("SELECT COUNT(*) FROM cpds").fetchone()[0]
        self._migrar(db)
        with sqlite3.connect(str(db)) as c:
            depois = c.execute("SELECT COUNT(*) FROM cpds").fetchone()[0]
        self.assertEqual(antes, depois)

    # ------------------------------------------------------------------
    # Regras de negócio das tabelas novas
    # ------------------------------------------------------------------

    def test_arruela_comeca_ativa_e_sem_desativado_em(self):
        db = self._copia("arruela_ativa")
        self._migrar(db)
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            arruela_id = self._arruela_ficticia(c)
            row = c.execute("SELECT ativo, desativado_em FROM arruelas WHERE id=?", (arruela_id,)).fetchone()
        self.assertEqual(row[0], 1)
        self.assertIsNone(row[1])

    def test_apenas_uma_descricao_canonica_por_arruela(self):
        db = self._copia("canonica_unica_arruela")
        self._migrar(db)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            arruela_id = self._arruela_ficticia(c)
            c.execute(
                "INSERT INTO arruela_descricoes_fontes(arruela_id, codigo_original, descricao, fonte, descricao_canonica, criado_em) "
                "VALUES (?,?,?,?,1,?)", (arruela_id, "AW-999", "Arruela lisa", "LISTA_OFICIAL", agora),
            )
            c.commit()
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute(
                    "INSERT INTO arruela_descricoes_fontes(arruela_id, codigo_original, descricao, fonte, descricao_canonica, criado_em) "
                    "VALUES (?,?,?,?,1,?)", (arruela_id, "AW-999", "Arruela lisa (outra fonte)", "MANUAL_CPD", agora),
                )

    def test_fonte_invalida_em_arruela_e_rejeitada(self):
        db = self._copia("fonte_invalida_arruela")
        self._migrar(db)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            arruela_id = self._arruela_ficticia(c)
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute(
                    "INSERT INTO arruela_descricoes_fontes(arruela_id, codigo_original, descricao, fonte, criado_em) "
                    "VALUES (?,?,?,?,?)", (arruela_id, "AW-999", "X", "ORIGEM_INVALIDA", agora),
                )

    def test_origem_invalida_em_cliente_arruela_e_rejeitada(self):
        db = self._copia("origem_invalida_cliente_arruela")
        self._migrar(db)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            cliente_id = self._cliente_ficticio(c)
            arruela_id = self._arruela_ficticia(c)
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute(
                    "INSERT INTO cliente_arruelas(cliente_id, arruela_id, origem, criado_em) VALUES (?,?,?,?)",
                    (cliente_id, arruela_id, "ORIGEM_QUE_NAO_EXISTE", agora),
                )

    def test_cliente_arruela_e_grupo_arruela_aceitos(self):
        db = self._copia("vinculos_arruela")
        self._migrar(db)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            cliente_id = self._cliente_ficticio(c)
            grupo_id = self._grupo_ficticio(c)
            arruela_id = self._arruela_ficticia(c)
            c.execute(
                "INSERT INTO cliente_arruelas(cliente_id, arruela_id, origem, criado_em) VALUES (?,?,?,?)",
                (cliente_id, arruela_id, "LISTA_OFICIAL", agora),
            )
            c.execute(
                "INSERT INTO grupo_arruelas(grupo_id, arruela_id, criado_em) VALUES (?,?,?)",
                (grupo_id, arruela_id, agora),
            )
            c.commit()
            total_cliente = c.execute("SELECT COUNT(*) FROM cliente_arruelas").fetchone()[0]
            total_grupo = c.execute("SELECT COUNT(*) FROM grupo_arruelas").fetchone()[0]
        self.assertEqual(total_cliente, 1)
        self.assertEqual(total_grupo, 1)

    def test_codigo_de_arruela_e_unico(self):
        db = self._copia("codigo_unico_arruela")
        self._migrar(db)
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            self._arruela_ficticia(c, "AW-999")
            with self.assertRaises(sqlite3.IntegrityError):
                self._arruela_ficticia(c, "AW-999")


if __name__ == "__main__":
    unittest.main()
