"""Miniatura 1280x720 no estilo do canal: título laranja grande com contorno, selo escuro com número, personagem à direita."""
import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from fabrica.comum import FONTES

W, H = 1280, 720


def _fonte(nome, tam):
    return ImageFont.truetype(os.path.join(FONTES, nome), tam)


def _gradiente(tam, topo, base):
    g = Image.new("RGB", tam)
    d = ImageDraw.Draw(g)
    for y in range(tam[1]):
        t = y / max(1, tam[1] - 1)
        d.line([(0, y), (tam[0], y)], fill=tuple(int(a * (1 - t) + b * t) for a, b in zip(topo, base)))
    return g


def _texto_grad(txt, tam, topo=(255, 236, 70), base=(255, 120, 10), contorno=16, inclinar=-0.10):
    f = _fonte("Anton-Regular.ttf", tam)
    x0, y0, x1, y1 = f.getbbox(txt, stroke_width=contorno)
    w, h = x1 - x0 + 40, y1 - y0 + 40
    cam = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    d.text((20 - x0, 20 - y0), txt, font=f, fill=(0, 0, 0, 255), stroke_width=contorno, stroke_fill=(0, 0, 0, 255))
    mascara = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mascara).text((20 - x0, 20 - y0), txt, font=f, fill=255)
    cam.paste(_gradiente((w, h), topo, base), (0, 0), mascara)
    sombra = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sombra.paste((0, 0, 0, 170), (8, 10), cam.split()[3])
    out = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(5)), cam)
    return out.transform(out.size, Image.AFFINE, (1, inclinar, 0 if inclinar > 0 else -inclinar * h, 0, 1, 0), Image.BICUBIC)


def _ampulheta(d, x, y, s, cor):
    d.polygon([(x, y), (x + s, y), (x + s / 2, y + s / 2)], fill=cor)
    d.polygon([(x, y + s), (x + s, y + s), (x + s / 2, y + s / 2)], fill=cor)
    d.rectangle([x - 3, y - 5, x + s + 3, y], fill=cor)
    d.rectangle([x - 3, y + s, x + s + 3, y + s + 5], fill=cor)


def compor(fundo, linha1, titulo, etiqueta, saida):
    im = Image.open(fundo).convert("RGB").resize((W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2.5, percent=120, threshold=2))
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.15)).enhance(1.08).convert("RGBA")
    # escurece o lado esquerdo para o texto aparecer
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(sombra)
    for x in range(W):
        a = int(max(0, 150 * (1 - x / (W * 0.62))))
        d.line([(x, 0), (x, H)], fill=(0, 0, 0, a))
    im = Image.alpha_composite(im, sombra)
    d = ImageDraw.Draw(im)
    # linha pequena em cima
    f1 = _fonte("InterDisplay-Black.otf", 46)
    d.text((44, 38), linha1, font=f1, fill=(255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0))
    # título grande
    y = 110
    for linha in titulo.split("\n"):
        t = _texto_grad(linha, 190 if len(linha) <= 8 else 150)
        im.alpha_composite(t, (24, y))
        y += t.size[1] - 40
    # selo da etiqueta
    if etiqueta:
        fe = _fonte("InterDisplay-Black.otf", 50)
        wt = fe.getlength(etiqueta)
        bx, by, bw, bh = 40, H - 120, int(wt + 110), 82
        d.rounded_rectangle([bx, by, bx + bw, by + bh], 16, fill=(24, 18, 12), outline=(232, 180, 47), width=5)
        _ampulheta(d, bx + 26, by + 20, 34, (255, 230, 16))
        d.text((bx + 80, by + 12), etiqueta, font=fe, fill=(255, 230, 16))
    # borda escura fina
    d.rectangle([0, 0, W - 1, H - 1], outline=(0, 0, 0), width=6)
    im.convert("RGB").save(saida, quality=92)
    return saida
