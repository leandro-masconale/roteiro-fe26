"""Gera index.html a partir de src/app.html + src/app-data.json.
Uso: python3 src/build.py   (na raiz do repositório)
O endereço da planilha (Apps Script /exec) fica em src/api-url.txt."""
import os
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
head = open(os.path.join(here, 'head.html'), encoding='utf-8').read()
app = open(os.path.join(here, 'app.html'), encoding='utf-8').read()
api = os.environ.get('FE26_API') or open(os.path.join(here, 'api-url.txt'), encoding='utf-8').read().strip()
data = open(os.path.join(here, 'app-data.json'), encoding='utf-8').read().replace('</', '<\\/')
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(head + app.replace('%%DATA%%', data).replace('%%API%%', api) + '\n</body>\n</html>\n')
print('index.html ok')
