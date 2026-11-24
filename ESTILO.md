# Ficha de estilo visual — Destino Paralelo

Feita em 24/11/2026 a partir das imagens reais do canal (pasta `referencias/estilo/`):
- `quadros_tita_fundador.jpg`: 8 quadros do vídeo publicado "E se você herdasse o Titã Fundador?"
- `pagina_do_canal.jpg`: banner, logo e miniaturas dos vídeos Titã Fundador e Death Note
- `miniaturas_fabrica_A_B.jpg`: miniaturas A/B geradas pela fábrica (Sukuna)
- `short1_aprovado.jpg`, `short2_aprovado.jpg`, `short3_aprovado.jpg`: Shorts da primeira produção (Cloudflare FLUX), o look que o usuário aprovou em 20/11

**Regra de ouro:** todo vídeo novo do Destino Paralelo (longo, Short, miniatura) segue esta ficha. Antes de gerar imagens, abrir as imagens de `referencias/estilo/` para conferir o look.

## 1. Look geral
Anime **chibi** estilo "key visual" de ação: cabeça grande, olhos enormes e brilhantes com reflexo, corpo pequeno, expressão forte (determinado, chocado, boca aberta).
- Contorno **grosso e limpo**, sombreado **cel** (cores chapadas, sem realismo).
- Fundo **dramático e saturado**: explosão com faíscas, raios, fogo, lua cheia, corredor neon, cidade em chamas.
- Personagem em **close ou plano médio**, centralizado ou no terço direito, olhando para a câmera.
- Um **símbolo gigante** atrás do herói conta a história da cena (ampulheta, muralha, titã, mão com dedo brilhando, trono de demônio).
- Escala exagerada: ameaça enorme e escura atrás, herói pequeno na frente.

## 2. Paleta (medida nos 8 quadros do vídeo publicado)
| Família | Parcela | Uso |
|---|---|---|
| Vermelho | 28% | fogo, perigo, lenço, olhos |
| Laranja | 26% | explosões, céu, brilho principal |
| Roxo / magenta | 11% | céu de tensão, raios, vilões |
| Amarelo | 9% | números, palavra falada, faíscas |
| Azul / ciano | 6% | noite e calma, contraste pontual |
| Verde | 4% | capa do herói (contraste complementar com o laranja) |
| Neutros escuros | 14% | bordas e fundos de noite |

Saturação média 0,49 e brilho médio 0,61: cores vivas, mas com áreas escuras em volta para o personagem destacar.

Cores de apoio: laranja `#E68E38`, laranja-queimado `#D46632`, vermelho `#B3492A`, rosa-vermelho `#C2536B`, roxo `#772F55`, roxo-escuro `#34213B`, amarelo `#F9EE50`, creme `#FDDF94`, noite `#151A21`.

Atenção: o pedido de "cores menos saturadas" vale só para o **Crónicas del Pergamino**. No Destino Paralelo a cor é viva e quente.

## 3. Personagens
- **Herói = "você"**: chibi, cabelo preto ou castanho-escuro espetado, olhos grandes âmbar/vermelho-castanho, rosto com blush leve. Vídeo do Titã Fundador: capa/capuz verde + jaqueta marrom com cintos. Shorts do Sukuna: blazer escuro com lenço vermelho.
- **Mesmo herói em todas as cenas** do vídeo (mesmo texto de descrição `PROTAG`; nunca trocar cabelo, roupa ou cor dos olhos).
- **Personagens de apoio**: também chibi, em grupo ao fundo ou ao lado, cada um com cabelo e roupa diferentes.
- **Ameaça/vilão**: silhueta grande e escura, olhos brilhando (vermelho/âmbar), mesmo desenho em todas as cenas. Para vilão cômico, rosto caricato com sorriso enorme.
- Só personagens **originais** (herói e vilão). Não desenhar personagem protegido de franquia, nem copiar capa/pôster/logo.

## 4. Texto em tela (editor da fábrica, nunca dentro da imagem)
- **Selo** no canto superior esquerdo: "ESCOLHA N · TÍTULO", pílula escura, texto branco pequeno em negrito.
- **Número gigante**: amarelo, fonte Anton, contorno preto grosso, rótulo branco embaixo (ex.: 13 / ANOS, 45 / MURALHA).
- **Legenda**: Inter Display ExtraBold, branca, contorno preto grosso, 1 ou 2 linhas na faixa inferior, **palavra falada em amarelo**.
- Deixar o rosto e a ação **acima da faixa da legenda**.

## 5. Miniatura (1280x720, versões A e B)
- Texto em coluna à esquerda: linha curta branca ("E SE VOCÊ ENGOLISSE O") + palavra-chave enorme em degradê amarelo→laranja, Anton, contorno preto grosso.
- Etiqueta arredondada embaixo com ícone de ampulheta + curiosidade ("20 DEDOS AMALDIÇOADOS", "13 ANOS DE VIDA").
- Personagem expressivo do outro lado (olhos grandes, boca aberta ou sorriso de vilão), fundo de explosão laranja/vermelha com raios, borda preta fina.
- A e B com ângulos e emoções diferentes, para o teste do YouTube.

## 6. Marca do canal
- Banner: preto, vermelho e branco; "DESTINO PARALELO" em itálico pesado com sombra vermelha; faixa "UMA ESCOLHA. MIL CONSEQUÊNCIAS."; 3 pilares: Histórias alternativas, Escolhas e consequências, Universos de anime.
- Logo: personagem de capuz escuro com ampulheta, em moldura redonda azul/roxa/dourada. A **ampulheta** é o símbolo do canal.

## 7. Prompt-base para o gerador de imagens (inglês)
```
cute chibi anime illustration, big head, huge glossy eyes with highlights, thick clean black outlines,
cel shading, vibrant warm palette (orange, crimson, magenta), dramatic key visual lighting,
explosive background with sparks and lightning, character close-up facing the camera,
clean hands, no text, no watermark
```
O que a fábrica usa hoje: prefixo "Colorful anime illustration, cute chibi characters, thick clean outlines, cel shading." (`fabrica/nuvem.py`) e sufixo "vibrant saturated colors, thick clean outlines, cel shading, anime key visual…" (`fabrica/plano.py`). Está alinhado; ao escrever cenas, acrescentar fundo dramático quente e o símbolo da cena.

Cada cena: `@H` (herói) + emoção + ação + símbolo + fundo. Ex.: `@H shocked, giant hourglass behind, burning city, red sky`.

## 8. Qualidade e consistência
- Fonte de imagem: **só FLUX (Cloudflare)**. O modelo local SD-Turbo foi testado e rejeitado em 20/11 (herói e vilão mudam a cada cena, traço sujo). Manter `SEM_LOCAL: "1"` no workflow: sem cota da nuvem, o vídeo **não é montado**.
- Conferir uma folha de contato dos quadros antes de mostrar ao usuário: mesmo herói, mesma paleta, sem texto gerado, sem imagem repetida.

## 9. Evitar
- Herói que muda de roupa, cabelo ou cor entre cenas.
- Cores lavadas ou fundo cinza (perde o look do canal).
- Realismo, foto, 3D, traço fino.
- Texto desenhado dentro da imagem (a legenda e o selo vêm do editor).
- Cena sem ação (herói parado sem emoção nem símbolo).
- Personagem protegido de franquia, pôster ou logo.
