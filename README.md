# Fábrica do Destino Paralelo

Gera vídeos do canal **Destino Paralelo** (anime, "E se você…", português) de ponta a ponta, só com ferramentas grátis,
no GitHub Actions. Fábrica separada da Crónicas del Pergamino — nada é compartilhado.

## Como funciona
1. Um roteiro em `videos/<nome>/roteiro.py` (blocos `GANCHO`, `ESCOLHA N`, `FECHAMENTO`; cada linha = 1 imagem).
2. `pedidos.txt` com `<nome>` (vídeo longo + miniaturas) ou `<nome>:shorts`.
3. Ao salvar, o GitHub: gera as imagens anime (modelo grátis em CPU, dividido em vários computadores),
   narra em português (Kokoro), edita (zoom/deslize/impacto, legenda com palavra amarela, selo da escolha,
   número em destaque), cria as miniaturas A/B e publica o MP4 em um Release.
4. O resultado fica em `saida/<nome>/` (`info.json` com título, descrição com capítulos, tags, comentário fixado; `thumb_A.jpg`, `thumb_B.jpg`; `short_N.json`).

## Usar suas próprias imagens (ex.: geradas no Tubefy)
Em vez do modelo grátis, você pode mandar as imagens prontas:
1. `python -m fabrica.cenas videos/<nome>` cria `videos/<nome>/cenas.txt` (lista numerada das cenas, só com a narração).
2. Gere as imagens na sua ferramenta e nomeie com o número da cena: `001.png`, `002.png`… (ou ZIP) em `videos/<nome>/imagens/`.
   Shorts: `imagens/short_1/`, `short_2/`, `short_3/` (vertical 9:16). Miniaturas: `imagens/miniatura_A.png`, `miniatura_B.png`.
3. Cenas sem imagem repetem a anterior (padrão) — ou, com `IMAGENS_FALTANTES = "gerar"` no roteiro, o modelo grátis completa.
A fábrica só gera o que não foi enviado; narração, legendas, selos, números, edição e miniaturas continuam automáticos.

## Formato do roteiro
```python
SLUG = "titan"; TITULO = "E se Você Herdasse o Titã Fundador?"
PROTAG = "chibi, 1boy, spiky black hair, green hooded cape"   # herói original ("você"), repetido em todas as cenas com @H
BLOCOS = [dict(nome="ESCOLHA 1", titulo="A INJEÇÃO", humor="tenso", local="burning city, red sky", texto="""
Você tem {NUM:13|ANOS} de vida. {BOOM} || @H shocked, giant hourglass behind
""")]
```
- Antes de `||`: narração. Depois: descrição da imagem em inglês (`@H` = o herói).
- `{NUM:13|ANOS}` número grande na tela (e falado); `{BOOM}` impacto + tremor + flash; `{FLASH}` só flash.
- `humor`: `tenso`, `epico` ou `calmo` (música de fundo).

## Regras do canal (não esquecer)
- Título "E se você…", narração em 2ª pessoa, blocos de escolha, slogan "Uma escolha. Mil consequências." no fecho.
- Só anime. Nunca repetir tema (`temas_feitos.txt`). Herói original, sem desenhar personagens protegidos.
- Roteiro longo 1.500–2.200 palavras; curto ~130.
- Publicar sempre público; horários que o usuário diz são horário da Espanha (Madrid).
