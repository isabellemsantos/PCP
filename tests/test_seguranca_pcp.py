"""Testes seguros da etapa de segurança/backup/migrações do PCP.

Importante: nenhum teste aqui toca no pcp.sqlite3 real. setUpClass cria uma
cópia isolada do banco de produção (usando a própria API de backup do
SQLite, sem exigir lock exclusivo) dentro de um diretório temporário, e usa
variáveis de ambiente (PCP_DB_FILE etc.) para apontar todo o servidor para
essa cópia antes de importar o módulo `servidor_pcp`. O banco/Excel/log/
backups reais nunca são abertos em modo escrita por este arquivo.

Rodar com:  py -m unittest tests.test_seguranca_pcp -v
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

ROOT = Path(__file__).resolve().parent.parent
REAL_DB = ROOT / "pcp.sqlite3"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _copiar_banco_real(destino: Path) -> None:
    """Copia o banco real para `destino` usando a API oficial de backup do
    SQLite (funciona com o banco em modo WAL e não precisa de lock
    exclusivo, então é seguro rodar com o servidor de produção no ar)."""
    origem = sqlite3.connect(str(REAL_DB))
    dest = sqlite3.connect(str(destino))
    try:
        with dest:
            origem.backup(dest)
    finally:
        dest.close()
        origem.close()


class SegurancaMigracoesPCPTest(unittest.TestCase):
    servidor = None
    dbm = None
    tmp_dir: Path

    @classmethod
    def setUpClass(cls):
        if not REAL_DB.exists():
            raise unittest.SkipTest(f"Banco real não encontrado em {REAL_DB}; nada para testar.")

        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_"))
        cls.db_copia = cls.tmp_dir / "pcp_copia.sqlite3"
        _copiar_banco_real(cls.db_copia)

        # Aponta TODOS os caminhos sensíveis do servidor para o diretório
        # temporário antes de importar o módulo, para isolamento total.
        os.environ["PCP_DB_FILE"] = str(cls.db_copia)
        os.environ["PCP_EXCEL_FILE"] = str(cls.tmp_dir / "dados_pcp_teste.xlsx")
        os.environ["PCP_EXCEL_PENDING_FILE"] = str(cls.tmp_dir / "dados_pcp_pendente_teste.xlsx")
        os.environ["PCP_LOG_FILE"] = str(cls.tmp_dir / "servidor_pcp_teste.log")
        os.environ["PCP_BACKUP_DIR"] = str(cls.tmp_dir / "backups")

        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)

        cls.servidor = importlib.import_module("servidor_pcp")
        cls.dbm = importlib.import_module("db_manutencao")

        # Confere que o módulo realmente pegou os caminhos de teste, não os reais.
        assert cls.servidor.DB_FILE == cls.db_copia, "Isolamento falhou: servidor não usou a cópia de teste"
        assert cls.servidor.DB_FILE != REAL_DB

        cls.servidor.init_db()

    @classmethod
    def tearDownClass(cls):
        for var in ("PCP_DB_FILE", "PCP_EXCEL_FILE", "PCP_EXCEL_PENDING_FILE", "PCP_LOG_FILE", "PCP_BACKUP_DIR"):
            os.environ.pop(var, None)
        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # 1) Backup oficial via sqlite3.Connection.backup()
    # ------------------------------------------------------------------

    def test_backup_oficial_abre_e_integro(self):
        destino_dir = self.tmp_dir / "backups_manual"
        caminho = self.dbm.criar_backup_sqlite(self.db_copia, destino_dir, prefixo="teste")
        self.assertIsNotNone(caminho, "Backup deveria ter sido criado com sucesso")
        self.assertTrue(caminho.exists())

        # Reabre o backup de forma independente e confirma integridade.
        conexao = sqlite3.connect(str(caminho))
        try:
            resultado = conexao.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            conexao.close()
        self.assertEqual(resultado, "ok")
        self.assertEqual(self.dbm.verificar_integridade(caminho), "ok")

    def test_backup_nao_apaga_backups_existentes(self):
        destino_dir = self.tmp_dir / "backups_multiplos"
        primeiro = self.dbm.criar_backup_sqlite(self.db_copia, destino_dir, prefixo="teste")
        segundo = self.dbm.criar_backup_sqlite(self.db_copia, destino_dir, prefixo="teste")
        self.assertIsNotNone(primeiro)
        self.assertIsNotNone(segundo)
        self.assertTrue(primeiro.exists(), "Backup anterior não pode ser apagado")
        self.assertTrue(segundo.exists())

    # ------------------------------------------------------------------
    # 2) Versão de schema
    # ------------------------------------------------------------------

    def test_schema_version_comeca_em_1(self):
        with self.servidor.conn() as c:
            versao = self.dbm.get_schema_version(c)
        self.assertEqual(versao, 1)

    def test_set_e_get_schema_version(self):
        with self.servidor.conn() as c:
            self.dbm.set_schema_version(c, 5)
            c.commit()
            self.assertEqual(self.dbm.get_schema_version(c), 5)
            # Restaura para não afetar os demais testes.
            self.dbm.set_schema_version(c, 1)
            c.commit()

    # ------------------------------------------------------------------
    # 3) Migração é idempotente e não altera nada sem migrações registradas
    # ------------------------------------------------------------------

    def test_run_migrations_sem_migracoes_e_no_op(self):
        with self.servidor.conn() as c:
            resultado = self.dbm.run_migrations(c, self.db_copia, self.tmp_dir / "backups_migracao")
        self.assertEqual(resultado["versao_final"], 1)
        self.assertEqual(resultado["migracoes_aplicadas"], [])

    # ------------------------------------------------------------------
    # 4) Validação dos dados: totais antes/depois da (não-)migração batem
    # ------------------------------------------------------------------

    def test_totais_antes_e_depois_da_migracao_sao_iguais(self):
        antes = self.dbm.gerar_relatorio_validacao(self.db_copia)
        with self.servidor.conn() as c:
            self.dbm.run_migrations(c, self.db_copia, self.tmp_dir / "backups_migracao2")
        depois = self.dbm.gerar_relatorio_validacao(self.db_copia)

        campos = [
            "total_pedidos", "total_datas_secoes", "total_pedidos_ativos",
            "total_pedidos_finalizados", "total_pedidos_lixeira",
            "total_datas_lixeira", "total_registros_auditoria",
            "total_cpds_cadastrados",
        ]
        for campo in campos:
            self.assertEqual(antes[campo], depois[campo], f"Total mudou em '{campo}'")
        self.assertEqual(antes["integrity_check"], "ok")
        self.assertEqual(depois["integrity_check"], "ok")

    def test_relatorio_pode_ser_salvo_em_json(self):
        alvo = self.tmp_dir / "backups" / "validacao_banco_teste.json"
        relatorio = self.dbm.gerar_relatorio_validacao(self.db_copia, salvar_em=alvo)
        self.assertTrue(alvo.exists())
        self.assertIn("total_pedidos", relatorio)

    # ------------------------------------------------------------------
    # 5) Servidor inicia sem erro / tela principal abre / rotas bloqueadas
    # ------------------------------------------------------------------

    def test_servidor_inicia_sem_erro_e_tela_principal_abre(self):
        cliente = self.servidor.app.test_client()
        resp = cliente.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.content_type)
        corpo = resp.get_data(as_text=True)
        self.assertGreater(len(corpo), 1000, "Página principal veio vazia/curta demais")

    def test_rotas_de_arquivos_sensiveis_sao_bloqueadas(self):
        cliente = self.servidor.app.test_client()
        rotas_proibidas = [
            "/pcp.sqlite3",
            "/pcp.sqlite3-wal",
            "/pcp.sqlite3-shm",
            "/dados_pcp.xlsx",
            "/dados_pcp_pendente.xlsx",
            "/servidor_pcp.log",
            "/servidor_pcp.py",
            "/db_manutencao.py",
            "/.env",
            "/backups/pcp_backup_qualquer.sqlite3",
            "/base_cpds.json",
            "/requirements_pcp.txt",
        ]
        for rota in rotas_proibidas:
            resp = cliente.get(rota)
            self.assertIn(
                resp.status_code, (403, 404),
                f"Rota {rota} deveria ser bloqueada, retornou {resp.status_code}",
            )

    def test_rotas_publicas_continuam_funcionando(self):
        cliente = self.servidor.app.test_client()
        for rota in ("/", "/pcp_prototype.html", "/pcp_prototype_sqlite.html"):
            resp = cliente.get(rota)
            self.assertEqual(resp.status_code, 200, f"Rota pública {rota} deveria continuar funcionando")

    def test_api_state_continua_funcionando(self):
        cliente = self.servidor.app.test_client()
        resp = cliente.get("/api/state")
        self.assertEqual(resp.status_code, 200)
        dados = resp.get_json()
        self.assertIn("orders", dados)
        self.assertIn("sections", dados)

    # ------------------------------------------------------------------
    # 6) current_actor()/import_cpds_from_excel_file() fora de requisição
    # ------------------------------------------------------------------

    def test_current_actor_fora_de_contexto_retorna_default_sem_erro(self):
        # Sem app.test_request_context(): não há requisição HTTP ativa,
        # exatamente a situação da inicialização do servidor.
        self.assertEqual(self.servidor.current_actor(), "Não informado")
        self.assertEqual(self.servidor.current_actor("Sistema/Inicialização"), "Sistema/Inicialização")
        self.assertEqual(self.servidor.current_actor("Importação Excel"), "Importação Excel")

    def test_current_actor_dentro_de_contexto_mantem_comportamento(self):
        with self.servidor.app.test_request_context("/", headers={"X-PCP-User": "Fulano"}):
            self.assertEqual(self.servidor.current_actor(), "Fulano")

    def test_import_cpds_from_excel_file_fora_de_contexto_nao_gera_traceback(self):
        excel_real = ROOT / "dados_pcp.xlsx"
        if not excel_real.exists():
            self.skipTest("dados_pcp.xlsx não existe neste ambiente")
        copia_excel = self.tmp_dir / "dados_pcp_copia_teste.xlsx"
        shutil.copy2(excel_real, copia_excel)  # cópia somente-leitura da origem

        # Chamado fora de qualquer requisição Flask, igual à inicialização
        # real do servidor. Antes da correção, isso levantava
        # "RuntimeError: Working outside of request context".
        try:
            resultado = self.servidor.import_cpds_from_excel_file(copia_excel, actor="Sistema/Inicialização")
        except RuntimeError as exc:
            self.fail(f"import_cpds_from_excel_file levantou RuntimeError fora de contexto: {exc}")
        self.assertIn("imported", resultado)

        with self.servidor.conn() as c:
            ultimo = c.execute(
                "SELECT actor FROM audit_log WHERE entity='cpd_xlsx' ORDER BY id DESC LIMIT 1"
            ).fetchone()
        self.assertIsNotNone(ultimo)
        self.assertEqual(ultimo["actor"], "Sistema/Inicialização")


if __name__ == "__main__":
    unittest.main()
