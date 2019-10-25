#! /usr/bin/env python3
import time

from flask import Flask, request, make_response

import background_worker
import common
from common import Error
from handlers import exec_service, manage_service, function_callback

app = Flask(__name__)
app.url_map.strict_slashes = False


@app.route('/service', methods=['POST'])
def handle_service():
    res = manage_service.create_new_service()
    return res.to_flask_response()


@app.route('/service/<name>', methods=['PUT', 'DELETE'])
def handle_one_service(name):
    if request.method == 'PUT':
        res = manage_service.update_service(name)
    else:
        res = manage_service.delete_service(name)

    return res.to_flask_response()


@app.route('/exec/<name>', methods=['POST'])
def handle_exec(name):
    res = exec_service.exec_function_sync(name)
    return res.to_flask_response()


@app.route('/exec-async/<name>', methods=['POST'])
def handle_async_exec(name):
    res = exec_service.exec_function_async(name)
    return res.to_flask_response()


@app.route('/callback', methods=['POST'])
def handle_function_callback():
    # route used by openfaas, not user
    # update database / push result into queue, ...
    function_callback.process_callback()
    return ''


@app.errorhandler(404)
def not_found(error):
    return make_response(common.Response(Error.BAD_REQUEST, msg='API path not found').to_flask_response())


if __name__ == "__main__":
    background_worker.start_worker()
    app.run(host='0.0.0.0', port=80, debug=True)
