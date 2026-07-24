"""Testes da revisão final da lista oficial de CPDs: candidatos de zero à
esquerda, clientes da lista oficial x pedidos, e classificação conservadora
de conflitos de descrição (A/B/C/D).

Todos os dados são fictícios (códigos 9472/09472, 8888/08888, 7000-7004,
clientes FICTICIO_*) -- nenhum CPD, cliente ou pedido real é usado.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.analisar_lista_oficial_cpds as analisador
import scripts.analisar_migracao_clientes_cpds as base_analise


def _sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _criar_planilha_ficticia(caminho: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Lista"
    ws.append(["CPD", "Descrição", "Cliente"])
    # Candidato de zero à esquerda com evidência forte (descrição e cliente compatíveis).
    ws.append([9472, "MP TESTE ZNA TRIV", "FICTICIO_HONDA"])
    # Mesmo valor numérico de um código existente, mas evidência fraca (descrição
    # e cliente bem diferentes) -- não deve virar candidato de alta confiança.
    ws.append([8888, "ITEM COMPLETAMENTE DIFERENTE XYZ", "FICTICIO_OUTRO"])
    # Conflitos de descrição para classificar.
    ws.append(["7000", "PECA TESTE", "FICTICIO_SO_PLANILHA"])
    ws.append(["7001", "PECA, TESTE.", "FICTICIO_SO_PLANILHA"])
    ws.append(["7002", "PECA TESTE DOIS", "FICTICIO_SO_PLANILHA"])
    ws.append(["7003", "PARAF MP 6X16 ZNA TRIV", "FICTICIO_SO_PLANILHA"])
    ws.append(["7004", "PARAF MP 6X16 ZNA TRIV", "FICTICIO_SO_PLANILHA"])
    # Cliente com célula vazia.
    ws.append(["7005", "Peça sem cliente informado", ""])
    # Cliente presente em ambas as fontes (mesmo nome usado num pedido).
    ws.append(["1", "Peça qualquer", "FICTICIO_AMBAS"])
    wb.save(caminho)


class RevisaoListaOficialTestCase(unittest.TestCase):
    tmp_dir: Path
    db_path: Path
    planilha_path: Path
    servidor = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_revisao_lista_oficial_"))
        cls.db_path = cls.tmp_dir / "fake.sqlite3"
        cls.planilha_path = cls.tmp_dir / "lista_oficial_ficticia.xlsx"
        _criar_planilha_ficticia(cls.planilha_path)

        os.environ["PCP_DB_FILE"] = str(cls.db_path)
        os.environ["PCP_EXCEL_FILE"] = str(cls.tmp_dir / "excel_inexistente.xlsx")
        os.environ["PCP_EXCEL_PENDING_FILE"] = str(cls.tmp_dir / "pendente.xlsx")
        os.environ["PCP_LOG_FILE"] = str(cls.tmp_dir / "log.txt")
        os.environ["PCP_BACKUP_DIR"] = str(cls.tmp_dir / "backups")
        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        cls.servidor = importlib.import_module("servidor_pcp")
        cls.dbm = importlib.import_module("db_manutencao")
        cls.servidor.init_db()

        with sqlite3.connect(str(cls.db_path)) as conn:
            conn.execute("PRAGMA foreign_keys=ON")
            cls.dbm.run_migrations(conn, cls.db_path, cls.tmp_dir / "backups_migracao", log=lambda _msg: None)

        with sqlite3.connect(str(cls.db_path)) as conn:
            # 09472 -- deve casar com "9472" da planilha (descrição/cliente compatíveis).
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("09472", "PARAF MP teste ZNA triv", "2026-01-01 10:00:00"),
            )
            # 08888 -- mesmo valor numérico de "8888" da planilha, mas descrição/cliente muito diferentes.
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("08888", "PARAF OUTRA PECA TOTALMENTE DISTINTA ABC", "2026-01-01 10:00:00"),
            )
            # Conflitos de descrição (planilha x manual_cpd).
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("7000", "peca teste", "2026-01-01 10:00:00"),  # só maiúsculas/minúsculas -> A
            )
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("7001", "PECA TESTE", "2026-01-01 10:00:00"),  # só pontuação -> A
            )
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("7002", "PARAF PECA TESTE DOIS", "2026-01-01 10:00:00"),  # só prefixo PARAF -> B
            )
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("7003", "PARAF MP 6X20 ZNA TRIV", "2026-01-01 10:00:00"),  # dimensão diferente (16 vs 20) -> C
            )
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("7004", "PARAF MP 6X16 ZNB TRIV", "2026-01-01 10:00:00"),  # acabamento diferente (ZNA vs ZNB) -> C
            )

            def _pedido(order_id, cliente, cpd):
                payload = json.dumps({
                    "id": order_id, "cliente": cliente, "cpd": cpd, "descricao": "",
                    "deleted": False, "criadoEm": "2026-01-01 10:00:00", "alteradoEm": "2026-01-01 10:00:00",
                })
                conn.execute("INSERT INTO orders(id, payload, updated_at) VALUES (?,?,?)", (order_id, payload, "2026-01-01 10:00:00"))

            # Cliente existente em ambas as fontes (aparece em pedidos E na planilha, mesmo nome).
            _pedido("ped_ambas", "FICTICIO_AMBAS", "1")
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("1", "Peça qualquer", "2026-01-01 10:00:00"),
            )
            # Cliente só em pedidos (não aparece na planilha oficial).
            _pedido("ped_so_pedidos", "FICTICIO_SO_PEDIDOS", "2")
            # 09472 também usado num pedido pelo mesmo cliente (evidência extra de compatibilidade).
            _pedido("ped_9472", "FICTICIO_HONDA", "09472")
            conn.commit()

        cls.resultado = cls._analisar()

    @classmethod
    def tearDownClass(cls):
        for var in ("PCP_DB_FILE", "PCP_EXCEL_FILE", "PCP_EXCEL_PENDING_FILE", "PCP_LOG_FILE", "PCP_BACKUP_DIR"):
            os.environ.pop(var, None)
        for nome in ("servidor_pcp", "db_manutencao"):
            sys.modules.pop(nome, None)
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    @classmethod
    def _analisar(cls) -> dict:
        conn = base_analise.abrir_somente_leitura(cls.db_path)
        try:
            return analisador.executar_analise_lista_oficial(conn, cls.planilha_path, set())
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Zeros à esquerda
    # ------------------------------------------------------------------

    def test_9472_e_candidato_de_09472_com_alta_confianca(self):
        candidatos = self.resultado["zeros_esquerda"]["candidatos"]
        item = next((c for c in candidatos if c["cpd_lista_oficial"] == "9472" and c["cpd_existente"] == "09472"), None)
        self.assertIsNotNone(item, "9472 deveria ser candidato de 09472")
        self.assertEqual(item["nivel_confianca"], "alta")

    def test_mesmo_valor_numerico_nao_e_unido_automaticamente(self):
        # 8888 x 08888: mesmo valor numérico, mas evidência fraca -- ainda assim
        # aparece como candidato (não é descartado), só que com confiança baixa,
        # e em NENHUM caso a análise "une" nada (não existe uma tabela consolidada
        # que já mescle os dois; cada um continua com seu próprio registro).
        candidatos = self.resultado["zeros_esquerda"]["candidatos"]
        item = next((c for c in candidatos if c["cpd_lista_oficial"] == "8888" and c["cpd_existente"] == "08888"), None)
        self.assertIsNotNone(item)
        self.assertEqual(item["nivel_confianca"], "baixa")
        cons = self.resultado["consolidacao"]["consolidados"]
        self.assertIn("8888", cons)
        self.assertIn("08888", cons)
        self.assertNotEqual(cons["8888"]["codigo_pai"], "")  # cada um continua com seu próprio registro
        self.assertEqual(cons["8888"]["codigo_original"], "8888")
        self.assertEqual(cons["08888"]["codigo_original"], "08888")

    # ------------------------------------------------------------------
    # Clientes
    # ------------------------------------------------------------------

    def test_cliente_existente_em_ambas_fontes(self):
        clientes = self.resultado["clientes"]
        self.assertIn("FICTICIO_AMBAS", clientes["clientes_presentes_em_ambas_fontes"])

    def test_cliente_somente_na_planilha(self):
        clientes = self.resultado["clientes"]
        self.assertIn("FICTICIO_SO_PLANILHA", clientes["clientes_somente_na_lista_oficial"])

    def test_cliente_somente_em_pedidos(self):
        clientes = self.resultado["clientes"]
        self.assertIn("FICTICIO_SO_PEDIDOS", clientes["clientes_somente_em_pedidos"])

    def test_celula_de_cliente_vazia_e_contabilizada(self):
        clientes = self.resultado["clientes"]
        self.assertGreaterEqual(clientes["total_celulas_cliente_vazias_na_planilha"], 1)

    # ------------------------------------------------------------------
    # Classificação de conflitos A/B/C/D
    # ------------------------------------------------------------------

    def _categoria_do_codigo(self, codigo: str) -> str:
        item = next(c for c in self.resultado["conflitos_tecnicos"]["classificados"] if c["codigo"] == codigo)
        return item["categoria"]

    def test_conflito_apenas_maiusculas_e_categoria_a(self):
        self.assertEqual(self._categoria_do_codigo("7000"), "A")

    def test_conflito_apenas_pontuacao_e_categoria_a(self):
        self.assertEqual(self._categoria_do_codigo("7001"), "A")

    def test_conflito_prefixo_paraf_e_categoria_b(self):
        self.assertEqual(self._categoria_do_codigo("7002"), "B")

    def test_conflito_tecnico_dimensao_e_categoria_c(self):
        self.assertEqual(self._categoria_do_codigo("7003"), "C")

    def test_conflito_tecnico_acabamento_e_categoria_c(self):
        self.assertEqual(self._categoria_do_codigo("7004"), "C")

    def test_categoria_a_e_b_propoem_descricao_canonica(self):
        item_a = next(c for c in self.resultado["conflitos_tecnicos"]["classificados"] if c["codigo"] == "7000")
        item_b = next(c for c in self.resultado["conflitos_tecnicos"]["classificados"] if c["codigo"] == "7002")
        self.assertIsNotNone(item_a["descricao_canonica_proposta"])
        self.assertIsNotNone(item_b["descricao_canonica_proposta"])

    def test_categoria_c_nao_propoe_descricao_canonica(self):
        item_c = next(c for c in self.resultado["conflitos_tecnicos"]["classificados"] if c["codigo"] == "7003")
        self.assertIsNone(item_c["descricao_canonica_proposta"])

    # ------------------------------------------------------------------
    # Somente leitura
    # ------------------------------------------------------------------

    def test_nenhuma_escrita_no_banco(self):
        hash_antes = _sha256_arquivo(self.db_path)
        self._analisar()
        hash_depois = _sha256_arquivo(self.db_path)
        self.assertEqual(hash_antes, hash_depois)

    def test_nenhuma_alteracao_na_planilha(self):
        hash_antes = _sha256_arquivo(self.planilha_path)
        self._analisar()
        hash_depois = _sha256_arquivo(self.planilha_path)
        self.assertEqual(hash_antes, hash_depois)


if __name__ == "__main__":
    unittest.main()
