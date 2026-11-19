"""App da Modal: roda o FLUX.1 schnell numa GPU (plano grátis da Modal: US$ 30 de crédito por mês, sem cartão).

NÃO é importado pela fábrica. O GitHub publica este arquivo na Modal com `modal deploy fabrica/modal_flux.py`
e depois a fábrica chama a classe `Flux` (ver fabrica/nuvem.py).
Secrets no GitHub: MODAL_TOKEN_ID e MODAL_TOKEN_SECRET.
"""
import io
import os

import modal

GPU = os.environ.get("MODAL_GPU", "A100-40GB")        # troque para "L40S" ou "A10G" se quiser outra GPU
MODELO = "black-forest-labs/FLUX.1-schnell"           # Apache 2.0, sem pedir acesso


def baixar_modelo():
    from huggingface_hub import snapshot_download
    # só o formato do diffusers (ignora os arquivos soltos de 23 GB do topo do repositório)
    snapshot_download(MODELO, ignore_patterns=["flux1-schnell.safetensors", "ae.safetensors", "*.md", ".gitattributes"])


imagem = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("numpy==1.26.4", "torch==2.5.1", "diffusers==0.32.2", "transformers==4.48.3", "accelerate==1.3.0",
                 "sentencepiece", "protobuf", "pillow", "huggingface_hub==0.27.1")
    .run_function(baixar_modelo)
)

app = modal.App("fabrica-flux", image=imagem)


@app.cls(gpu=GPU, timeout=900, scaledown_window=120, max_containers=4)
class Flux:
    @modal.enter()
    def carregar(self):
        import torch
        from diffusers import FluxPipeline
        self.torch = torch
        self.pipe = FluxPipeline.from_pretrained(MODELO, torch_dtype=torch.bfloat16).to("cuda")

    @modal.method()
    def gerar(self, prompt: str, w: int, h: int, passos: int = 4, seed: int = -1) -> bytes:
        """Devolve um JPEG (qualidade 95). Tamanho nativo: 1024x576 (horizontal), 576x1024 (vertical) ou 1024x1024."""
        W, H = (1024, 576) if w > h else ((576, 1024) if h > w else (1024, 1024))
        g = self.torch.Generator("cuda")
        g.manual_seed(seed if seed >= 0 else int.from_bytes(os.urandom(4), "little"))
        im = self.pipe(prompt=prompt[:2000], width=W, height=H, num_inference_steps=max(1, min(8, passos)),
                       guidance_scale=0.0, max_sequence_length=256, generator=g).images[0]
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "JPEG", quality=95)
        return buf.getvalue()
