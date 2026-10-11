import json, re, collections, unicodedata, sys, os

D = sys.argv[1]  # data dir
OUT = sys.argv[2]
d = json.load(open(os.path.join(D, 'fe26-dados.json')))
m = json.load(open(os.path.join(D, 'fe26-mapa.json')))
SP = m['spaces']


def strip_acc(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def slug(s):
    s = strip_acc(s).lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s[:60] or 'x'


def norm(t):
    t = strip_acc(t.upper())
    t = re.sub(r'[-\s\.]*DEP\.?', '', t)
    return re.sub(r'[\s\-\.]', '', t)


# ---------- map space index ----------
idx = collections.defaultdict(list)
for i, (t, p, c) in enumerate(SP):
    idx[norm(t)].append(i)
    for tok in re.split(r',|DEP\.?', t):
        tok = tok.strip()
        if tok:
            idx[norm(tok)].append(i)
numeric = {}
for i, (t, p, c) in enumerate(SP):
    for tok in re.findall(r'\d+', t):
        numeric.setdefault(int(tok), i)


def find_stage_space(name):
    n = norm(name)
    if n in idx:
        return idx[n][0]
    for i, (t, p, c) in enumerate(SP):
        if norm(t).startswith(n[:14]):
            return i
    return -1


STAGE_ALIAS = {
    'CIDADES QUE INSPIRAM - CRIE POLÍTICAS PÚBLICAS': 'CIDADES QUE INSPIRAM - TEATRO',
    'LOJA DO FUTURO': 'INSPIRA VAREJO - LOJA MODELO',
}
crescer = [i for i, s in enumerate(SP) if s[0] == 'MÃO NA MASSA - SALA CRESCER']


def stage_space(name):
    if name == 'MÃO NA MASSA - SALA PLANEJAR' and len(crescer) > 1:
        return crescer[1]
    if name == 'MÃO NA MASSA - SALA CRESCER' and crescer:
        return crescer[0]
    return find_stage_space(STAGE_ALIAS.get(name, name))


SHORT = {
    'ARENA DE NOVOS NEGÓCIOS E FRANQUIAS': 'Arena de Novos Negócios e Franquias',
    'ARENA CONECTA NEGÓCIOS': 'Arena Conecta Negócios',
    'CIDADES QUE INSPIRAM - CRIE POLÍTICAS PÚBLICAS': 'Cidades que Inspiram – Políticas Públicas',
    'ATENDIMENTO SEBRAE': 'Atendimento Sebrae',
    'ARENA DE MARKETING - Apresentado por Nuvemshop': 'Arena de Marketing',
    'ARENA DE INTELIGÊNCIA ARTIFICIAL - Apresentado por Google Gemini': 'Arena de Inteligência Artificial',
    'INSPIRA SABOR - RESTAURANTE MODELO': 'Inspira Sabor',
    'EXPRESSO DA INCLUSÃO': 'Expresso da Inclusão',
    'LOJA DO FUTURO': 'Loja do Futuro',
    'EMPREENDER SUSTENTÁVEL': 'Empreender Sustentável',
    'ARENA DA FELICIDADE': 'Arena da Felicidade',
    'MÃO NA MASSA - SALA VENDER': 'Mão na Massa – Vender',
    'CRIE SEBRAE': 'Crie Sebrae',
    'ARENA SERVIÇOS FINANCEIROS': 'Arena Serviços Financeiros',
    'ESPETÁCULO DELAS': 'Espetáculo Delas',
    'MÃO NA MASSA - SALA CRESCER': 'Mão na Massa – Crescer',
    'MÃO NA MASSA - SALA PLANEJAR': 'Mão na Massa – Planejar',
    'CLIQUE E VENDA': 'Clique e Venda',
    'SHOPPING COMPRE DO PEQUENO - SEBRAE COMUNIDADES': 'Shopping Compre do Pequeno',
    'JORNADA FACULDADE SEBRAE': 'Jornada Faculdade Sebrae',
    'FAÇA NEGÓCIOS COM O SEBRAE': 'Faça Negócios com o Sebrae',
    'MÃO NA MASSA - SALA LIDERAR': 'Mão na Massa – Liderar',
    'CIDADES QUE INSPIRAM - TEATRO': 'Cidades que Inspiram – Teatro',
    'INSPIRA BELEZA': 'Inspira Beleza',
    'ARENA TECH SEBRAE': 'Arena Tech Sebrae',
    'ARENA DO CONHECIMENTO': 'Arena do Conhecimento',
}

stages = []
for s in d['stages']:
    stages.append([SHORT.get(s['t'], s['t'].title()), s['e'], stage_space(s['t']), s['b']])
missing = [s[0] for s in stages if s[2] < 0]
print('stages w/o space:', missing, file=sys.stderr)

# ---------- interests ----------
R_FOOD = re.compile(r'aliment|gastronom|cozinha|restaurant|card[aá]pio|ficha t[eé]cnica|\bcmv\b|food|delivery|ifood|\bbares\b|confeit|\bdoce|caf[eé]\b|cafez|sabor|\bchef\b|marmita|receita|comida|lanche|hospitalidade|mocot|queij|chocolat|cacha[cç]a|culin|cervej|sorvet|padar|bebida|su[ií]no|charcut|petisc|geleia|gelei|tempero|desperd[ií]cio', re.I)
R_MKT = re.compile(r'marketplace|mercado livre|shopee|amazon|magalu|e-?commerce|loja virtual|loja online|vend(er|as?) (online|na internet|pela internet)|vendendo online|live ?(shop|commerce)|nuvemshop|log[ií]stic|embalage|\bfrete|alibaba|fornecedor|importa|atacad|dropship|marca registrada|registro de marca|\binpi\b|m[uú]sic|instrumento|\barte\b|artista|desenh|ilustra|papelaria|pincel|aquarela|artesanato|tintas?\b', re.I)
R_DES = re.compile(r'design|\bux\b|experi[eê]ncia d|startup|branding|identidade|marca\b|marcas\b|criativ|economia criativa|audiovisual|pitch|inova', re.I)
SEG_FOOD = {'Alimentação e Gastronomia', 'Máquinas e Equipamentos'}
SEG_MKT = {'Artesanato'}


def interest(text, seg='', stage=''):
    mask = 0
    if R_FOOD.search(text) or seg in SEG_FOOD or stage.startswith('INSPIRA SABOR'):
        mask |= 1
    if R_MKT.search(text) or seg in SEG_MKT or stage == 'CLIQUE E VENDA':
        mask |= 2
    if R_DES.search(text) or stage == 'CRIE SEBRAE':
        mask |= 4
    return mask


def hm(s):
    return int(s[:2]) * 60 + int(s[2:])


acts = []
for (pid, si, ci, start, end, title, spk) in d['acts']:
    day = int(start[:2])
    st = d['stages'][si]['t']
    msk = interest(title + ' ' + spk, '', st)
    acts.append([pid, si, ci, day, hm(start[2:]), hm(end), title, spk, msk])

# ---------- exhibitors ----------
SEGS = sorted({e['s'] for e in d['ex'] if e['s']})
EIXOS = sorted({e['e'] for e in d['ex'] if e['e']})


def ex_space(e):
    st = e['st']
    if 'cidades que inspiram' in st.lower():
        return find_stage_space('CIDADES QUE INSPIRAM - TEATRO'), 1
    if 'arena' in st.lower():
        nm = re.sub(r'^\d+-\s*', '', st).strip()
        i = find_stage_space(nm)
        if i < 0:
            for j, s in enumerate(SP):
                if norm(nm) in norm(s[0]):
                    i = j
                    break
        return i, 0
    s2 = re.sub(r'^PA\s*,\s*', 'PA - ', st)
    for tok in [x for x in re.split(r'[,/]', s2) if x.strip()]:
        k = norm(tok)
        if k in idx:
            return idx[k][0], 0
        if k.startswith('PA'):
            for kk, v in idx.items():
                if kk.startswith(k) and len(kk) <= len(k) + 3:
                    return v[0], 0
    nums = [int(x) for x in re.findall(r'\d+', st)]
    if nums and not st.upper().startswith(('C', 'P')):
        n = nums[0]
        for delta in (1, -1, 2, -2):
            if n + delta in numeric:
                return numeric[n + delta], 1
    return -1, 0


ex = []
keys = set()
unm = []
for e in d['ex']:
    si, approx = ex_space(e)
    if si < 0:
        unm.append(e['n'] + ' ' + e['st'])
    k = 'e-' + slug(e['n'])
    if k in keys:
        k = k + '-' + slug(e['st'])
    keys.add(k)
    msk = interest(e['n'] + ' ' + e['b'], e['s'])
    bio = e['b']
    if len(bio) > 240:
        bio = bio[:237].rsplit(' ', 1)[0] + '…'
    ex.append([k, e['n'], SEGS.index(e['s']) if e['s'] else -1, e['tp'], e['st'], EIXOS.index(e['e']) if e['e'] else -1,
               bio, e['l'], si, approx, msk])
print('exhibitors w/o space:', len(unm), unm, file=sys.stderr)

# ---------- plan ----------
def find_act(day, start, needle):
    t = hm(start)
    c = [a for a in acts if a[3] == day and a[4] == t and needle.lower() in a[6].lower()]
    if len(c) != 1:
        raise SystemExit(f'plan miss {day} {start} {needle}: {len(c)}')
    return c[0][0]


def ex_by(needle):
    c = [i for i, e in enumerate(ex) if needle.lower() == e[1].lower()] or \
        [i for i, e in enumerate(ex) if e[1].lower().startswith(needle.lower())]
    if not c:
        raise SystemExit('ex miss ' + needle)
    return c[0]


ROUTES = {
    'mkt': ['GRUPO AZIN', 'VIANG COMMERCE', 'SELLER HOUSE', 'GESTAO WISE', 'VENDIZAP', 'INVERSU', 'NYC DO BRASIL',
            'SRS EMBALAGENS', 'PAGHIPER', 'JADLOG', 'LALAMOVE', 'NUVEMSHOP'],
    'sabores': ['MANGI BONE', 'BENDITTA HORA', 'LU DELÍCIAS NO POTE', 'DOCE MORADA', 'CASA DO BOLO DE ROLO', 'CACAU & CAFÉ',
                'ALVA NA COZINHA', 'VIVORO CHOCOLATES', 'NÉCTAR PURO', 'SABOR DA CASA AFEGÃ', 'BOLIVITA CAFÉ',
                'RCIB SALGADOS E BOLOS', 'TORRES DE TENTAÇÃO', 'MALU DULCES DOCES', 'HANUKKAH CONFEITARIA',
                'CHEVERE RESTAURANTE', 'GRANDE CHARCUTARIA', 'É DE CENOURA', 'QUINTA DAS MAGNÓLIAS', 'QUEIJARIA BOLDERINI'],
    'equip': ['REGRA 3', 'ESCOLA SORVETE', 'STI3 SISTEMAS', 'CONTROL/P', 'PIDOAI', 'MEGACOMM', 'CHOCOLAB', 'REFRIGERAÇÃO FABRICIO',
              'INDUSFRITAS', 'TEKNOVA', 'TOTAL VENDING', 'MERCADINHO SEO JUCA', 'OPINE MARKET'],
    'design': ['AOTANI DESIGN', 'ATREVO DESIGN', 'VER CONSULTORIA', 'KHYMERA', 'CONNECTMEE', 'TENDENCY BRASIL', 'SYNCOHUB',
               'DOCUMENTA MARCAS', 'FOR MARCA', 'MODAL MARCAS', 'REGISTRE FACIL', 'CUMARU ESTUDIO'],
    'arte': ['H2OMAIS TINTAS', 'KAHDERNOS', 'CURSIVA', 'GARIMPANDO ARTES', 'AFETO QUE SE BORDA', 'LINARTES', 'STILOGIZ',
             'CÊ TÁ FAZENDO ARTE', 'DACUNHA MUSICS KIDS'],
}
routes = {k: [ex_by(n) for n in v] for k, v in ROUTES.items()}

I, B, O = 3, 2, 1  # peso
plan = {
    19: {'tema': 'Reconhecer a feira + marketplaces',
         'lead': 'Dia de entender o mapa e abrir o tema marketplaces com três visões: panorama, fornecedores (Alibaba) e operação (Magalu).',
         'items': [
             ['blk', '10:45', '11:00', 'chegada', 'Chegada: pegar o mapa e achar Inspira Sabor, Clique e Venda, Arena de Novos Negócios e Arena do Conhecimento'],
             ['talk', find_act(19, '1100', 'crescimento dos marketplaces'), I],
             ['talk', find_act(19, '1130', 'Experiência e jornada do cliente'), B, 'Chegue a partir de 11h40, depois da palestra anterior.'],
             ['blk', '12:15', '13:20', 'almoco', 'Almoço'],
             ['talk', find_act(19, '1330', 'Desperdícios na cozinha'), I],
             ['talk', find_act(19, '1425', 'redesenhando as oportunidade'), I],
             ['blk', '15:00', '15:50', 'estandes', 'Estandes: marketplace e logística', 'mkt'],
             ['talk', find_act(19, '1600', 'Negócio no Azul'), I],
             ['blk', '16:30', '17:00', 'pausa', 'Pausa'],
             ['talk', find_act(19, '1700', 'Design Thinking'), O],
         ],
         'alts': [[find_act(19, '1530', 'Seu cliente já te avaliou'), 'Bate com a Magalu. Fiquei com a Magalu por ser o único conteúdo específico desse marketplace.'],
                  [find_act(19, '1200', 'agentes de IA no WhatsApp'), 'Durante o almoço, se quiser comer depois.']]},
    20: {'tema': 'Dia da comida',
         'lead': 'O dia mais denso: Mocotó à tarde e dois conteúdos de margem no fim do dia, com uma pausa longa no meio.',
         'items': [
             ['talk', find_act(20, '1030', 'IA com foco no cardápio'), B],
             ['blk', '11:15', '12:00', 'estandes', 'Estandes: sabores artesanais', 'sabores'],
             ['blk', '12:00', '12:55', 'almoco', 'Almoço'],
             ['talk', find_act(20, '1300', 'Mercado Livre'), I],
             ['blk', '13:35', '14:00', 'chegada', 'Ir direto para a Arena do Conhecimento garantir lugar'],
             ['talk', find_act(20, '1400', 'Mocotó'), I],
             ['blk', '15:00', '16:50', 'pausa', 'Pausa longa: café, sentar, anotar'],
             ['talk', find_act(20, '1700', 'Presente do futuro'), B],
             ['talk', find_act(20, '1730', 'Marmita rentável'), I],
             ['talk', find_act(20, '1830', 'Precificação Estratégica'), I],
         ],
         'alts': [[find_act(20, '1230', 'Cozinha Blindada'), 'Bate com o Mercado Livre. Volta como "Ficha técnica na prática" na quarta.'],
                  [find_act(20, '1430', 'NRA SHOW'), 'Bate com o Mocotó. Tema parecido na quinta, 12h30.'],
                  [find_act(20, '1530', 'Harmonização de Cafés'), 'Opcional durante a pausa longa.'],
                  [find_act(20, '1240', 'lucro de um restaurante'), 'Durante o almoço.'],
                  [find_act(20, '1200', 'fazendo cultura'), 'Durante o almoço. Conversa com o nicho de acessórios musicais.']]},
    21: {'tema': 'Números da cozinha + Shopee',
         'lead': 'Três palestras no mesmo palco formam um mini-curso: ficha técnica, CMV e engenharia de cardápio. O dia fecha com a Shopee.',
         'items': [
             ['blk', '11:00', '11:25', 'chegada', 'Chegada e café'],
             ['talk', find_act(21, '1130', 'Ficha Técnica na prática'), I],
             ['blk', '12:15', '13:20', 'almoco', 'Almoço'],
             ['talk', find_act(21, '1330', 'CMV'), I],
             ['blk', '14:20', '15:20', 'estandes', 'Estandes: equipamentos e food service', 'equip'],
             ['talk', find_act(21, '1530', 'Engenharia de cardápio'), I],
             ['talk', find_act(21, '1620', 'bares e restaurantes'), B],
             ['blk', '16:50', '17:30', 'pausa', 'Pausa'],
             ['talk', find_act(21, '1730', 'Pitchs dos expositores'), O, 'Vai até 19h15. Assista o começo: é onde aparecem fundadores que podem precisar de design.'],
             ['talk', find_act(21, '1800', 'Shopee'), I],
         ],
         'alts': [[find_act(21, '1600', 'Humor que vende'), 'Rafaella Tuma bate com a engenharia de cardápio. É a melhor do eixo design.'],
                  [find_act(21, '1400', 'Pipó Gourmet'), 'Cabe no lugar dos estandes das 14h20.'],
                  [find_act(21, '1300', 'PROFISSÃO AINDA NÃO EXISTIR'), 'Transição de carreira. Bate com o CMV.']]},
    22: {'tema': 'Food design, tendências e delivery',
         'lead': 'Food Design à tarde, roteiro de design e marca de manhã e delivery no fim do dia.',
         'items': [
             ['talk', find_act(22, '1030', 'Rota da Fama'), B],
             ['blk', '11:20', '12:20', 'estandes', 'Estandes: design, marca e startups', 'design'],
             ['talk', find_act(22, '1230', 'Tendências para serviços de alimentação'), I],
             ['blk', '13:15', '14:15', 'almoco', 'Almoço'],
             ['blk', '14:15', '15:20', 'estandes', 'Estandes: artesanato e arte (opcional)', 'arte'],
             ['talk', find_act(22, '1530', 'Food Design'), I],
             ['talk', find_act(22, '1630', 'Hospitalidade em Serviços'), O],
             ['talk', find_act(22, '1720', 'Digital Commerce'), B],
             ['blk', '17:50', '18:25', 'pausa', 'Pausa'],
             ['talk', find_act(22, '1830', 'Digitalização e Delivery'), I],
         ],
         'alts': [[find_act(22, '1900', 'iFood'), 'Mais focada em iFood. Dá para sair da anterior às 19h e pegar quase toda.'],
                  [find_act(22, '1100', 'Estratégias de conteúdo'), 'Painel de conteúdo para e-commerce com Nuvemshop e marcas.'],
                  [find_act(22, '1740', 'Pare de disputar preço'), 'Marca e posicionamento.'],
                  [find_act(22, '1800', 'Brasil Feito à Mão'), 'Artesanato para exportação (ApexBrasil).']]},
}

app = {
    'stages': stages, 'cats': d['cats'], 'segs': SEGS, 'eixos': EIXOS,
    'acts': acts, 'ex': ex,
    'centers': [s[2] for s in SP], 'stitles': [s[0] for s in SP],
    'plan': plan, 'routes': routes, 'fetched': d.get('fetched', ''),
}
json.dump(app, open(os.path.join(OUT, 'app-data.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
mp = {'w': m['w'], 'h': m['h'], 'imgH': m['imgH'], 'polys': [s[1] for s in SP], 'mask': m['mask']}
json.dump(mp, open(os.path.join(OUT, 'mapa.json'), 'w'), separators=(',', ':'))
print('ok', os.path.getsize(os.path.join(OUT, 'app-data.json')), os.path.getsize(os.path.join(OUT, 'mapa.json')), file=sys.stderr)
