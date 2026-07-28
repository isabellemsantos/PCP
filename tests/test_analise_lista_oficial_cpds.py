"""Testes do script de análise da lista oficial de CPDs
(scripts/analisar_lista_oficial_cpds.py), somente leitura.

Todos os dados são fictícios (códigos 9000-9005, 0700/0800, clientes
FICTICIO1 etc.) -- nenhum CPD, cliente ou pedido real é usado. A planilha
de teste é escrita como .xlsx (openpyxl) -- o formato .xls real (via xlrd)
já foi validado manualmente contra o arquivo entregue; aqui testamos a
lógica de detecção/consolidação, que é comum aos dois formatos.
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
    ws.append(["9000", "Peça nova A", "FICTICIO1"])
    ws.append(["9000.1", "Peça nova A variante 1", "FICTICIO1"])
    ws.append([9001, "Peça código numérico", "FICTICIO2"])  # célula numérica de verdade
    ws.append(["9002", "Peça duplicada igual", "FICTICIO1"])
    ws.append(["9002", "Peça duplicada igual", "FICTICIO1"])  # duplicidade EXATA, mesma descrição
    ws.append(["9003", "Descrição A do 9003", "FICTICIO1"])
    ws.append(["9003", "Descrição B do 9003", "FICTICIO2"])  # duplicidade com descrições DIFERENTES
    ws.append(["0800", "Peça zero à esquerda na planilha", "FICTICIO1"])
    wb.save(caminho)


class AnaliseListaOficialTestCase(unittest.TestCase):
    tmp_dir: Path
    db_path: Path
    planilha_path: Path
    servidor = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_lista_oficial_"))
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
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("0700", "Peça zero à esquerda existente, ausente da planilha", "2026-01-01 10:00:00"),
            )
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("9002", "Peça duplicada igual", "2026-01-01 10:00:00"),  # mesma descrição da planilha: sem conflito
            )
            conn.execute(
                "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
                ("9004", "Só em manual_cpd, ausente da planilha e de pedidos", "2026-01-01 10:00:00"),
            )
            payload_pedido = json.dumps({
                "id": "ped_ficticio_1", "cliente": "FICTICIO1", "cpd": "9005",
                "descricao": "Peça só em pedidos", "deleted": False,
                "criadoEm": "2026-01-01 10:00:00", "alteradoEm": "2026-01-01 10:00:00",
            })
            conn.execute(
                "INSERT INTO orders(id, payload, updated_at) VALUES (?,?,?)",
                ("ped_ficticio_1", payload_pedido, "2026-01-01 10:00:00"),
            )
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

    def test_todos_os_codigos_recebem_ativo_1(self):
        for codigo, item in self.resultado["consolidacao"]["consolidados"].items():
            self.assertEqual(item["ativo"], 1, f"{codigo} deveria ter ativo=1")
            self.assertIsNone(item["desativado_em"], f"{codigo} deveria ter desativado_em=None")
        self.assertTrue(self.resultado["resumo"]["todos_ficariam_ativos"])
        self.assertTrue(self.resultado["resumo"]["todos_com_desativado_em_nulo"])

    def test_codigo_ausente_da_planilha_e_preservado(self):
        cons = self.resultado["consolidacao"]["consolidados"]
        self.assertIn("0700", cons, "Código só em manual_cpd não pode sumir da consolidação")
        self.assertIn("0700", self.resultado["consolidacao"]["existentes_em_manual_cpd_ausentes_da_lista"])

    def test_codigo_novo_da_planilha_e_adicionado(self):
        novos = self.resultado["consolidacao"]["novos_da_lista_oficial"]
        self.assertIn("9000", novos)
        self.assertIn("0800", novos)

    def test_extensao_e_vinculada_ao_pai(self):
        pais = self.resultado["consolidacao"]["pais"]
        self.assertIn("9000", pais)
        codigos_do_pai = {item["codigo_original"] for item in pais["9000"]}
        self.assertEqual(codigos_do_pai, {"9000", "9000.1"})

    def test_zero_a_esquerda_preservado_em_manual_cpd(self):
        cons = self.resultado["consolidacao"]["consolidados"]
        self.assertEqual(cons["0700"]["codigo_original"], "0700")
        self.assertEqual(cons["0700"]["codigo_pai"], "0700")

    def test_zero_a_esquerda_preservado_na_planilha(self):
        cons = self.resultado["consolidacao"]["consolidados"]
        self.assertIn("0800", cons)
        self.assertEqual(cons["0800"]["codigo_original"], "0800")

    def test_celula_numerica_e_convertida_sem_inventar_zero(self):
        linha_9001 = next(l for l in self.resultado["leitura"]["linhas"] if l["codigo_original"] == "9001")
        self.assertTrue(linha_9001["zero_esquerda_desconhecido"], "Célula numérica deve sinalizar zero_esquerda_desconhecido")

    def test_duplicidade_com_mesma_descricao_e_consolidada_sem_conflito(self):
        dup = next(d for d in self.resultado["duplicidades"] if d["codigo"] == "9002")
        self.assertEqual(dup["descricao_que_seria_escolhida"], "Peça duplicada igual")
        cons = self.resultado["consolidacao"]["consolidados"]["9002"]
        self.assertFalse(cons["conflito_descricao"])
        self.assertEqual(cons["descricao"], "Peça duplicada igual")

    def test_descricoes_conflitantes_nao_sao_resolvidas_silenciosamente(self):
        dup = next(d for d in self.resultado["duplicidades"] if d["codigo"] == "9003")
        self.assertIsNone(dup["descricao_que_seria_escolhida"])
        cons = self.resultado["consolidacao"]["consolidados"]["9003"]
        self.assertTrue(cons["conflito_descricao"])
        self.assertIsNone(cons["descricao"], "Não deve escolher descrição sozinho quando há conflito")
        conflito = next(c for c in self.resultado["consolidacao"]["conflitos_para_decisao"] if c["codigo"] == "9003")
        self.assertIn("Descrição A do 9003", conflito["descricoes_por_fonte"]["lista_oficial"])
        self.assertIn("Descrição B do 9003", conflito["descricoes_por_fonte"]["lista_oficial"])

    def test_codigo_apenas_em_pedidos_entra_na_consolidacao(self):
        cons = self.resultado["consolidacao"]["consolidados"]
        self.assertIn("9005", cons)
        self.assertEqual(cons["9005"]["fontes"], ["pedidos"])

    def test_codigo_apenas_em_manual_cpd_entra_na_consolidacao(self):
        cons = self.resultado["consolidacao"]["consolidados"]
        self.assertIn("9004", cons)
        self.assertEqual(cons["9004"]["fontes"], ["manual_cpd"])

    def test_aba_principal_detectada_corretamente(self):
        escolhida = self.resultado["leitura"]["deteccao"]["escolhida"]
        self.assertEqual(escolhida["aba"], "Lista")
        self.assertEqual(escolhida["coluna_cliente"], 2)

    # ------------------------------------------------------------------
    # Somente leitura / sem efeitos colaterais
    # ------------------------------------------------------------------

    def test_planilha_e_banco_permanecem_inalterados(self):
        hash_planilha_antes = _sha256_arquivo(self.planilha_path)
        hash_banco_antes = _sha256_arquivo(self.db_path)

        self._analisar()

        hash_planilha_depois = _sha256_arquivo(self.planilha_path)
        hash_banco_depois = _sha256_arquivo(self.db_path)
        self.assertEqual(hash_planilha_antes, hash_planilha_depois)
        self.assertEqual(hash_banco_antes, hash_banco_depois)

    def test_nenhuma_auditoria_e_criada(self):
        with sqlite3.connect(str(self.db_path)) as c:
            antes = c.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        self._analisar()
        with sqlite3.connect(str(self.db_path)) as c:
            depois = c.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        self.assertEqual(antes, depois)

    def test_nenhuma_tabela_nova_recebe_dados_durante_a_analise(self):
        with sqlite3.connect(str(self.db_path)) as c:
            antes = {
                t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("clientes", "cpds", "cpd_variacoes", "cliente_cpds", "grupo_cpds")
            }
        self._analisar()
        with sqlite3.connect(str(self.db_path)) as c:
            depois = {
                t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("clientes", "cpds", "cpd_variacoes", "cliente_cpds", "grupo_cpds")
            }
        self.assertEqual(antes, depois)
        self.assertTrue(all(v == 0 for v in depois.values()))


class ClassificarParDescricoesTestCase(unittest.TestCase):
    """Regra oficial: quando duas descrições são tecnicamente equivalentes e
    a única diferença é o prefixo inicial "PARAF"/"PARAF."/"PARAFUSO", isso é
    categoria B (convenção de descrição, não informação técnica) -- nunca
    remove o prefixo se não estiver no início, nunca remove parte de outra
    palavra, e qualquer diferença técnica real (dimensão/material/classe/
    tratamento/acabamento/norma) continua virando categoria C ou D."""

    def test_paraf_sem_ponto_e_removido(self):
        categoria, _ = analisador.classificar_par_descricoes("PARAF TESTE 4X10 ZNA", "TESTE 4X10 ZNA")
        self.assertEqual(categoria, "B")

    def test_paraf_com_ponto_e_removido(self):
        categoria, _ = analisador.classificar_par_descricoes("PARAF. TESTE 4X10 ZNA", "TESTE 4X10 ZNA")
        self.assertEqual(categoria, "B")

    def test_parafuso_e_removido(self):
        categoria, _ = analisador.classificar_par_descricoes("PARAFUSO TESTE 4X10 ZNA", "TESTE 4X10 ZNA")
        self.assertEqual(categoria, "B")

    def test_descricao_ja_sem_prefixo_permanece_igual(self):
        # Nenhuma das duas tem prefixo -- se o resto for idêntico, categoria A.
        categoria, _ = analisador.classificar_par_descricoes("TESTE 4X10 ZNA", "TESTE 4X10 ZNA")
        self.assertEqual(categoria, "A")
        self.assertEqual(analisador._remover_prefixo_paraf(analisador._normalizar_cosmetico("TESTE 4X10 ZNA")), "TESTE 4X10 ZNA")

    def test_palavra_com_paraf_no_meio_nao_e_alterada(self):
        # "SUPARAFUSO" não é o prefixo oficial (não está exatamente no
        # início como token próprio) -- não deve virar categoria B só por
        # conter as letras "PARAF".
        normalizada = analisador._normalizar_cosmetico("SUPARAFUSO TESTE 4X10")
        self.assertEqual(analisador._remover_prefixo_paraf(normalizada), "SUPARAFUSO TESTE 4X10")

    def test_prefixo_paraf_no_meio_da_frase_nao_e_removido(self):
        # O prefixo só é removido se estiver no INÍCIO da descrição -- uma
        # ocorrência de "PARAF" no meio da frase (dentro de outra palavra)
        # tem que sobreviver à normalização.
        normalizada = analisador._normalizar_cosmetico("TESTE COMPARAFUSADO 4X10")
        self.assertEqual(analisador._remover_prefixo_paraf(normalizada), "TESTE COMPARAFUSADO 4X10")

    def test_diferenca_de_dimensao_gera_conflito(self):
        categoria, _ = analisador.classificar_par_descricoes("PARAF TESTE 4X10 ZNA", "TESTE 4X12 ZNA")
        self.assertIn(categoria, ("C", "D"))

    def test_diferenca_de_acabamento_gera_conflito(self):
        categoria, _ = analisador.classificar_par_descricoes("PARAF TESTE 4X10 ZNA TRIV", "TESTE 4X10 ZNA NYLON")
        self.assertIn(categoria, ("C", "D"))


if __name__ == "__main__":
    unittest.main()
