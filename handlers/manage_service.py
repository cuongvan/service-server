import json
import os
import shutil
import subprocess
from contextlib import contextmanager
from http import HTTPStatus as status
from pathlib import Path
from typing import Union

from flask import request

import background_worker
import openfaas
from common import Response, Error


ROOT = Path('.').resolve()
FUNCTIONS_DIR = ROOT / 'functions'

def run_cmd(cmd, **kargs) -> int:
    return subprocess.call(cmd, shell=True, **kargs)


@contextmanager
def change_cwd(dir):
    cwd = None
    try:
        cwd = os.getcwd()
        os.chdir(dir)
        yield
    finally:
        if cwd is not None:
            os.chdir(cwd)

def rm_dir(path: Union[str, Path]):
    try:
        shutil.rmtree(path)
    except Exception:
        pass


def rm_file(path: Union[str, Path]):
    if type(path) is str:
        path = Path(path)
    try:
        path.unlink()
    except Exception:
        pass


def remove_function_files(name):
    rm_dir(FUNCTIONS_DIR / name)


def build_image(func_name, handler_file, requir_file):
    # image name == func_name
    remove_function_files(func_name)

    # create files
    func_dir = FUNCTIONS_DIR / func_name
    template_dir = ROOT / 'templates' / 'python3'
    shutil.copytree(template_dir, func_dir)

    # move user submmited files
    code_dir = func_dir / 'function'
    handler_file.save(str(code_dir / './handler.py'))
    if requir_file is not None:
        requir_file.save(str(code_dir / './requirements.txt'))
    else:
        (code_dir / './requirements.txt').touch()

    # build image
    run_cmd('docker build . -t {}'.format(func_name), cwd=str(func_dir))


###############################################################################
def create_new_service() -> Response:
    if 'json' not in request.files:
        return Response(Error.BAD_REQUEST, msg='Missing json data file', status=status.BAD_REQUEST)

    if 'handler.py' not in request.files:
        return Response(Error.BAD_REQUEST, msg='Missing required file: handler.py', status=status.BAD_REQUEST)
    try:
        data = json.load(request.files['json'])
    except json.JSONDecodeError:
        return Response(Error.BAD_REQUEST, msg='Json data file is not in valid JSON format')

    service = data['name']

    # Check if function exists
    r = openfaas.function_info(service)

    if r.status_code == status.OK:
        return Response(Error.FUNCTION_ALREADY_EXISTS)
    elif r.status_code == status.INTERNAL_SERVER_ERROR:
        return Response(Error.FAAS_SERVER_INTERNAL_ERROR)

    build_image(service, request.files['handler.py'], request.files.get('requirements.txt', None))
    r = openfaas.deploy_function(service)
    if r.status_code == status.ACCEPTED:
        return Response(Error.OK)
    elif r.status_code == status.BAD_REQUEST:
        return Response(Error.INTERNAL_SERVER_ERROR)
    elif r.status_code == status.INTERNAL_SERVER_ERROR:
        return Response(Error.FAAS_SERVER_INTERNAL_ERROR)


def delete_service(name) -> Response:
    # remove code directory in ROOT
    remove_function_files(name)

    code = openfaas.remove_function(name).status_code
    if code == status.NOT_FOUND:
        return Response(Error.FUNCTION_NOT_FOUND)
    elif code == status.BAD_REQUEST:
        return Response(Error.INTERNAL_SERVER_ERROR)
    elif code == status.INTERNAL_SERVER_ERROR:
        return Response(Error.FAAS_SERVER_INTERNAL_ERROR)

    # successfully removed function from faas server

    # delete docker image
    def remove_image():
        cmd = 'docker container ls -f ancestor=' + name
        out = subprocess.check_output(cmd, shell=True)
        out = out.decode('utf-8').strip()
        lines = out.split('\n')
        for i, l in enumerate(lines):
            print(i, l)
        running_containers = lines[1:]
        if not running_containers:
            ret = subprocess.call('docker image rm ' + name, shell=True)
            if ret == 0:
                return background_worker.SUCCESS
            return None
        else:
            return None

    background_worker.submit_task(remove_image)

    return Response(Error.OK)


def update_service(name):
    return Response(Error.NOT_INPLEMENTED)
