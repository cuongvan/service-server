# Copyright (c) Alex Ellis 2017. All rights reserved.
# Copyright (c) OpenFaaS Author(s) 2018. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import sys, os, json
from enum import Enum, auto
import timeout_decorator

from function import handler
import traceback
from urllib.parse import parse_qs



class err(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    OK = auto()
    ACCEPTED = auto()
    # requests
    BAD_REQUEST = auto()
    MISSING_PARAM = auto()
    MISSING_FILE = auto()
    IS_NOT_JSON = auto()
    FUNCTION_ALREADY_EXISTS = auto()
    FUNCTION_NOT_FOUND = auto()

    FAAS_SERVER_INTERNAL_ERROR = auto()
    INTERNAL_SERVER_ERROR = auto()

    # execute
    FUNCTION_EXEC_SUCCESS = auto()
    FUNCTION_TIMEOUT = auto()
    FUNCTION_THROW_EXCEPTION = auto()

def get_stdin():
    buf = ""
    while True:
        line = sys.stdin.readline()
        buf += line
        if line == "":
            break
    return buf


def populate_env_vars():
    params = os.environ.get('Http_Query', '')  # parse this
    params = parse_qs(params)
    for p, val in params.items():
        os.environ[p] = val[0] # val is a list


def process():
    # try to convert input to json
    populate_env_vars()

    # timeout
    timeout = os.getenv('TIMEOUT', None)
    if timeout is None:
        return {'error': err.MISSING_PARAM, 'param': 'TIMEOUT'}
    timeout = int(timeout)
    @timeout_decorator.timeout(timeout)
    def handle_wrapper(input_):
        return handler.handle(input_)

    # call user's handler
    try:
        return_val = handle_wrapper(get_stdin())
    except timeout_decorator.TimeoutError:
        return  {'error': err.FUNCTION_TIMEOUT}
    except Exception as e:
        return {
            'error': err.FUNCTION_THROW_EXCEPTION,
            'exeception': str(e) + '\n' + traceback.format_exc()
        }

    # convert return value to string
    if return_val is None:
        return_val = ''
    elif isinstance(return_val, dict):
        pass
    elif not isinstance(return_val, str):
        return_val = str(return_val)

    # return function value as string
    return { 'error': err.FUNCTION_EXEC_SUCCESS,
             'result': return_val}


def main():
    json_ = process()
    print(json.dumps(json_))

if __name__ == "__main__":
    main()
