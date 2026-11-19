"""Legendas ASS no estilo do canal: palavra falada em amarelo, selo da escolha, número em destaque."""
import os
from PIL import ImageFont
from fabrica.comum import FONTES

AMARELO = "&H10E6FF&"   # BGR de #FFE610
OURO = "&H2FB4E8&"      # borda dourada do selo
ESCURO = "&H10131A&"
BRANCO = "&HFFFFFF&"


def ts(x):
    x = max(0, x)
    h, r = divmod(x, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _largura(txt, tam, arq="InterDisplay-ExtraBold.otf"):
    return ImageFont.truetype(os.path.join(FONTES, arq), tam).getlength(txt)


def _rr(w, h, r):
    """Retângulo arredondado no formato de desenho do ASS."""
    w, h, r = int(w), int(h), int(r)
    return (f"m {r} 0 l {w-r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h-r} b {w} {h} {w} {h} {w-r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h-r} l 0 {r} b 0 0 0 0 {r} 0")


def _grupos(palavras, max_car, max_pal):
    """Divide as palavras em blocos que cabem na tela."""
    G, atual = [], []
    for p in palavras:
        teste = " ".join(x[0] for x in atual + [p])
        if atual and (len(teste) > max_car or len(atual) >= max_pal):
            G.append(atual); atual = []
        atual.append(p)
        if p[0][-1] in ".?!…" and len(atual) >= 2:
            G.append(atual); atual = []
    if atual:
        G.append(atual)
    return G


def montar_ass(W, H, cenas, tempos, blocos_info, vertical=False):
    """cenas/tempos: lista paralela; tempos[i] = dict(t0, t1, palavras absolutas).
    blocos_info: lista de dict(nome, titulo, t0, t1) das escolhas."""
    fs = 74 if vertical else 62
    margem_v = int(H * (0.27 if vertical else 0.115))
    max_car, max_pal = (15, 3) if vertical else (27, 4)
    L = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "",
         "[V4+ Styles]",
         "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
         f"Style: Leg,Inter Display ExtraBold,{fs},&HFFFFFF&,&HFFFFFF&,&H000000&,&H80000000&,0,0,0,0,100,100,0,0,1,{5 if not vertical else 6},0,2,60,60,{margem_v},1",
         f"Style: Num,Anton,{300 if not vertical else 300},{AMARELO},{AMARELO},&H000000&,&H80000000&,0,0,0,0,100,100,2,0,1,9,3,5,0,0,0,1",
         f"Style: Pal,Inter Display Black,{80 if not vertical else 90},&HFFFFFF&,&HFFFFFF&,&H000000&,&H80000000&,0,0,0,0,100,100,2,0,1,7,2,5,0,0,0,1",
         f"Style: Esc,Anton,{170 if not vertical else 150},{AMARELO},{AMARELO},&H000000&,&H80000000&,0,0,0,0,100,100,4,0,1,8,3,5,0,0,0,1",
         f"Style: Selo,Inter Display ExtraBold,{40 if not vertical else 44},&HFFFFFF&,&HFFFFFF&,&H000000&,&H00000000&,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1",
         "", "[Events]", "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text"]

    # legenda: palavra falada em amarelo
    for c, t in zip(cenas, tempos):
        gs = _grupos(t["palavras"], max_car, max_pal)
        for gi, g in enumerate(gs):
            prox = gs[gi + 1][0][1] if gi + 1 < len(gs) else t["t1"]
            for i, (w, a, b) in enumerate(g):
                fim = g[i + 1][1] if i + 1 < len(g) else min(b + 0.25, prox)
                txt = " ".join((f"{{\\c{AMARELO}}}{x[0]}{{\\c{BRANCO}}}" if j == i else x[0]) for j, x in enumerate(g))
                L.append(f"Dialogue: 0,{ts(a)},{ts(fim)},Leg,,0,0,0,,{{\\an2}}{txt}")

    # selo da escolha (canto superior esquerdo) + cartão de entrada
    for b in blocos_info:
        if not b["nome"] or not b["titulo"]:
            continue
        rotulo = f"{b['nome']} • {b['titulo']}"
        tam = 40 if not vertical else 44
        w = _largura(rotulo, tam) + 44
        h = tam + 30
        x, y = 30, 28
        d = f"Dialogue: 1,{ts(b['t0'])},{ts(b['t1'])},Selo,,0,0,0,,"
        L.append(d + f"{{\\an7\\pos({x},{y})\\bord0\\shad0\\1c{OURO}\\fad(150,150)\\p1}}{_rr(w, h, 14)}{{\\p0}}")
        L.append(d.replace("Dialogue: 1", "Dialogue: 2") + f"{{\\an7\\pos({x+3},{y+3})\\bord0\\shad0\\1c{ESCURO}\\fad(150,150)\\p1}}{_rr(w-6, h-6, 11)}{{\\p0}}")
        L.append(d.replace("Dialogue: 1", "Dialogue: 3") + f"{{\\an7\\pos({x+22},{y+14})\\fad(150,150)}}{rotulo}")
        # cartão grande de entrada (1,6 s)
        t0 = b["t0"]
        pos = f"\\pos({W//2},{int(H*0.40)})"
        L.append(f"Dialogue: 4,{ts(t0)},{ts(t0+1.7)},Esc,,0,0,0,,{{\\an5{pos}\\fscx60\\fscy60\\fad(120,350)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{b['nome']}")
        L.append(f"Dialogue: 4,{ts(t0+0.12)},{ts(t0+1.7)},Pal,,0,0,0,,{{\\an5\\pos({W//2},{int(H*0.40)+150})\\fad(150,350)}}{b['titulo']}")

    # número em destaque
    for c, t in zip(cenas, tempos):
        if c.get("numero"):
            num, pal = c["numero"]
            a, b = t["t0"] + 0.15, t["t1"] - 0.1
            cx = W // 2
            L.append(f"Dialogue: 5,{ts(a)},{ts(b)},Num,,0,0,0,,{{\\an5\\pos({cx},{int(H*0.27)})\\fscx70\\fscy70\\fad(80,200)\\t(0,160,\\fscx116\\fscy116)\\t(160,300,\\fscx100\\fscy100)}}{num}")
            if pal:
                L.append(f"Dialogue: 5,{ts(a+0.08)},{ts(b)},Pal,,0,0,0,,{{\\an5\\pos({cx},{int(H*0.27)+215})\\fad(100,200)}}{pal}")
    return "\n".join(L) + "\n"
