"""Teste de qualidade (Crónicas del Pergamino): gera 3 imagens pela Cloudflare (FLUX schnell). Só biblioteca padrão."""
import base64, json, os, sys, time, urllib.request, urllib.error

MODELO = "@cf/black-forest-labs/flux-1-schnell"
ESTILO = ("Vibrant comic book illustration, manga-inspired cartoon style, thick bold black outlines, highly detailed, "
          "saturated colors with strong red and yellow tones, exaggerated expressive faces with huge eyes, dynamic dramatic composition, "
          "cel shading, ancient Egypt, no text, no letters. ")
HEROI = "a young Egyptian commoner boy with messy spiky black hair, big wide eyes and a simple yellow linen tunic"
PROMPTS = {
    "teste_1": f"{HEROI}, terrified, holding a clay jar full of dark red blood-colored water, the Nile river behind him turned blood red, frogs jumping around his feet, a stern Pharaoh with blue and gold striped headdress glaring in the background, pyramids and a red sky",
    "teste_2": "a grim elderly Pharaoh with blue and gold striped nemes headdress sitting on a golden throne, an old bearded man Moses in a brown robe holding a wooden staff standing in front of him, a giant swarm of locusts flying through the palace columns, dramatic stormy orange sky",
    "teste_3": f"{HEROI}, hiding with his family in total pitch darkness, only their huge scared white eyes visible glowing in the black, a tiny warm lit window of a house far away in the distance, thick heavy darkness plague in ancient Egypt",
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
