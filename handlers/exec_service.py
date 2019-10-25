from http import HTTPStatus as status

import requests
from flask import request
import logging

import openfaas
from common import Response, Error
from uuid import uuid1

import environments

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.BASIC_FORMAT
handler.setFormatter(logging.Formatter(formatter))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


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
    call_id = str(uuid1())
    # cb_url = 'http://localhost:5000/callback/' + call_id
    cb_url = 'https://en1bcxbjvxxa.x.pipedream.net/' + call_id
    # cb_url = 'http://localhost:9999'
    r = openfaas.invoke_function_async(name, data, environments.env, cb_url)
    logger.info('Async call: function=%s, code=%d', name, r.status_code)

    code = r.status_code
    if code == status.ACCEPTED:
        return Response(Error.OK, status=status.ACCEPTED, data={ 'call_id': call_id })
    elif code == status.NOT_FOUND:
        return Response(Error.FUNCTION_NOT_FOUND, status=status.NOT_FOUND)
    else:
        return Response(Error.INTERNAL_SERVER_ERROR, status=status.INTERNAL_SERVER_ERROR)
