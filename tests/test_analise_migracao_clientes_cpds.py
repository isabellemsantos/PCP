"""Testes do script de análise de migração de clientes/CPDs
(scripts/analisar_migracao_clientes_cpds.py), somente leitura.

Todos os dados usados aqui são fictícios (ACME, GLOBEX CORP, INITECH,
códigos 1000/2000/etc.) -- nenhum cliente, CPD ou pedido real é usado.
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

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.analisar_migracao_clientes_cpds as analisador


def _inserir_order(
    conn: sqlite3.Connection,
    order_id: str,
    cliente=None,
    cpd=None,
    descricao: str = "",
    deleted: bool = False,
    criado_em: str = "2026-01-01 10:00:00",
    alterado_em: str = "2026-01-02 10:00:00",
) -> None:
    payload = {
        "id": order_id,
        "cliente": cliente,
        "cpd": cpd,
        "descricao": descricao,
        "deleted": deleted,
        "criadoEm": criado_em,
        "alteradoEm": alterado_em,
    }
    conn.execute(
        "INSERT INTO orders(id, payload, updated_at) VALUES (?,?,?)",
        (order_id, json.dumps(payload), alterado_em),
    )


def _inserir_manual_cpd(conn: sqlite3.Connection, codigo: str, descricao: str, updated_at: str = "2026-01-01 10:00:00") -> None:
    conn.execute(
        "INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES (?,?,?)",
        (codigo, descricao, updated_at),
    )


def _sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class AnaliseMigracaoTestCase(unittest.TestCase):
    tmp_dir: Path
    db_path: Path
    servidor = None

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_analise_migracao_"))
        cls.db_path = cls.tmp_dir / "fake.sqlite3"
        cls.config_clientes_path = cls.tmp_dir / "config_clientes_teste.json"
        cls.config_clientes_path.write_text(
            json.dumps({"grupo_honda": [], "aliases": {}, "placeholders_invalidos": []}), encoding="utf-8",
        )

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
            # Aliases por caixa e espaços -- devem colidir na forma normalizada.
            _inserir_order(conn, "ped1", cliente="ACME", cpd="1000", descricao="Peça A")
            _inserir_order(conn, "ped2", cliente="Acme", cpd="1000.1", descricao="Peça A variante 1")
            _inserir_order(conn, "ped3", cliente="ACME ", cpd="1000.10", descricao="Peça A variante 10")

            # Clientes distintos que NÃO devem ser unidos (nomes bem diferentes).
            _inserir_order(conn, "ped4", cliente="GLOBEX CORP", cpd="2000", descricao="Peça B")
            _inserir_order(conn, "ped9", cliente="INITECH", cpd="2000", descricao="Peça B por Initech")  # CPD ligado a vários clientes

            _inserir_order(conn, "ped5", cliente=None, cpd="4000", descricao="Peça sem cliente")  # pedido sem cliente
            _inserir_order(conn, "ped6", cliente="ACME", cpd=None, descricao="")  # pedido sem CPD
            _inserir_order(conn, "ped7", cliente="ACME", cpd="9999", descricao="Só lixeira", deleted=True)  # lixeira separada

            # Descrição conflitante entre pedido e manual_cpd.
            _inserir_order(conn, "ped10", cliente="ACME", cpd="6000", descricao="Descrição divergente do pedido")

            _inserir_manual_cpd(conn, "1000", "Peça A")
            _inserir_manual_cpd(conn, "1000.1", "Peça A variante 1")
            _inserir_manual_cpd(conn, "1000.10", "Peça A variante 10")
            _inserir_manual_cpd(conn, "0500", "Peça zero à esquerda")
            _inserir_manual_cpd(conn, "0500.01", "Peça zero à esquerda variante")  # extensão com zero à esquerda
            _inserir_manual_cpd(conn, "A.B.25", "Peça com múltiplos pontos")
            _inserir_manual_cpd(conn, "01234.A", "Peça com sufixo não numérico")
            _inserir_manual_cpd(conn, "5000.1", "Só variação, pai 5000 não existe")  # pai ausente
            _inserir_manual_cpd(conn, "6000", "Descrição original do cadastro")
            _inserir_manual_cpd(conn, "7000", "CPD cadastrado, nunca usado em pedidos")
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
        conn = analisador.abrir_somente_leitura(cls.db_path)
        try:
            return analisador.executar_analise(conn, set())
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Clientes: aliases e não-união
    # ------------------------------------------------------------------

    def test_aliases_por_caixa_e_espacos_sao_detectados(self):
        alta = self.resultado["analise_clientes"]["possiveis_aliases_alta_confianca"]
        formas = {item["forma_normalizada"] for item in alta}
        self.assertIn("ACME", formas)
        entrada = next(item for item in alta if item["forma_normalizada"] == "ACME")
        self.assertEqual(set(entrada["variantes_originais"]), {"ACME", "Acme", "ACME "})

    def test_clientes_distintos_nao_sao_unidos(self):
        detalhado = self.resultado["analise_clientes"]["detalhado_por_cliente"]
        self.assertIn("GLOBEX CORP", detalhado)
        self.assertIn("INITECH", detalhado)
        # Nenhum dos dois some ou vira alias um do outro.
        alta = self.resultado["analise_clientes"]["possiveis_aliases_alta_confianca"]
        for item in alta:
            self.assertNotIn("GLOBEX CORP", item["variantes_originais"])
            self.assertNotIn("INITECH", item["variantes_originais"])
        decisao = self.resultado["analise_clientes"]["possiveis_aliases_para_decisao_humana"]
        pares = {(d["cliente_a"], d["cliente_b"]) for d in decisao} | {(d["cliente_b"], d["cliente_a"]) for d in decisao}
        self.assertNotIn(("GLOBEX CORP", "INITECH"), pares)

    def test_pedido_sem_cliente_e_contabilizado(self):
        ac = self.resultado["analise_clientes"]
        self.assertEqual(ac["pedidos_sem_cliente"], 1)
        self.assertIn("ped5", ac["ids_pedidos_sem_cliente"])

    def test_cliente_usado_somente_em_lixeira_e_separado(self):
        # ACME tem pedidos ativos (ped1) e um pedido só na lixeira (ped7) --
        # ACME continua listado como "ativos e históricos", não "só lixeira".
        ac = self.resultado["analise_clientes"]
        self.assertIn("ACME", ac["clientes_usados_em_pedidos_ativos_ou_historicos"])
        self.assertNotIn("ACME", ac["clientes_usados_somente_em_lixeira"])

    # ------------------------------------------------------------------
    # CPDs: normalizar_cpd aplicada corretamente
    # ------------------------------------------------------------------

    def test_cpd_sem_extensao(self):
        pais = self.resultado["analise_cpds"]["pais"]
        self.assertIn("1000", pais)
        item = next(v for v in pais["1000"] if v["codigo_original"] == "1000")
        self.assertIsNone(item["extensao"])

    def test_cpd_com_extensao_ponto_1(self):
        pais = self.resultado["analise_cpds"]["pais"]
        item = next(v for v in pais["1000"] if v["codigo_original"] == "1000.1")
        self.assertEqual(item["extensao"], "1")

    def test_cpd_com_extensao_ponto_10(self):
        pais = self.resultado["analise_cpds"]["pais"]
        item = next(v for v in pais["1000"] if v["codigo_original"] == "1000.10")
        self.assertEqual(item["extensao"], "10")

    def test_cpd_com_zero_a_esquerda_preservado(self):
        pais = self.resultado["analise_cpds"]["pais"]
        self.assertIn("0500", pais)
        item = next(v for v in pais["0500"] if v["codigo_original"] == "0500.01")
        self.assertEqual(item["extensao"], "01")

    def test_cpd_com_multiplos_pontos_usa_ultimo(self):
        pais = self.resultado["analise_cpds"]["pais"]
        self.assertIn("A.B", pais)
        item = next(v for v in pais["A.B"] if v["codigo_original"] == "A.B.25")
        self.assertEqual(item["extensao"], "25")

    def test_cpd_com_sufixo_nao_numerico(self):
        acpd = self.resultado["analise_cpds"]
        self.assertIn("01234.A", acpd["exemplos_sufixo_nao_numerico"])
        pais = acpd["pais"]
        self.assertIn("01234.A", pais)  # pai é o código inteiro, sem extensão reconhecida

    def test_pai_ausente_e_detectado(self):
        conflitos = self.resultado["conflitos_descricao"]
        self.assertIn("5000", conflitos)
        self.assertEqual(conflitos["5000"]["categoria"], "D")
        self.assertTrue(conflitos["5000"]["pai_ausente"])

    def test_descricao_conflitante_entre_pedido_e_manual_cpd(self):
        cruz = self.resultado["cruzamento_pedidos_manual_cpd"]
        codigos = {item["codigo"] for item in cruz["codigos_com_descricao_diferente_pedido_vs_manual"]}
        self.assertIn("6000", codigos)

    # ------------------------------------------------------------------
    # Cruzamento pedidos x manual_cpd
    # ------------------------------------------------------------------

    def test_cpd_ligado_a_varios_clientes(self):
        vinc = self.resultado["vinculos_sugeridos"]
        self.assertIn("2000", vinc["cpds_pai_ligados_a_varios_clientes"])
        self.assertEqual(set(vinc["cpds_pai_ligados_a_varios_clientes"]["2000"]), {"GLOBEX CORP", "INITECH"})

    def test_cpd_usado_em_pedido_ausente_de_manual_cpd(self):
        cruz = self.resultado["cruzamento_pedidos_manual_cpd"]
        self.assertIn("4000", cruz["cpds_usados_e_ausentes_em_manual_cpd"])

    def test_cpd_de_manual_cpd_nunca_usado(self):
        cruz = self.resultado["cruzamento_pedidos_manual_cpd"]
        self.assertIn("7000", cruz["cpds_em_manual_cpd_nunca_usados_em_pedidos"])

    def test_pedido_sem_cpd(self):
        cruz = self.resultado["cruzamento_pedidos_manual_cpd"]
        self.assertIn("ped6", cruz["pedidos_sem_cpd"])

    def test_lixeira_separada_dos_pedidos_visiveis(self):
        cruz = self.resultado["cruzamento_pedidos_manual_cpd"]
        self.assertIn("9999", cruz["cpds_presentes_apenas_em_pedidos_na_lixeira"])
        # 9999 não deveria aparecer como "usado e existente" já que não está em manual_cpd,
        # mas o importante aqui é que a lixeira é contabilizada separadamente dos visíveis.
        self.assertNotIn("9999", cruz["cpds_usados_e_existentes_em_manual_cpd"])

    # ------------------------------------------------------------------
    # Script não modifica o banco analisado
    # ------------------------------------------------------------------

    def test_script_nao_modifica_o_banco_analisado(self):
        hash_antes = _sha256_arquivo(self.db_path)
        with sqlite3.connect(str(self.db_path)) as c:
            auditorias_antes = c.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
            versao_antes = self.dbm.get_schema_version(c)

        conn = analisador.abrir_somente_leitura(self.db_path)
        try:
            analisador.executar_analise(conn, set())
        finally:
            conn.close()

        hash_depois = _sha256_arquivo(self.db_path)
        with sqlite3.connect(str(self.db_path)) as c:
            auditorias_depois = c.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
            versao_depois = self.dbm.get_schema_version(c)

        self.assertEqual(hash_antes, hash_depois, "Banco analisado não pode mudar de conteúdo")
        self.assertEqual(auditorias_antes, auditorias_depois, "Análise não deve criar auditoria")
        self.assertEqual(versao_antes, versao_depois, "Análise não deve alterar schema_version")

    def test_conexao_somente_leitura_rejeita_escrita(self):
        conn = analisador.abrir_somente_leitura(self.db_path)
        try:
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute("INSERT INTO manual_cpd(codigo, descricao, updated_at) VALUES ('X','Y','Z')")
        finally:
            conn.close()

    def test_main_com_usar_copia_nao_altera_o_arquivo_original(self):
        pasta_saida = self.tmp_dir / "saida_cli"
        hash_antes = _sha256_arquivo(self.db_path)
        codigo = analisador.main([
            "--banco", str(self.db_path), "--usar-copia", "--saida", str(pasta_saida), "--formato", "json",
            "--config-clientes", str(self.config_clientes_path),
        ])
        self.assertEqual(codigo, 0)
        hash_depois = _sha256_arquivo(self.db_path)
        self.assertEqual(hash_antes, hash_depois)
        self.assertTrue((pasta_saida / "resumo_migracao_clientes_cpds.json").exists())

    def test_main_sem_usar_copia_cria_copia_propria_e_nao_toca_na_origem(self):
        origem = self.tmp_dir / "origem_para_copiar.sqlite3"
        origem_conn = sqlite3.connect(str(self.db_path))
        destino_conn = sqlite3.connect(str(origem))
        try:
            with destino_conn:
                origem_conn.backup(destino_conn)
        finally:
            destino_conn.close()
            origem_conn.close()
        hash_origem_antes = _sha256_arquivo(origem)
        pasta_saida = self.tmp_dir / "saida_cli_copia"
        codigo = analisador.main([
            "--banco", str(origem), "--saida", str(pasta_saida), "--formato", "json",
            "--config-clientes", str(self.config_clientes_path),
        ])
        self.assertEqual(codigo, 0)
        hash_origem_depois = _sha256_arquivo(origem)
        self.assertEqual(hash_origem_antes, hash_origem_depois, "main() sem --usar-copia não pode alterar --banco original")
        copias = list((pasta_saida / "_copias_temporarias").glob("*.sqlite3"))
        self.assertEqual(len(copias), 1)


if __name__ == "__main__":
    unittest.main()
