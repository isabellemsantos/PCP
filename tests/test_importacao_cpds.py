"""Testes da desativação da importação automática de CPDs no início do
servidor e da importação administrativa controlada (scripts/importar_cpds_excel.py).

Nenhum teste aqui toca no pcp.sqlite3 real nem no dados_pcp.xlsx real.
Cada teste isola servidor_pcp.DB_FILE/EXCEL_FILE via unittest.mock.patch.object
apontando para cópias/arquivos fictícios criados no diretório temporário.

Rodar com:  py -m unittest tests.test_importacao_cpds -v
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
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _criar_excel_fake(caminho: Path, cpds: list[tuple[str, str]]) -> None:
    """Cria um Excel fictício mínimo com a aba 'Base CPDs', nunca o real."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Base CPDs"
    ws.append(["Código", "Descrição"])
    for codigo, descricao in cpds:
        ws.append([codigo, descricao])
    wb.save(caminho)


def _copiar_via_backup(origem: Path, destino: Path) -> None:
    origem_conn = sqlite3.connect(str(origem))
    destino_conn = sqlite3.connect(str(destino))
    try:
        with destino_conn:
            origem_conn.backup(destino_conn)
    finally:
        destino_conn.close()
        origem_conn.close()


class ImportacaoCpdsTestCase(unittest.TestCase):
    tmp_dir: Path
    db_base: Path
    excel_fake: Path
    servidor = None
    dbm = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_import_cpds_"))
        cls.db_base = cls.tmp_dir / "base.sqlite3"
        cls.excel_fake = cls.tmp_dir / "excel_fake_base.xlsx"
        _criar_excel_fake(cls.excel_fake, [("TESTE-001", "Peça de teste 1"), ("TESTE-002", "Peça de teste 2")])

        os.environ["PCP_DB_FILE"] = str(cls.db_base)
        os.environ["PCP_EXCEL_FILE"] = str(cls.tmp_dir / "dados_pcp_teste_inexistente.xlsx")
        os.environ["PCP_EXCEL_PENDING_FILE"] = str(cls.tmp_dir / "dados_pcp_pendente_teste.xlsx")
        os.environ["PCP_LOG_FILE"] = str(cls.tmp_dir / "servidor_pcp_teste.log")
        os.environ["PCP_BACKUP_DIR"] = str(cls.tmp_dir / "backups")
        os.environ.pop("PCP_IMPORTAR_CPDS_INICIALIZACAO", None)

        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        cls.servidor = importlib.import_module("servidor_pcp")
        cls.dbm = importlib.import_module("db_manutencao")
        cls.servidor.init_db()

    @classmethod
    def tearDownClass(cls):
        for var in (
            "PCP_DB_FILE", "PCP_EXCEL_FILE", "PCP_EXCEL_PENDING_FILE",
            "PCP_LOG_FILE", "PCP_BACKUP_DIR", "PCP_IMPORTAR_CPDS_INICIALIZACAO",
        ):
            os.environ.pop(var, None)
        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def _copia_excel_fake(self, nome: str) -> Path:
        # Cópia própria por teste: import_cpds_from_excel_file() aciona
        # after_write_state() -> save_excel_snapshot_safely(), que SOBRESCREVE
        # EXCEL_FILE com um export do banco. Se todo teste apontasse pro
        # mesmo self.excel_fake compartilhado, o primeiro teste que importasse
        # substituiria o fixture de 2 linhas por um export completo do banco,
        # contaminando os testes seguintes.
        destino = self.tmp_dir / f"{nome}.xlsx"
        shutil.copy2(self.excel_fake, destino)
        return destino

    def _copia_isolada(self, nome: str) -> Path:
        destino = self.tmp_dir / f"{nome}.sqlite3"
        _copiar_via_backup(self.db_base, destino)
        return destino

    def tearDown(self):
        os.environ.pop("PCP_IMPORTAR_CPDS_INICIALIZACAO", None)


# ---------------------------------------------------------------------------
# 1) Gate deve_importar_cpds_na_inicializacao()
# ---------------------------------------------------------------------------

class GateImportacaoTest(ImportacaoCpdsTestCase):

    def test_variavel_ausente_nao_importa(self):
        os.environ.pop("PCP_IMPORTAR_CPDS_INICIALIZACAO", None)
        self.assertFalse(self.servidor.deve_importar_cpds_na_inicializacao())

    def test_variavel_0_nao_importa(self):
        os.environ["PCP_IMPORTAR_CPDS_INICIALIZACAO"] = "0"
        self.assertFalse(self.servidor.deve_importar_cpds_na_inicializacao())

    def test_variavel_1_permite_importar(self):
        os.environ["PCP_IMPORTAR_CPDS_INICIALIZACAO"] = "1"
        self.assertTrue(self.servidor.deve_importar_cpds_na_inicializacao())


# ---------------------------------------------------------------------------
# 2) executar_importacao_cpds_na_inicializacao() -- chamada real do __main__
# ---------------------------------------------------------------------------

