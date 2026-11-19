"""Funções comuns da fábrica do Destino Paralelo."""
import hashlib, importlib.util, os, sys, time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTES = os.path.join(RAIZ, "fonts")
MODELOS = os.path.join(RAIZ, "modelos")
_T0 = time.time()


def log(*a):
    print(f"[destino +{(time.time() - _T0) / 60:.1f}min]", *a, flush=True)


def md5(s, n=12):
    return hashlib.md5(s.encode()).hexdigest()[:n]


def carregar_roteiro(pasta_video):
    caminho = os.path.join(pasta_video, "roteiro.py")
    spec = importlib.util.spec_from_file_location("roteiro_" + md5(caminho, 6), caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def pasta_trabalho(slug):
    p = os.path.join(RAIZ, "trabalho", slug)
    os.makedirs(p, exist_ok=True)
    return p
