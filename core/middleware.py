import logging
import re
import time
import uuid

from django.conf import settings
from django.core.exceptions import BadRequest, PermissionDenied, SuspiciousOperation
from django.http import Http404, JsonResponse
from django.core.signals import got_request_exception


from .context import reset_request_id, set_request_id

access_logger = logging.getLogger("access")
error_logger = logging.getLogger('app.errors')

#  it aonly accepts "safe incomming IDs: stops log injection "
_SAFE_REQUEST_ID = re.compiler(r"[a-zA-Z0-9_\-\.]{1, 64}]")

class RequestIDMiddleware:
    def __init__ (self, get_response):
        self.get_response = get_response
        self.header = getattr(settings, "REQUEST_ID_HEADER", "HTTP_X_REQUEST_ID")
        self.meta_key = "HTTP_" + self.header.upper().replace("-","_")


    def __call__(self, request):
        incomming = request.META.get(self.meta_key)
        request_id = incomming if incomming and _SAFE_REQUEST_ID.match(incomming) else str(uuid.uuid4())

        request.request_id = request_id
        token = set_request_id(request_id)
        try:
            response = self.get_response(request)
        finally:
            reset_request_id(token)

        response[self.header] = request_id
        return response

            

