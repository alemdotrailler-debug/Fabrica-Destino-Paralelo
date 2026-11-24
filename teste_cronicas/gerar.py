"""Teste de qualidade (Crónicas del Pergamino): gera 3 imagens pela Cloudflare (FLUX schnell). Só biblioteca padrão."""
import base64, json, os, sys, time, urllib.request, urllib.error

MODELO = "@cf/black-forest-labs/flux-1-schnell"
ESTILO = ("Beautiful polished cartoon comic illustration, clean confident black outlines, soft cinematic lighting, "
          "muted earthy color palette with warm sand, dusty ochre, terracotta, deep teal and soft gold, balanced contrast, "
          "gentle desaturated tones, subtle gradients, rich atmospheric depth, expressive faces with large eyes, "
          "detailed ancient Egypt setting, wide cinematic 16:9 composition, no text, no letters, no symbols on clothing. ")
HEROI = "a young Egyptian commoner boy with messy black hair, big brown eyes and a plain cream linen tunic"
PROMPTS = {
    "teste2_1": f"{HEROI}, terrified, holding a clay jar full of dark red blood-colored water, the Nile river behind him turned blood red but a deep natural crimson, frogs jumping around his feet, a stern Pharaoh with blue and gold striped headdress glaring in the background, pyramids and a hazy dusty orange sky",
    "teste2_2": "a grim elderly Pharaoh with blue and gold striped nemes headdress sitting on a golden throne, an old bearded man Moses in a brown robe holding a wooden staff standing in front of him, a large swarm of brown grasshopper-like locusts flying through the palace columns, dusty golden sky",
    "teste2_3": f"{HEROI}, hiding with his family in total pitch darkness, only their huge scared white eyes visible glowing in the black, a tiny warm lit window of a house far away in the distance, thick heavy darkness plague in ancient Egypt",
}


def chamar(corpo):
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/{MODELO}"
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST", headers={
        "Authorization": "Bearer " + os.environ["CF_API_TOKEN"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


os.makedirs("teste_cronicas/saida", exist_ok=True)
for nome, p in PROMPTS.items():
    for tent in range(3):
        try:
            try:
                r = chamar({"prompt": (ESTILO + p)[:2000], "steps": 8, "width": 1280, "height": 720})
            except urllib.error.HTTPError:
                r = chamar({"prompt": (ESTILO + p)[:2000], "steps": 8})
            img = r["result"]["image"]
            open(f"teste_cronicas/saida/{nome}.jpg", "wb").write(base64.b64decode(img))
            print("ok", nome, flush=True)
            break
        except urllib.error.HTTPError as e:
            print("erro", nome, e.code, e.read().decode()[:300], flush=True)
            time.sleep(5)
        except Exception as e:
            print("erro", nome, repr(e)[:300], flush=True)
            time.sleep(5)
