/* Roteiro FE26 — gerador de roteiro sem IA (árvore de decisão + pontuação).
   Mesmos critérios usados no roteiro feito à mão:
   1) tema de interesse no título vale mais que o palco; 2) prioridade dos interesses pesa;
   3) palestras/painéis/cases > atividades repetidas ou culturais; 4) nada sobreposto
   (tolerância de 15 min com aviso "chegue a partir de…"); 5) almoço sem pressa;
   6) ritmo limita palestras por dia; 7) bloco de estandes do tema do dia, em ordem de caminhada;
   8) pausa à tarde no ritmo leve/equilibrado; 9) alternativas para os conflitos. */
(function (root) {
'use strict';

const THEMES = [
  {id:'gastro', label:'Gastronomia e alimentação', short:'gastronomia',
   re:/aliment|gastronom|cozinha|restaurant|card[aá]pio|ficha t[eé]cnica|\bcmv\b|food|delivery|ifood|\bbares\b|confeit|\bdoces?\b|caf[eé]\b|cafez|sabor|\bchef\b|marmita|receita|comida|lanche|hospitalidade|queij|chocolat|cacha[cç]a|culin|cervej|sorvet|padar|bebida|charcut|petisc|gelei|tempero|desperd[ií]cio/i,
   stages:['Inspira Sabor'], segs:['Alimentação e Gastronomia']},
  {id:'online', label:'Vendas online e marketplaces', short:'vendas online',
   re:/marketplace|mercado livre|shopee|amazon|magalu|e-?commerce|loja virtual|loja online|vend\w* (online|na internet|pela internet)|live ?(shop|commerce)|nuvemshop|log[ií]stic|embalage|\bfrete|alibaba|fornecedor|importa|dropship|whats ?app|instagram|tiktok/i,
   stages:['Clique e Venda'], segs:['Marketing, Marketing Digital e Vendas']},
  {id:'mkt', label:'Marketing, marca e clientes', short:'marketing',
   re:/marketing|\bmarcas?\b|branding|redes sociais|conte[uú]do|v[ií]deo|tr[aá]fego|an[uú]ncio|clientes?\b|fideliza|vend(a|as|er)\b|posicionamento|comunica[cç]/i,
   stages:['Arena de Marketing'], segs:['Marketing, Marketing Digital e Vendas']},
  {id:'criativa', label:'Design, moda e economia criativa', short:'criatividade',
   re:/design|\bux\b|criativ|economia criativa|moda\b|autoral|audiovisual|m[uú]sic|\barte\b|artista|artesan|ilustra|identidade|cultura/i,
   stages:['Crie Sebrae', 'Shopping Compre do Pequeno'], segs:['Artesanato', 'Moda e Acessório']},
  {id:'ia', label:'Inteligência artificial e tecnologia', short:'IA e tecnologia',
   re:/intelig[eê]ncia artificial|\bIAs?\b|tecnolog|digital|google|gemini|chat ?gpt|automa|startup|inova/i,
   stages:['Arena de Inteligência Artificial', 'Arena Tech Sebrae'], segs:['Sistemas e Soluções Tecnológicas']},
  {id:'fin', label:'Finanças, preço e crédito', short:'finanças',
   re:/finan|cr[eé]dito|dinheiro|pre[cç]o|precifica|custo|fluxo de caixa|d[ií]vida|score|imposto|tribut|microcr[eé]dito|investim/i,
   stages:['Arena Serviços Financeiros'], segs:['Finanças e Investimentos']},
  {id:'comecar', label:'Abrir um negócio e franquias', short:'abrir negócio',
   re:/franquia|abrir|come[cç]ar|primeiros? passos|ideia|\bMEI\b|formaliz|valide|novo neg[oó]cio|empreender/i,
   stages:['Arena de Novos Negócios e Franquias', 'Atendimento Sebrae'], segs:['Franquias']},
  {id:'beleza', label:'Beleza e bem-estar', short:'beleza',
   re:/beleza|est[eé]tica|cabel|barb|unha|nails|maquiagem|pele\b|sal[aã]o|visagismo|corte\b|bem-estar/i,
   stages:['Inspira Beleza'], segs:['Saúde, Beleza e Bem-estar']},
  {id:'gestao', label:'Gestão, equipe e liderança', short:'gestão',
   re:/lideran|equipe|gest[aã]o de pessoas|feedback|felicidade|prop[oó]sito|produtividade|gerenciando|decis[oõ]es|planejamento|estrat[eé]gi/i,
   stages:['Arena da Felicidade', 'Arena do Conhecimento'], segs:['Assessorias e Treinamentos']},
  {id:'sustent', label:'Sustentabilidade e impacto', short:'sustentabilidade',
   re:/sustent|\besg\b|recicl|verde|impacto|inclus|economia circular|pl[aá]stico/i,
   stages:['Empreender Sustentável', 'Expresso da Inclusão'], segs:[]},
  {id:'varejo', label:'Varejo e loja física', short:'varejo',
   re:/varejo|loja f[ií]sica|vitrine|ponto de venda|atendimento ao cliente|trade marketing|omnicanal/i,
   stages:['Loja do Futuro'], segs:['Representações / Porta a porta']}
];
const THEME = Object.fromEntries(THEMES.map(t => [t.id, t]));
const PACE = {
  leve:       {max:3, lunch:75, pause:true,  label:'Leve'},
  equilibrado:{max:5, lunch:60, pause:true,  label:'Equilibrado'},
  intenso:    {max:7, lunch:50, pause:false, label:'Intenso'}
};
const CAT_W = {'Palestra':1, 'Painel':1.1, 'Case':1.1, 'Talk Show':1, 'Aula show':0.8, 'Oficina':0.8, 'Pitch':0.5,
  'Desfile':0.3, 'Apresentação Cultural':0.1, 'Visita Guiada':0.1, 'Demonstração/exibição de jogos':0.1};
const PRACTICAL = new Set(['Aula show', 'Oficina']);
const W_PRIO = [3, 2, 1.4];
const DAYS = [19, 20, 21, 22];
const DAYW = {19:'Segunda', 20:'Terça', 21:'Quarta', 22:'Quinta'};
const fmt = m => String(Math.floor(m / 60)).padStart(2, '0') + 'h' + String(m % 60).padStart(2, '0');
const hhmm = m => String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');

function prepare(D){
  const stages = D.stages.map(s => ({name:s[0], eixo:s[1], sp:s[2]}));
  const acts = D.acts.map(a => ({id:a[0], st:a[1], cat:D.cats[a[2]], day:a[3], s:a[4], e:a[5], title:a[6], spk:a[7]}));
  // atividades que se repetem 3+ vezes no mesmo dia (labirinto, loja-modelo, teatro…) ficam de fora das escolhas principais
  const rep = {}; acts.forEach(a => { const k = a.day + '|' + a.title.toLowerCase(); rep[k] = (rep[k] || 0) + 1; });
  acts.forEach(a => { a.rep = rep[a.day + '|' + a.title.toLowerCase()] >= 3; });
  const ex = D.ex.map((e, i) => ({i, name:e[1], seg:e[2] >= 0 ? D.segs[e[2]] : '', stand:e[4], bio:e[6] || '', sp:e[8]}));
  return {stages, acts, ex, cen: D.centers};
}

function themeHits(text, stageName, th){
  let v = 0;
  if (th.re.test(text)) v += 1;
  if (th.stages.includes(stageName)) v += 0.6;
  return v;
}

function scoreAct(a, P, ans){
  const st = P.stages[a.st];
  let s = 0; const hits = [];
  ans.themes.forEach((id, i) => {
    const h = themeHits(a.title, st.name, THEME[id]);
    if (h) { s += W_PRIO[i] * h; hits.push(id); }
  });
  if (!s) return null;
  s *= CAT_W[a.cat] == null ? 0.6 : CAT_W[a.cat];
  if (a.rep) s *= 0.25;
  if (ans.format === 'ouvir' && PRACTICAL.has(a.cat)) s *= 0.8;
  if (ans.format === 'pratica' && PRACTICAL.has(a.cat)) s *= 1.35;
  if (ans.stage === 'ideia' && /Comece seu Neg/.test(st.eixo)) s += 0.5;
  if (ans.stage === 'crescer' && /Melhore|Amplie/.test(st.eixo)) s += 0.5;
  if (st.name === 'Arena do Conhecimento') s += 0.4;      // palco principal, nomes grandes
  if (a.e - a.s < 20) s *= 0.7;
  return {a, s, hits};
}

function travel(P, a, b, walkLess){
  if (a.st === b.st) return 0;
  const sa = P.stages[a.st].sp, sb = P.stages[b.st].sp;
  const ca = P.cen[sa], cb = P.cen[sb];
  if (!ca || !cb) return 5;
  const d = Math.hypot(ca[0] - cb[0], ca[1] - cb[1]);            // unidades do mapa (~1px = 1m aprox.)
  return Math.min(walkLess ? 20 : 12, 3 + Math.round(d / (walkLess ? 80 : 120)));
}

// encaixe guloso: maior nota primeiro, sem conflito (tolerância de 15 min no início com aviso)
function fit(cands, P, ans, pace, blocks, win, usedTitles){
  const picked = [], left = cands.filter(c => !usedTitles.has(c.a.title.toLowerCase()));
  const same = {};   // variedade: cada palestra do mesmo assunto principal vale um pouco menos
  while (picked.length < pace.max && left.length) {
    let bi = -1, bv = 0;
    for (let i = 0; i < left.length; i++) { const v = left[i].s * Math.pow(0.8, same[left[i].hits[0]] || 0); if (v > bv) { bv = v; bi = i; } }
    if (bi < 0) break;
    const c = left.splice(bi, 1)[0];
    if (picked.some(p => p.a.title.toLowerCase() === c.a.title.toLowerCase())) continue;
    const a = c.a;
    if (a.s < win[0] || a.e > win[1]) continue;
    if (blocks.some(b => a.s < b[1] && a.e > b[0])) continue;
    let ok = true, late = 0, after = null;
    for (const p of picked) {
      const q = p.a;
      const gapAfter = a.s - q.e, gapBefore = q.s - a.e;
      if (a.s >= q.s) { // a depois de q
        const need = travel(P, q, a, ans.walkLess);
        if (gapAfter >= need) continue;
        const lateness = q.e + need - a.s;
        if (lateness <= 15 && a.e - a.s >= 40 && lateness < (a.e - a.s) / 3) { late = Math.max(late, lateness); after = q; continue; }
        ok = false; break;
      } else {          // a antes de q
        const need = travel(P, a, q, ans.walkLess);
        if (gapBefore >= need) continue;
        const lateness = a.e + need - q.s;
        if (lateness <= 15 && q.e - q.s >= 40 && !p.late && lateness < (q.e - q.s) / 3) { continue; }
        ok = false; break;
      }
    }
    if (!ok) continue;
    picked.push(Object.assign({}, c, late ? {late, arrive: a.s + late} : {}));
    same[c.hits[0]] = (same[c.hits[0]] || 0) + 1;
  }
  // recalcula avisos de chegada atrasada com a ordem final
  picked.sort((x, y) => x.a.s - y.a.s);
  for (let i = 1; i < picked.length; i++) {
    const q = picked[i - 1].a, a = picked[i].a;
    const need = travel(P, q, a, ans.walkLess);
    if (q.e + need > a.s) picked[i].note = `Chegue a partir de ${fmt(q.e + need)}, depois da palestra anterior.`;
  }
  return picked;
}

function standScore(e, id){
  const th = THEME[id]; let v = 0;
  if (th.segs.includes(e.seg)) v += 1;
  if (th.re.test(e.name + ' ' + e.bio)) v += 1.5;
  return v;
}

function makePlan(D, ans){
  const P = D.__prep || (D.__prep = prepare(D));
  const pace = PACE[ans.pace] || PACE.equilibrado;
  const win = [ans.arrive, ans.leave];
  const scored = P.acts.map(a => scoreAct(a, P, ans)).filter(Boolean);
  const maxS = Math.max(1, ...scored.map(c => c.s));
  const usedStands = new Set(), usedTitles = new Set();
  const plan = {answers: ans, days: {}, routes: {}};
  const attending = DAYS.filter(d => ans.days.includes(d));
  attending.forEach((day, di) => {
    const cands = scored.filter(c => c.a.day === day).sort((x, y) => y.s - x.s || (x.a.e - x.a.s) - (y.a.e - y.a.s));
    const lunchLen = pace.lunch, standLen = ans.stands;
    // tenta várias posições para almoço e estandes e fica com a combinação de maior nota total
    let best = null;
    // quem chega depois de 12h30 ou sai antes de 13h30 já almoça fora da feira
    const lunchStarts = []; if (win[0] < 750 && win[1] > 810) for (let m = 690; m <= 810; m += 15) if (m >= win[0] && m + lunchLen <= win[1]) lunchStarts.push(m);
    if (!lunchStarts.length) lunchStarts.push(null);
    const standStarts = [null]; if (standLen) for (let m = Math.max(win[0], 780); m + standLen <= win[1]; m += 30) standStarts.push(m);
    for (const L of lunchStarts) for (const S of standStarts) {
      if (L != null && S != null && S < L + lunchLen && S + standLen > L) continue;
      if (standLen && S == null && standStarts.length > 1) continue;
      const blocks = []; if (L != null) blocks.push([L, L + lunchLen]); if (S != null) blocks.push([S, S + standLen]);
      const picked = fit(cands, P, ans, pace, blocks, win, usedTitles);
      const tot = picked.reduce((t, c) => t + c.s, 0) - (L == null ? 0 : Math.abs(L - 735) / 120);
      if (!best || tot > best.tot) best = {tot, picked, L, S};
    }
    const items = [];
    const pk = best.picked;
    pk.forEach(c => usedTitles.add(c.a.title.toLowerCase()));
    pk.forEach(c => items.push({t:c.a.s, it:['talk', c.a.id, c.s >= 0.62 * maxS ? 3 : c.s >= 0.38 * maxS ? 2 : 1].concat(c.note ? [c.note] : [])}));
    if (best.L != null) items.push({t:best.L, it:['blk', hhmm(best.L), hhmm(best.L + lunchLen), 'almoco', 'Almoço']});
    // tema do dia pelos assuntos mais presentes
    const tally = {}; pk.forEach(c => c.hits.forEach(h => { tally[h] = (tally[h] || 0) + c.s; }));
    const top = Object.keys(tally).sort((x, y) => tally[y] - tally[x]);
    // estandes: tema que gira entre os interesses, sem repetir estande entre os dias
    if (best.S != null) {
      const tid = ans.themes[di % ans.themes.length];
      const n = Math.max(6, Math.round(standLen / 5));
      const list = P.ex.filter(e => !usedStands.has(e.i)).map(e => [standScore(e, tid), e]).filter(x => x[0] > 0)
        .sort((x, y) => y[0] - x[0]).slice(0, n).map(x => x[1]);
      list.forEach(e => usedStands.add(e.i));
      // ordem de caminhada: da esquerda para a direita no mapa, quem não tem posição vai por último
      list.sort((x, y) => (x.sp >= 0 && P.cen[x.sp] ? P.cen[x.sp][0] : 1e9) - (y.sp >= 0 && P.cen[y.sp] ? P.cen[y.sp][0] : 1e9));
      if (list.length) {
        const rk = 'g' + day; plan.routes[rk] = list.map(e => e.i);
        items.push({t:best.S, it:['blk', hhmm(best.S), hhmm(best.S + standLen), 'estandes', 'Estandes: ' + THEME[tid].short, rk]});
      }
    }
    // pausa: maior intervalo livre da tarde (30 min), nos ritmos leve e equilibrado
    if (pace.pause) {
      const busy = items.map(x => x.it[0] === 'talk' ? [P.acts.find(a => a.id === x.it[1]).s, P.acts.find(a => a.id === x.it[1]).e] : [hm(x.it[1]), hm(x.it[2])]).sort((x, y) => x[0] - y[0]);
      let gap = null, cur = Math.max(win[0], 900);
      for (const [s, e] of busy) { if (e <= cur) continue; if (s - cur >= 30 && (!gap || s - cur > gap[1] - gap[0])) gap = [cur, s]; cur = Math.max(cur, e); }
      if (busy.length && win[1] - cur >= 30 && cur < win[1] - 30 && (!gap || win[1] - cur > gap[1] - gap[0]) && cur < Math.max(...busy.map(b => b[1]))) gap = [cur, win[1]];
      if (gap) items.push({t:gap[0], it:['blk', hhmm(gap[0]), hhmm(gap[0] + 30), 'pausa', 'Pausa']});
    }
    // chegada
    items.sort((x, y) => x.t - y.t);
    const first = items.length ? items[0].t : win[0];
    const stNames = [...new Set(pk.map(c => P.stages[c.a.st].name))].slice(0, 4);
    const arr = Math.max(win[0], first - 15);
    if (first - arr >= 10) items.unshift({t:arr, it:['blk', hhmm(arr), hhmm(first), 'chegada', di === 0 && stNames.length ? 'Chegada: pegar o mapa e achar ' + listPt(stNames) : 'Chegada e café']});
    // alternativas: boas palestras que ficaram de fora
    const chosen = new Set(pk.map(c => c.a.id));
    const altSeen = new Set();
    const alts = cands.filter(c => !chosen.has(c.a.id) && !usedTitles.has(c.a.title.toLowerCase()) && !altSeen.has(c.a.title.toLowerCase()) && altSeen.add(c.a.title.toLowerCase()) && !c.a.rep && c.s >= 0.45 * maxS && c.a.s >= win[0] && c.a.e <= win[1]).slice(0, 3).map(c => {
      const clash = pk.find(p => c.a.s < p.a.e && c.a.e > p.a.s);
      return [c.a.id, clash ? `No mesmo horário de “${short(clash.a.title)}”. Troque se preferir.` : 'Cabe se sobrar energia no dia.'];
    });
    const labels = top.slice(0, 2).map(id => THEME[id].short);
    const tema = (di === 0 ? 'Reconhecer a feira' + (labels.length ? ' + ' + labels[0] : '') : labels.length ? cap(labels.join(' + ')) : 'Dia livre para explorar');
    plan.days[day] = {tema, lead:'', items: items.map(x => x.it), alts};
  });
  return plan;
}
const hm = s => +s.slice(0, 2) * 60 + +s.slice(3, 5);
const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
const short = t => t.length > 48 ? t.slice(0, 46).replace(/\s+\S*$/, '') + '…' : t;
const listPt = a => a.length > 1 ? a.slice(0, -1).join(', ') + ' e ' + a[a.length - 1] : a[0];

root.FE26Planner = {THEMES, PACE, makePlan, DAYW, fmt};
})(typeof window !== 'undefined' ? window : globalThis);
