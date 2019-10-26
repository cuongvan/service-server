#! /usr/bin/env python
from pathlib import Path

import requests, json, sys
from pprint import PrettyPrinter
from argparse import ArgumentParser

pprint = PrettyPrinter(indent=4).pprint

from enum import IntEnum


class Error(IntEnum):
    OK = 0

    # requests
    BAD_REQUEST = 1
    FUNCTION_ALREADY_EXISTS = 2
    FAAS_SERVER_INTERNAL_ERROR = 3
    INTERNAL_SERVER_ERROR = 4
    FUNCTION_NOT_FOUND = 5

    # execute
    FUNCTION_TIMEOUT = 10
    REQUEST_NOT_JSON_FORMAT = 11
    MISSING_REQUIRED_PARAM = 12
    FUNCTION_THROW_EXCEPTION = 13

    NOT_INPLEMENTED = 99


def parse_args():
    p = ArgumentParser()
    p.add_argument('func_name')
    p.add_argument('action')
    a = p.parse_args()
    return a.action, a.func_name


def show_result(self):
    try:
        data = self.json()
        # data['error_code'] = Error(data['error_code']).name
        for key, val in data.items():
            try:
                data[key] = json.loads(val)
            except Exception:
                pass
        print(json.dumps(data, indent=4))
    except json.JSONDecodeError:
        print(self.text)


requests.Response.show_result = show_result

API = 'http://localhost:5000'

action, func_name = parse_args()

func_dir = Path('funcs', func_name)

if action == 'new':
    data = {'service_name': func_name}
    files = {
        'handler.py': ('name1', open(func_dir / 'handler.py', 'rb'), 'application/octet-stream'),
        'json': ('name3', json.dumps(data), 'application/json')
    }

    if (func_dir / 'requirements.txt').exists():
        files['requirements.txt'] =  ('name2', open(func_dir / 'requirements.txt', 'rb'), 'application/octet-stream'),

    r = requests.post(API + '/services', files=files)
    r.show_result()

elif action == 'up':
    files = {
        'handler.py': ('name1', open(func_dir / 'handler.py', 'rb'), 'application/octet-stream'),
    }

    if (func_dir / 'requirements.txt').exists():
        files['requirements.txt'] =  ('name2', open(func_dir / 'requirements.txt', 'rb'), 'application/octet-stream'),
    r = requests.put(API + '/service/' + func_name, files=files)
    r.show_result()

elif action == 'del':
    r = requests.delete(API + '/service/' + func_name)
    r.show_result()

elif action == 'sync':
    r = requests.post(API + '/exec/' + func_name, json={})
    r.show_result()

elif action == 'async':
    r = requests.post(API + '/exec-async/' + func_name, json={})
    r.show_result()

elif action == 'get':
    r = requests.get(API + '/service/' + func_name)
    r.show_result()
else:
    print('??????')
