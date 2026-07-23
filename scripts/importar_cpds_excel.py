"""Importação administrativa e controlada de CPDs a partir do Excel.

Diferente do antigo comportamento automático do servidor (que reimportava
dados_pcp.xlsx em todo início, mesmo sem nenhuma mudança), este script só
importa quando alguém executa e confirma explicitamente. Não inicia o
Flask, não roda migrações, e não faz nada sozinho se for apenas importado
como módulo — só quando executado diretamente com --confirmar.

Uso:
    .venv\\Scripts\\python.exe scripts\\importar_cpds_excel.py --confirmar
    .venv\\Scripts\\python.exe scripts\\importar_cpds_excel.py --confirmar --excel caminho\\outro.xlsx

Sem --confirmar, o script só mostra o que faria (dry-run) e não altera nada.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ATOR_IMPORTACAO_ADMINISTRATIVA = "Sistema/Importação administrativa"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Importação administrativa de CPDs a partir do Excel.")
    parser.add_argument(
        "--excel",
        type=Path,
        default=None,
        help="Caminho do Excel a importar (padrão: dados_pcp.xlsx na raiz do projeto).",
    )
    parser.add_argument(
        "--confirmar",
        action="store_true",
        help="Confirma explicitamente a execução da importação. Sem isso, o script não altera nada.",
    )
    return parser.parse_args(argv)


def executar(excel_path: Path, confirmar: bool) -> dict:
    """Executa (ou simula, se confirmar=False) a importação administrativa de CPDs.

    Retorna um resumo com contagens antes/depois. Não inicia Flask nem roda
    migrações — só abre a conexão via servidor_pcp.conn() para contar
    manual_cpd e chama a função oficial import_cpds_from_excel_file().
    """
    import servidor_pcp  # import tardio: só dentro de executar(), nunca ao só carregar este módulo

    if not excel_path.exists():
        raise FileNotFoundError(f"Excel não encontrado: {excel_path}")

    with servidor_pcp.conn() as c:
        total_antes = c.execute("SELECT COUNT(*) FROM manual_cpd").fetchone()[0]

    if not confirmar:
        return {
            "executado": False,
            "motivo": "Rode novamente com --confirmar para aplicar de verdade.",
            "excel": str(excel_path),
            "total_cpds_antes": total_antes,
        }

    resultado_import = servidor_pcp.import_cpds_from_excel_file(excel_path, actor=ATOR_IMPORTACAO_ADMINISTRATIVA)
    processados = resultado_import["imported"]["cpds"]

    with servidor_pcp.conn() as c:
        total_depois = c.execute("SELECT COUNT(*) FROM manual_cpd").fetchone()[0]

    novos = max(0, total_depois - total_antes)
    atualizados = max(0, processados - novos)

    return {
        "executado": True,
        "excel": str(excel_path),
        "ator": ATOR_IMPORTACAO_ADMINISTRATIVA,
        "total_cpds_antes": total_antes,
        "total_cpds_depois": total_depois,
        "processados_pelo_excel": processados,
        "novos": novos,
        "atualizados_ou_ignorados": atualizados,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    excel_path = args.excel or (ROOT / "dados_pcp.xlsx")

    if not args.confirmar:
        print("Modo dry-run (sem --confirmar): nada será alterado.")

    try:
        resultado = executar(excel_path, args.confirmar)
    except Exception as exc:
        print(f"ERRO: {exc}")
        return 1

    for chave, valor in resultado.items():
        print(f"{chave}: {valor}")

    if not resultado["executado"]:
        print("\nNada foi importado. Use --confirmar para aplicar de verdade.")
        return 0

    print("\nImportação concluída.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
