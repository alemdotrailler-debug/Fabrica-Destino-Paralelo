"""Narração em português (Kokoro, grátis) e tempos de cada cena."""
import os, re, urllib.request
import numpy as np
import soundfile as sf
from fabrica.comum import MODELOS, md5, log

SR = 24000
URL_MODELOS = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
PAUSA_FRASE = 0.16   # entre frases da mesma cena
INICIO = 0.10        # antes da fala
FIM = 0.28           # depois da fala
MINIMO = 2.6         # duração mínima de uma cena


def frases(t):
    p = re.split(r'(?<=[\.\?!…])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ¿¡«"])', t)
    return [x.strip() for x in p if x.strip()]


def _limpar(t):
    return t.replace("…", ",").replace("—", ",").replace(":", ",").replace("«", "").replace("»", "").replace("  ", " ")


def _kokoro():
    os.makedirs(MODELOS, exist_ok=True)
    for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
        if not os.path.exists(os.path.join(MODELOS, f)):
            log("baixando modelo de voz", f)
            urllib.request.urlretrieve(URL_MODELOS + f, os.path.join(MODELOS, f))
    from kokoro_onnx import Kokoro
    return Kokoro(os.path.join(MODELOS, "kokoro-v1.0.onnx"), os.path.join(MODELOS, "voices-v1.0.bin"))


def _aparar(a, limiar=0.012):
    idx = np.where(np.abs(a) > limiar)[0]
    if len(idx) == 0:
        return 0, len(a)
    return int(idx[0]), int(idx[-1]) + 1


def narrar(R, cenas, pasta):
    """Gera a narração de cada cena. Devolve, por cena, o áudio, a duração e o tempo de cada palavra."""
    voz = getattr(R, "VOZ", "pm_alex")
    vel = getattr(R, "VELOCIDADE", 0.95)
    os.makedirs(os.path.join(pasta, "wav"), exist_ok=True)
    k = None
    out = []
    for n, c in enumerate(cenas):
        partes, palavras = [], []
        t = INICIO
        partes.append(np.zeros(int(INICIO * SR)))
        for s in frases(c["texto"]):
            f = os.path.join(pasta, "wav", md5(f"{voz}|{vel}|{s}") + ".wav")
            if not os.path.exists(f):
                k = k or _kokoro()
                a, sr = k.create(_limpar(s), voice=voz, speed=vel, lang="pt-br")
                sf.write(f, a, sr)
            a, _ = sf.read(f)
            i0, i1 = _aparar(a)
            dur = len(a) / SR
            ws = s.split()
            pesos = np.array([len(w) + 1.5 for w in ws], float)
            ini, fim = i0 / SR, i1 / SR
            lim = np.concatenate([[0], np.cumsum(pesos) / pesos.sum()])
            for w, p0, p1 in zip(ws, lim[:-1], lim[1:]):
                palavras.append((w, t + ini + (fim - ini) * p0, t + ini + (fim - ini) * p1))
            partes.append(a)
            t += dur
            partes.append(np.zeros(int(PAUSA_FRASE * SR)))
            t += PAUSA_FRASE
        partes.append(np.zeros(int(FIM * SR)))
        audio = np.concatenate(partes)
        dur = max(MINIMO, len(audio) / SR - PAUSA_FRASE + FIM)
        if len(audio) < dur * SR:
            audio = np.pad(audio, (0, int(dur * SR) - len(audio)))
        out.append(dict(audio=audio, dur=len(audio) / SR, palavras=palavras))
        if n % 20 == 0:
            log(f"narração {n+1}/{len(cenas)}")
    return out
