# Copyright (c) Alex Ellis 2017. All rights reserved.
# Copyright (c) OpenFaaS Author(s) 2018. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import sys, os, json
from function import handler
import traceback
from urllib.parse import parse_qs

OK = 0
REQUEST_NOT_JSON_FORMAT = 11
MISSING_REQUIRED_PARAM = 12
FUNCTION_THROW_EXCEPTION = 13


def get_stdin():
    buf = ""
    while (True):
        line = sys.stdin.readline()
        buf += line
        if line == "":
            break
    return buf


required_params = [
    'CKAN_HOST',
    'CKAN_PORT',
]


# returns: missing variable
def populate_env_params(request):
    params = os.environ.get('Http_Query', '')  # parse this
    params = parse_qs(params)
    for p in required_params:
        if p not in params.keys():
            return p
        else:
            request[p] = params[p][0]
    request['CKAN_PORT'] = int(request['CKAN_PORT'])
    return None


def process():
    # try to convert input to json
    try:
        stdin = get_stdin()
        input_ = json.loads(stdin)
    except json.JSONDecodeError:
        return {'error_code': REQUEST_NOT_JSON_FORMAT}

    # missing = populate_env_params(input_)
    # if missing is not None:
    #     return {'error_code': MISSING_REQUIRED_PARAM,
    #             'msg': 'Missing param: ' + missing}

    # call user's handler
    try:
        return_val = handler.handle(input_)
    except Exception as e:
        return {
            'error_code': FUNCTION_THROW_EXCEPTION,
            'data': str(e) + '\n' + traceback.format_exc()
        }

    # convert return value to string
    if return_val is None:
        return_val = ''
    elif isinstance(return_val, dict):
        pass
    elif not isinstance(return_val, str):
        return_val = str(return_val)

    # return function value as string
    return {
        'error_code': OK,
        'data': return_val
    }


def main():
    json_ = process()
    print(json.dumps(json_))


if __name__ == "__main__":
    main()
