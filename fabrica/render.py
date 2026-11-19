"""Edição: câmera em movimento em cada imagem (zoom, deslize, impacto), flash e tremor, legendas e áudio."""
import math, os, random, subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageFilter, ImageEnhance
from fabrica.comum import FONTES, log

FPS = 24
MOVIMENTOS = ["in", "out", "esq", "dir", "in_cima", "in_baixo"]


def _suave(p):
    return p * p * (3 - 2 * p)


def preparar_imagem(caminho, W, H, fator=1.25):
    """Amplia a imagem gerada (768x432) para um pouco mais que a tela, com nitidez leve e vinheta."""
    im = Image.open(caminho).convert("RGB")
    alvo = (int(W * fator), int(H * fator))
    im = im.resize(alvo, Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=110, threshold=2))
    im = ImageEnhance.Color(im).enhance(1.08)
    # vinheta suave
    mask = Image.radial_gradient("L").resize(alvo)          # 0 no centro, 255 nas bordas
    mask = mask.point(lambda v: int(max(0, v - 120) * 0.55))
    escuro = Image.new("RGB", alvo, (0, 0, 0))
    return Image.composite(escuro, im, mask)


def _caixa(Sw, Sh, W, H, mov, p, shake):
    z0, z1 = {"in": (1.0, 1.15), "out": (1.15, 1.0), "esq": (1.07, 1.07), "dir": (1.07, 1.07),
              "in_cima": (1.0, 1.14), "in_baixo": (1.0, 1.14), "punch": (1.0, 1.22)}[mov]
    z = z0 + (z1 - z0) * p
    cw, ch = Sw / z, Sh / z
    folga_x, folga_y = Sw - cw, Sh - ch
    cx, cy = folga_x / 2, folga_y / 2
    if mov == "esq":
        cx = folga_x * (1 - p)
    elif mov == "dir":
        cx = folga_x * p
    elif mov == "in_cima":
        cy = folga_y * (1 - p) * 0.8
    elif mov == "in_baixo":
        cy = folga_y * (0.2 + 0.8 * p)
    cx = min(max(0, cx + shake[0]), folga_x)
    cy = min(max(0, cy + shake[1]), folga_y)
    return (cx, cy, cx + cw, cy + ch)


def renderizar(cenas, tempos, pasta_img, W, H, ass, audio_wav, saida_mp4, pasta, vertical=False):
    total = tempos[-1]["t1"]
    n_frames = int(round(total * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", audio_wav,
           "-vf", f"ass={ass}:fontsdir={FONTES},fade=t=in:st=0:d=0.5,fade=t=out:st={total-1.5:.2f}:d=1.5",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "160k", "-shortest", saida_mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    rnd = random.Random(11)
    pool = ThreadPoolExecutor(max_workers=os.cpu_count() or 2)
    branco = Image.new("RGB", (W, H), (255, 255, 255))
    f_global = 0
    for i, (c, t) in enumerate(zip(cenas, tempos)):
        f0, f1 = int(round(t["t0"] * FPS)), int(round(t["t1"] * FPS))
        if i == len(cenas) - 1:
            f1 = n_frames
        n = max(1, f1 - f0)
        src = preparar_imagem(os.path.join(pasta_img, c["id"] + ".jpg"), W, H)
        Sw, Sh = src.size
        mov = "punch" if "BOOM" in c["eventos"] else MOVIMENTOS[(i + rnd.randint(0, 2)) % len(MOVIMENTOS)]
        flash = "BOOM" in c["eventos"] or "FLASH" in c["eventos"]
        tremor = "BOOM" in c["eventos"]
        ruidos = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(n)]

        def quadro(k):
            p = _suave(k / max(1, n - 1))
            seg = k / FPS
            amp = (Sw * 0.012) * math.exp(-seg * 6) if tremor else 0
            sh = (ruidos[k][0] * amp, ruidos[k][1] * amp)
            fr = src.resize((W, H), Image.BICUBIC, box=_caixa(Sw, Sh, W, H, mov, p, sh))
            if flash and seg < 0.28:
                fr = Image.blend(fr, branco, 0.65 * (1 - seg / 0.28))
            return fr.tobytes()

        for k0 in range(0, n, 32):
            for b in pool.map(quadro, range(k0, min(n, k0 + 32))):
                proc.stdin.write(b)
        f_global += n
        if i % 10 == 0:
            log(f"edição: cena {i+1}/{len(cenas)}")
    proc.stdin.close()
    proc.wait()
    pool.shutdown()
    if proc.returncode != 0:
        raise RuntimeError("ffmpeg falhou")
    return saida_mp4
