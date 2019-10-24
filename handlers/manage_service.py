import json
import os
import shutil
import subprocess
from contextlib import contextmanager
from http import HTTPStatus as status
from pathlib import Path
from typing import Union

from flask import request

import openfaas
from common import Response, Error


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

ROOT = Path('./functions')

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
    rm_dir(ROOT / name)
    rm_file(ROOT / (name + '.yml'))
    rm_dir(ROOT / 'build' / name)

# def build_image(func_name, handler_file, requir_file):
#     remove_function_files(func_name)
#
#     # create template
#     with change_cwd(ROOT):
#         run_cmd('faas-cli new --lang python3 {}'.format(func_name))
#
#     # move user submmited files
#     user_code_dir = ROOT / func_name
#     with change_cwd(user_code_dir):
#         handler_file.save('./handler.py')
#         if requir_file is not None:
#             requir_file.save('./requirements.txt')
#
#     # build image
#     with change_cwd(ROOT):
#         run_cmd('faas-cli build -f {}.yml'.format(func_name))
#
#     # TODO: push image to registy: faas-cli push

def remove_function_files1(name):
    rm_dir(ROOT / name)
    rm_file(ROOT / (name + '.yml'))
    rm_dir(ROOT / 'build' / name)

def build_image(func_name, handler_file, requir_file):
    # image name == func_name
    remove_function_files1(func_name)
    template_dir = ROOT / 'template-fixing'


    # create template
    run_cmd('faas-cli new --lang python3 {}'.format(func_name), cwd=str(ROOT))

    # move user submmited files
    user_code_dir = ROOT / func_name
    handler_file.save(str(user_code_dir / './handler.py'))
    if requir_file is not None:
        requir_file.save(str(user_code_dir / './requirements.txt'))

    # build image
    run_cmd('faas-cli build -f {}.yml'.format(func_name), cwd=str(ROOT))

    # TODO: push image to registy: faas-cli push

###############################################################################
# return: code
def create_new_service() -> Response:
    if 'json' not in request.files:
        return Response(Error.BAD_REQUEST, msg='Missing json data file')

    if 'handler.py' not in request.files:
        return Response(Error.BAD_REQUEST, msg='Missing required file: handler.py')
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
    run_cmd('docker image rm -f {}'.format(name)) # no exception!

    return Response(Error.OK)


def update_service(name):
    return Response(Error.NOT_INPLEMENTED)
