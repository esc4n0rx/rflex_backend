#!/usr/bin/env python3
"""
Script de execução do servidor RFlex License Server.

Uso:
    python run.py                    # Modo desenvolvimento
    python run.py --production       # Modo produção
"""
import sys
import argparse
from pathlib import Path

# Adiciona diretório ao path
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="RFlex License Server"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Executar em modo produção (sem reload)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host para bind (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Porta para bind (default: 8000)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Número de workers (produção apenas, default: 1)"
    )

    args = parser.parse_args()

    import uvicorn
    from app.core.config import settings

    # Sobrescreve config com args de CLI
    host = args.host
    port = args.port
    reload = not args.production

    if args.production:
        print("=" * 60)
        print("[*] RFlex License Server - Modo Produção")
        print("=" * 60)
        print(f"[+] Host: {host}")
        print(f"[+] Porta: {port}")
        print(f"[+] Workers: {args.workers}")
        print(f"[+] Ambiente: {settings.environment}")
        print("=" * 60)
        print()

        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            workers=args.workers,
            log_level="info",
            access_log=True
        )
    else:
        print("=" * 60)
        print("[*] RFlex License Server - Modo Desenvolvimento")
        print("=" * 60)
        print(f"[+] Host: {host}")
        print(f"[+] Porta: {port}")
        print(f"[+] Auto-reload: Ativado")
        print(f"[+] Docs: http://{host}:{port}/docs")
        print("=" * 60)
        print()

        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="debug"
        )


if __name__ == "__main__":
    main()
