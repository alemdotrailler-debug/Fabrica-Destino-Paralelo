"""E se você e a Hinata acordassem na noite do Pain atacando Konoha? (Naruto) — Short de teste (roteiro aprovado em 24/11).
Imagens: elenco ORIGINAL (herói "você", amiga, vilão da torre, garoto da máquina); nada de personagens protegidos nos prompts.
Visual: segue ESTILO.md (anime chibi quente, contorno grosso, fundo dramático)."""
SLUG = "hinata_pain"
TITULO = "E se Você e a Hinata Acordassem na Noite do Pain Atacando Konoha?"
TITULOS = [TITULO]
PROTAG = ("cute chibi anime boy with messy short black hair, big brown eyes, navy blue school blazer with white trim, "
          "long red scarf")
VILAO = ("an original tall chibi warlord with long spiky jet-black hair, glowing violet eyes, calm cruel expression, "
         "black high-collar coat with crimson trim")
AMIGA = ("cute chibi anime girl with long wavy silver-white hair tied in a low ponytail, gentle face, big mint-green eyes, "
         "cream jacket with teal trim")
GAROTO = ("a frail pale chibi boy with messy auburn hair, exhausted face")
BLOCOS = []
VOZ = "pm_alex"
VELOCIDADE = 0.95
TAGS = ["e se você", "naruto", "hinata", "pain", "nagato", "ataque a konoha", "naruto shippuden",
        "e se naruto", "história alternativa", "anime", "destino paralelo", "escolhas e consequências"]
COMENTARIO = ("Você ia atrás do Nagato ou enfrentava o Pain? Conta aqui nos comentários 👇 "
              "E diga qual anime você quer ver no próximo \"E se você...\"")
DESCRICAO = dict(
    gancho="Você acorda na noite em que o Pain destrói Konoha, e dessa vez você lembra de tudo. A Hinata também.",
    resumo="Existe uma coisa que o Nagato vai escutar. Qual é? Vídeo completo em breve no canal.",
    hashtags=["#Naruto", "#Hinata", "#EseVocê"],
)
THUMBS = []
SHORTS_GERAR = [1]


def _p(t):
    return t.replace("@G", AMIGA).replace("@N", GAROTO)


SHORTS = [
    dict(titulo="Você e a Hinata acordam na noite do Pain #shorts", humor="tenso",
         local="dramatic warm key visual lighting, orange and crimson palette, sparks and dust",
         descricao=("Você e a Hinata acordam na noite do Pain #shorts\n\n"
                    "QUER SABER O FINAL? 👉 O vídeo completo \"E se você e a Hinata acordassem na noite do Pain atacando Konoha?\" "
                    "vem aí no canal Destino Paralelo.\n\n"
                    "🔔 Se inscreva para mais \"E se você...\"\n\n"
                    "⚠️ Canal independente, sem associação oficial com as franquias. Conteúdo de fã.\n"
                    "#shorts #Naruto #eseVocê"),
         texto=_p("""
Você acorda e o chão inteiro treme. || @H waking up in bed at night in a tiny apartment, shocked wide eyes, the room shaking, books falling off shelves, cracks in the ceiling, orange glow through the window
Lá fora, uma torre de pedra sobe no meio de Konoha. {BOOM} || wide shot of a hidden mountain village at night with wooden rooftops, a gigantic jagged stone tower bursting out of the ground in the center, flying debris, blood red sky
No topo dela, um homem de olhos roxos. || @V standing on top of the jagged stone spire, glowing violet eyes, long black coat blowing in the wind, a huge red moon behind him
É o Pain. {FLASH} || extreme close-up of @V's glowing violet eyes, bright flash, dark red background
E você já viveu essa noite antes. || @H standing in a street at night staring at the burning village, haunted eyes, ghostly faded memory images of the same scene around him
Na primeira vez, você chegou tarde, e a vila inteira foi destruída. || wide shot of a completely destroyed village, giant crater, smoking ruins, tiny @H kneeling in the rubble
Desta vez, você lembra de tudo. || extreme close-up of @H's determined eyes, flames reflected in his eyes, golden light on his face
E a Hinata também. || @H and @G standing back to back, both with serious faces, the village burning behind them
Você não corre pra lutar. Você corre até ela. || @H running through a dark street with falling debris, motion lines, determined face, @G waiting in the distance
Ela olha pra você e diz: eu também me lembro. || close-up of @G with teary determined eyes looking forward, warm light on her face, @H blurred in the foreground
Então ela ativa o Byakugan. {FLASH} || @G with eyes glowing bright white-mint, a wide ring of pale light radiating around her, hair floating in the air
Mas não olha pros seis corpos. || six menacing chibi masked warriors in dark coats standing in a ruined street, @G ignoring them and looking far away
Ela olha pra longe, seguindo o chakra que controla todos eles. || @G with glowing eyes looking into the distance, glowing blue threads of energy stretching from the six warriors across the sky toward a faraway tower
E encontra um garoto ruivo, preso a uma máquina, escondido numa torre. || @N strapped to a huge cold metal machine with glowing cables inside a dark stone chamber, tiny and exhausted
Você sabe que ele não escuta ninguém com uma kunai na mão. || @H lowering a throwing knife in his hand, thoughtful, the shadow of a dark chamber ahead
Mas existe uma coisa que ele vai escutar. || close-up of @H with a mysterious determined smile, a single beam of light on his face, dark background
Quer saber o que é? O vídeo completo está no canal. || @H pointing toward the viewer with wide excited eyes, bright orange background with sparkles
Uma escolha. Mil consequências. || @H and @G side by side facing the dawn, a giant glowing hourglass symbol in the sky, warm golden light
""")),
]
