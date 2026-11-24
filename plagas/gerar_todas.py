"""Gera as imagens do vídeo das plagas (Crónicas del Pergamino) pela Cloudflare (FLUX schnell). Pula as que já existem."""
import base64, json, os, sys, time, urllib.request, urllib.error
MODELO = "@cf/black-forest-labs/flux-1-schnell"
D = json.load(open("plagas/prompts.json", encoding="utf-8"))

def chamar(corpo):
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/{MODELO}"
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST", headers={
        "Authorization": "Bearer " + os.environ["CF_API_TOKEN"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())

falhas = []
for nome, p in D["prompts"].items():
    arq = f"plagas/imagens/{nome}.jpg"
    if os.path.exists(arq):
        continue
    ok = False
    for tent in range(4):
        try:
            r = chamar({"prompt": (D["estilo"] + p)[:2000], "steps": 8})
            open(arq, "wb").write(base64.b64decode(r["result"]["image"]))
            print("ok", nome, flush=True); ok = True; break
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:200]
            print("erro", nome, e.code, msg, flush=True)
            if e.code == 429 or "limit" in msg.lower():
                time.sleep(20)
            else:
                time.sleep(6)
        except Exception as e:
            print("erro", nome, repr(e)[:200], flush=True); time.sleep(6)
    if not ok:
        falhas.append(nome)
print("FALHAS", falhas)
