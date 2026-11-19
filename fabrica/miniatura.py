"""Miniatura 1280x720 no padrão do canal Destino Paralelo.

Layout (igual às miniaturas do canal): coluna de texto de um lado, personagem grande do outro — o texto NUNCA
passa por cima do rosto. Texto: linha pequena branca em cima, título em Anton laranja→amarelo com contorno escuro
(cada linha ajustada à largura da coluna) e selo escuro com borda dourada e ampulheta embaixo.
"""
import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from fabrica.comum import FONTES

W, H = 1280, 720
COL = 560          # largura da coluna de texto
MARGEM = 38


def _fonte(nome, tam):
    return ImageFont.truetype(os.path.join(FONTES, nome), int(tam))


def _gradiente(tam, topo, base):
    g = Image.new("RGB", tam)
    d = ImageDraw.Draw(g)
    for y in range(tam[1]):
        t = y / max(1, tam[1] - 1)
        d.line([(0, y), (tam[0], y)], fill=tuple(int(a * (1 - t) + b * t) for a, b in zip(topo, base)))
    return g


def _tamanho_para_largura(txt, larg, max_tam, fonte="Anton-Regular.ttf", prop_contorno=0.085):
    """Maior tamanho de fonte em que o texto (com contorno) cabe na largura da coluna."""
    lo, hi = 20, int(max_tam)
    while lo < hi:
        m = (lo + hi + 1) // 2
        f = _fonte(fonte, m)
        c = max(6, int(m * prop_contorno))
        x0, _, x1, _ = f.getbbox(txt, stroke_width=c)
        if x1 - x0 <= larg:
            lo = m
        else:
            hi = m - 1
    return lo


def _texto_grad(txt, tam, topo=(255, 232, 64), base=(255, 118, 8), prop_contorno=0.085, inclinar=0.0):
    f = _fonte("Anton-Regular.ttf", tam)
    c = max(6, int(tam * prop_contorno))
    x0, y0, x1, y1 = f.getbbox(txt, stroke_width=c)
    w, h = x1 - x0 + 30, y1 - y0 + 30
    cam = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    d.text((15 - x0, 15 - y0), txt, font=f, fill=(30, 14, 6, 255), stroke_width=c, stroke_fill=(30, 14, 6, 255))
    mascara = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mascara).text((15 - x0, 15 - y0), txt, font=f, fill=255)
    cam.paste(_gradiente((w, h), topo, base), (0, 0), mascara)
    sombra = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sombra.paste((0, 0, 0, 160), (6, 8), cam.split()[3])
    out = Image.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(4)), cam)
    if inclinar:
        out = out.transform(out.size, Image.AFFINE, (1, inclinar, 0 if inclinar > 0 else -inclinar * h, 0, 1, 0), Image.BICUBIC)
    return out


def _ampulheta(d, x, y, s, cor):
    d.polygon([(x, y), (x + s, y), (x + s / 2, y + s / 2)], fill=cor)
    d.polygon([(x, y + s), (x + s, y + s), (x + s / 2, y + s / 2)], fill=cor)
    d.rectangle([x - 3, y - 5, x + s + 3, y], fill=cor)
    d.rectangle([x - 3, y + s, x + s + 3, y + s + 5], fill=cor)


def _fundo(caminho, lado):
    """Personagem grande de um lado; o outro lado é uma extensão desfocada e quente da própria imagem."""
    img = Image.open(caminho).convert("RGB")
    bg = ImageOps.fit(img, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(26))
    bg = ImageEnhance.Brightness(ImageEnhance.Color(bg).enhance(1.25)).enhance(0.72)
    fg = img.resize((H, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2.5, percent=120, threshold=2))
    fg = ImageEnhance.Contrast(ImageEnhance.Color(fg).enhance(1.18)).enhance(1.08)
    # transição suave entre a imagem nítida e o fundo desfocado, do lado do texto
    mask = Image.new("L", (H, H), 255)
    md = ImageDraw.Draw(mask)
    faixa = 190
    for i in range(faixa):
        a = int(255 * (i / faixa) ** 1.4)
        x = i if lado == "esq" else H - 1 - i
        md.line([(x, 0), (x, H)], fill=a)
    x0 = W - H if lado == "esq" else 0
    bg.paste(fg, (x0, 0), mask)
    return bg.convert("RGBA")


