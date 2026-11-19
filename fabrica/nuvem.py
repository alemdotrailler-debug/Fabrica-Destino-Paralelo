"""Gera imagens pela API grátis da Cloudflare (Workers AI, modelo FLUX.1 schnell). Só biblioteca padrão + Pillow.

Precisa de duas variáveis (no GitHub: Settings > Secrets > Actions):
  CF_ACCOUNT_ID  e  CF_API_TOKEN
Plano grátis: cota diária. Quando a cota acaba, levanta CotaAcabou e a fábrica completa com o modelo local.
"""
import base64, io, json, os, time, urllib.error, urllib.request

MODELO = "@cf/black-forest-labs/flux-1-schnell"
_ACEITA_TAMANHO = True          # vira False se a API recusar width/height


class CotaAcabou(Exception):
    pass


class ErroNuvem(Exception):
    pass


def _tem_cf():
    return bool(os.environ.get("CF_API_TOKEN") and os.environ.get("CF_ACCOUNT_ID"))


def _tem_together():
    return bool(os.environ.get("TOGETHER_API_KEY"))


def disponivel():
    return _tem_cf() or _tem_together()


def _texto(prompt):
    # FLUX entende frase melhor que lista de tags; este prefixo puxa para o visual do canal.
    p = "Colorful anime illustration, cute chibi characters, thick clean outlines, cel shading. " + prompt
    return p[:2000]


def _chamar(corpo):
    base = os.environ.get("CF_API_BASE", "https://api.cloudflare.com/client/v4")     # (CF_API_BASE só para testes)
    url = f"{base}/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/{MODELO}"
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST", headers={
        "Authorization": "Bearer " + os.environ["CF_API_TOKEN"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def _gerar_cf(prompt, w, h, passos=4):
    """Cloudflare Workers AI. Devolve uma imagem PIL (cortada para w:h). Levanta CotaAcabou ou ErroNuvem."""
    global _ACEITA_TAMANHO
    from PIL import Image, ImageOps
    tent = 0
    while True:
        tent += 1
        corpo = {"prompt": _texto(prompt), "steps": max(1, min(8, passos))}
        if _ACEITA_TAMANHO:
            corpo.update(width=1024 if w >= h else 576, height=1024 if h >= w else 576)
        try:
            d = _chamar(corpo)
            res = d.get("result", d) if isinstance(d, dict) else {}
            b64 = res.get("image") if isinstance(res, dict) else None
            if not b64:
                raise ErroNuvem("resposta sem imagem: " + json.dumps(d)[:300])
            im = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
            if abs(w / h - im.width / im.height) > 0.02:       # ex.: veio quadrado -> corta para 16:9 / 9:16
                alvo = (im.width, round(im.width * h / w)) if w >= h else (round(im.height * w / h), im.height)
                im = ImageOps.fit(im, alvo, Image.LANCZOS)
            return im if im.width >= w else im.resize((w, h), Image.LANCZOS)      # mantém a resolução maior da nuvem
        except urllib.error.HTTPError as e:
            txt = e.read().decode("utf-8", "ignore")
            low = txt.lower()
            if e.code in (401, 403):
                raise ErroNuvem(f"acesso negado ({e.code}): confira o token e o Account ID. {txt[:200]}")
            if e.code == 429:
                if any(k in low for k in ("allocation", "daily", "neurons", "quota")):
                    raise CotaAcabou(txt[:200])
                if tent >= 5:
                    raise ErroNuvem("muitas tentativas (429)")
                time.sleep(15 * tent)
                continue
            if e.code in (400, 422) and _ACEITA_TAMANHO and ("width" in low or "height" in low):
                _ACEITA_TAMANHO = False                       # esta API não aceita tamanho: usa o padrão e corta
                continue
            if e.code >= 500 and tent < 4:
                time.sleep(8 * tent)
                continue
            raise ErroNuvem(f"HTTP {e.code}: {txt[:200]}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if tent >= 4:
                raise ErroNuvem(f"rede: {e}")
            time.sleep(8 * tent)


# ---------------------------------------------------------------- Together AI (reserva, mesmo modelo FLUX schnell)
MODELO_TOGETHER = os.environ.get("TOGETHER_MODELO", "black-forest-labs/FLUX.1-schnell-Free")


def _gerar_together(prompt, w, h, passos=4):
    from PIL import Image, ImageOps
    base = os.environ.get("TOGETHER_API_BASE", "https://api.together.xyz/v1")        # (só para testes)
    W, H = (1024, 576) if w > h else ((576, 1024) if h > w else (1024, 1024))
    corpo = {"model": MODELO_TOGETHER, "prompt": _texto(prompt), "width": W, "height": H, "steps": max(1, min(4, passos)),
             "n": 1, "response_format": "b64_json"}
    tent = 0
    while True:
        tent += 1
        req = urllib.request.Request(base + "/images/generations", data=json.dumps(corpo).encode(), method="POST", headers={
            "Authorization": "Bearer " + os.environ["TOGETHER_API_KEY"], "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read().decode())
            b64 = d["data"][0].get("b64_json")
            if not b64:
                raise ErroNuvem("Together: resposta sem imagem")
            im = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
            if abs(w / h - im.width / im.height) > 0.02:
                alvo = (im.width, round(im.width * h / w)) if w >= h else (round(im.height * w / h), im.height)
                im = ImageOps.fit(im, alvo, Image.LANCZOS)
            return im if im.width >= w else im.resize((w, h), Image.LANCZOS)
        except urllib.error.HTTPError as e:
            txt = e.read().decode("utf-8", "ignore")
            low = txt.lower()
            if e.code in (401, 403):
                raise ErroNuvem(f"Together: acesso negado ({e.code}). {txt[:160]}")
            if e.code == 402 or any(k in low for k in ("credit", "quota", "limit exceeded", "daily")) and e.code != 429:
                raise CotaAcabou("Together: " + txt[:160])
            if e.code == 429:
                if tent >= 5:
                    raise CotaAcabou("Together: limite de uso (429): " + txt[:120])
                time.sleep(12 * tent)
                continue
            if e.code >= 500 and tent < 4:
                time.sleep(8 * tent)
                continue
            raise ErroNuvem(f"Together HTTP {e.code}: {txt[:160]}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if tent >= 4:
                raise ErroNuvem(f"Together rede: {e}")
            time.sleep(8 * tent)


# ---------------------------------------------------------------- cadeia de provedores
_ESGOTADOS = set()


def gerar(prompt, w, h, passos=4):
    """Tenta a Cloudflare e, se a cota diária acabar, a Together AI (mesmo modelo, mesmo visual)."""
    erros = []
    for nome, tem, fn in (("Cloudflare", _tem_cf, _gerar_cf), ("Together", _tem_together, _gerar_together)):
        if nome in _ESGOTADOS or not tem():
            continue
        try:
            return fn(prompt, w, h, passos)
        except CotaAcabou as e:
            _ESGOTADOS.add(nome)
            erros.append(f"{nome}: {e}")
        except ErroNuvem as e:
            erros.append(f"{nome}: {e}")
            if "acesso negado" in str(e):
                _ESGOTADOS.add(nome)
    ativos = [n for n, t in (("Cloudflare", _tem_cf), ("Together", _tem_together)) if t()]
    if ativos and all(n in _ESGOTADOS for n in ativos):
        raise CotaAcabou(" | ".join(erros) or "cota diária esgotada em: " + ", ".join(ativos))
    raise ErroNuvem(" | ".join(erros) or "nenhum provedor configurado")
