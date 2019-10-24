#! /usr/bin/env python3

from flask import Flask, request, make_response
import common
from common import Error
from handlers import exec_service, manage_service

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
    res = exec_service.exec_function_sync(name)
    return res.to_flask_response()

@app.route('/callback/<call_id>', methods=['POST'])
def handle_function_callback(call_id):
    # route used by openfaas, not user
    # update database / push result into queue, ...
    return ''


@app.errorhandler(404)
def not_found(error):
    return make_response(common.Response(Error.BAD_REQUEST, msg='API path not found').to_flask_response())

if __name__ == "__main__":
    app.run(debug=True)