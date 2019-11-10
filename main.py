#! /usr/bin/env python3.6

from flask import Flask
from flask_restful import Api

import api_handlers
import background_worker
import project_conf
import utils

app = Flask(__name__)
app.url_map.strict_slashes = False
api = Api(app)

api.add_resource(api_handlers.Services, '/services')
api.add_resource(api_handlers.OneService, '/service/<string:service_name>')
api.add_resource(api_handlers.SyncExec, '/sync/<string:service_name>')
api.add_resource(api_handlers.AsyncExec, '/async/<string:service_name>')
api.add_resource(api_handlers.FunctionCallback, '/callback/<string:service_name>')

def config_flask_logging():
    from flask.logging import wsgi_errors_stream
    import logging
    log = logging.getLogger('werkzeug')
    handler = logging.StreamHandler(wsgi_errors_stream)
    handler.setFormatter(utils.log_formatter)
    log.addHandler(handler)

if __name__ == "__main__":
    background_worker.start_worker()
    config_flask_logging()
    app.run(host='0.0.0.0', port=project_conf.PORT, debug=False)
