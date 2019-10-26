import json
import logging

from flask import request
from flask_restful import Resource
from mysql.connector import IntegrityError

import utils
from call_result_db import DBConnection
from common import err

logger = utils.create_logger('callback', logging.DEBUG)


class FunctionCallback(Resource):
    def post(self, service_name):
        call_id = request.headers.get('X-Call-Id')
        body = request.get_data()
        func_status = request.headers.get('X-Function-Status')
        if func_status == '502': # real tested
            call_status = err.FUNCTION_TIMEOUT.value
            return_val = ''
        else:
            body = body.decode('utf-8')
            body = json.loads(body)
            call_status = body.get('error', 'Unknown')
            if call_status == err.FUNCTION_EXEC_SUCCESS:
                return_val = str(body['result'])
            elif call_status == err.MISSING_PARAM:
                logger.critical('Missing env var for index.py: %s', body['param'])
                return ''
            elif call_status == err.FUNCTION_TIMEOUT:
                return_val = ''
            else:
                assert call_status == err.FUNCTION_THROW_EXCEPTION
                return_val = body['exception']

        logger.info('Callback: [%s]\t%s\t%s', service_name, call_id, call_status)
        conn = DBConnection()
        try:
            conn.insert_result(call_id, service_name, call_status, return_val)
        except IntegrityError:
            logger.warning('Function was retried????')
