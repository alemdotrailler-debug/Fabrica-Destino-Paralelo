"""Trilha do vídeo: narração + música de fundo gerada por código + efeitos (corte e impacto)."""
import numpy as np
import soundfile as sf

SR = 24000

# acordes (Hz) por clima
CLIMAS = {
    "tenso": [[110, 130.8, 164.8], [87.3, 110, 130.8], [98, 116.5, 146.8], [82.4, 98, 123.5]],
    "epico": [[110, 138.6, 164.8], [98, 123.5, 146.8], [87.3, 110, 130.8], [98, 123.5, 146.8]],
    "calmo": [[130.8, 164.8, 196], [98, 123.5, 146.8], [110, 130.8, 164.8], [87.3, 110, 130.8]],
}


def _acorde(freqs, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.003 * tt) + 0.15 * np.sin(2 * np.pi * f * 0.5 * tt) for f in freqs)
    env = np.minimum(1, np.minimum(tt / 1.0, (dur - tt) / 1.0))
    return s * env * (0.65 + 0.35 * np.sin(2 * np.pi * 0.2 * tt))


def _pulso(n, bpm=96):
    """Batida suave e grave, só para dar tensão."""
    out = np.zeros(n)
    passo = int(60 / bpm * SR)
    tt = np.arange(int(0.35 * SR)) / SR
    kick = np.sin(2 * np.pi * (52 + 90 * np.exp(-tt * 28)) * tt) * np.exp(-tt * 9)
    for i in range(0, n - len(kick), passo):
        out[i:i + len(kick)] += kick
    return out


def mixar(cenas, tempos, saida_wav, total):
    voz = np.concatenate([t["audio"] for t in tempos])
    n = len(voz)
    # música por trecho de clima
    mus = np.zeros(n)
    pulso = _pulso(n)
    ativo = np.zeros(n)
    i = 0
    while i < len(cenas):
        j = i
        while j < len(cenas) and cenas[j]["humor"] == cenas[i]["humor"]:
            j += 1
        a, b = int(tempos[i]["t0"] * SR), min(n, int(tempos[j - 1]["t1"] * SR))
        prog = CLIMAS.get(cenas[i]["humor"], CLIMAS["tenso"])
        pos, k = a, 0
        while pos < b:
            seg = _acorde(prog[k % 4], 5.0)
            m = min(len(seg), b - pos)
            mus[pos:pos + m] += seg[:m]
            pos += int(4.0 * SR); k += 1
        if cenas[i]["humor"] in ("tenso", "epico"):
            ativo[a:b] = 1.0
        i = j
    mus = mus / max(1e-6, np.abs(mus).max()) * 0.07
    pulso = pulso * ativo
    pulso = pulso / max(1e-6, np.abs(pulso).max()) * 0.05
    mix = voz / max(1e-6, np.abs(voz).max()) * 0.92 + mus + pulso
    rng = np.random.RandomState(7)
    tt = np.arange(int(0.45 * SR)) / SR
    whoosh = rng.randn(len(tt)) * np.exp(-((tt - 0.12) / 0.06) ** 2) * 0.12
    boom = np.convolve(rng.randn(len(tt)), np.ones(60) / 60, "same") * np.exp(-tt * 5) * 2.4
    for c, t in zip(cenas[1:], tempos[1:]):
        i0 = max(0, int((t["t0"] - 0.1) * SR))
        seg = whoosh[:max(0, min(len(whoosh), n - i0))]
        mix[i0:i0 + len(seg)] += seg
    for c, t in zip(cenas, tempos):
        if "BOOM" in c["eventos"]:
            i0 = int(t["t0"] * SR)
            seg = boom[:max(0, min(len(boom), n - i0))]
            mix[i0:i0 + len(seg)] += seg
    mix = mix / max(1.0, np.abs(mix).max() / 0.98)
    f = int(1.8 * SR)
    mix[-f:] *= np.linspace(1, 0, f)
    sf.write(saida_wav, mix, SR)
    return saida_wav
