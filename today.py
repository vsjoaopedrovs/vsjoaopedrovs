import datetime
from dateutil import relativedelta
import requests
import os
from lxml import etree
import time
import hashlib

# Configurações de Ambiente (Devem estar no GitHub Secrets)
HEADERS = {'authorization': 'token '+ os.environ['ACCESS_TOKEN']}
USER_NAME = os.environ.get('USER_NAME', 'vsjoaopedrovs') 

QUERY_COUNT = {'user_getter': 0, 'follower_getter': 0, 'graph_repos_stars': 0, 'recursive_loc': 0, 'graph_commits': 0, 'loc_query': 0}

def daily_readme(birthday):
    """Calcula o tempo de vida: 'XX years, XX months, XX days'"""
    diff = relativedelta.relativedelta(datetime.datetime.today(), birthday)
    return '{} {}, {} {}, {} {}{}'.format(
        diff.years, 'year' + format_plural(diff.years), 
        diff.months, 'month' + format_plural(diff.months), 
        diff.days, 'day' + format_plural(diff.days),
        ' 🎂' if (diff.months == 0 and diff.days == 0) else '')

def format_plural(unit):
    return 's' if unit != 1 else ''

def simple_request(func_name, query, variables):
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables':variables}, headers=HEADERS)
    if request.status_code == 200:
        return request
    raise Exception(f"{func_name} failed: {request.status_code} {request.text}")

def user_getter(username):
    query_count('user_getter')
    query = '''query($login: String!){ user(login: $login) { id createdAt } }'''
    request = simple_request(user_getter.__name__, query, {'login': username})
    data = request.json()['data']['user']
    return {'id': data['id']}, data['createdAt']

def query_count(funct_id):
    global QUERY_COUNT
    QUERY_COUNT[funct_id] += 1

def perf_counter(funct, *args):
    start = time.perf_counter()
    return funct(*args), time.perf_counter() - start

# --- COLOQUE AQUI AS FUNÇÕES DE LOC (recursive_loc, loc_query, etc.) DO ARQUIVO ORIGINAL ---

def svg_overwrite(filename, age_data, commit_data, star_data, repo_data, contrib_data, follower_data, loc_data):
    """Edita os SVGs com as suas informações"""
    try:
        tree = etree.parse(filename)
        root = tree.getroot()
        
        # O script procura por IDs específicos dentro do arquivo SVG para substituir o texto
        justify_format(root, 'commit_data', commit_data, 22)
        justify_format(root, 'star_data', star_data, 14)
        justify_format(root, 'repo_data', repo_data, 6)
        justify_format(root, 'contrib_data', contrib_data)
        justify_format(root, 'follower_data', follower_data, 10)
        justify_format(root, 'loc_data', loc_data[2], 9)
        justify_format(root, 'loc_add', loc_data[0])
        justify_format(root, 'loc_del', loc_data[1], 7)
        justify_format(root, 'age_data', age_data) # Adicionado para mostrar sua idade
        
        tree.write(filename, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        print(f"Erro ao processar SVG {filename}: {e}")

def justify_format(root, element_id, new_text, length=0):
    if isinstance(new_text, int):
        new_text = f"{'{:,}'.format(new_text)}"
    new_text = str(new_text)
    
    element = root.find(f".//*[@id='{element_id}']")
    if element is not None:
        element.text = new_text
        
    just_len = max(0, length - len(new_text))
    dot_string = ' ' + ('.' * just_len) + ' ' if just_len > 2 else '. '
    dots_element = root.find(f".//*[@id='{element_id}_dots']")
    if dots_element is not None:
        dots_element.text = dot_string

if __name__ == '__main__':
    # 1. SUA DATA DE NASCIMENTO CONFIGURADA
    BIRTHDAY = datetime.datetime(2009, 8, 19) 
    
    # 2. PEGA SEU OWNER_ID AUTOMATICAMENTE
    user_data, _ = perf_counter(user_getter, USER_NAME)
    OWNER_ID = user_data[0] 
    
    age_data, _ = perf_counter(daily_readme, BIRTHDAY)
    
    if not os.path.exists('cache'): os.makedirs('cache')
    
    # ... (Restante da execução de métricas como no código anterior)
    
    print(f"Sucesso! Metrics atualizadas para {USER_NAME} (Nascido em: {BIRTHDAY.strftime('%d/%m/%Y')})")
