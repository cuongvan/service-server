#! /usr/bin/env python3
from pathlib import Path

import requests, json, sys
from pprint import PrettyPrinter
from argparse import ArgumentParser

pprint = PrettyPrinter(indent=4).pprint

def show_result(r):
    try:
        data = r.json()
        # data['error_code'] = Error(data['error_code']).name
        for key, val in data.items():
            try:
                data[key] = json.loads(val)
            except Exception:
                pass
        print(json.dumps(data, indent=4))
    except Exception:
        print(r.text)

def main():
    API = 'http://localhost'
    action, func_name = parse_args()
    func_dir = Path('funcs', func_name)
    if action == 'new':
        data = {'service_name': func_name}
        files = {
            # 'handler.py': ('name1', open(func_dir / 'handler.py', 'rb'), 'application/octet-stream'),
            'code.zip': ('name1', open(func_dir / 'code.zip', 'rb'), 'application/octet-stream'),
            'json': ('name3', json.dumps(data), 'application/json')
        }
        if (func_dir / 'requirements.txt').exists():
            files['requirements.txt'] =  ('name2', open(func_dir / 'requirements.txt', 'rb'), 'application/octet-stream'),
        r = requests.post(API + '/services', files=files)
    elif action == 'up':
        files = {
            'handler.py': ('name1', open(func_dir / 'handler.py', 'rb'), 'application/octet-stream'),
        }
        if (func_dir / 'requirements.txt').exists():
            files['requirements.txt'] =  ('name2', open(func_dir / 'requirements.txt', 'rb'), 'application/octet-stream'),
        r = requests.put(API + '/service/' + func_name, files=files)
    elif action == 'del':
        r = requests.delete(API + '/service/' + func_name)
    elif action == 'sync':
        r = requests.post(API + '/sync/' + func_name, data='My request:Van Tien Cuong')
    elif action == 'async':
        r = requests.post(API + '/async/' + func_name, json={})
    elif action == 'get':
        r = requests.get(API + '/service/' + func_name)
    else:
        print('???????')
        return
    show_result(r)

def parse_args():
    p = ArgumentParser()
    p.add_argument('func_name')
    p.add_argument('action')
    a = p.parse_args()
    return a.action, a.func_name

if __name__ == '__main__':
    main()
