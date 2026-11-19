"""VÍDEO DE TESTE TÉCNICO (não é para publicar): serve só para validar imagens, narração, legendas e edição."""
SLUG = "teste"
TITULO = "E se Você Acordasse com a Cidade em Chamas? (TESTE)"
TITULOS = [TITULO]
PROTAG = "chibi, 1boy, spiky black hair, green hooded cape, brown leather harness"
VOZ = "pm_alex"
VELOCIDADE = 0.95
TAGS = ["e se você", "teste"]
COMENTARIO = "Teste técnico."
DESCRICAO = dict(gancho="Teste técnico da fábrica.", resumo="Não publicar.", hashtags=["#teste"])

BLOCOS = [
    dict(nome="GANCHO", titulo=None, capitulo="O gancho", humor="tenso", local="burning medieval city at night, red sky", texto="""
Você acorda e o céu da cidade está em chamas. || @H waking up, shocked, burning city behind
Faltam apenas {NUM:13|ANOS} para o seu tempo acabar. {BOOM} || @H extreme close-up of eyes, giant hourglass red sand behind
Mas antes disso, você vai precisar fazer uma escolha. || wide shot, giant stone wall breaking, tiny chibi villagers running
"""),
    dict(nome="ESCOLHA 1", titulo="A INJEÇÃO", humor="epico", local="dark moonlit forest, glowing fireflies", texto="""
Um velho soldado segura uma seringa brilhante na sua frente. || medium shot, old chibi soldier holding glowing syringe, @H in front
Ele diz que ela guarda um poder gigantesco. || close-up of glowing syringe, sparks
Você aceita sem pensar duas vezes. {FLASH} || @H determined, huge orange explosion behind
Esse foi o primeiro erro. || @H serious, low angle shot, dark clouds
"""),
    dict(nome="FECHAMENTO", titulo=None, capitulo="O desfecho", humor="calmo", local="sunrise over ruined wall", texto="""
Uma escolha. Mil consequências. || @H looking at the sunrise, calm, wide shot
Qual seria a sua escolha? || @H smiling, close-up portrait, golden light
"""),
]
THUMBS = [
    dict(linha1="E SE VOCÊ ACORDASSE COM A", titulo="CIDADE\nEM CHAMAS?", etiqueta="13 ANOS DE VIDA",
         prompt="@H extreme close-up, shocked face on the right side of the frame, huge orange explosion, burning city, empty space on the left"),
]
SHORTS = [
    dict(titulo="E se você tivesse 13 anos de vida? (TESTE)", humor="tenso", local="burning city, red sky", texto="""
Você tem só {NUM:13|ANOS} de vida. {BOOM} || @H shocked, giant hourglass behind
E o mundo inteiro está caindo. || wide shot, burning city, giant wall breaking
O que você faria? || @H determined, close-up portrait
"""),
]
