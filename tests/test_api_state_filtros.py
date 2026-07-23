"""Documenta e testa o único filtro aplicado por /api/state: registros com
payload["deleted"]=True (lixeira) ficam fora; tudo o mais aparece, inclusive
pedidos finalizados/cancelados e seções com active=False (ocultas, mas não
na lixeira). Ver load_state_from_conn() em servidor_pcp.py.

Nenhum teste aqui usa o pcp.sqlite3 real: trabalha com um banco sintético
isolado por cópia via sqlite3.Connection.backup().
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

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class ApiStateFiltrosTest(unittest.TestCase):
    tmp_dir: Path
    db_base: Path
    servidor = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_api_state_"))
        cls.db_base = cls.tmp_dir / "base.sqlite3"

        os.environ["PCP_DB_FILE"] = str(cls.db_base)
        os.environ["PCP_EXCEL_FILE"] = str(cls.tmp_dir / "dados_pcp_teste.xlsx")
        os.environ["PCP_EXCEL_PENDING_FILE"] = str(cls.tmp_dir / "dados_pcp_pendente_teste.xlsx")
        os.environ["PCP_LOG_FILE"] = str(cls.tmp_dir / "servidor_pcp_teste.log")
        os.environ["PCP_BACKUP_DIR"] = str(cls.tmp_dir / "backups")

        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        cls.servidor = importlib.import_module("servidor_pcp")
        cls.servidor.init_db()

    @classmethod
    def tearDownClass(cls):
        for var in ("PCP_DB_FILE", "PCP_EXCEL_FILE", "PCP_EXCEL_PENDING_FILE", "PCP_LOG_FILE", "PCP_BACKUP_DIR"):
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

    def _api_state(self):
        from unittest.mock import patch
        with patch.object(self.servidor, "DB_FILE", self.db):
            cliente = self.servidor.app.test_client()
            resp = cliente.get("/api/state")
            return resp.status_code, resp.get_json()

    def _inserir_order(self, order_id, **payload_extra):
        payload = {"id": order_id, "cpd": "TESTE", "descricao": "Pedido teste", "setor": "Pendente"}
        payload.update(payload_extra)
        conn = sqlite3.connect(str(self.db))
        conn.execute(
            "INSERT INTO orders(id, payload, updated_at) VALUES (?,?,datetime('now'))",
            (order_id, json.dumps(payload)),
        )
        conn.commit()
        conn.close()

    def _inserir_section(self, section_id, **payload_extra):
        payload = {"id": section_id, "name": "Data teste", "defaultDate": "2026-01-01"}
        payload.update(payload_extra)
        conn = sqlite3.connect(str(self.db))
        conn.execute(
            "INSERT INTO sections(id, payload, updated_at) VALUES (?,?,datetime('now'))",
            (section_id, json.dumps(payload)),
        )
        conn.commit()
        conn.close()

    def test_pedido_ativo_aparece_na_api(self):
        self._inserir_order("ped_ativo", setor="Pendente")
        status, dados = self._api_state()
        self.assertEqual(status, 200)
        ids = {o["id"] for o in dados["orders"]}
        self.assertIn("ped_ativo", ids)

    def test_pedido_concluido_aparece_na_api(self):
        self._inserir_order("ped_concluido", setor="Concluído")
        status, dados = self._api_state()
        ids = {o["id"] for o in dados["orders"]}
        self.assertIn("ped_concluido", ids, "Pedidos concluídos continuam visíveis, só a lixeira é filtrada")

    def test_pedido_cancelado_aparece_na_api(self):
        self._inserir_order("ped_cancelado", setor="Cancelado")
        status, dados = self._api_state()
        ids = {o["id"] for o in dados["orders"]}
        self.assertIn("ped_cancelado", ids, "Pedidos cancelados continuam visíveis, só a lixeira é filtrada")

    def test_pedido_na_lixeira_fica_fora_da_api(self):
        self._inserir_order("ped_lixeira", deleted=True)
        status, dados = self._api_state()
        ids = {o["id"] for o in dados["orders"]}
        self.assertNotIn("ped_lixeira", ids, "deleted=True é o único critério que remove um pedido de /api/state")

    def test_secao_ativa_aparece_na_api(self):
        self._inserir_section("sec_ativa", active=True)
        status, dados = self._api_state()
        ids = {s["id"] for s in dados["sections"]}
        self.assertIn("sec_ativa", ids)

    def test_secao_oculta_active_false_ainda_aparece_na_api(self):
        # "Oculta" (active=False) é diferente de "lixeira" (deleted=True):
        # só o segundo é filtrado por load_state_from_conn().
        self._inserir_section("sec_oculta", active=False)
        status, dados = self._api_state()
        ids = {s["id"] for s in dados["sections"]}
        self.assertIn("sec_oculta", ids, "Seção oculta (active=False) não é removida, só a lixeira é")

    def test_secao_na_lixeira_fica_fora_da_api(self):
        self._inserir_section("sec_lixeira", deleted=True)
        status, dados = self._api_state()
        ids = {s["id"] for s in dados["sections"]}
        self.assertNotIn("sec_lixeira", ids)

    def test_total_da_api_e_coerente_com_o_filtro_de_lixeira(self):
        self._inserir_order("o1", setor="Pendente")
        self._inserir_order("o2", setor="Concluído")
        self._inserir_order("o3", deleted=True)
        self._inserir_order("o4", deleted=True)
        self._inserir_section("s1", active=True)
        self._inserir_section("s2", active=False)
        self._inserir_section("s3", deleted=True)

        with sqlite3.connect(str(self.db)) as c:
            total_orders_banco = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            total_sections_banco = c.execute("SELECT COUNT(*) FROM sections").fetchone()[0]

        status, dados = self._api_state()
        with sqlite3.connect(str(self.db)) as c:
            total_orders_lixeira = sum(
                1 for row in c.execute("SELECT payload FROM orders") if json.loads(row[0]).get("deleted")
            )
            total_sections_lixeira = sum(
                1 for row in c.execute("SELECT payload FROM sections") if json.loads(row[0]).get("deleted")
            )

        self.assertEqual(len(dados["orders"]), total_orders_banco - total_orders_lixeira)
        self.assertEqual(len(dados["sections"]), total_sections_banco - total_sections_lixeira)


if __name__ == "__main__":
    unittest.main()
