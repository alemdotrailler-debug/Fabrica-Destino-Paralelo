"""Teste de qualidade (Crónicas del Pergamino): gera 3 imagens pela Cloudflare (FLUX schnell). Só biblioteca padrão."""
import base64, json, os, sys, time, urllib.request, urllib.error

MODELO = "@cf/black-forest-labs/flux-1-schnell"
ESTILO = ("Beautiful polished cartoon comic illustration in a bold graphic novel style, thick confident black outlines, "
          "dramatic cinematic lighting with strong contrast and deep shadows, rich but tasteful colors (not neon, not oversaturated): "
          "warm gold, burnt orange, deep crimson, teal shadows, sandy beige, detailed textured backgrounds, expressive faces with large eyes, "
          "wide cinematic composition, no text, no letters, no writing, no symbols on clothing. ")
HEROI = "a young Egyptian commoner boy with messy black hair, big brown eyes and a plain cream linen tunic"
PROMPTS = {
    "teste3_1": f"{HEROI}, standing on the muddy bank and holding a clay jar of thick dark red blood, looking horrified, the whole wide Nile river behind him is a deep crimson blood red from bank to bank with dead fish floating, palm trees, pyramids in the hazy distance, burnt orange sunset sky",
    "teste3_2": "a grim Pharaoh with blue and gold striped nemes headdress seated on a golden throne in a grand palace hall, an elderly bearded man Moses in a brown robe holding a wooden staff standing calmly in front of him, a huge dark cloud of locusts, each a green-brown grasshopper with long jumping hind legs and antennae, swarming through the stone columns, golden dusty light",
    "teste3_3": f"{HEROI}, huddled with his family inside a mud brick house in total thick darkness, one tiny flame-less shaft of faint blue moonlight, their wide frightened eyes barely visible in the black, a distant warm glowing window far away on the horizon, dramatic chiaroscuro",
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
