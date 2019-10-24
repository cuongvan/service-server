import requests
from urllib.parse import urlencode
OPENFAAS_GATEWAY = 'http://localhost:8080'
OPENFAAS_FUNCTION_URI = 'http://localhost:8080/system/functions'


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
    r = requests.post(OPENFAAS_FUNCTION_URI, json=data)
    return r

def remove_function(func_name: str):
    data = { 'functionName': func_name }
    r = requests.delete(OPENFAAS_FUNCTION_URI, json=data)
    return r

def invoke_function_sync(func_name, data, query):
    q = urlencode(query)
    url = '{}/function/{}?{}'.format(OPENFAAS_GATEWAY, func_name, q)
    r = requests.post(url, json=data)
    return r


def invoke_function_async(func_name, data, cb_url):
    url = OPENFAAS_GATEWAY + '/async-function/' + func_name
    data['X-Callback-Url'] = cb_url
    r = requests.post(url, json=data)
    return r

