import logging
import subprocess
from http import HTTPStatus as http

from flask import request
from flask_restful import Resource

import background_worker
import openfaas
import utils
from common import err
from .services import remove_function_files, take_user_code_files, build_image

logger = utils.create_logger('service', logging.DEBUG)

class OneService(Resource):
    def get(self, service_name):
        # Check if function exists
        r = openfaas.function_info(service_name)
        if r.status_code == http.OK:
            return {'error': err.OK }, http.OK
        elif r.status_code == http.NOT_FOUND:
            return { 'error': err.FUNCTION_NOT_FOUND }, http.NOT_FOUND
        elif r.status_code == http.INTERNAL_SERVER_ERROR:
            return {'error': err.FAAS_SERVER_INTERNAL_ERROR}, http.INTERNAL_SERVER_ERROR
        else:
            return { 'error': err.INTERNAL_SERVER_ERROR,
                     'msg': 'Unknown return code from FaaS'}, http.INTERNAL_SERVER_ERROR


    def put(self, service_name):
        error, status = self.get(service_name)
        if error['error'] != err.OK:
            return error, status

        if 'handler.py' not in request.files:
            return {'error': err.MISSING_FILE, 'file': 'handler.py'}, http.BAD_REQUEST

        handler_file_data, requirements_file_data = take_user_code_files()

        handler_file_data, requirements_file_data = take_user_code_files()
        # pass build & redeploy task to task queue
        def create_function():
            try:
                ok = build_image(service_name, handler_file_data, requirements_file_data)
                if not ok:
                    return background_worker.SUCCESS
                logger.info("Redeploying function: '%s'", service_name)
                r = openfaas.redeploy_function(service_name)
                if r.status_code == http.ACCEPTED:
                    logger.info("Function '%s' deployed", service_name)
                elif r.status_code == http.INTERNAL_SERVER_ERROR:
                    logger.warning("Fail to deploy function '%s', FaaS internal error", service_name)
                else:
                    logger.warning("Deploy: receive unexpected status code: %d", r.status_code)
            finally:
                return background_worker.SUCCESS

        background_worker.submit_task(create_function)
        # chờ hay sao?
        return { 'error': err.ACCEPTED }, http.ACCEPTED


    def delete(self, service_name):
        ret = delete_function(service_name)
        if ret is not None:
            return ret

        # delete docker image
        logger.info('Removing docker image %s', service_name)
        def wait_and_remove_image():
            cmd = 'docker container ls -f ancestor=' + service_name
            out = subprocess.getoutput(cmd)
            lines = out.split('\n')
            running_containers = lines[1:]
            if not running_containers:
                # std err will go to the terminal
                # TODO change to log file if needed
                retcode, out = subprocess.getstatusoutput('docker image rm %s' % service_name)
                if retcode == 0 or 'Error: No such image:' in out:
                    logger.info("Docker image '%s' removed", service_name)
                    return background_worker.SUCCESS

        background_worker.submit_task(wait_and_remove_image)

        return { 'error': err.ACCEPTED }, http.ACCEPTED

def delete_function(name):
    # None means success
    remove_function_files(name)
    logger.info('Removing function %s', name)
    code = openfaas.remove_function(name).status_code
    if code == http.NOT_FOUND:
        return { 'error': err.FUNCTION_NOT_FOUND }, http.NOT_FOUND
    elif code == http.BAD_REQUEST:
        return { 'error': err.INTERNAL_SERVER_ERROR }, http.INTERNAL_SERVER_ERROR
    elif code == http.INTERNAL_SERVER_ERROR:
        return { 'error': err.FAAS_SERVER_INTERNAL_ERROR }, http.INTERNAL_SERVER_ERROR
    elif code != http.ACCEPTED:
        return { 'error': err.FAAS_SERVER_INTERNAL_ERROR,
                 'msg': 'Got unexpected return code: %d' % code }, http.INTERNAL_SERVER_ERROR
    else:
        return None