def _quebrar(txt, fonte, larg):
    linhas, atual = [], ""
    for p in txt.split():
        t = (atual + " " + p).strip()
        if atual and fonte.getlength(t) > larg:
            linhas.append(atual); atual = p
        else:
            atual = t
    return linhas + [atual]


def compor(fundo, linha1, titulo, etiqueta, saida, lado="esq", inclinar=0.0):
    """lado = onde fica o TEXTO ('esq' ou 'dir'); o personagem fica do lado oposto."""
    im = _fundo(fundo, lado)
    # escurece levemente a coluna do texto
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sombra)
    for i in range(COL + 120):
        a = int(110 * (1 - i / (COL + 120)) ** 1.2)
        x = i if lado == "esq" else W - 1 - i
        sd.line([(x, 0), (x, H)], fill=(0, 0, 0, a))
    im = Image.alpha_composite(im, sombra)
    d = ImageDraw.Draw(im)
    x_col = MARGEM if lado == "esq" else W - COL - MARGEM

    # --- etiqueta (embaixo) ---
    fe_tam = 50
    if etiqueta:
        fe = _fonte("InterDisplay-Black.otf", fe_tam)
        while fe.getlength(etiqueta) + 120 > COL and fe_tam > 26:
            fe_tam -= 2; fe = _fonte("InterDisplay-Black.otf", fe_tam)
        bw = int(fe.getlength(etiqueta) + 118)
        bh = fe_tam + 36
        bx, by = x_col, H - bh - 38
    else:
        bh, by = 0, H - 38

    # --- linha pequena (em cima, quebrada em linhas para caber na coluna) ---
    f1 = _fonte("InterDisplay-Black.otf", 44)
    linhas1 = _quebrar(linha1, f1, COL)
    y = 30
    for l in linhas1:
        d.text((x_col, y), l, font=f1, fill=(255, 255, 255), stroke_width=7, stroke_fill=(20, 10, 4))
        y += 52
    topo_titulo = y + 6

    # --- título: cada linha ajustada à largura da coluna; se não couber na altura, reduz tudo ---
    partes = titulo.split("\n")
    espaco = by - 14 - topo_titulo
    fator = 1.0
    while True:
        camadas, altura = [], 0
        for j, ln in enumerate(partes):
            limite = (250 if j == 0 else 190) * fator
            tam = _tamanho_para_largura(ln, COL - 30, limite)
            cam = _texto_grad(ln, tam, inclinar=inclinar)
            camadas.append(cam)
            altura += cam.size[1] - int(tam * 0.18)
        if altura <= espaco or fator < 0.5:
            break
        fator *= 0.93
    y = topo_titulo
    for cam in camadas:
        xx = x_col + (COL - cam.size[0]) // 2 if lado == "dir" else x_col - 8
        im.alpha_composite(cam, (int(xx), int(y)))
        y += cam.size[1] - int(cam.size[1] * 0.18)

    # --- selo da etiqueta ---
    d = ImageDraw.Draw(im)
    if etiqueta:
        d.rounded_rectangle([bx, by, bx + bw, by + bh], 16, fill=(26, 19, 13), outline=(232, 180, 47), width=5)
        _ampulheta(d, bx + 26, by + (bh - 34) // 2 - 2, 34, (255, 230, 16))
        d.text((bx + 80, by + (bh - fe_tam) // 2 - 4), etiqueta, font=fe, fill=(255, 230, 16))
    d.rectangle([0, 0, W - 1, H - 1], outline=(0, 0, 0), width=6)
    im.convert("RGB").save(saida, quality=93)
    return saida
