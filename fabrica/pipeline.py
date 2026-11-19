"""Fábrica do Destino Paralelo.

Uso:  python -m fabrica.pipeline videos/<slug> [--shorts]
Pré-requisito: as imagens já geradas em trabalho/<slug>/img (python -m fabrica.imagens ...).
Etapas: narração -> tempos -> legendas -> trilha -> edição (FFmpeg) -> miniaturas -> saida/<slug>/*.json
"""
import argparse, json, os, shutil
from fabrica import plano, narracao, legendas, audio, render, miniatura
from fabrica.comum import RAIZ, carregar_roteiro, log, pasta_trabalho


def mmss(x):
    x = int(x)
    return f"{x // 60}:{x % 60:02d}"


def montar_tempos(cenas, narr):
    t, tempos = 0.0, []
    for c, n in zip(cenas, narr):
        tempos.append(dict(audio=n["audio"], t0=t, t1=t + n["dur"],
                           palavras=[(w, t + a, t + b) for (w, a, b) in n["palavras"]]))
        t += n["dur"]
    return tempos


def blocos_info(cenas, tempos):
    B = {}
    for c, t in zip(cenas, tempos):
        b = B.setdefault(c["bloco"], dict(nome=c["bnome"], titulo=c["btitulo"], t0=t["t0"], t1=t["t1"], cap=None))
        b["t1"] = t["t1"]
    return [B[k] for k in sorted(B)]


def produzir(R, prod, pasta, saida_mp4):
    W, H = plano.SAIDA[prod["orient"]]
    vertical = prod["orient"] == "v"
    cenas = prod["cenas"]
    log(f"produzindo {prod['id']}: {len(cenas)} cenas")
    narr = narracao.narrar(R, cenas, pasta)
    tempos = montar_tempos(cenas, narr)
    bl = blocos_info(cenas, tempos)
    ass_txt = legendas.montar_ass(W, H, cenas, tempos, bl, vertical)
    ass = os.path.join(pasta, prod["id"] + ".ass")
    open(ass, "w", encoding="utf-8").write(ass_txt)
    wav = audio.mixar(cenas, tempos, os.path.join(pasta, prod["id"] + ".wav"), tempos[-1]["t1"])
    render.renderizar(cenas, tempos, os.path.join(pasta, "img"), W, H, ass, wav, saida_mp4, pasta, vertical)
    return tempos, bl


def descricao_longa(R, bl):
    caps = []
    for k, b in enumerate(bl):
        if b["titulo"]:
            nome = f"{b['nome'].title()} · {b['titulo'].capitalize()}"
        else:
            nome = (R.BLOCOS[k].get("capitulo") or ("O gancho" if k == 0 else "O desfecho"))
        caps.append(f"{mmss(b['t0'])} {nome}")
    D = getattr(R, "DESCRICAO", {})
    partes = [D.get("gancho", ""), D.get("resumo", ""), "⏱️ CAPÍTULOS\n" + "\n".join(caps),
              "🔔 Se inscreva no canal e ative o sininho para não perder nenhum \"E se você...\".",
              D.get("pergunta", "💬 Qual escolha você faria? Conta aqui nos comentários!"),
              ("▶️ Próximo vídeo: " + D["proximo"]) if D.get("proximo") else "",
              "⚠️ Canal independente, sem associação oficial com as franquias citadas. Conteúdo de fã, feito para entretenimento.",
              " ".join(D.get("hashtags", ["#eseVocê", "#anime", "#historiaalternativa"]))]
    return "\n\n".join(p for p in partes if p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--shorts", action="store_true")
    a = ap.parse_args()
    R = carregar_roteiro(a.pasta)
    pasta = pasta_trabalho(R.SLUG)
    saida = os.path.join(RAIZ, "saida", R.SLUG)
    os.makedirs(saida, exist_ok=True)
    if not a.shorts:
        prod = plano.producoes(R, "longo")[0]
        mp4 = os.path.join(pasta, R.SLUG + ".mp4")
        tempos, bl = produzir(R, prod, pasta, mp4)
        thumbs = []
        for i, t in enumerate(getattr(R, "THUMBS", [])):
            fundo = os.path.join(pasta, "img", f"{R.SLUG}_thumb_{i}.jpg")
            letra = "AB"[i]
            f = os.path.join(saida, f"thumb_{letra}.jpg")
            miniatura.compor(fundo, t["linha1"], t["titulo"], t.get("etiqueta", ""), f)
            thumbs.append(os.path.basename(f))
        info = dict(slug=R.SLUG, titulo=R.TITULO, titulos=getattr(R, "TITULOS", [R.TITULO]),
                    descricao=descricao_longa(R, bl), tags=getattr(R, "TAGS", []),
                    comentario_fixado=getattr(R, "COMENTARIO", ""), duracao=mmss(tempos[-1]["t1"]),
                    thumbs=thumbs, video_url="")
        json.dump(info, open(os.path.join(saida, "info.json"), "w"), indent=1, ensure_ascii=False)
        log("pronto:", mp4, info["duracao"])
    else:
        for i, prod in enumerate(plano.producoes(R, "shorts"), 1):
            mp4 = os.path.join(pasta, prod["id"] + ".mp4")
            tempos, _ = produzir(R, prod, pasta, mp4)
            s = prod["short"]
            desc = s.get("descricao") or (f"{s.get('titulo', '')}\n\n▶️ Vídeo completo no canal: " + getattr(R, "TITULO", "")
                                          + "\n\n🔔 Se inscreva para mais \"E se você...\"\n\n"
                                          + "⚠️ Canal independente, sem associação oficial com as franquias.\n#shorts #anime #eseVocê")
            info = dict(slug=R.SLUG, titulo=s.get("titulo", prod["id"]), descricao=desc,
                        tags=getattr(R, "TAGS", [])[:12], duracao=mmss(tempos[-1]["t1"]), video_url="")
            json.dump(info, open(os.path.join(saida, f"short_{i}.json"), "w"), indent=1, ensure_ascii=False)
            log("short pronto:", mp4)


if __name__ == "__main__":
    main()
