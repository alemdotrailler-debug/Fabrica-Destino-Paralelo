"""Transforma o roteiro em um plano: lista de cenas (1 cena = 1 imagem = 1 trecho de narração).

Somente biblioteca padrão (usado também pelo job que descobre quantas imagens serão geradas).
"""
import re
from fabrica.comum import md5

ESTILO = "vibrant saturated colors, thick clean outlines, cel shading, anime key visual, masterpiece, best quality"
NEGATIVO = ("lowres, bad anatomy, bad hands, text, error, cropped, worst quality, low quality, jpeg artifacts, "
            "signature, watermark, blurry, realistic, photo")
CAMERAS = ["close-up portrait", "wide shot", "low angle shot", "medium shot", "over the shoulder shot",
           "dutch angle", "extreme close-up of eyes", "high angle shot"]
EMOCOES = ["shocked, wide eyes", "determined", "scared, sweating", "angry, shouting", "crying",
           "smirking", "worried", "serious"]

RE_TOKEN = re.compile(r"\{([A-Z]+)(?::([^}]*))?\}")

# tamanho de geração (largura, altura) e de saída final
GERACAO = {"h": (768, 432), "v": (432, 768)}
SAIDA = {"h": (1920, 1080), "v": (1080, 1920)}


def limpar(texto):
    """'{BOOM} Você tem {NUM:13|ANOS}.' -> ('Você tem 13 anos.', ['BOOM'], ('13','ANOS'))"""
    eventos, numero = [], None

    def troca(m):
        nonlocal numero
        if m.group(1) == "NUM":
            a, _, b = (m.group(2) or "").partition("|")
            numero = (a.strip(), b.strip())
            return f"{a.strip()} {b.strip().lower()}".strip()
        eventos.append(m.group(1))
        return ""

    limpo = re.sub(r"\s+", " ", RE_TOKEN.sub(troca, texto)).strip()
    return limpo, eventos, numero


def _cenas_do_bloco(R, bloco, pid, bi, orient, inicio, nome_bloco, titulo_bloco):
    protag = getattr(R, "PROTAG", "")
    local = bloco.get("local", "")
    out = []
    n = inicio
    for linha in bloco["texto"].strip().split("\n"):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        fala, _, extra = linha.partition("||")
        texto, eventos, numero = limpar(fala)
        extra = extra.strip().replace("@H", protag).replace("@V", getattr(R, "VILAO", ""))
        if not extra:
            extra = f"{CAMERAS[n % len(CAMERAS)]}, {protag}, {EMOCOES[n % len(EMOCOES)]}"
        prompt = ", ".join(x for x in (extra, local, ESTILO) if x)
        w, h = GERACAO[orient]
        out.append(dict(id=f"{pid}_{n:03d}", bloco=bi, bnome=nome_bloco, btitulo=titulo_bloco,
                        texto=texto, eventos=eventos, numero=numero, prompt=prompt,
                        seed=int(md5(prompt + pid, 8), 16) % 2**31, w=w, h=h, orient=orient,
                        humor=bloco.get("humor", "tenso")))
        n += 1
    return out


def producoes(R, modo="longo"):
    """Lista de produções: o vídeo longo (horizontal) ou cada Short (vertical)."""
    P = []
    if modo == "longo":
        cenas, n = [], 0
        for bi, b in enumerate(R.BLOCOS):
            c = _cenas_do_bloco(R, b, R.SLUG, bi, "h", n, b.get("nome"), b.get("titulo"))
            n += len(c); cenas += c
        P.append(dict(id=R.SLUG, orient="h", cenas=cenas, titulo=R.TITULO))
    else:
        ativos = getattr(R, "SHORTS_GERAR", None)          # ex.: [1, 2] = só os Shorts 1 e 2
        for i, s in enumerate(getattr(R, "SHORTS", []), 1):
            if ativos and i not in ativos:
                continue
            pid = f"{R.SLUG}_short_{i}"
            c = _cenas_do_bloco(R, s, pid, 0, "v", 0, None, None)
            P.append(dict(id=pid, orient="v", cenas=c, titulo=s.get("titulo", pid), short=s, n=i))
    return P


def miniaturas(R):
    """Imagens-base das miniaturas: vários candidatos por miniatura (quadrado 512x512, mais nítido)."""
    out = []
    protag = getattr(R, "PROTAG", "")
    n = getattr(R, "THUMB_CANDIDATOS", 4)
    for i, t in enumerate(getattr(R, "THUMBS", [])):
        base = ", ".join(x for x in (t["prompt"].replace("@H", protag).replace("@V", getattr(R, "VILAO", "")), ESTILO) if x)
        for k in range(n):
            out.append(dict(id=f"{R.SLUG}_thumb_{i}_{k}", prompt=base, seed=int(md5(base + str(k), 8), 16) % 2**31,
                            w=512, h=512, orient="h", passos=4))
    return out


def todas_as_imagens(R, modo="longo"):
    if modo == "miniaturas":
        return miniaturas(R)
    imgs = []
    for p in producoes(R, modo):
        imgs += p["cenas"]
    if modo == "longo":
        imgs += miniaturas(R)
    return imgs
