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
    INVALID_NAME = auto()
    NOT_JSON_FORMAT = auto()
    NOT_ZIP_FILE = auto()
    FUNCTION_ALREADY_EXISTS = auto()
    FUNCTION_NOT_FOUND = auto()

    FAAS_SERVER_INTERNAL_ERROR = auto()
    INTERNAL_SERVER_ERROR = auto()

    # execute
    FUNCTION_EXEC_SUCCESS = auto()
    FUNCTION_TIMEOUT = auto()
    FUNCTION_THROW_EXCEPTION = auto()



err = Error
