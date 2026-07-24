"""Carrega a configuração LOCAL (nunca versionada) de regras de negócio de
clientes usadas na migração: quais clientes formam o grupo Honda, quais
grafias são aliases de qual cliente canônico, e quais valores de cliente
são tratados como "não informado" (placeholders).

Nenhum nome real de cliente fica hardcoded em código versionado -- essas
regras vivem só num arquivo JSON local (ex.: config_local/regras_clientes_migracao.json,
ignorado pelo Git; ver config_local/regras_clientes_migracao.example.json
pro modelo, que contém só dados fictícios).

Nunca cai silenciosamente numa configuração vazia: arquivo ausente,
malformado ou com estrutura incompleta sempre levanta uma exceção clara,
nunca é tratado como "config vazia = sem regras".
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

_CHAVES_OBRIGATORIAS = ("grupo_honda", "aliases", "placeholders_invalidos")


class ConfigClientesInvalida(ValueError):
    """Levantada quando o arquivo existe mas o conteúdo não é uma
    configuração de clientes válida (JSON malformado ou estrutura incompleta/
    com tipos errados)."""


class ConfigClientes:
    """Regras de clientes já carregadas e validadas, prontas pra uso.

    - grupo_honda: set de nomes canônicos que pertencem ao grupo Honda.
    - aliases: dict {cliente_canonico: [grafias alternativas]}, exatamente
      como veio do arquivo (preserva acentos/caixa originais).
    - placeholders_invalidos: set de valores (já normalizados p/ maiúsculas)
      tratados como "cliente não informado".
    - caminho / hash_sha256: só o suficiente pra rastreabilidade em
      relatórios -- NUNCA o conteúdo completo do arquivo.
    """

    __slots__ = ("grupo_honda", "aliases", "placeholders_invalidos", "caminho", "hash_sha256")

    def __init__(self, grupo_honda: set[str], aliases: dict[str, list[str]], placeholders_invalidos: set[str], caminho: str, hash_sha256: str):
        self.grupo_honda = grupo_honda
        self.aliases = aliases
        self.placeholders_invalidos = placeholders_invalidos
        self.caminho = caminho
        self.hash_sha256 = hash_sha256


def hash_arquivo_config(caminho: Path) -> str:
    """SHA-256 do arquivo de configuração -- é isso (nunca o conteúdo) que
    deve ir em relatórios/logs, pra rastrear qual configuração foi usada sem
    expor nomes reais de clientes."""
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def carregar_config_clientes(caminho: Path) -> ConfigClientes:
    """Lê, valida e devolve a configuração de clientes em `caminho`.

    Levanta:
      FileNotFoundError -- arquivo não existe (mensagem já explica como
        criar um, apontando pro .example.json).
      ConfigClientesInvalida -- arquivo existe mas não é um JSON válido, ou
        não tem a estrutura esperada (chave ausente ou tipo errado).
    """
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração de clientes não encontrado: {caminho}\n"
            "Use --config-clientes apontando pro seu arquivo local (ex.: "
            "config_local/regras_clientes_migracao.json). Veja o modelo em "
            "config_local/regras_clientes_migracao.example.json."
        )

    texto = caminho.read_text(encoding="utf-8")
    try:
        bruto = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ConfigClientesInvalida(f"JSON inválido em {caminho}: {exc}") from exc

    if not isinstance(bruto, dict):
        raise ConfigClientesInvalida(f"Configuração de clientes precisa ser um objeto JSON: {caminho}")

    faltando = [chave for chave in _CHAVES_OBRIGATORIAS if chave not in bruto]
    if faltando:
        raise ConfigClientesInvalida(
            f"Configuração de clientes incompleta em {caminho}: faltam as chaves {faltando}"
        )

    grupo_honda_bruto = bruto["grupo_honda"]
    aliases_bruto = bruto["aliases"]
    placeholders_bruto = bruto["placeholders_invalidos"]

    if not isinstance(grupo_honda_bruto, list) or not all(isinstance(x, str) for x in grupo_honda_bruto):
        raise ConfigClientesInvalida(f"'grupo_honda' deve ser uma lista de strings em {caminho}")

    if not isinstance(aliases_bruto, dict) or not all(
        isinstance(canonico, str) and isinstance(variantes, list) and all(isinstance(v, str) for v in variantes)
        for canonico, variantes in aliases_bruto.items()
    ):
        raise ConfigClientesInvalida(f"'aliases' deve ser um objeto {{canonico: [variantes]}} de strings em {caminho}")

    if not isinstance(placeholders_bruto, list) or not all(isinstance(x, str) for x in placeholders_bruto):
        raise ConfigClientesInvalida(f"'placeholders_invalidos' deve ser uma lista de strings em {caminho}")

    return ConfigClientes(
        grupo_honda=set(grupo_honda_bruto),
        aliases={canonico: list(variantes) for canonico, variantes in aliases_bruto.items()},
        placeholders_invalidos={str(p).strip().upper() for p in placeholders_bruto},
        caminho=str(caminho),
        hash_sha256=hash_arquivo_config(caminho),
    )
