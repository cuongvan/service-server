import logging

from flask import request

logger = logging.getLogger(__name__)


def process_callback():
    print(request.json)
