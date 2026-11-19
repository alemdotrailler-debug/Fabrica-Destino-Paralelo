"""Gera as imagens anime (grátis, rodando em CPU no GitHub Actions).

Uso: python -m fabrica.imagens videos/<slug> [--shorts] [--lote N --total M]
Cada cena vira trabalho/<slug>/img/<id>.jpg. Se o arquivo já existe, é pulado (cache).
Com FABRICA_IMAGENS=falso gera quadros de teste (só para testar a montagem sem modelo).
"""
import argparse, os, sys
from fabrica import plano, importadas, nuvem
from fabrica.comum import RAIZ, carregar_roteiro, log, pasta_trabalho

# Modelo escolhido após testes no GitHub: SD-Turbo (2 passos, ~36 s/imagem em 768x432 na CPU) deu o melhor visual
# chibi/anime colorido. Testados e descartados: Pollinations (marca d'água/instável), Anything-v5+LCM (composição ruim, 81 s).
CONFIG = dict(familia="turbo", repo="stabilityai/sd-turbo", passos=2, gs=0.0, taesd=False)


def carregar_modelo():
    import torch
    torch.set_num_threads(os.cpu_count() or 2)
    if CONFIG["familia"] == "turbo":
        from diffusers import AutoPipelineForText2Image
        return AutoPipelineForText2Image.from_pretrained(CONFIG["repo"], torch_dtype=torch.float32)
    from diffusers import StableDiffusionPipeline, LCMScheduler
    pipe = StableDiffusionPipeline.from_pretrained(CONFIG["repo"], torch_dtype=torch.float32, safety_checker=None)
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5")
    pipe.fuse_lora()
    if CONFIG.get("taesd"):
        from diffusers import AutoencoderTiny
        pipe.vae = AutoencoderTiny.from_pretrained("madebyollin/taesd", torch_dtype=torch.float32)
    return pipe


def gerar_uma(pipe, c):
    import torch
    kw = dict(num_inference_steps=c.get("passos", CONFIG["passos"]), guidance_scale=CONFIG["gs"], width=c["w"], height=c["h"],
              generator=torch.Generator().manual_seed(c["seed"]))
    if CONFIG["familia"] != "turbo":
        kw["negative_prompt"] = plano.NEGATIVO
    return pipe(c["prompt"], **kw).images[0]


def registrar(saida, modo, lote, novas):
    """Guarda de onde veio cada imagem (nuvem x local) para o relatório final."""
    import json
    f = os.path.join(saida, f"_fontes_{lote}_{modo}.json")
    d = json.load(open(f)) if os.path.exists(f) else {}
    d.update(novas)
    json.dump(d, open(f, "w"))


def quadro_falso(c):
    """Imagem de teste (sem modelo): degradê colorido + formas, diferente por cena."""
    import random
    from PIL import Image, ImageDraw
    r = random.Random(c["seed"])
    w, h = c["w"], c["h"]
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    c1 = (r.randint(40, 255), r.randint(0, 120), r.randint(0, 80))
    c2 = (r.randint(0, 120), r.randint(20, 120), r.randint(120, 255))
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(a * (1 - t) + b * t) for a, b in zip(c1, c2)))
    for _ in range(12):
        x, y, s = r.randint(0, w), r.randint(0, h), r.randint(20, 160)
        d.ellipse([x - s, y - s, x + s, y + s], fill=(r.randint(150, 255), r.randint(100, 255), r.randint(0, 120)))
    d.text((20, 20), c["id"], fill=(255, 255, 255))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--shorts", action="store_true")
    ap.add_argument("--miniaturas", action="store_true")
    ap.add_argument("--nuvem", action="store_true", help="só a API da Cloudflare (não carrega o modelo local)")
    ap.add_argument("--local", action="store_true", help="só o modelo local (pula a Cloudflare)")
    ap.add_argument("--contar", action="store_true", help="só diz quantas imagens ainda faltam neste lote")
    ap.add_argument("--lote", type=int, default=0)
    ap.add_argument("--total", type=int, default=1)
    a = ap.parse_args()
    R = carregar_roteiro(a.pasta)
    modo = "shorts" if a.shorts else ("miniaturas" if a.miniaturas else "longo")
    saida = os.path.join(pasta_trabalho(R.SLUG), "img")
    os.makedirs(saida, exist_ok=True)
    todas = importadas.faltantes(R, a.pasta, modo)          # o que você importou não precisa ser gerado
    minhas = [c for i, c in enumerate(todas) if i % a.total == a.lote]

    def faltam():
        return [c for c in minhas if not os.path.exists(os.path.join(saida, c["id"] + ".jpg"))]

    if a.contar:
        n = len(faltam())
        print(f"restam={n}")
        if os.environ.get("GITHUB_OUTPUT"):
            open(os.environ["GITHUB_OUTPUT"], "a").write(f"restam={n}\n")
        return
    pendentes = faltam()
    log(f"{len(minhas)} imagens neste lote ({len(pendentes)} por fazer)")
    falso = os.environ.get("FABRICA_IMAGENS") == "falso"

    fontes = {}
    # 1) Cloudflare (grátis, FLUX): rápida e de melhor qualidade, mas com cota diária
    if pendentes and not falso and not a.local and nuvem.disponivel():
        log("gerando pela Cloudflare (FLUX)")
        for i, c in enumerate(pendentes):
            try:
                nuvem.gerar(c["prompt"], c["w"], c["h"], c.get("passos", 4)).save(
                    os.path.join(saida, c["id"] + ".jpg"), quality=95)
                fontes[c["id"]] = "nuvem"
                log(f"nuvem {i+1}/{len(pendentes)} {c['id']}")
            except nuvem.CotaAcabou as e:
                log("cota diária da Cloudflare acabou:", e)
                fontes["_erro_nuvem"] = "COTA: " + str(e)[:300]
                break
            except nuvem.ErroNuvem as e:
                log("Cloudflare falhou nesta imagem:", e)
                fontes["_erro_nuvem"] = str(e)[:300]
                if "acesso negado" in str(e):
                    break
    elif pendentes and not a.local and not falso:
        log("Cloudflare não configurada (faltam CF_ACCOUNT_ID / CF_API_TOKEN): usando só o modelo local")
    registrar(saida, modo, a.lote, fontes)
    if a.nuvem:
        return

    # 2) modelo local (SD-Turbo na CPU) para o que sobrou
    pendentes = faltam()
    pipe = None if falso or not pendentes else carregar_modelo()
    for i, c in enumerate(pendentes):
        img = quadro_falso(c) if falso else gerar_uma(pipe, c)
        img.save(os.path.join(saida, c["id"] + ".jpg"), quality=95)
        fontes[c["id"]] = "local"
        log(f"imagem {i+1}/{len(pendentes)} {c['id']}")
    registrar(saida, modo, a.lote, fontes)


if __name__ == "__main__":
    main()
