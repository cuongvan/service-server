#! /usr/bin/env python

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
    p.add_argument('action')
    p.add_argument('func_name')
    a = p.parse_args()
    return a.action, a.func_name

def show_result(r):
    try:
        data = r.json()
        data['error_code'] = Error(data['error_code']).name
        for key, val in data.items():
            try:
                data[key] = json.loads(val)
            except Exception:
                pass
        print(json.dumps(data, indent=4))
    except json.JSONDecodeError:
        print(r.text)

API = 'http://localhost:5000'

action, func_name = parse_args()

if action == 'new':
    data = { 'name': func_name }
    files = {
        'handler.py': ('name1', open('./data/handler.py', 'rb'), 'application/octet-stream'),
        'requirements.txt': ('name2', open('./data/requirements.txt', 'rb'), 'application/octet-stream'),
        'json': ('name3', json.dumps(data), 'application/json')
    }

    r = requests.post(API + '/service', files=files)
    show_result(r)

elif action == 'up':
    r = requests.put(API + '/service/' + func_name)
    show_result(r)

elif action == 'del':
    r = requests.delete(API + '/service/' + func_name)
    show_result(r)

elif action == 'exec':
    r = requests.post(API + '/exec/' + func_name, json={})
    show_result(r)

else:
    print('??????')
