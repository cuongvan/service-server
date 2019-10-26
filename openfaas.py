import requests
from urllib.parse import urlencode

OPENFAAS_GATEWAY = 'http://localhost:8080'
EXEC_TIMEOUT = 10    # seconds, first time can be slow!

def function_info(func_name) -> requests.Response:
    uri = OPENFAAS_GATEWAY + '/system/function/' + func_name
    r = requests.get(uri)
    return r


def deploy_function(func_name) -> requests.Response:
    data = {
        'service': func_name,
        'image': func_name,
        'envProcess': 'python3 index.py',
    }
    url = OPENFAAS_GATEWAY + '/system/functions'
    r = requests.post(url, json=data)
    return r

def redeploy_function(func_name) -> requests.Response:
    data = {
        'service': func_name,
        'image': func_name,
        'envProcess': 'python3 index.py',
    }
    url = OPENFAAS_GATEWAY + '/system/functions'
    r = requests.put(url, json=data)
    return r


def remove_function(func_name: str):
    data = {'functionName': func_name}
    url = OPENFAAS_GATEWAY + '/system/functions'
    r = requests.delete(url, json=data)
    return r


def invoke_function_sync(func_name, data, query):
    q = urlencode(query)
    url = '{}/function/{}?{}'.format(OPENFAAS_GATEWAY, func_name, q)
    r = requests.post(url, json=data, timeout=EXEC_TIMEOUT)
    return r


def invoke_function_async(func_name, data, query, cb_url):
    q = urlencode(query)
    url = '{}/async-function/{}?{}'.format(OPENFAAS_GATEWAY, func_name, q)
    headers = {'X-Callback-Url': cb_url}
    r = requests.post(url, headers=headers, json=data)
    return r
