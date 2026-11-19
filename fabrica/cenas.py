"""Lista de cenas (storyboard) para você gerar as imagens em outra ferramenta (ex.: Tubefy).

Uso: python -m fabrica.cenas videos/<slug>   -> escreve videos/<slug>/cenas.txt
Cada cena = 1 imagem. Nomeie o arquivo com o número da cena (001.png, 002.png...) e coloque em videos/<slug>/imagens/.
Só traz a narração e o clima da cena (não descreve visual de personagens).
"""
import os, sys
from fabrica import plano
from fabrica.comum import RAIZ, carregar_roteiro


def main(pasta):
    R = carregar_roteiro(pasta)
    L = [f"CENAS DO VÍDEO: {R.TITULO}", "Estilo do canal: anime chibi colorido, 16:9 (horizontal). Short: 9:16 (vertical).",
         "Nomeie cada imagem com o número da cena: 001.png, 002.png ... e envie para videos/" + R.SLUG + "/imagens/",
         "Dica: se quiser menos imagens, faça só algumas cenas — as cenas sem imagem repetem a anterior.", ""]
    for p in plano.producoes(R, "longo") + plano.producoes(R, "shorts"):
        L.append("=" * 60)
        L.append(("VÍDEO LONGO" if p["orient"] == "h" else "SHORT " + p["id"].rsplit("_", 1)[1]) +
                 f" — {len(p['cenas'])} cenas")
        if p["orient"] == "v":
            L.append(f"(imagens em videos/{R.SLUG}/imagens/short_{p['id'].rsplit('_', 1)[1]}/ — formato vertical 9:16)")
        bloco = None
        for i, c in enumerate(p["cenas"], 1):
            if c["bnome"] != bloco and p["orient"] == "h":
                bloco = c["bnome"]
                L.append(f"\n[{c['bnome']}{' — ' + c['btitulo'] if c['btitulo'] else ''}]  clima: {c['humor']}")
            L.append(f"{i:03d}  {c['texto']}")
        L.append("")
    out = os.path.join(pasta, "cenas.txt")
    open(out, "w", encoding="utf-8").write("\n".join(L))
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
