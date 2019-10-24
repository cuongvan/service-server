# Copyright (c) Alex Ellis 2017. All rights reserved.
# Copyright (c) OpenFaaS Author(s) 2018. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import sys
import json
from function import handler

REQ_JSON_FORMAT_ERR = 5

def get_stdin():
    buf = ""
    while(True):
        line = sys.stdin.readline()
        buf += line
        if line == "":
            break
    return buf

def toResponseVal(val):
    if val is None:
        return ''

    if isinstance(val, dict):
        return val

    if not isinstance(val, str):
        val = str(val)

    try:
        return json.loads(val)
    except JSONDecodeError:
        return val

if __name__ == "__main__":
    st = get_stdin()
    try:
        js = json.loads(st)
    except json.JSONDecodeError:
        print(json.dumps({'error': REQ_JSON_FORMAT_ERR}))
        return

    ret = handler.handle(js)
    response = { 'error': 0, 'response': toResponseVal(ret) }
    print(json.dumps(response))
    

