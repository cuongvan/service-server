from typing import Optional

from dataclasses import dataclass
from flask import jsonify
from enum import IntEnum
from http import HTTPStatus

class Error(IntEnum):
    OK = 0

    # requests
    BAD_REQUEST = 1
    FUNCTION_ALREADY_EXISTS = 2
    FAAS_SERVER_INTERNAL_ERROR = 3
    INTERNAL_SERVER_ERROR = 4
    FUNCTION_NOT_FOUND = 5

    # execute
    FUNCTION_TIMEOUT = 10
    REQUEST_NOT_JSON_FORMAT = 11
    MISSING_REQUIRED_PARAM = 12
    FUNCTION_THROW_EXCEPTION = 13

    NOT_INPLEMENTED = 99


@dataclass
class Response:
    error_code: Error
    msg: Optional[str] = None   # additional information, often exists when about error_code != 0
    data: Optional[str] = None
    status: HTTPStatus = HTTPStatus.OK

    def to_dict(self) -> dict:
        d = dict(error_code=self.error_code)
        if self.msg is not None:
            d['msg'] = self.msg
        if self.data is not None:
            d['data'] = self.data
        return d

    def to_flask_response(self):
        return jsonify(self.to_dict()), self.status


