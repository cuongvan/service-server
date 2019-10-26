from http import HTTPStatus as status

import requests
from flask import request
import logging

import openfaas
import utils
from common import Response, Error

import environments

logger = utils.create_logger(__name__, logging.DEBUG)

def exec_function_sync(name) -> Response:
    data = request.json or {}
    try:
        r = openfaas.invoke_function_sync(name, data, environments.env)
    except requests.Timeout:
        return Response(Error.FUNCTION_TIMEOUT, status=status.REQUEST_TIMEOUT)
    logger.info('Call "%s" with params %s, returns %s', name, data, r.text)

    code = r.status_code
    if code == status.NOT_FOUND:
        return Response(Error.FUNCTION_NOT_FOUND, status=status.NOT_FOUND)
    elif code == status.INTERNAL_SERVER_ERROR:
        return Response(Error.FAAS_SERVER_INTERNAL_ERROR, status=status.INTERNAL_SERVER_ERROR)
    elif code == status.REQUEST_TIMEOUT:
        return Response(Error.FUNCTION_TIMEOUT, status=status.REQUEST_TIMEOUT)

    # got a result
    res = r.json()
    code = res['error_code']
    if code == Error.MISSING_REQUIRED_PARAM:
        logger.critical(res['msg'])
        return Response(Error.INTERNAL_SERVER_ERROR)
    else:
        data = res.get('data', None)
        return Response(Error(code), data=data)


def exec_function_async(name) -> Response:
    data = request.json.get('data', {})
    cb_url = 'http://192.168.100.6:80/callback'
    # cb_url = 'https://en1bcxbjvxxa.x.pipedream.net/async/' + call_id
    # cb_url = 'http://localhost:9999'
    r = openfaas.invoke_function_async(name, data, environments.env, cb_url)
    code = r.status_code
    if code == status.ACCEPTED:
        call_id = r.headers['X-Call-Id']
        return Response(Error.OK, status=status.ACCEPTED, data={'call_id': call_id})
    elif code == status.NOT_FOUND:
        return Response(Error.FUNCTION_NOT_FOUND, status=status.NOT_FOUND)
    else:
        return Response(Error.INTERNAL_SERVER_ERROR, status=status.INTERNAL_SERVER_ERROR)
