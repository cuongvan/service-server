import requests
from urllib.parse import urlencode

from project_conf import OPENFAAS_GATEWAY, EXEC_TIMEOUT


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

