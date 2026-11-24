"""Gera as imagens do vídeo das plagas (Crónicas del Pergamino) pela Cloudflare (FLUX schnell). Pula as que já existem."""
import base64, json, os, subprocess, sys, time, urllib.request, urllib.error
MODELO = "@cf/black-forest-labs/flux-1-schnell"
D = json.load(open("plagas/prompts.json", encoding="utf-8"))

def chamar(corpo):
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/{MODELO}"
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST", headers={
        "Authorization": "Bearer " + os.environ["CF_API_TOKEN"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

os.makedirs("plagas/imagens", exist_ok=True)
falhas = []
LOG = open("plagas/log.txt", "a")
def log(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); LOG.write(m + "\n"); LOG.flush()
def salvar():
    cmds = [["git", "config", "user.name", "fabrica"], ["git", "config", "user.email", "fabrica@users.noreply.github.com"],
            ["git", "add", "plagas/imagens", "plagas/log.txt"], ["git", "commit", "-m", "Imagens plagas (parcial)"],
            ["git", "pull", "--rebase", "-X", "theirs", "origin", "teste-cronicas"], ["git", "push", "origin", "HEAD:teste-cronicas"]]
    for c in cmds:
        subprocess.run(c, capture_output=True)
feitas = 0
for nome, p in D["prompts"].items():
    arq = f"plagas/imagens/{nome}.jpg"
    if os.path.exists(arq):
        continue
    ok = False
    for tent in range(4):
        try:
            r = chamar({"prompt": (D["estilo"] + p)[:2000], "steps": 8})
            open(arq, "wb").write(base64.b64decode(r["result"]["image"]))
            log("ok", nome); ok = True; feitas += 1; break
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:200]
            log("erro", nome, e.code, msg); salvar()
            if e.code == 429 or "limit" in msg.lower():
                time.sleep(20)
            else:
                time.sleep(6)
        except Exception as e:
            log("erro", nome, repr(e)[:200]); time.sleep(6)
    if not ok:
        falhas.append(nome)
    if feitas and feitas % 5 == 0 and ok:
        salvar()
log("FALHAS", falhas); salvar()
