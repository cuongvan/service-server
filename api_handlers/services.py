import json
import logging
import re
import shutil
import subprocess
from pathlib import Path

from flask import request
from flask_restful import Resource

import background_worker
import openfaas
import utils
from common import err, http

ROOT = Path('.').resolve()
FUNCTIONS_DIR = ROOT / 'functions'

logger = utils.create_logger(__name__, logging.DEBUG)

class Services(Resource):
    def post(self):
        if 'json' not in request.files:
            return {'error': err.MISSING_FILE, 'file': 'json'}, http.BAD_REQUEST

        if 'handler.py' not in request.files:
            return {'error': err.MISSING_FILE, 'file': 'handler.py'}, http.BAD_REQUEST

        try:
            data = json.load(request.files['json'])
        except json.JSONDecodeError:
            return {'error': err.IS_NOT_JSON}, http.BAD_REQUEST

        if 'service_name' not in data:
            return {'error': err.MISSING_PARAM, 'param': 'service_name'}, http.BAD_REQUEST

        service_name = data['service_name']
        if not re.match('[-a-z0-9]+', service_name):
            return {'error': err.INVALID_NAME, 'msg': 'Name can only contain a-z, 0-9 and dashes (-)'}, http.BAD_REQUEST

        # Check if function exists
        r = openfaas.function_info(service_name)

        if r.status_code == http.OK:
            return {'error': err.FUNCTION_ALREADY_EXISTS}, http.CONFLICT
        elif r.status_code == http.INTERNAL_SERVER_ERROR:
            return {'error': err.FAAS_SERVER_INTERNAL_ERROR}, http.INTERNAL_SERVER_ERROR

        handler_file_data, requirements_file_data = take_user_code_files()

        # pass build & deploy task to task queue
        def create_function():
            try:
                ok = build_image(service_name, handler_file_data, requirements_file_data)
                if not ok:
                    return background_worker.SUCCESS
                logger.info("Deploying function: '%s'", service_name)
                r = openfaas.deploy_function(service_name)
                if r.status_code == http.ACCEPTED:
                    logger.info("Function '%s' deployed", service_name)
                elif r.status_code == http.INTERNAL_SERVER_ERROR:
                    logger.warning("Fail to deploy function '%s', FaaS internal error", service_name)
                else:
                    logger.warning("Deploy: receive unexpected status code: %d", r.status_code)
            finally:
                return background_worker.SUCCESS
        background_worker.submit_task(create_function)

        return { 'error': err.ACCEPTED }, http.ACCEPTED


def take_user_code_files():
    handler_file = request.files['handler.py']
    handler_file.seek(0) # move position to beginning
    handler_file_data = handler_file.read()

    requirements_file = request.files.get('requirements.txt', None)
    if requirements_file is not None:
        requirements_file.seek(0)
        requirements_file_data = requirements_file.read()
    else:
        requirements_file_data = None
    return handler_file_data, requirements_file_data


def remove_function_files(name):
    func_dir = (FUNCTIONS_DIR / name)
    try:
        shutil.rmtree(func_dir)
    except Exception:
        pass


def build_image(func_name, handler_file_data, requirements_file_data):
    # image name == func_name
    logger.info("Building image: '%s'", func_name)
    remove_function_files(func_name)

    # create files
    func_dir = FUNCTIONS_DIR / func_name
    template_dir = ROOT / 'templates' / 'python3'
    shutil.copytree(template_dir, func_dir)

    # move user submmited files
    code_dir = func_dir / 'function'
    handler_file = code_dir / './handler.py'
    handler_file.write_bytes(handler_file_data)

    requirements_file = code_dir / './requirements.txt'
    if requirements_file_data is not None:
        requirements_file.write_bytes(requirements_file_data)
    else:
        requirements_file.touch()

    # build image
    ret = subprocess.call('docker build . -t {}'.format(func_name), cwd=str(func_dir), shell=True, stdout=subprocess.DEVNULL)
    ok = (ret == 0)
    if not ok:
        logger.warning("Failed to build image '%s'", func_name)
        return background_worker.SUCCESS
    else:
        logger.info("Image '%s' built", func_name)
    return ok
