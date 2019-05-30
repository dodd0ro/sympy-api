import json
from datetime import date, datetime


DEFAULT = object()


def success(data=DEFAULT):
    response = {'status': 'success'}
    if not data == DEFAULT:
        response['data'] = data
    return json.dumps(response, default=_json_serial)


def error(message=None, code=None, data=None):
    response = {'status': 'fail'}
    if message: response['message'] = message
    if code: response['code'] = code
    if data: response['data'] = data
    return json.dumps(response, default=_json_serial)


### HELPERS ####

def _json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))
