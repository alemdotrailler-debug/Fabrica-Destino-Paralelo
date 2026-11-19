"""Gera as imagens anime (grátis, rodando em CPU no GitHub Actions).

Uso: python -m fabrica.imagens videos/<slug> [--shorts] [--lote N --total M]
Cada cena vira trabalho/<slug>/img/<id>.jpg. Se o arquivo já existe, é pulado (cache).
Com FABRICA_IMAGENS=falso gera quadros de teste (só para testar a montagem sem modelo).
"""
import argparse, os, sys
from fabrica import plano
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
    kw = dict(num_inference_steps=CONFIG["passos"], guidance_scale=CONFIG["gs"], width=c["w"], height=c["h"],
              generator=torch.Generator().manual_seed(c["seed"]))
    if CONFIG["familia"] != "turbo":
        kw["negative_prompt"] = plano.NEGATIVO
    return pipe(c["prompt"], **kw).images[0]


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
    ap.add_argument("--lote", type=int, default=0)
    ap.add_argument("--total", type=int, default=1)
    a = ap.parse_args()
    R = carregar_roteiro(a.pasta)
    modo = "shorts" if a.shorts else "longo"
    saida = os.path.join(pasta_trabalho(R.SLUG), "img")
    os.makedirs(saida, exist_ok=True)
    todas = plano.todas_as_imagens(R, modo)
    minhas = [c for i, c in enumerate(todas) if i % a.total == a.lote]
    pendentes = [c for c in minhas if not os.path.exists(os.path.join(saida, c["id"] + ".jpg"))]
    log(f"{len(minhas)} imagens neste lote ({len(pendentes)} por fazer)")
    falso = os.environ.get("FABRICA_IMAGENS") == "falso"
    pipe = None if falso or not pendentes else carregar_modelo()
    for i, c in enumerate(pendentes):
        img = quadro_falso(c) if falso else gerar_uma(pipe, c)
        img.save(os.path.join(saida, c["id"] + ".jpg"), quality=95)
        log(f"imagem {i+1}/{len(pendentes)} {c['id']}")


if __name__ == "__main__":
    main()
