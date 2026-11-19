"""Usado pelo GitHub Actions: lê os pedidos e diz quais vídeos e quantos lotes de imagens gerar.

Uso: python -m fabrica.descobrir "<pedidos separados por espaço>"   (saída JSON em duas linhas)
"""
import json, math, os, sys
from fabrica import plano, importadas
from fabrica.comum import RAIZ, carregar_roteiro

POR_LOTE = 18  # imagens por computador


def main(pedidos):
    itens, lotes = [], []
    for p in pedidos.split():
        slug, _, modo = p.partition(":")
        modo = modo if modo in ("shorts", "miniaturas") else "longo"
        R = carregar_roteiro(os.path.join(RAIZ, "videos", slug))
        n = len(importadas.faltantes(R, os.path.join(RAIZ, "videos", slug), modo))   # só o que falta gerar
        total = min(8, math.ceil(n / POR_LOTE))
        nome = f"{slug}-{modo}"
        itens.append(dict(slug=slug, modo=modo, nome=nome, imagens=n))
        for s in range(total):
            lotes.append(dict(slug=slug, modo=modo, nome=nome, lote=s, total=total))
    print(json.dumps(itens))
    print(json.dumps(lotes))


if __name__ == "__main__":
    main(sys.argv[1])
