import json
import logging
from datetime import datetime , timezone

from .context import get_request_id


_STANDARD_ATTRS = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message":"asctime"}


class RequestIdFilter(logging.filter):

    def filter ( self, record: logging.LogRecord) -> bool :
        record._request_id = get_request_id()
        return True


class JSONFormatter(logging.Formatter):

    def format( self, record: logging.LogRecord) -> str:
        payload ={
            "ts": datetime.fromtimestamp(record.created, tz= timezone.utc).isoformat(timespec="milliseconds")
            ,"level": record.levelname
            ,"logger": record.name
            ,"msg": record.getMessage()
        }

        for key, value in record.__dict__.items():
            if key not in _STANDARD_ATTRS and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


