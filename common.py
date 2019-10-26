from typing import Optional, Union

from dataclasses import dataclass
from flask import jsonify
from enum import auto, Enum
from http import HTTPStatus as http


class Error(str, Enum):
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
    FAAS_SERVER_INTERNAL_ERROR = auto()
    INTERNAL_SERVER_ERROR = auto()
    FUNCTION_NOT_FOUND = auto()
    # execute
    FUNCTION_TIMEOUT = auto()
    REQUEST_NOT_JSON_FORMAT = auto()
    MISSING_REQUIRED_PARAM = auto()
    FUNCTION_THROW_EXCEPTION = auto()
    NOT_INPLEMENTED = auto()



err = Error


@dataclass
class Response:
    error_code: Error
    msg: Optional[str] = None  # additional information, often exists when about error_code != 0
    data: Optional[Union[str, dict]] = None
    status: http = http.OK

    def to_dict(self) -> dict:
        d = dict(error_code=self.error_code)
        if self.msg is not None:
            d['msg'] = self.msg
        if self.data is not None:
            d['data'] = self.data
        d['error_code'] = self.error_code.name  # DEBUG
        return d

    def to_flask_response(self):
        return jsonify(self.to_dict()), self.status