class ExecutarImportacaoNaInicializacaoTest(ImportacaoCpdsTestCase):

    def test_startup_normal_nao_importa_nem_abre_excel_nem_cria_auditoria(self):
        db = self._copia_isolada("startup_normal")
        os.environ.pop("PCP_IMPORTAR_CPDS_INICIALIZACAO", None)
        with patch.object(self.servidor, "DB_FILE", db), patch.object(self.servidor, "EXCEL_FILE", self.excel_fake):
            with sqlite3.connect(str(db)) as c:
                cpds_antes = c.execute("SELECT COUNT(*) FROM manual_cpd").fetchone()[0]
                auditorias_antes = c.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]

            resultado = self.servidor.executar_importacao_cpds_na_inicializacao()

            with sqlite3.connect(str(db)) as c:
                cpds_depois = c.execute("SELECT COUNT(*) FROM manual_cpd").fetchone()[0]
                auditorias_depois = c.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]

        self.assertEqual(resultado, {"importou": False})
        self.assertEqual(cpds_antes, cpds_depois, "manual_cpd não deveria mudar sem PCP_IMPORTAR_CPDS_INICIALIZACAO=1")
        self.assertEqual(auditorias_antes, auditorias_depois, "audit_log não deveria crescer sem autorização explícita")

    def test_variavel_1_importa_e_cria_auditoria_com_ator_sistema_inicializacao(self):
        db = self._copia_isolada("startup_com_flag")
        excel = self._copia_excel_fake("excel_startup_com_flag")
        os.environ["PCP_IMPORTAR_CPDS_INICIALIZACAO"] = "1"
        with patch.object(self.servidor, "DB_FILE", db), patch.object(self.servidor, "EXCEL_FILE", excel):
            resultado = self.servidor.executar_importacao_cpds_na_inicializacao()
            with sqlite3.connect(str(db)) as c:
                c.row_factory = sqlite3.Row
                codigos = {r["codigo"] for r in c.execute("SELECT codigo FROM manual_cpd").fetchall()}
                ultima_auditoria = c.execute(
                    "SELECT action, entity, actor FROM audit_log ORDER BY id DESC LIMIT 1"
                ).fetchone()

        self.assertTrue(resultado["importou"])
        self.assertEqual(resultado["cpds"], 2)
        self.assertIn("TESTE-001", codigos)
        self.assertIn("TESTE-002", codigos)
        self.assertEqual(ultima_auditoria["action"], "import")
        self.assertEqual(ultima_auditoria["entity"], "cpd_xlsx")
        self.assertEqual(ultima_auditoria["actor"], "Sistema/Inicialização")

    def test_schema_version_nao_e_afetado_pela_importacao(self):
        db = self._copia_isolada("schema_version_import")
        excel = self._copia_excel_fake("excel_schema_version_import")
        with sqlite3.connect(str(db)) as c:
            versao_antes = self.dbm.get_schema_version(c)
        os.environ["PCP_IMPORTAR_CPDS_INICIALIZACAO"] = "1"
        with patch.object(self.servidor, "DB_FILE", db), patch.object(self.servidor, "EXCEL_FILE", excel):
            self.servidor.executar_importacao_cpds_na_inicializacao()
        with sqlite3.connect(str(db)) as c:
            versao_depois = self.dbm.get_schema_version(c)
        self.assertEqual(versao_antes, versao_depois)

    def test_current_actor_fora_de_contexto_continua_seguro(self):
        # Mesma garantia da suíte de segurança: chamar fora de uma requisição
        # Flask nunca levanta RuntimeError, mesmo com a nova função de gate.
        self.assertEqual(self.servidor.current_actor(), "Não informado")
        self.assertEqual(self.servidor.current_actor("Sistema/Inicialização"), "Sistema/Inicialização")


# ---------------------------------------------------------------------------
# 3) Script administrativo scripts/importar_cpds_excel.py
# ---------------------------------------------------------------------------

class ScriptImportacaoAdministrativaTest(ImportacaoCpdsTestCase):

    def setUp(self):
        sys.modules.pop("scripts.importar_cpds_excel", None)
        import scripts.importar_cpds_excel as modulo
        self.modulo = modulo

    def test_script_sem_confirmar_e_dry_run_nao_altera_nada(self):
        db = self._copia_isolada("script_sem_confirmar")
        with patch.object(self.servidor, "DB_FILE", db):
            with sqlite3.connect(str(db)) as c:
                cpds_antes = c.execute("SELECT COUNT(*) FROM manual_cpd").fetchone()[0]
            resultado = self.modulo.executar(self.excel_fake, confirmar=False)
            with sqlite3.connect(str(db)) as c:
                cpds_depois = c.execute("SELECT COUNT(*) FROM manual_cpd").fetchone()[0]

        self.assertFalse(resultado["executado"])
        self.assertEqual(cpds_antes, cpds_depois)

    def test_script_main_sem_flag_confirmar_retorna_ok_sem_alterar(self):
        db = self._copia_isolada("script_main_sem_confirmar")
        with patch.object(self.servidor, "DB_FILE", db):
            codigo_saida = self.modulo.main(["--excel", str(self.excel_fake)])
        self.assertEqual(codigo_saida, 0)

    def test_script_com_confirmar_importa_e_usa_ator_administrativo(self):
        db = self._copia_isolada("script_confirmar")
        with patch.object(self.servidor, "DB_FILE", db):
            resultado = self.modulo.executar(self.excel_fake, confirmar=True)
            with sqlite3.connect(str(db)) as c:
                c.row_factory = sqlite3.Row
                ultima_auditoria = c.execute(
                    "SELECT action, entity, actor FROM audit_log ORDER BY id DESC LIMIT 1"
                ).fetchone()

        self.assertTrue(resultado["executado"])
        self.assertEqual(resultado["processados_pelo_excel"], 2)
        self.assertEqual(resultado["ator"], "Sistema/Importação administrativa")
        self.assertEqual(ultima_auditoria["actor"], "Sistema/Importação administrativa")

    def test_script_excel_inexistente_da_erro_controlado(self):
        db = self._copia_isolada("script_excel_inexistente")
        with patch.object(self.servidor, "DB_FILE", db):
            with self.assertRaises(FileNotFoundError):
                self.modulo.executar(self.tmp_dir / "nao_existe.xlsx", confirmar=True)


if __name__ == "__main__":
    unittest.main()
