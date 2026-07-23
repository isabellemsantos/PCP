"""Testes da migração de schema_version 1 -> 2 (estrutura e configurações).

Importante: nenhum teste aqui toca no pcp.sqlite3 real nem depende dele
existir. Cada teste trabalha sobre uma cópia isolada de um banco sintético
em schema_version 1 (criado do zero por servidor_pcp.init_db() dentro de um
diretório temporário), copiada para cada teste com sqlite3.Connection.backup()
— nunca com cópia de arquivo bruta e nunca reaproveitando a mesma conexão
entre testes que migram o schema.

Rodar com:  py -m unittest tests.test_migracao_v1_v2 -v
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
    """Copia um arquivo sqlite usando a API oficial de backup (nunca cópia crua)."""
    origem_conn = sqlite3.connect(str(origem))
    destino_conn = sqlite3.connect(str(destino))
    try:
        with destino_conn:
            origem_conn.backup(destino_conn)
    finally:
        destino_conn.close()
        origem_conn.close()


class MigracaoV1V2TestCase(unittest.TestCase):
    """Base: monta um banco v1 sintético uma vez e distribui cópias por teste."""

    tmp_dir: Path
    db_v1_base: Path
    servidor = None
    dbm = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_migracao_"))
        cls.db_v1_base = cls.tmp_dir / "base_v1.sqlite3"

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
        cls.servidor.init_db()  # cria schema v1 (meta/orders/sections/manual_cpd/audit_log)

        with sqlite3.connect(str(cls.db_v1_base)) as c:
            versao = cls.dbm.get_schema_version(c)
        assert versao == 1, f"Base de teste deveria começar em schema_version 1, veio {versao}"

    @classmethod
    def tearDownClass(cls):
        for var in ("PCP_DB_FILE", "PCP_EXCEL_FILE", "PCP_EXCEL_PENDING_FILE", "PCP_LOG_FILE", "PCP_BACKUP_DIR"):
            os.environ.pop(var, None)
        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def _nova_copia(self, nome: str) -> Path:
        destino = self.tmp_dir / f"{nome}.sqlite3"
        _copiar_via_backup(self.db_v1_base, destino)
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
# 1) Registro da migração e transição de versão
# ---------------------------------------------------------------------------

class RegistroEVersaoTest(MigracaoV1V2TestCase):

    def test_migracao_registrada_em_migrations_1(self):
        self.assertIn(1, self.dbm.MIGRATIONS)
        self.assertIs(self.dbm.MIGRATIONS[1], self.dbm.migrar_v1_para_v2)

    def test_copia_base_comeca_em_schema_version_1(self):
        db = self._nova_copia("versao_inicial")
        with sqlite3.connect(str(db)) as c:
            self.assertEqual(self.dbm.get_schema_version(c), 1)

    def test_migracao_termina_em_schema_version_2(self):
        # Chama migrar_v1_para_v2() diretamente (não via run_migrations):
        # desde que a migração v2->v3 também foi registrada, run_migrations()
        # avançaria o schema além da v2 nesta cópia, o que é o comportamento
        # correto do motor de migrações, mas não é o que este teste
        # específico quer verificar (isso é coberto em
        # tests.test_migracao_v2_v3.TransicaoVersaoTest.test_banco_v1_executa_1_2_3_corretamente).
        db = self._nova_copia("versao_final")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            self.dbm.migrar_v1_para_v2(c)
            self.dbm.set_schema_version(c, 2)
            c.commit()
        with sqlite3.connect(str(db)) as c:
            self.assertEqual(self.dbm.get_schema_version(c), 2)


# ---------------------------------------------------------------------------
# 2) Estrutura criada: tabelas, colunas, FKs, índices/UNIQUE
# ---------------------------------------------------------------------------

_TABELAS_V2_ESPERADAS = (
    "areas", "perfis", "permissoes", "perfil_permissoes", "usuarios", "usuario_permissoes",
    "grupos_clientes", "clientes", "cliente_aliases", "cliente_grupos",
    "cpds", "cpd_variacoes", "cliente_cpds", "grupo_cpds",
    "processos", "fornecedores", "processo_fornecedores",
    "rotas_processo", "rota_etapas",
    "niveis_urgencia", "regras_urgencia",
    "configuracoes_sistema", "historico_configuracoes",
)


class EstruturaTest(MigracaoV1V2TestCase):

    def setUp(self):
        self.db = self._nova_copia(f"estrutura_{self._testMethodName}")
        self._migrar(self.db)
        self.conn = sqlite3.connect(str(self.db))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")

    def tearDown(self):
        self.conn.close()

    def test_todas_as_tabelas_novas_existem(self):
        existentes = {r[0] for r in self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        faltando = set(_TABELAS_V2_ESPERADAS) - existentes
        self.assertEqual(faltando, set(), f"Tabelas não criadas: {faltando}")

    def test_tabelas_antigas_nao_foram_tocadas(self):
        existentes = {r[0] for r in self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        for antiga in ("meta", "orders", "sections", "manual_cpd", "audit_log"):
            self.assertIn(antiga, existentes)

    def test_colunas_usuarios_esperadas(self):
        cols = {r["name"]: r["type"] for r in self.conn.execute("PRAGMA table_info(usuarios)").fetchall()}
        esperado = {
            "id": "INTEGER", "nome_completo": "TEXT", "area_id": "INTEGER",
            "login": "TEXT", "senha_hash": "TEXT", "perfil_id": "INTEGER",
            "ativo": "INTEGER", "bloqueado": "INTEGER", "deve_trocar_senha": "INTEGER",
            "tentativas_falhas": "INTEGER", "bloqueado_ate": "TEXT",
            "ultimo_acesso": "TEXT", "criado_em": "TEXT", "atualizado_em": "TEXT",
            "desativado_em": "TEXT",
        }
        for nome, tipo in esperado.items():
            self.assertIn(nome, cols, f"Coluna {nome} ausente em usuarios")
            self.assertEqual(cols[nome], tipo, f"Coluna {nome} deveria ser {tipo}, é {cols[nome]}")

    def test_colunas_cpds_e_variacoes_sao_text(self):
        cols_cpds = {r["name"]: r["type"] for r in self.conn.execute("PRAGMA table_info(cpds)").fetchall()}
        cols_var = {r["name"]: r["type"] for r in self.conn.execute("PRAGMA table_info(cpd_variacoes)").fetchall()}
        self.assertEqual(cols_cpds["codigo_pai"], "TEXT")
        self.assertEqual(cols_var["codigo_completo"], "TEXT")

    def test_foreign_keys_declaradas(self):
        fks_usuarios = {r["table"] for r in self.conn.execute("PRAGMA foreign_key_list(usuarios)").fetchall()}
        self.assertEqual(fks_usuarios, {"areas", "perfis"})

        fks_cliente_cpds = {r["table"] for r in self.conn.execute("PRAGMA foreign_key_list(cliente_cpds)").fetchall()}
        self.assertEqual(fks_cliente_cpds, {"clientes", "cpds"}, "cliente_cpds deve referenciar cpds, não cpd_variacoes")

        fks_grupo_cpds = {r["table"] for r in self.conn.execute("PRAGMA foreign_key_list(grupo_cpds)").fetchall()}
        self.assertEqual(fks_grupo_cpds, {"grupos_clientes", "cpds"}, "grupo_cpds deve referenciar cpds, não cpd_variacoes")

    def test_cascade_somente_em_associacoes(self):
        def acoes(tabela):
            return {r["table"]: r["on_delete"] for r in self.conn.execute(f"PRAGMA foreign_key_list({tabela})").fetchall()}

        for tabela in ("perfil_permissoes", "usuario_permissoes", "cliente_grupos", "cliente_cpds", "grupo_cpds", "processo_fornecedores"):
            for ref_tabela, acao in acoes(tabela).items():
                self.assertEqual(acao, "CASCADE", f"{tabela}.{ref_tabela} deveria ser CASCADE (é tabela associativa)")

        for tabela, esperado in {
            "usuarios": {"areas": "RESTRICT", "perfis": "RESTRICT"},
            "cliente_aliases": {"clientes": "RESTRICT"},
            "cpd_variacoes": {"cpds": "RESTRICT"},
            "rota_etapas": {"rotas_processo": "RESTRICT", "processos": "RESTRICT", "fornecedores": "SET NULL"},
        }.items():
            self.assertEqual(acoes(tabela), esperado, f"Ações de FK inesperadas em {tabela}")

    def test_indices_unique_existem(self):
        def is_unique(tabela, coluna):
            for idx in self.conn.execute(f"PRAGMA index_list({tabela})").fetchall():
                info = self.conn.execute(f"PRAGMA index_info({idx['name']})").fetchall()
                if idx["unique"] and len(info) == 1 and info[0]["name"] == coluna:
                    return True
            return False

        self.assertTrue(is_unique("usuarios", "login"))
        self.assertTrue(is_unique("cpds", "codigo_pai"))
        self.assertTrue(is_unique("cpd_variacoes", "codigo_completo"))
        self.assertTrue(is_unique("niveis_urgencia", "codigo"))

    def test_pks_compostas_das_associacoes(self):
        for tabela, colunas in {
            "perfil_permissoes": {"perfil_id", "permissao_id"},
            "usuario_permissoes": {"usuario_id", "permissao_id"},
            "cliente_grupos": {"cliente_id", "grupo_id"},
            "cliente_cpds": {"cliente_id", "cpd_id"},
            "grupo_cpds": {"grupo_id", "cpd_id"},
            "processo_fornecedores": {"processo_id", "fornecedor_id"},
        }.items():
            pk_cols = {r["name"] for r in self.conn.execute(f"PRAGMA table_info({tabela})").fetchall() if r["pk"] > 0}
            self.assertEqual(pk_cols, colunas, f"PK composta inesperada em {tabela}")


# ---------------------------------------------------------------------------
# 3) Restrições de negócio (dados de teste, nunca reais)
# ---------------------------------------------------------------------------

class RestricoesTest(MigracaoV1V2TestCase):

    def setUp(self):
        self.db = self._nova_copia(f"restricoes_{self._testMethodName}")
        self._migrar(self.db)
        self.conn = sqlite3.connect(str(self.db))
        self.conn.execute("PRAGMA foreign_keys=ON")
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "INSERT INTO areas(nome, ativo, criado_em, atualizado_em) VALUES ('PCP-Teste',1,?,?)", (agora, agora)
        )
        self.conn.execute(
            "INSERT INTO perfis(nome, ativo, criado_em, atualizado_em) VALUES ('Perfil-Teste',1,?,?)", (agora, agora)
        )
        self.conn.commit()
        self.area_id = 1
        self.perfil_id = 1

    def tearDown(self):
        self.conn.close()

    def _inserir_usuario(self, login: str):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            """
            INSERT INTO usuarios
                (nome_completo, area_id, login, senha_hash, perfil_id, criado_em, atualizado_em)
            VALUES (?,?,?,?,?,?,?)
            """,
            (f"Usuário {login}", self.area_id, login, self.dbm.hash_senha("teste123"), self.perfil_id, agora, agora),
        )

    def test_login_nao_diferencia_maiusculas_minusculas(self):
        self._inserir_usuario("Maria")
        self.conn.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            self._inserir_usuario("maria")

    def test_senha_hash_obrigatorio(self):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO usuarios(nome_completo, area_id, login, senha_hash, perfil_id, criado_em, atualizado_em) "
                "VALUES ('Sem Senha', ?, 'semsenha', NULL, ?, ?, ?)",
                (self.area_id, self.perfil_id, agora, agora),
            )

    def test_defaults_de_usuario(self):
        self._inserir_usuario("defaulttest")
        self.conn.commit()
        row = self.conn.execute(
            "SELECT ativo, bloqueado, deve_trocar_senha, tentativas_falhas FROM usuarios WHERE login='defaulttest'"
        ).fetchone()
        self.assertEqual(row, (1, 0, 0, 0))

    def test_area_invalida_e_rejeitada(self):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO usuarios(nome_completo, area_id, login, senha_hash, perfil_id, criado_em, atualizado_em) "
                "VALUES ('X', 9999, 'xuser', 'h', ?, ?, ?)",
                (self.perfil_id, agora, agora),
            )

    def test_codigo_pai_unico(self):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute("INSERT INTO cpds(codigo_pai, ativo, criado_em, atualizado_em) VALUES ('04772',1,?,?)", (agora, agora))
        self.conn.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO cpds(codigo_pai, ativo, criado_em, atualizado_em) VALUES ('04772',1,?,?)", (agora, agora))

    def test_codigo_completo_unico(self):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute("INSERT INTO cpds(codigo_pai, ativo, criado_em, atualizado_em) VALUES ('04772',1,?,?)", (agora, agora))
        cpd_id = self.conn.execute("SELECT id FROM cpds WHERE codigo_pai='04772'").fetchone()[0]
        self.conn.execute(
            "INSERT INTO cpd_variacoes(cpd_id, codigo_completo, extensao, ativo, criado_em, atualizado_em) "
            "VALUES (?, '04772.1', '1', 1, ?, ?)", (cpd_id, agora, agora),
        )
        self.conn.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO cpd_variacoes(cpd_id, codigo_completo, extensao, ativo, criado_em, atualizado_em) "
                "VALUES (?, '04772.1', '1', 1, ?, ?)", (cpd_id, agora, agora),
            )

    def test_associacao_duplicada_e_rejeitada(self):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute("INSERT INTO clientes(nome, ativo, criado_em, atualizado_em) VALUES ('Cliente Teste',1,?,?)", (agora, agora))
        cliente_id = self.conn.execute("SELECT id FROM clientes WHERE nome='Cliente Teste'").fetchone()[0]
        grupo_id = self.conn.execute("SELECT id FROM grupos_clientes WHERE nome='Honda'").fetchone()[0]
        self.conn.execute("INSERT INTO cliente_grupos(cliente_id, grupo_id, criado_em) VALUES (?,?,?)", (cliente_id, grupo_id, agora))
        self.conn.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO cliente_grupos(cliente_id, grupo_id, criado_em) VALUES (?,?,?)", (cliente_id, grupo_id, agora))

    def test_processo_interno_e_externo_nao_podem_ser_ambos_falsos(self):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO processos(nome, interno, externo, criado_em, atualizado_em) VALUES ('Nulo',0,0,?,?)",
                (agora, agora),
            )

    def test_processo_pode_ser_interno_e_externo_ao_mesmo_tempo(self):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Não é proibido: um processo pode ser feito tanto internamente quanto terceirizado.
        self.conn.execute(
            "INSERT INTO processos(nome, interno, externo, criado_em, atualizado_em) VALUES ('Flexivel',1,1,?,?)",
            (agora, agora),
        )
        self.conn.commit()

    def test_regra_urgencia_dias_minimos_maior_que_maximos_e_rejeitada(self):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nivel_id = self.conn.execute("SELECT id FROM niveis_urgencia WHERE codigo='NORMAL'").fetchone()[0]
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO regras_urgencia(nome, dias_minimos, dias_maximos, nivel_urgencia_id, criado_em, atualizado_em) "
                "VALUES ('Invalida', 10, 5, ?, ?, ?)",
                (nivel_id, agora, agora),
            )

    def test_regra_urgencia_aceita_dias_nulos(self):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nivel_id = self.conn.execute("SELECT id FROM niveis_urgencia WHERE codigo='NORMAL'").fetchone()[0]
        self.conn.execute(
            "INSERT INTO regras_urgencia(nome, dias_minimos, dias_maximos, nivel_urgencia_id, criado_em, atualizado_em) "
            "VALUES ('SemLimite', NULL, NULL, ?, ?, ?)",
            (nivel_id, agora, agora),
        )
        self.conn.commit()

    def test_rota_etapa_fornecedor_id_e_opcional(self):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute("INSERT INTO rotas_processo(nome, ativo, criado_em, atualizado_em) VALUES ('Rota',1,?,?)", (agora, agora))
        rota_id = self.conn.execute("SELECT id FROM rotas_processo WHERE nome='Rota'").fetchone()[0]
        self.conn.execute(
            "INSERT INTO processos(nome, interno, externo, criado_em, atualizado_em) VALUES ('P1',1,0,?,?)", (agora, agora)
        )
        processo_id = self.conn.execute("SELECT id FROM processos WHERE nome='P1'").fetchone()[0]
        self.conn.execute(
            "INSERT INTO rota_etapas(rota_id, processo_id, fornecedor_id, ordem, criado_em) VALUES (?,?,NULL,1,?)",
            (rota_id, processo_id, agora),
        )
        self.conn.commit()


# ---------------------------------------------------------------------------
# 4) Seeds idempotentes (grupos padrão, níveis de urgência)
# ---------------------------------------------------------------------------

class SeedsTest(MigracaoV1V2TestCase):

    def test_grupos_honda_e_diversos_inseridos_uma_unica_vez(self):
        db = self._nova_copia("seed_grupos")
        self._migrar(db)
        with sqlite3.connect(str(db)) as c:
            nomes = [r[0] for r in c.execute("SELECT nome FROM grupos_clientes ORDER BY nome").fetchall()]
        self.assertEqual(nomes, ["Diversos", "Honda"])

    def test_cinco_niveis_de_urgencia_inseridos_uma_unica_vez(self):
        db = self._nova_copia("seed_niveis")
        self._migrar(db)
        with sqlite3.connect(str(db)) as c:
            codigos = [r[0] for r in c.execute("SELECT codigo FROM niveis_urgencia ORDER BY prioridade").fetchall()]
        self.assertEqual(codigos, ["ATRASADO", "CRITICO", "ALTO", "ATENCAO", "NORMAL"])

    def test_segunda_execucao_da_migracao_e_no_op(self):
        db = self._nova_copia("segunda_execucao")
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            self.dbm.migrar_v1_para_v2(c)
            c.commit()
            total_tabelas_1 = c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
            grupos_1 = c.execute("SELECT COUNT(*) FROM grupos_clientes").fetchone()[0]
            niveis_1 = c.execute("SELECT COUNT(*) FROM niveis_urgencia").fetchone()[0]

            self.dbm.migrar_v1_para_v2(c)  # roda de novo, sem levantar exceção
            c.commit()
            total_tabelas_2 = c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
            grupos_2 = c.execute("SELECT COUNT(*) FROM grupos_clientes").fetchone()[0]
            niveis_2 = c.execute("SELECT COUNT(*) FROM niveis_urgencia").fetchone()[0]

        self.assertEqual(total_tabelas_1, total_tabelas_2)
        self.assertEqual(grupos_1, grupos_2, "Segunda execução duplicou grupos_clientes")
        self.assertEqual(niveis_1, niveis_2, "Segunda execução duplicou niveis_urgencia")

    def test_run_migrations_segunda_chamada_nao_reaplica(self):
        # Desde que migrar_v2_para_v3 também está registrada, run_migrations()
        # numa cópia v1 encadeia até a versão mais recente (LATEST_SCHEMA_VERSION);
        # o que este teste verifica é que uma segunda chamada não reaplica nada.
        db = self._nova_copia("run_migrations_segunda_chamada")
        primeiro = self._migrar(db, self.tmp_dir / "backups_seg1")
        segundo = self._migrar(db, self.tmp_dir / "backups_seg2")
        self.assertEqual(primeiro["versao_final"], self.dbm.LATEST_SCHEMA_VERSION)
        self.assertEqual(segundo["migracoes_aplicadas"], [], "run_migrations não deveria reaplicar migrações já aplicadas")
        self.assertEqual(segundo["versao_final"], self.dbm.LATEST_SCHEMA_VERSION)


# ---------------------------------------------------------------------------
# 5) Falha simulada -> rollback total, schema_version intacta
# ---------------------------------------------------------------------------

class RollbackTest(MigracaoV1V2TestCase):

    def test_falha_na_migracao_gera_rollback_total_e_versao_nao_muda(self):
        db = self._nova_copia("falha_rollback")
        original = self.dbm.MIGRATIONS[1]

        def migracao_quebrada(c):
            c.execute("CREATE TABLE marcador_de_falha (id INTEGER)")
            raise RuntimeError("falha simulada proposital")

        self.dbm.MIGRATIONS[1] = migracao_quebrada
        try:
            resultado = self._migrar(db, self.tmp_dir / "backups_falha")
        finally:
            self.dbm.MIGRATIONS[1] = original

        self.assertEqual(resultado["versao_final"], 1, "schema_version não pode mudar quando a migração falha")
        self.assertEqual(resultado["migracoes_aplicadas"], [])

        with sqlite3.connect(str(db)) as c:
            self.assertEqual(self.dbm.get_schema_version(c), 1)
            existe_marcador = c.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='marcador_de_falha'"
            ).fetchone()[0]
        self.assertEqual(existe_marcador, 0, "Rollback deveria ter desfeito a tabela criada pela migração quebrada")

    def test_backup_pre_migracao_e_criado_e_valido(self):
        db = self._nova_copia("backup_pre_migracao")
        backup_dir = self.tmp_dir / "backups_validacao"
        self._migrar(db, backup_dir)
        arquivos = list(backup_dir.glob("pcp_pre_migracao_v1_para_v2_*.sqlite3"))
        self.assertEqual(len(arquivos), 1, "Deveria existir exatamente um backup pré-migração v1->v2")
        self.assertEqual(self.dbm.verificar_integridade(arquivos[0]), "ok")


# ---------------------------------------------------------------------------
# 6) Dados antigos preservados + integridade pós-migração
# ---------------------------------------------------------------------------

class DadosAntigosEIntegridadeTest(MigracaoV1V2TestCase):

    def test_contagens_das_tabelas_antigas_nao_mudam(self):
        db = self._nova_copia("contagens_antigas")
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(str(db)) as c:
            c.execute("INSERT INTO orders(id, payload, updated_at) VALUES ('o1','{}',?)", (agora,))
            c.execute("INSERT INTO sections(id, payload, updated_at) VALUES ('s1','{}',?)", (agora,))
            c.execute("INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES ('TESTE-9999','Teste',?)", (agora,))
            c.execute(
                "INSERT INTO audit_log(action, entity, entity_id, payload, created_at) VALUES ('create','order','o1','{}',?)",
                (agora,),
            )
            c.commit()

        antes = self.dbm.gerar_relatorio_validacao(db)
        self._migrar(db)
        depois = self.dbm.gerar_relatorio_validacao(db)

        for campo in ("total_pedidos", "total_datas_secoes", "total_registros_auditoria", "total_cpds_cadastrados"):
            self.assertEqual(antes[campo], depois[campo], f"Total mudou em '{campo}'")

    def test_integrity_check_ok_apos_migracao(self):
        db = self._nova_copia("integrity_ok")
        self._migrar(db)
        self.assertEqual(self.dbm.verificar_integridade(db), "ok")

    def test_foreign_key_check_sem_violacoes_apos_migracao(self):
        db = self._nova_copia("fk_check_ok")
        self._migrar(db)
        with sqlite3.connect(str(db)) as c:
            c.execute("PRAGMA foreign_keys=ON")
            violacoes = c.execute("PRAGMA foreign_key_check").fetchall()
        self.assertEqual(violacoes, [], f"foreign_key_check encontrou violações: {violacoes}")


# ---------------------------------------------------------------------------
# 7) normalizar_cpd()
# ---------------------------------------------------------------------------

class NormalizarCpdTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for nome in ("db_manutencao",):
            sys.modules.pop(nome, None)
        cls.dbm = importlib.import_module("db_manutencao")

    def test_codigo_sem_extensao(self):
        r = self.dbm.normalizar_cpd("04772")
        self.assertEqual(r, {"codigo_original": "04772", "codigo_pai": "04772", "extensao": None})

    def test_codigo_com_extensao_um_digito(self):
        r = self.dbm.normalizar_cpd("04772.1")
        self.assertEqual(r, {"codigo_original": "04772.1", "codigo_pai": "04772", "extensao": "1"})
        self.assertIsInstance(r["extensao"], str)

    def test_codigo_com_extensao_dois_digitos(self):
        r = self.dbm.normalizar_cpd("04772.10")
        self.assertEqual(r["codigo_pai"], "04772")
        self.assertEqual(r["extensao"], "10")

    def test_extensao_alfabetica_nao_e_reconhecida(self):
        r = self.dbm.normalizar_cpd("01234.A")
        self.assertEqual(r["codigo_pai"], "01234.A")
        self.assertIsNone(r["extensao"])

    def test_pai_alfabetico_com_extensao_numerica(self):
        r = self.dbm.normalizar_cpd("ABC.1")
        self.assertEqual(r["codigo_pai"], "ABC")
        self.assertEqual(r["extensao"], "1")

    def test_usa_o_ultimo_ponto_para_separar(self):
        r = self.dbm.normalizar_cpd("A.B.25")
        self.assertEqual(r["codigo_pai"], "A.B")
        self.assertEqual(r["extensao"], "25")

    def test_espacos_antes_e_depois_sao_removidos(self):
        r = self.dbm.normalizar_cpd("  04772.1  ")
        self.assertEqual(r["codigo_original"], "04772.1")
        self.assertEqual(r["codigo_pai"], "04772")
        self.assertEqual(r["extensao"], "1")

    def test_string_vazia(self):
        r = self.dbm.normalizar_cpd("")
        self.assertEqual(r, {"codigo_original": "", "codigo_pai": "", "extensao": None})

    def test_none(self):
        r = self.dbm.normalizar_cpd(None)
        self.assertEqual(r, {"codigo_original": "", "codigo_pai": "", "extensao": None})

    def test_apenas_ponto_e_digito(self):
        r = self.dbm.normalizar_cpd(".1")
        self.assertEqual(r["codigo_pai"], ".1")
        self.assertIsNone(r["extensao"])

    def test_ponto_final_sem_digitos(self):
        r = self.dbm.normalizar_cpd("04772.")
        self.assertEqual(r["codigo_pai"], "04772.")
        self.assertIsNone(r["extensao"])

    def test_extensao_com_zero_a_esquerda_preservado(self):
        r = self.dbm.normalizar_cpd("04772.01")
        self.assertEqual(r["codigo_pai"], "04772")
        self.assertEqual(r["extensao"], "01")

    def test_nunca_converte_pai_ou_extensao_para_numero(self):
        r = self.dbm.normalizar_cpd("00100.007")
        self.assertEqual(r["codigo_pai"], "00100")
        self.assertEqual(r["extensao"], "007")
        self.assertIsInstance(r["codigo_pai"], str)
        self.assertIsInstance(r["extensao"], str)


# ---------------------------------------------------------------------------
# 8) hash_senha() / verificar_senha()
# ---------------------------------------------------------------------------

class SenhaTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for nome in ("db_manutencao",):
            sys.modules.pop(nome, None)
        cls.dbm = importlib.import_module("db_manutencao")

    def test_hash_nao_contem_a_senha_original(self):
        h = self.dbm.hash_senha("MinhaSenhaSecreta123")
        self.assertNotIn("MinhaSenhaSecreta123", h)
        self.assertTrue(h.startswith("pbkdf2_sha256$"))

    def test_verificar_senha_correta(self):
        h = self.dbm.hash_senha("correta123")
        self.assertTrue(self.dbm.verificar_senha("correta123", h))

    def test_verificar_senha_incorreta(self):
        h = self.dbm.hash_senha("correta123")
        self.assertFalse(self.dbm.verificar_senha("errada456", h))

    def test_hash_senha_vazia_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.dbm.hash_senha("")


# ---------------------------------------------------------------------------
# 9) Gatilho de migração automática ao iniciar o servidor
# ---------------------------------------------------------------------------

class GatilhoAutomaticoTest(MigracaoV1V2TestCase):

    def test_default_e_falso_sem_variavel_de_ambiente(self):
        os.environ.pop("PCP_APLICAR_MIGRACOES", None)
        self.assertFalse(self.servidor.deve_aplicar_migracoes_automaticamente())

    def test_default_e_falso_com_qualquer_outro_valor(self):
        os.environ["PCP_APLICAR_MIGRACOES"] = "true"
        try:
            self.assertFalse(self.servidor.deve_aplicar_migracoes_automaticamente())
        finally:
            os.environ.pop("PCP_APLICAR_MIGRACOES", None)

    def test_verdadeiro_somente_com_valor_1(self):
        os.environ["PCP_APLICAR_MIGRACOES"] = "1"
        try:
            self.assertTrue(self.servidor.deve_aplicar_migracoes_automaticamente())
        finally:
            os.environ.pop("PCP_APLICAR_MIGRACOES", None)


if __name__ == "__main__":
    unittest.main()
