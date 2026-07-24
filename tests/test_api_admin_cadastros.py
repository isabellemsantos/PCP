"""Testes das APIs somente-leitura /api/admin/* (Clientes/CPDs/Arruelas/
Itens/Pendências) da tela administrativa /cadastros.

Regra oficial atual: CPDs não têm variações. "12345", "12345.1", "12345/1" e
"12345.01" são só formas históricas do MESMO CPD ("12345", 5 dígitos) --
cpd_variacoes segue existindo no schema (migração v1->v2, já aplicada no
banco real) só como estrutura órfã, nunca populada nem lida aqui.

Tudo fictício, tudo em cópias temporárias via sqlite3.Connection.backup() --
nenhum teste aqui toca o pcp.sqlite3 real. A base compartilhada (setUpClass)
já nasce em schema_version=5 (v1->v2->v3->v4->v5 aplicadas manualmente, sem
depender do servidor real ou de PCP_APLICAR_MIGRACOES).
"""

from __future__ import annotations

import importlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class ApiAdminCadastrosTestCase(unittest.TestCase):
    tmp_dir: Path
    db_base: Path
    servidor = None
    dbm = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_api_admin_"))
        cls.db_base = cls.tmp_dir / "base.sqlite3"

        os.environ["PCP_DB_FILE"] = str(cls.db_base)
        os.environ["PCP_EXCEL_FILE"] = str(cls.tmp_dir / "dados_teste.xlsx")
        os.environ["PCP_EXCEL_PENDING_FILE"] = str(cls.tmp_dir / "dados_pendente_teste.xlsx")
        os.environ["PCP_LOG_FILE"] = str(cls.tmp_dir / "servidor_teste.log")
        os.environ["PCP_BACKUP_DIR"] = str(cls.tmp_dir / "backups")
        os.environ["PCP_HABILITAR_CADASTROS_NOVOS"] = "1"

        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        cls.servidor = importlib.import_module("servidor_pcp")
        cls.dbm = importlib.import_module("db_manutencao")
        cls.servidor.init_db()

        agora = "2026-07-24 10:00:00"
        with cls.servidor.lock, cls.servidor.conn() as c:
            cls.dbm.migrar_v1_para_v2(c)
            cls.dbm.migrar_v2_para_v3(c)
            cls.dbm.migrar_v3_para_v4(c)
            cls.dbm.migrar_v4_para_v5(c)
            cls.dbm.set_schema_version(c, 5)

            grupo_id = c.execute("SELECT id FROM grupos_clientes WHERE nome='Honda'").fetchone()[0]

            c.execute(
                "INSERT INTO clientes(nome, ativo, criado_em, atualizado_em) VALUES (?,1,?,?)",
                ("CLIENTE FICTICIO ALFA", agora, agora),
            )
            cls.cliente_alfa_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]
            c.execute(
                "INSERT INTO cliente_aliases(cliente_id, alias, ativo, criado_em) VALUES (?,?,1,?)",
                (cls.cliente_alfa_id, "ALFA LTDA", agora),
            )
            c.execute(
                "INSERT INTO cliente_grupos(cliente_id, grupo_id, criado_em) VALUES (?,?,?)",
                (cls.cliente_alfa_id, grupo_id, agora),
            )

            c.execute(
                "INSERT INTO clientes(nome, ativo, criado_em, atualizado_em) VALUES (?,1,?,?)",
                ("CLIENTE FICTICIO GAMA", agora, agora),
            )
            cls.cliente_gama_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]

            c.execute(
                "INSERT INTO clientes(nome, ativo, criado_em, atualizado_em, desativado_em) VALUES (?,0,?,?,?)",
                ("CLIENTE FICTICIO BETA INATIVO", agora, agora, agora),
            )
            cls.cliente_beta_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]

            # CPD "12345" -- colapso de extensões históricas: as fontes
            # "12345", "12345.1" e "12345/1" (já normalizada p/ "12345.1" na
            # análise, mas o texto ORIGINAL de cada linha de
            # cpd_descricoes_fontes é preservado) resolvem pro MESMO cpd_id.
            # Nenhuma linha em cpd_variacoes é criada.
            c.execute(
                "INSERT INTO cpds(codigo_pai, descricao_padrao, ativo, criado_em, atualizado_em) VALUES ('12345','Peça fictícia canônica',1,?,?)",
                (agora, agora),
            )
            cls.cpd_colapsado_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]
            c.execute(
                "INSERT INTO cliente_cpds(cliente_id, cpd_id, criado_em) VALUES (?,?,?)",
                (cls.cliente_alfa_id, cls.cpd_colapsado_id, agora),
            )
            # Cliente ligado só pela extensão histórica "12345.1" -- também
            # tem que ficar consolidado no mesmo CPD-base, deduplicado.
            c.execute(
                "INSERT INTO cliente_cpds(cliente_id, cpd_id, criado_em) VALUES (?,?,?)",
                (cls.cliente_gama_id, cls.cpd_colapsado_id, agora),
            )
            c.execute(
                "INSERT INTO grupo_cpds(grupo_id, cpd_id, criado_em) VALUES (?,?,?)",
                (grupo_id, cls.cpd_colapsado_id, agora),
            )
            c.execute(
                "INSERT INTO cpd_descricoes_fontes(cpd_id, cpd_variacao_id, codigo_completo, descricao, fonte, descricao_canonica, criado_em) "
                "VALUES (?,NULL,?,?,?,1,?)",
                (cls.cpd_colapsado_id, "12345", "Peça fictícia canônica", "LISTA_OFICIAL", agora),
            )
            c.execute(
                "INSERT INTO cpd_descricoes_fontes(cpd_id, cpd_variacao_id, codigo_completo, descricao, fonte, descricao_canonica, criado_em) "
                "VALUES (?,NULL,?,?,?,0,?)",
                (cls.cpd_colapsado_id, "12345.1", "Peça fictícia variante histórica", "MANUAL_CPD", agora),
            )

            # Segundo CPD, sem histórico de extensão nenhuma.
            c.execute(
                "INSERT INTO cpds(codigo_pai, descricao_padrao, ativo, criado_em, atualizado_em) VALUES ('99999','Peça fictícia simples',1,?,?)",
                (agora, agora),
            )
            cls.cpd_simples_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]
            c.execute(
                "INSERT INTO cpd_descricoes_fontes(cpd_id, cpd_variacao_id, codigo_completo, descricao, fonte, descricao_canonica, criado_em) "
                "VALUES (?,NULL,?,?,?,1,?)",
                (cls.cpd_simples_id, "99999", "Peça fictícia simples", "LISTA_OFICIAL", agora),
            )

            # Terceiro CPD, sem nenhuma pendência -- usado pra testar o
            # filtro possui_pendencia nos dois sentidos.
            c.execute(
                "INSERT INTO cpds(codigo_pai, descricao_padrao, ativo, criado_em, atualizado_em) VALUES ('11111','Peça fictícia sem pendência',1,?,?)",
                (agora, agora),
            )
            cls.cpd_sem_pendencia_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]
            c.execute(
                "INSERT INTO cpd_descricoes_fontes(cpd_id, cpd_variacao_id, codigo_completo, descricao, fonte, descricao_canonica, criado_em) "
                "VALUES (?,NULL,?,?,?,1,?)",
                (cls.cpd_sem_pendencia_id, "11111", "Peça fictícia sem pendência", "LISTA_OFICIAL", agora),
            )

            # Pendências de tipos diferentes para agregação por tipo.
            for tipo, codigo, cpd_id in (
                ("CONFLITO_DESCRICAO", "12345", cls.cpd_colapsado_id),
                ("CONFLITO_DESCRICAO", "99999", cls.cpd_simples_id),
                ("CODIGO_INVALIDO", "00ABC", None),
            ):
                c.execute(
                    "INSERT INTO cpd_pendencias_revisao(cpd_id, cpd_variacao_id, codigo_completo, tipo, nivel_confianca, detalhes_json, status, criado_em) "
                    "VALUES (?,NULL,?,?,?,?,?,?)",
                    (cpd_id, codigo, tipo, "media", json.dumps({"motivo": "teste"}), "PENDENTE", agora),
                )
            cls.pendencia_id = c.execute("SELECT id FROM cpd_pendencias_revisao WHERE codigo_completo='12345'").fetchone()[0]
            # Uma pendência já resolvida, para não contar como "aberta".
            c.execute(
                "INSERT INTO cpd_pendencias_revisao(cpd_id, cpd_variacao_id, codigo_completo, tipo, nivel_confianca, detalhes_json, status, criado_em, resolvido_em) "
                "VALUES (?,NULL,?,?,?,?,?,?,?)",
                (cls.cpd_colapsado_id, "12345", "PAI_AUSENTE", "alta", json.dumps({}), "RESOLVIDO", agora, agora),
            )

            # Pendência com detalhes_json malformado -- não pode derrubar a API.
            c.execute(
                "INSERT INTO cpd_pendencias_revisao(cpd_id, cpd_variacao_id, codigo_completo, tipo, nivel_confianca, detalhes_json, status, criado_em) "
                "VALUES (NULL,NULL,?,?,?,?,?,?)",
                ("77777", "CODIGO_INVALIDO", "baixa", "{isso nao e json valido", "PENDENTE", agora),
            )
            cls.pendencia_json_invalido_id = c.execute(
                "SELECT id FROM cpd_pendencias_revisao WHERE codigo_completo='77777'"
            ).fetchone()[0]

            # Arruela (categoria separada de CPD -- nunca aparece como CPD).
            c.execute(
                "INSERT INTO arruelas(codigo, descricao_padrao, ativo, criado_em, atualizado_em) VALUES ('ZZ-090','Arruela fictícia',1,?,?)",
                (agora, agora),
            )
            cls.arruela_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]
            c.execute(
                "INSERT INTO cliente_arruelas(cliente_id, arruela_id, origem, criado_em) VALUES (?,?,?,?)",
                (cls.cliente_alfa_id, cls.arruela_id, "LISTA_OFICIAL", agora),
            )
            c.execute(
                "INSERT INTO grupo_arruelas(grupo_id, arruela_id, criado_em) VALUES (?,?,?)",
                (grupo_id, cls.arruela_id, agora),
            )

            # Clientes/CPDs extras só para exercitar paginação (>25 registros).
            for i in range(30):
                c.execute(
                    "INSERT INTO clientes(nome, ativo, criado_em, atualizado_em) VALUES (?,1,?,?)",
                    (f"CLIENTE FICTICIO PAGINACAO {i:03d}", agora, agora),
                )

            c.commit()

    @classmethod
    def tearDownClass(cls):
        for var in (
            "PCP_DB_FILE", "PCP_EXCEL_FILE", "PCP_EXCEL_PENDING_FILE",
            "PCP_LOG_FILE", "PCP_BACKUP_DIR", "PCP_HABILITAR_CADASTROS_NOVOS",
        ):
            os.environ.pop(var, None)
        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def setUp(self):
        self.db = self.tmp_dir / f"{self._testMethodName}.sqlite3"
        origem = sqlite3.connect(str(self.db_base))
        destino = sqlite3.connect(str(self.db))
        try:
            with destino:
                origem.backup(destino)
        finally:
            destino.close()
            origem.close()

    def _cliente_ligado(self):
        return patch.object(self.servidor, "DB_FILE", self.db)

    def _get(self, url):
        with self._cliente_ligado():
            cliente = self.servidor.app.test_client()
            resp = cliente.get(url)
            return resp.status_code, resp.get_json()

    def _contagem_tabela(self, tabela):
        c = sqlite3.connect(str(self.db))
        try:
            return c.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        finally:
            c.close()

    # ------------------------------------------------------------------
    # Feature flag e gate de schema
    # ------------------------------------------------------------------

    def test_flag_desligada_bloqueia_api_com_404(self):
        valor_original = os.environ.pop("PCP_HABILITAR_CADASTROS_NOVOS", None)
        try:
            for nome in ("servidor_pcp", "db_manutencao"):
                sys.modules.pop(nome, None)
            servidor_sem_flag = importlib.import_module("servidor_pcp")
            with patch.object(servidor_sem_flag, "DB_FILE", self.db):
                cliente = servidor_sem_flag.app.test_client()
                resp = cliente.get("/api/admin/resumo")
                self.assertEqual(resp.status_code, 404)
                resp_pagina = cliente.get("/cadastros")
                self.assertEqual(resp_pagina.status_code, 404)
                resp_state = cliente.get("/api/state")
                self.assertEqual(resp_state.status_code, 200, "/api/state deve continuar respondendo com a flag desligada")
        finally:
            if valor_original is not None:
                os.environ["PCP_HABILITAR_CADASTROS_NOVOS"] = valor_original
            for nome in ("servidor_pcp", "db_manutencao"):
                sys.modules.pop(nome, None)
            self.__class__.servidor = importlib.import_module("servidor_pcp")
            self.__class__.dbm = importlib.import_module("db_manutencao")

    def test_schema_v3_retorna_503_controlado_nas_novas_apis(self):
        c = sqlite3.connect(str(self.db))
        try:
            c.execute("UPDATE meta SET value='3' WHERE key='schema_version'")
            c.commit()
        finally:
            c.close()
        status, dados = self._get("/api/admin/resumo")
        self.assertEqual(status, 503)
        self.assertFalse(dados["ok"])
        self.assertEqual(dados["codigo"], "CADASTROS_NOVOS_INDISPONIVEIS")
        self.assertNotIn("Traceback", json.dumps(dados))

    def test_schema_v3_api_state_continua_respondendo(self):
        c = sqlite3.connect(str(self.db))
        try:
            c.execute("UPDATE meta SET value='3' WHERE key='schema_version'")
            c.commit()
        finally:
            c.close()
        status, dados = self._get("/api/state")
        self.assertEqual(status, 200)
        self.assertIn("orders", dados)

    def test_schema_v3_continua_iniciando_normalmente(self):
        # init_db()/o servidor não deve falhar com o banco ainda em v3 --
        # já é exercitado implicitamente por toda a suíte (setUp faz cópias
        # do banco em v5, mas o servidor real de produção segue em v3 e
        # continua respondendo /api/state normalmente, ver teste acima).
        c = sqlite3.connect(str(self.db))
        try:
            c.execute("UPDATE meta SET value='3' WHERE key='schema_version'")
            c.commit()
        finally:
            c.close()
        with self._cliente_ligado():
            cliente = self.servidor.app.test_client()
            resp = cliente.get("/")
            self.assertEqual(resp.status_code, 200)

    def test_schema_v5_resumo_disponivel(self):
        status, dados = self._get("/api/admin/resumo")
        self.assertEqual(status, 200)
        self.assertTrue(dados["ok"])
        self.assertIn("total_clientes_ativos", dados)

    # ------------------------------------------------------------------
    # Resumo
    # ------------------------------------------------------------------

    def test_resumo_nao_retorna_mais_variacoes_ou_codigos_completos(self):
        status, dados = self._get("/api/admin/resumo")
        self.assertEqual(status, 200)
        self.assertNotIn("total_variacoes", dados)
        self.assertNotIn("total_codigos_completos", dados)

    def test_resumo_retorna_total_de_itens_e_cpds(self):
        status, dados = self._get("/api/admin/resumo")
        self.assertEqual(status, 200)
        self.assertIn("total_cpds", dados)
        self.assertIn("total_arruelas", dados)
        self.assertEqual(dados["total_itens"], dados["total_cpds"] + dados["total_arruelas"])
        self.assertEqual(dados["total_cpds"], 3)  # colapsado + simples + sem_pendencia, nunca mais por causa da extensão

    def test_resumo_conta_pendencias_abertas_por_tipo(self):
        status, dados = self._get("/api/admin/resumo")
        self.assertEqual(status, 200)
        self.assertEqual(dados["pendencias_por_tipo"].get("CONFLITO_DESCRICAO"), 2)
        self.assertEqual(dados["pendencias_por_tipo"].get("CODIGO_INVALIDO"), 2)
        self.assertNotIn("PAI_AUSENTE", dados["pendencias_por_tipo"], "Pendência já resolvida não deve contar como aberta")

    def test_resumo_conta_clientes_ativos_e_inativos(self):
        status, dados = self._get("/api/admin/resumo")
        self.assertGreaterEqual(dados["total_clientes_ativos"], 32)  # alfa + gama + 30 de paginação
        self.assertGreaterEqual(dados["total_clientes_inativos"], 1)

    # ------------------------------------------------------------------
    # Paginação
    # ------------------------------------------------------------------

    def test_paginacao_padrao_25_por_pagina(self):
        status, dados = self._get("/api/admin/clientes")
        self.assertEqual(status, 200)
        self.assertEqual(dados["paginacao"]["por_pagina"], 25)
        self.assertEqual(len(dados["itens"]), 25)
        self.assertGreaterEqual(dados["paginacao"]["total_paginas"], 2)

    def test_paginacao_segunda_pagina_traz_itens_diferentes(self):
        _, pagina1 = self._get("/api/admin/clientes?pagina=1")
        _, pagina2 = self._get("/api/admin/clientes?pagina=2")
        ids1 = {i["id"] for i in pagina1["itens"]}
        ids2 = {i["id"] for i in pagina2["itens"]}
        self.assertEqual(ids1 & ids2, set())

    def test_paginacao_limite_maximo_100(self):
        status, dados = self._get("/api/admin/clientes?por_pagina=9999")
        self.assertEqual(status, 200)
        self.assertEqual(dados["paginacao"]["por_pagina"], 100)

    def test_pagina_muito_alem_do_total_retorna_vazio_sem_erro(self):
        status, dados = self._get("/api/admin/clientes?pagina=99999")
        self.assertEqual(status, 200)
        self.assertEqual(dados["itens"], [])
        self.assertEqual(dados["paginacao"]["pagina"], 99999)

    def test_por_pagina_zero_cai_no_padrao(self):
        status, dados = self._get("/api/admin/clientes?por_pagina=0")
        self.assertEqual(status, 200)
        self.assertEqual(dados["paginacao"]["por_pagina"], 25)

    def test_por_pagina_negativo_cai_no_padrao(self):
        status, dados = self._get("/api/admin/clientes?por_pagina=-10")
        self.assertEqual(status, 200)
        self.assertEqual(dados["paginacao"]["por_pagina"], 25)

    def test_por_pagina_acima_do_maximo_e_limitada_a_100(self):
        status, dados = self._get("/api/admin/clientes?por_pagina=99999")
        self.assertEqual(status, 200)
        self.assertEqual(dados["paginacao"]["por_pagina"], 100)

    # ------------------------------------------------------------------
    # Clientes
    # ------------------------------------------------------------------

    def test_busca_cliente_por_nome(self):
        status, dados = self._get("/api/admin/clientes?busca=ALFA")
        self.assertEqual(status, 200)
        nomes = {i["nome"] for i in dados["itens"]}
        self.assertIn("CLIENTE FICTICIO ALFA", nomes)

    def test_busca_cliente_por_alias(self):
        status, dados = self._get("/api/admin/clientes?busca=ALFA%20LTDA")
        self.assertEqual(status, 200)
        nomes = {i["nome"] for i in dados["itens"]}
        self.assertIn("CLIENTE FICTICIO ALFA", nomes)

    def test_filtro_grupo_cliente(self):
        status, dados = self._get("/api/admin/clientes?grupo=Honda")
        self.assertEqual(status, 200)
        nomes = {i["nome"] for i in dados["itens"]}
        self.assertIn("CLIENTE FICTICIO ALFA", nomes)
        self.assertNotIn("CLIENTE FICTICIO BETA INATIVO", nomes)

    def test_filtro_status_cliente_inativo(self):
        status, dados = self._get("/api/admin/clientes?ativo=0")
        self.assertEqual(status, 200)
        self.assertTrue(all(not i["ativo"] for i in dados["itens"]))
        nomes = {i["nome"] for i in dados["itens"]}
        self.assertIn("CLIENTE FICTICIO BETA INATIVO", nomes)

    def test_filtro_combinado_grupo_e_status(self):
        status, dados = self._get("/api/admin/clientes?grupo=Honda&ativo=1")
        self.assertEqual(status, 200)
        nomes = {i["nome"] for i in dados["itens"]}
        self.assertIn("CLIENTE FICTICIO ALFA", nomes)
        self.assertTrue(all(i["ativo"] for i in dados["itens"]))

    def test_detalhe_cliente_traz_cpds_e_arruelas_vinculados(self):
        status, dados = self._get(f"/api/admin/clientes/{self.cliente_alfa_id}")
        self.assertEqual(status, 200)
        self.assertEqual({c["codigo"] for c in dados["cpds"]}, {"12345"})
        self.assertEqual({a["codigo"] for a in dados["arruelas"]}, {"ZZ-090"})
        self.assertIn("ALFA LTDA", dados["aliases"])

    def test_detalhe_cliente_inexistente_404(self):
        status, dados = self._get("/api/admin/clientes/999999")
        self.assertEqual(status, 404)
        self.assertEqual(dados["codigo"], "NAO_ENCONTRADO")

    # ------------------------------------------------------------------
    # CPDs -- regra sem variações
    # ------------------------------------------------------------------

    def test_442_vira_00442(self):
        from scripts.migrar_clientes_cpds import normalizar_cpd_cinco_digitos
        self.assertEqual(normalizar_cpd_cinco_digitos("442")["codigo_pai"], "00442")

    def test_04772_ponto_1_vira_cpd_04772(self):
        from scripts.migrar_clientes_cpds import normalizar_cpd_cinco_digitos
        self.assertEqual(normalizar_cpd_cinco_digitos("04772.1")["codigo_pai"], "04772")

    def test_04772_barra_1_vira_cpd_04772(self):
        from scripts.migrar_clientes_cpds import normalizar_cpd_cinco_digitos
        self.assertEqual(normalizar_cpd_cinco_digitos("04772/1")["codigo_pai"], "04772")

    def test_busca_cpd_por_codigo(self):
        status, dados = self._get("/api/admin/cpds?busca=12345")
        self.assertEqual(status, 200)
        codigos = {i["codigo"] for i in dados["itens"]}
        self.assertIn("12345", codigos)

    def test_busca_cpd_por_descricao(self):
        status, dados = self._get("/api/admin/cpds?busca=fict%C3%ADcia%20can%C3%B4nica")
        self.assertEqual(status, 200)
        codigos = {i["codigo"] for i in dados["itens"]}
        self.assertIn("12345", codigos)

    def test_busca_com_acento_e_sem_acento_dao_o_mesmo_resultado(self):
        _, com_acento = self._get("/api/admin/cpds?busca=fict%C3%ADcia")
        _, sem_acento = self._get("/api/admin/cpds?busca=ficticia")
        ids_com = {i["id"] for i in com_acento["itens"]}
        ids_sem = {i["id"] for i in sem_acento["itens"]}
        self.assertEqual(ids_com, ids_sem)
        self.assertIn(self.cpd_colapsado_id, ids_com)

    def test_api_cpds_nao_tem_mais_campo_de_variacoes(self):
        status, dados = self._get("/api/admin/cpds")
        self.assertEqual(status, 200)
        for item in dados["itens"]:
            self.assertNotIn("total_variacoes", item)
            self.assertNotIn("variacoes", item)
            self.assertNotIn("extensao", item)
        status_det, det = self._get(f"/api/admin/cpds/{self.cpd_colapsado_id}")
        self.assertEqual(status_det, 200)
        self.assertNotIn("variacoes", det)
        self.assertNotIn("total_variacoes", det)

    def test_nao_existe_mais_filtro_com_variacoes(self):
        # O parâmetro é simplesmente ignorado (não quebra, não filtra nada) --
        # já não existe suporte funcional a variações.
        status, dados = self._get("/api/admin/cpds?com_variacoes=1")
        self.assertEqual(status, 200)
        codigos = {i["codigo"] for i in dados["itens"]}
        self.assertIn("12345", codigos)
        self.assertIn("99999", codigos)

    def test_extensoes_historicas_nao_criam_cpd_separado(self):
        status, dados = self._get("/api/admin/cpds")
        self.assertEqual(status, 200)
        codigos = [i["codigo"] for i in dados["itens"]]
        self.assertEqual(codigos.count("12345"), 1, "12345/12345.1/12345/1 devem colapsar num único CPD")

    def test_descricoes_de_extensoes_historicas_ficam_preservadas_como_fontes(self):
        status, dados = self._get(f"/api/admin/cpds/{self.cpd_colapsado_id}")
        self.assertEqual(status, 200)
        codigos_fontes = {d["codigo_completo"] for d in dados["descricoes_fontes"]}
        self.assertEqual(codigos_fontes, {"12345", "12345.1"})
        self.assertIn("12345.1", dados["codigos_originais_historicos"])

    def test_clientes_de_extensoes_historicas_sao_consolidados_no_cpd_base(self):
        status, dados = self._get(f"/api/admin/cpds/{self.cpd_colapsado_id}")
        self.assertEqual(status, 200)
        self.assertEqual(set(dados["clientes"]), {"CLIENTE FICTICIO ALFA", "CLIENTE FICTICIO GAMA"})

    def test_cpd_detalhe_traz_descricao_canonica_e_pendencias(self):
        status, dados = self._get(f"/api/admin/cpds/{self.cpd_colapsado_id}")
        self.assertEqual(status, 200)
        self.assertEqual(dados["descricao_canonica"], "Peça fictícia canônica")
        tipos = {p["tipo"] for p in dados["pendencias"]}
        self.assertIn("CONFLITO_DESCRICAO", tipos)

    def test_conflito_de_descricao_gera_pendencia_sem_criar_cpd_separado(self):
        status, dados = self._get("/api/admin/pendencias?tipo=CONFLITO_DESCRICAO")
        self.assertEqual(status, 200)
        codigos = {p["codigo_completo"] for p in dados["itens"]}
        self.assertIn("12345", codigos)
        status_cpds, dados_cpds = self._get("/api/admin/cpds?busca=12345")
        self.assertEqual(len(dados_cpds["itens"]), 1)

    def test_cpd_detalhe_inexistente_404(self):
        status, dados = self._get("/api/admin/cpds/999999")
        self.assertEqual(status, 404)

    def test_nenhum_cpd_variacoes_e_populado_pela_api_ou_migracao(self):
        self.assertEqual(self._contagem_tabela("cpd_variacoes"), 0)

    # ------------------------------------------------------------------
    # Arruelas (categoria separada de CPD)
    # ------------------------------------------------------------------

    def test_arruela_nao_aparece_na_listagem_de_cpds(self):
        status, dados = self._get("/api/admin/cpds?busca=ZZ-090")
        self.assertEqual(status, 200)
        self.assertEqual(dados["itens"], [])

    def test_arruela_aparece_na_listagem_propria(self):
        status, dados = self._get("/api/admin/arruelas?busca=ZZ-090")
        self.assertEqual(status, 200)
        codigos = {i["codigo"] for i in dados["itens"]}
        self.assertIn("ZZ-090", codigos)

    def test_arruela_detalhe_traz_clientes_e_grupos(self):
        status, dados = self._get(f"/api/admin/arruelas/{self.arruela_id}")
        self.assertEqual(status, 200)
        self.assertIn("CLIENTE FICTICIO ALFA", dados["clientes"])
        self.assertIn("Honda", dados["grupos"])

    def test_arruela_detalhe_inexistente_404(self):
        status, dados = self._get("/api/admin/arruelas/999999")
        self.assertEqual(status, 404)

    # ------------------------------------------------------------------
    # Itens (API unificada CPD + Arruela)
    # ------------------------------------------------------------------

    def test_itens_reune_cpds_e_arruelas(self):
        status, dados = self._get("/api/admin/itens?por_pagina=100")
        self.assertEqual(status, 200)
        tipos_por_codigo = {i["codigo"]: i["tipo"] for i in dados["itens"]}
        self.assertEqual(tipos_por_codigo.get("12345"), "CPD")
        self.assertEqual(tipos_por_codigo.get("ZZ-090"), "ARRUELA")

    def test_itens_filtro_tipo_cpd(self):
        status, dados = self._get("/api/admin/itens?tipo=CPD&por_pagina=100")
        self.assertEqual(status, 200)
        self.assertTrue(all(i["tipo"] == "CPD" for i in dados["itens"]))
        self.assertNotIn("ZZ-090", {i["codigo"] for i in dados["itens"]})

    def test_itens_filtro_tipo_arruela(self):
        status, dados = self._get("/api/admin/itens?tipo=ARRUELA")
        self.assertEqual(status, 200)
        self.assertTrue(all(i["tipo"] == "ARRUELA" for i in dados["itens"]))
        codigos = {i["codigo"] for i in dados["itens"]}
        self.assertEqual(codigos, {"ZZ-090"})

    def test_itens_filtro_possui_pendencia(self):
        status, dados = self._get("/api/admin/itens?possui_pendencia=1&por_pagina=100")
        self.assertEqual(status, 200)
        codigos = {i["codigo"] for i in dados["itens"]}
        self.assertIn("12345", codigos)
        self.assertNotIn("11111", codigos, "CPD sem pendência não pode aparecer com possui_pendencia=1")
        self.assertNotIn("ZZ-090", codigos, "Arruela nunca tem pendência própria neste schema")

        status2, dados2 = self._get("/api/admin/itens?possui_pendencia=0&por_pagina=100")
        self.assertEqual(status2, 200)
        codigos2 = {i["codigo"] for i in dados2["itens"]}
        self.assertIn("11111", codigos2)
        self.assertNotIn("12345", codigos2)

    def test_itens_filtro_busca(self):
        status, dados = self._get("/api/admin/itens?busca=99999")
        self.assertEqual(status, 200)
        codigos = {i["codigo"] for i in dados["itens"]}
        self.assertEqual(codigos, {"99999"})

    def test_itens_paginacao(self):
        status, dados = self._get("/api/admin/itens?por_pagina=1&pagina=1")
        self.assertEqual(status, 200)
        self.assertEqual(len(dados["itens"]), 1)
        self.assertGreaterEqual(dados["paginacao"]["total_itens"], 3)

    # ------------------------------------------------------------------
    # Pendências
    # ------------------------------------------------------------------

    def test_pendencias_filtro_por_tipo(self):
        status, dados = self._get("/api/admin/pendencias?tipo=CODIGO_INVALIDO")
        self.assertEqual(status, 200)
        self.assertTrue(all(p["tipo"] == "CODIGO_INVALIDO" for p in dados["itens"]))
        self.assertGreaterEqual(len(dados["itens"]), 1)

    def test_pendencias_filtro_por_status(self):
        status, dados = self._get("/api/admin/pendencias?status=RESOLVIDO")
        self.assertEqual(status, 200)
        self.assertTrue(all(p["status"] == "RESOLVIDO" for p in dados["itens"]))

    def test_pendencia_detalhe_traz_cpd_relacionado(self):
        status, dados = self._get(f"/api/admin/pendencias/{self.pendencia_id}")
        self.assertEqual(status, 200)
        self.assertEqual(dados["cpd_codigo_pai"], "12345")

    def test_pendencia_detalhe_inexistente_404(self):
        status, dados = self._get("/api/admin/pendencias/999999")
        self.assertEqual(status, 404)

    def test_detalhes_json_invalido_nao_derruba_a_api(self):
        status, dados = self._get(f"/api/admin/pendencias/{self.pendencia_json_invalido_id}")
        self.assertEqual(status, 200)
        self.assertIsNone(dados["detalhes"])

        status_lista, dados_lista = self._get("/api/admin/pendencias?codigo=77777")
        self.assertEqual(status_lista, 200)
        self.assertEqual(len(dados_lista["itens"]), 1)
        self.assertIsNone(dados_lista["itens"][0]["detalhes"])

    # ------------------------------------------------------------------
    # Métodos de escrita
    # ------------------------------------------------------------------

    def test_todos_endpoints_rejeitam_metodos_de_escrita(self):
        rotas_e_metodos = [
            ("/api/admin/resumo", ("post", "put", "patch", "delete")),
            ("/api/admin/clientes", ("post", "put", "patch", "delete")),
            (f"/api/admin/clientes/{self.cliente_alfa_id}", ("post", "put", "patch", "delete")),
            ("/api/admin/cpds", ("post", "put", "patch", "delete")),
            (f"/api/admin/cpds/{self.cpd_colapsado_id}", ("post", "put", "patch", "delete")),
            ("/api/admin/itens", ("post", "put", "patch", "delete")),
            ("/api/admin/arruelas", ("post", "put", "patch", "delete")),
            (f"/api/admin/arruelas/{self.arruela_id}", ("post", "put", "patch", "delete")),
            ("/api/admin/pendencias", ("post", "put", "patch", "delete")),
            (f"/api/admin/pendencias/{self.pendencia_id}", ("post", "put", "patch", "delete")),
            ("/cadastros", ("post", "put", "patch", "delete")),
        ]
        with self._cliente_ligado():
            cliente = self.servidor.app.test_client()
            for rota, metodos in rotas_e_metodos:
                for metodo in metodos:
                    resp = getattr(cliente, metodo)(rota)
                    self.assertEqual(
                        resp.status_code, 405,
                        f"{metodo.upper()} {rota} deveria ser rejeitado com 405, veio {resp.status_code}",
                    )

    def test_id_nao_numerico_retorna_404_em_todos_os_detalhes(self):
        for rota in ("/api/admin/clientes/abc", "/api/admin/cpds/abc", "/api/admin/arruelas/abc", "/api/admin/pendencias/abc"):
            status, _ = self._get(rota)
            self.assertEqual(status, 404, f"{rota} deveria retornar 404 para id não numérico")

    # ------------------------------------------------------------------
    # Nada disso escreve no banco
    # ------------------------------------------------------------------

    def test_consultas_nao_alteram_contagens_de_tabelas_normalizadas(self):
        antes = {
            tabela: self._contagem_tabela(tabela)
            for tabela in ("clientes", "cpds", "cpd_variacoes", "arruelas", "cpd_pendencias_revisao")
        }
        self._get("/api/admin/resumo")
        self._get("/api/admin/clientes")
        self._get(f"/api/admin/clientes/{self.cliente_alfa_id}")
        self._get("/api/admin/cpds")
        self._get(f"/api/admin/cpds/{self.cpd_colapsado_id}")
        self._get("/api/admin/itens")
        self._get("/api/admin/arruelas")
        self._get(f"/api/admin/arruelas/{self.arruela_id}")
        self._get("/api/admin/pendencias")
        self._get(f"/api/admin/pendencias/{self.pendencia_id}")
        depois = {
            tabela: self._contagem_tabela(tabela)
            for tabela in ("clientes", "cpds", "cpd_variacoes", "arruelas", "cpd_pendencias_revisao")
        }
        self.assertEqual(antes, depois)

    def test_consultas_nao_alteram_tabelas_legadas_nem_audit_log(self):
        antes = {
            tabela: self._contagem_tabela(tabela)
            for tabela in ("orders", "sections", "manual_cpd", "audit_log")
        }
        self._get("/api/admin/resumo")
        self._get("/api/admin/clientes")
        self._get("/api/admin/cpds")
        self._get("/api/admin/itens")
        self._get("/api/admin/arruelas")
        self._get("/api/admin/pendencias")
        depois = {
            tabela: self._contagem_tabela(tabela)
            for tabela in ("orders", "sections", "manual_cpd", "audit_log")
        }
        self.assertEqual(antes, depois, "Nenhuma rota /api/admin/* pode gravar em tabelas legadas ou no audit_log")

    def test_consultas_nao_alteram_schema_version(self):
        c = sqlite3.connect(str(self.db))
        try:
            antes = self.dbm.get_schema_version(c)
            c.commit()
        finally:
            c.close()
        self._get("/api/admin/resumo")
        c = sqlite3.connect(str(self.db))
        try:
            depois = self.dbm.get_schema_version(c)
            c.commit()
        finally:
            c.close()
        self.assertEqual(antes, depois)

    # ------------------------------------------------------------------
    # Interface sem menções a variações / dados reais
    # ------------------------------------------------------------------

    def test_interface_nao_contem_textos_sobre_variacoes(self):
        html = (ROOT / "cadastros_admin.html").read_text(encoding="utf-8")
        html_lower = html.lower()
        for termo_proibido in ("variação", "variações", "variacao", "variacoes", "código completo", "codigo completo", "com_variacoes"):
            self.assertNotIn(termo_proibido, html_lower, f"'{termo_proibido}' não deveria mais aparecer em cadastros_admin.html")

    def test_tela_cadastros_admin_nao_tem_dados_reais_hardcoded(self):
        config_real = ROOT / "config_local" / "regras_clientes_migracao.json"
        if not config_real.exists():
            self.skipTest("config_local/regras_clientes_migracao.json não existe neste ambiente")

        import scripts.config_clientes_migracao as config_clientes
        config = config_clientes.carregar_config_clientes(config_real)
        nomes_reais = set(config.grupo_honda)
        for variantes in config.aliases.values():
            nomes_reais.update(variantes)
        nomes_reais.update(config.aliases.keys())
        # "HONDA" sozinho é o nome estrutural do grupo (grupos_clientes.nome,
        # badge de grupo, etc.) desde a migração v1->v2 -- checar isso geraria
        # falso-positivo contra código legítimo, mesmo motivo documentado em
        # test_config_clientes_migracao.py.
        nomes_reais.discard("HONDA")
        nomes_reais.discard("Honda")

        html = (ROOT / "cadastros_admin.html").read_text(encoding="utf-8").upper()
        for nome in nomes_reais:
            nome_upper = nome.upper()
            self.assertNotIn(nome_upper, html, f"Nome real '{nome}' encontrado hardcoded em cadastros_admin.html")


if __name__ == "__main__":
    unittest.main()
