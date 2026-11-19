"""Imagens que VOCÊ gerou (ex.: no Tubefy) e colocou na pasta do vídeo, em vez de gerar com o modelo grátis.

Onde colocar (dentro de videos/<nome>/imagens/):
  imagens/001.png, 002.png ...      -> vídeo longo (o número do arquivo = o número da cena na lista cenas.txt)
  imagens/qualquer-nome.zip         -> pode mandar as imagens dentro de um ZIP (vale para as pastas abaixo também)
  imagens/short_1/01.png ...        -> Short 1 (idem short_2, short_3)
  imagens/miniatura_A.png           -> base da miniatura A (idem miniatura_B)

Arquivos com número no começo do nome (001.png, 12-lutando.png) vão para a cena de mesmo número; as cenas sem
arquivo repetem a imagem anterior. Sem número no nome, as imagens vão em ordem alfabética/numérica pelas cenas.
Se tiver MENOS imagens que cenas, o roteiro decide (IMAGENS_FALTANTES):
  "repetir" (padrão): espalha/repete as imagens pelas cenas, com movimentos de câmera diferentes
  "gerar": as cenas sem imagem sua são geradas pelo modelo grátis (personagens originais)
Imagens a mais que cenas: as sobras são ignoradas.
"""
import os, re
from fabrica import plano

EXT = (".png", ".jpg", ".jpeg", ".webp")


def _natural(nome):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", nome.lower())]


def _listar(pasta):
    """Imagens soltas + dentro de ZIPs na pasta, ordenadas pelo nome do arquivo (natural: 2 antes de 10)."""
    import hashlib, zipfile
    from fabrica.comum import RAIZ
    if not os.path.isdir(pasta):
        return []
    achados = []
    for f in os.listdir(pasta):
        cam = os.path.join(pasta, f)
        if not os.path.isfile(cam) or f.startswith("."):
            continue
        if f.lower().endswith(EXT) and not f.lower().startswith("miniatura"):
            achados.append((f, cam))
        elif f.lower().endswith(".zip"):
            tmp = os.path.join(RAIZ, "trabalho", "_zips", hashlib.md5(cam.encode()).hexdigest()[:10])
            os.makedirs(tmp, exist_ok=True)
            with zipfile.ZipFile(cam) as z:
                for m in z.namelist():
                    nome = os.path.basename(m)
                    if m.endswith("/") or "__MACOSX" in m or nome.startswith(".") or not nome.lower().endswith(EXT):
                        continue
                    dest = os.path.join(tmp, nome)
                    if not os.path.exists(dest):
                        with z.open(m) as src, open(dest, "wb") as out:
                            out.write(src.read())
                    achados.append((nome, dest))
    achados.sort(key=lambda t: _natural(t[0]))
    return [cam for _, cam in achados]


def _distribuir(cenas, arqs, politica):
    n, m = len(cenas), len(arqs)
    if m == 0:
        return {}
    numeros = [re.match(r"(\d+)", os.path.basename(a)) for a in arqs]
    if all(numeros):                                         # arquivos numerados: número = cena (começando em 1)
        por_cena = {}
        for a, mt in zip(arqs, numeros):
            por_cena.setdefault(int(mt.group(1)), a)
        out, ultimo = {}, None
        primeiro = por_cena[min(por_cena)]
        for i, c in enumerate(cenas, 1):
            if i in por_cena:
                ultimo = por_cena[i]
            if politica == "gerar" and i not in por_cena:
                continue
            out[c["id"]] = ultimo or primeiro
        return out
    if m >= n:
        return {c["id"]: arqs[i] for i, c in enumerate(cenas)}
    if politica == "gerar":
        return {c["id"]: arqs[i] for i, c in enumerate(cenas[:m])}
    return {c["id"]: arqs[min(m - 1, i * m // n)] for i, c in enumerate(cenas)}


def mapa(R, pasta_video, modo):
    """Dicionário id-da-imagem -> arquivo importado (só o que o usuário forneceu)."""
    base = os.path.join(pasta_video, "imagens")
    politica = getattr(R, "IMAGENS_FALTANTES", "repetir")
    out = {}
    if modo == "longo":
        p = plano.producoes(R, "longo")[0]
        out.update(_distribuir(p["cenas"], _listar(base), politica))
    elif modo == "shorts":
        for p in plano.producoes(R, "shorts"):
            out.update(_distribuir(p["cenas"], _listar(os.path.join(base, f"short_{p['n']}")), politica))
    if modo in ("longo", "miniaturas"):
        for i, _ in enumerate(getattr(R, "THUMBS", [])):
            letra = "AB"[i]
            for ext in EXT:
                f = os.path.join(base, f"miniatura_{letra}{ext}")
                if os.path.exists(f):
                    out[f"{R.SLUG}_thumb_{i}_0"] = f
                    break
    return out


def faltantes(R, pasta_video, modo):
    """Imagens que o modelo grátis ainda precisa gerar (tudo menos o que foi importado)."""
    feitas = mapa(R, pasta_video, modo)
    return [c for c in plano.todas_as_imagens(R, modo)
            if c["id"] not in feitas and not _thumb_extra_de_importada(R, c["id"], feitas)]


def _thumb_extra_de_importada(R, id_, feitas):
    """Miniatura com base importada: não precisa dos candidatos 1..N gerados."""
    m = re.fullmatch(re.escape(R.SLUG) + r"_thumb_(\d+)_(\d+)", id_)
    return bool(m and int(m.group(2)) > 0 and f"{R.SLUG}_thumb_{m.group(1)}_0" in feitas)


def aplicar(R, pasta_video, modo, destino):
    """Copia as imagens importadas para trabalho/<slug>/img/<id>.jpg, cortando para a proporção certa."""
    from PIL import Image, ImageOps
    os.makedirs(destino, exist_ok=True)
    dims = {c["id"]: (c["w"], c["h"]) for c in plano.todas_as_imagens(R, modo)}
    cache, n = {}, 0
    for id_, arq in mapa(R, pasta_video, modo).items():
        w, h = dims.get(id_, (768, 432))
        escala = 2 if id_.find("_thumb_") < 0 else 1            # guarda mais resolução que o modelo grátis
        chave = (arq, w, h)
        if chave not in cache:
            im = Image.open(arq).convert("RGB")
            cache[chave] = ImageOps.fit(im, (w * escala, h * escala), Image.LANCZOS)
        cache[chave].save(os.path.join(destino, id_ + ".jpg"), quality=95)
        n += 1
    return n
