import json, numpy as np, sys
from PIL import Image
TOP = 150  # px of banner trimmed from the top
im = Image.open('data/fe26-mapa-v2.webp').convert('RGB')
W, H = im.size
im = im.crop((0, TOP, W, H)); H = im.size[1]
im.save('site/mapa.webp', 'WEBP', quality=62, method=6)
m = json.load(open('data/fe26-mapa.json'))
polys = []; bad = set()
a = json.load(open('site/app-data.json'))
cents = []
for i, (t, p, c) in enumerate(m['spaces']):
    ok = bool(p) and all(v is not None for v in p)
    polys.append([v - TOP if k % 2 else v for k, v in enumerate(p)] if ok else [])
    if ok:
        xs, ys = p[0::2], p[1::2]; cents.append([round(sum(xs) / len(xs)), round(sum(ys) / len(ys)) - TOP])
    elif c and c[0] is not None and c[1] is not None:
        cents.append([c[0], c[1] - TOP])
    else:
        cents.append(None); bad.add(i)
a['centers'] = cents
for e in a['ex']:
    if e[8] in bad: e[8] = -1
for st in a['stages']:
    if st[2] in bad: st[2] = -1
print('spaces without position', len(bad))
json.dump(a, open('site/app-data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
C = 4; GW = (W + C - 1) // C; GH = (H + C - 1) // C
arr = np.asarray(im).astype(np.int16)
d = ~((arr[:, :, 0] > 222) & (arr[:, :, 1] > 222) & (arr[:, :, 2] > 222))
pad = np.zeros((GH * C, GW * C), bool); pad[:H, :W] = d
cnt = np.zeros((GH * C, GW * C)); cnt[:H, :W] = 1
s = pad.reshape(GH, C, GW, C).sum(axis=(1, 3)); n = cnt.reshape(GH, C, GW, C).sum(axis=(1, 3))
g = ((n > 0) & (s / np.maximum(n, 1) >= 0.45)).astype(np.uint8).ravel().tolist()
runs = []; cur = 0; run = 0
for v in g:
    if v == cur: run += 1
    else: runs.append(run); cur = v; run = 1
runs.append(run)
def b36(x):
    S = '0123456789abcdefghijklmnopqrstuvwxyz'; o = ''
    if x == 0: return '0'
    while x: o = S[x % 36] + o; x //= 36
    return o
json.dump({'w': W, 'h': H, 'imgH': H, 'polys': polys, 'mask': {'cell': C, 'w': GW, 'h': GH, 'rle': ','.join(b36(r) for r in runs)}},
          open('site/mapa.json', 'w'), separators=(',', ':'))
import os
print('img', os.path.getsize('site/mapa.webp'), 'map', os.path.getsize('site/mapa.json'), W, H)
