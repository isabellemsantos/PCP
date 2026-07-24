"""Testes de scripts/config_clientes_migracao.py (carregamento e validação
da configuração local de regras de clientes) e verificações estáticas de
que nenhum nome real de cliente ficou hardcoded nos scripts de migração.

Todos os dados usados aqui são fictícios. Não usa o arquivo real local
(config_local/regras_clientes_migracao.json) em nenhum teste -- só arquivos
temporários próprios ou o modelo versionado (.example.json), que também é
fictício.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.config_clientes_migracao as config_clientes

# Nomes FICTÍCIOS usados só para exercitar a checagem estática de que nenhum
# nome real de cliente fica hardcoded nos scripts -- os nomes reais em si só
# existem em config_local/regras_clientes_migracao.json, que é ignorado pelo
# Git e nunca lido por este arquivo de teste.
# "HONDA"/"Honda" sozinho fica FORA desta lista de propósito: virou também
# o nome estrutural do grupo (config.grupo_honda, grupos_clientes.nome="Honda",
# já existente desde a migração v1->v2) -- checar isso geraria falso-positivo
# contra código legítimo. A ausência do ROSTER hardcoded (que clientes
# específicos formam esse grupo) já é verificada em
# test_scripts_nao_definem_mais_constantes_de_clientes_reais.
_NOMES_TESTE_PROIBIDOS = (
    "METALFICTA", "YAMAFICTA", "INDUSFICTA", "INDUSFÍCTA",
    "ACME ACIO", "ACME (ACIO)", "Z TECH", "Z-TECH",
    "PLASTICOS FICTA", "PLASTICOS FÍCTA", "SOLARTECH", "NOVATRON", "GRUTAFICTA",
)

_ARQUIVOS_SEM_DADOS_REAIS = (
    ROOT / "scripts" / "migrar_clientes_cpds.py",
    ROOT / "scripts" / "analisar_migracao_clientes_cpds.py",
    ROOT / "scripts" / "analisar_lista_oficial_cpds.py",
    ROOT / "scripts" / "config_clientes_migracao.py",
)


class ConfigClientesMigracaoTestCase(unittest.TestCase):
    tmp_dir: Path

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = Path(tempfile.mkdtemp(prefix="pcp_teste_config_clientes_"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def _escrever(self, nome: str, conteudo) -> Path:
        caminho = self.tmp_dir / nome
        if isinstance(conteudo, str):
            caminho.write_text(conteudo, encoding="utf-8")
        else:
            caminho.write_text(json.dumps(conteudo, ensure_ascii=False), encoding="utf-8")
        return caminho

    # ------------------------------------------------------------------
    # Carregamento e validação
    # ------------------------------------------------------------------

    def test_arquivo_inexistente_gera_erro_claro(self):
        caminho = self.tmp_dir / "nao_existe.json"
        with self.assertRaises(FileNotFoundError) as ctx:
            config_clientes.carregar_config_clientes(caminho)
        self.assertIn(str(caminho), str(ctx.exception))
        self.assertIn("config-clientes", str(ctx.exception).lower().replace("_", "-"))

    def test_json_invalido_e_rejeitado(self):
        caminho = self._escrever("invalido.json", "{isso nao e json valido")
        with self.assertRaises(config_clientes.ConfigClientesInvalida):
            config_clientes.carregar_config_clientes(caminho)

    def test_estrutura_incompleta_e_rejeitada(self):
        caminho = self._escrever("incompleto.json", {"grupo_honda": []})
        with self.assertRaises(config_clientes.ConfigClientesInvalida):
            config_clientes.carregar_config_clientes(caminho)

    def test_tipo_errado_em_aliases_e_rejeitado(self):
        caminho = self._escrever("tipo_errado.json", {
            "grupo_honda": [], "aliases": "isso deveria ser um objeto", "placeholders_invalidos": [],
        })
        with self.assertRaises(config_clientes.ConfigClientesInvalida):
            config_clientes.carregar_config_clientes(caminho)

    def test_nao_e_objeto_json_e_rejeitado(self):
        caminho = self._escrever("lista.json", ["nao", "e", "um", "objeto"])
        with self.assertRaises(config_clientes.ConfigClientesInvalida):
            config_clientes.carregar_config_clientes(caminho)

    def test_grupo_e_carregado_do_arquivo(self):
        caminho = self._escrever("valido.json", {
            "grupo_honda": ["CLIENTE FICTICIO GRUPO A"],
            "aliases": {},
            "placeholders_invalidos": [],
        })
        config = config_clientes.carregar_config_clientes(caminho)
        self.assertEqual(config.grupo_honda, {"CLIENTE FICTICIO GRUPO A"})

    def test_aliases_sao_carregados_do_arquivo(self):
        caminho = self._escrever("valido.json", {
            "grupo_honda": [],
            "aliases": {"CLIENTE FICTICIO CANONICO": ["CLIENTE FICTÍCIO VARIANTE"]},
            "placeholders_invalidos": [],
        })
        config = config_clientes.carregar_config_clientes(caminho)
        self.assertEqual(config.aliases, {"CLIENTE FICTICIO CANONICO": ["CLIENTE FICTÍCIO VARIANTE"]})

    def test_placeholders_sao_carregados_do_arquivo(self):
        caminho = self._escrever("valido.json", {
            "grupo_honda": [], "aliases": {}, "placeholders_invalidos": ["***", "SEM_INFORMACAO_FICTICIA"],
        })
        config = config_clientes.carregar_config_clientes(caminho)
        self.assertIn("***", config.placeholders_invalidos)
        self.assertIn("SEM_INFORMACAO_FICTICIA", config.placeholders_invalidos)

    def test_acentos_e_nomes_originais_sao_preservados(self):
        caminho = self._escrever("valido.json", {
            "grupo_honda": ["CLIENTE ÁCÊNTUADO"],
            "aliases": {"CLIENTE ÁCÊNTUADO": ["Cliente Ácêntuado Variante"]},
            "placeholders_invalidos": [],
        })
        config = config_clientes.carregar_config_clientes(caminho)
        self.assertIn("CLIENTE ÁCÊNTUADO", config.grupo_honda)
        self.assertEqual(config.aliases["CLIENTE ÁCÊNTUADO"], ["Cliente Ácêntuado Variante"])

    def test_hash_e_sha256_do_arquivo_e_reproduzivel(self):
        caminho = self._escrever("valido.json", {"grupo_honda": [], "aliases": {}, "placeholders_invalidos": []})
        config1 = config_clientes.carregar_config_clientes(caminho)
        config2 = config_clientes.carregar_config_clientes(caminho)
        self.assertEqual(config1.hash_sha256, config2.hash_sha256)
        self.assertEqual(len(config1.hash_sha256), 64)  # hex de sha256

    def test_hash_muda_se_conteudo_muda(self):
        caminho = self._escrever("valido.json", {"grupo_honda": [], "aliases": {}, "placeholders_invalidos": []})
        config1 = config_clientes.carregar_config_clientes(caminho)
        self._escrever("valido.json", {"grupo_honda": ["OUTRO"], "aliases": {}, "placeholders_invalidos": []})
        config2 = config_clientes.carregar_config_clientes(caminho)
        self.assertNotEqual(config1.hash_sha256, config2.hash_sha256)

    # ------------------------------------------------------------------
    # Nenhum nome real hardcoded no código versionado
    # ------------------------------------------------------------------

    def test_nenhum_nome_real_hardcoded_nos_scripts(self):
        for caminho in _ARQUIVOS_SEM_DADOS_REAIS:
            texto = caminho.read_text(encoding="utf-8").upper()
            for nome_teste in _NOMES_TESTE_PROIBIDOS:
                self.assertNotIn(
                    nome_teste.upper(), texto,
                    f"Nome de teste '{nome_teste}' encontrado hardcoded em {caminho.relative_to(ROOT)}",
                )

    def test_scripts_nao_definem_mais_constantes_de_clientes_reais(self):
        for caminho in (ROOT / "scripts" / "migrar_clientes_cpds.py", ROOT / "scripts" / "analisar_migracao_clientes_cpds.py"):
            texto = caminho.read_text(encoding="utf-8")
            self.assertNotIn("ALIASES_CONHECIDOS", texto)
            self.assertNotIn("HONDA_GRUPO_HARDCODED", texto)

    # ------------------------------------------------------------------
    # Modelo versionável (.example.json) só com dados fictícios
    # ------------------------------------------------------------------

    def test_arquivo_example_e_valido_e_so_tem_dados_ficticios(self):
        caminho = ROOT / "config_local" / "regras_clientes_migracao.example.json"
        self.assertTrue(caminho.exists(), "config_local/regras_clientes_migracao.example.json deveria existir e ser versionado")
        config = config_clientes.carregar_config_clientes(caminho)

        texto_completo = " ".join([
            " ".join(config.grupo_honda),
            " ".join(config.aliases.keys()),
            " ".join(v for variantes in config.aliases.values() for v in variantes),
        ]).upper()
        for nome_teste in _NOMES_TESTE_PROIBIDOS:
            self.assertNotIn(nome_teste.upper(), texto_completo, f"Nome de teste '{nome_teste}' encontrado no arquivo example")

    def test_arquivo_real_local_esta_ignorado_pelo_git(self):
        # Só confirma que, SE o arquivo real existir localmente, ele nunca
        # seria commitado -- não depende do conteúdo dele, não lê o conteúdo.
        import subprocess
        caminho_real = ROOT / "config_local" / "regras_clientes_migracao.json"
        if not caminho_real.exists():
            self.skipTest("arquivo real local não existe neste ambiente")
        resultado = subprocess.run(
            ["git", "check-ignore", str(caminho_real)], cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(resultado.returncode, 0, "config_local/regras_clientes_migracao.json deveria estar ignorado pelo Git")


if __name__ == "__main__":
    unittest.main()
