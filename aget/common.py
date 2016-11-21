

from http import HTTPStatus

OK_STATUSES = (
    HTTPStatus.OK,
    HTTPStatus.CREATED,
    HTTPStatus.ACCEPTED,
    HTTPStatus.NON_AUTHORITATIVE_INFORMATION,
    HTTPStatus.NO_CONTENT,
    HTTPStatus.RESET_CONTENT,
    HTTPStatus.PARTIAL_CONTENT,
)


# Defines that should never be changed
OneK = 1024
OneM = OneK * OneK
OneG = OneM * OneK
OneT = OneG * OneK

DEFAULT_CHUCK_SIZE = 1 * OneM
DEFAULT_CONCURRENCY = 10
