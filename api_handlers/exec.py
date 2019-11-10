from urllib.parse import urlencode

import requests
from flask import request
from flask_restful import Resource
import logging

import openfaas
import project_conf
import utils
from common import err, http

import environments
from project_conf import OPENFAAS_GATEWAY, EXEC_TIMEOUT

logger = utils.create_logger(__name__, logging.DEBUG)


class SyncExec(Resource):
    def post(self, service_name):
        url = '{}/function/{}'.format(OPENFAAS_GATEWAY, service_name)
        try:
            r = requests.post(
                url,
                params=environments.env,
                data=request.get_data(),
                timeout=EXEC_TIMEOUT)
        except requests.Timeout:  # timeout from requests
            return { 'error': err.FUNCTION_TIMEOUT }, http.REQUEST_TIMEOUT
        logger.info('Call "%s" with params %s, returns %s', service_name, None, None)

        if r.status_code == http.NOT_FOUND:
            return { 'error': err.FUNCTION_NOT_FOUND }, http.NOT_FOUND
        elif r.status_code == http.INTERNAL_SERVER_ERROR:
            return { 'error': err.FAAS_SERVER_INTERNAL_ERROR }, http.INTERNAL_SERVER_ERROR
        elif r.status_code == http.REQUEST_TIMEOUT:  # timeout from faas server
            return { 'error': err.FUNCTION_TIMEOUT }, http.REQUEST_TIMEOUT

        # got a result
        # res = r.json()  # result from index.py
        return r.text


class AsyncExec(Resource):
    def post(self, service_name):
        cb_url = project_conf.THIS_SERVER_HOST + '/callback/' + service_name
        # cb_url = 'https://en9gk6ah6047d.x.pipedream.net/' + service_name
        url = '{}/async-function/{}'.format(OPENFAAS_GATEWAY, service_name)
        r = requests.post(
            url,
            headers={'X-Callback-Url': cb_url},
            params=environments.env,
            data=request.get_data())
        code = r.status_code
        if code == http.ACCEPTED:
            return {'error': err.ACCEPTED, 'call_id': r.headers['X-Call-Id']}, http.ACCEPTED
        elif code == http.NOT_FOUND:
            return {'error': err.FUNCTION_NOT_FOUND}, http.NOT_FOUND
        else:
            return {'error': err.INTERNAL_SERVER_ERROR}, http.INTERNAL_SERVER_ERROR
