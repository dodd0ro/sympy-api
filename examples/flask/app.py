from flask import Flask, request, session
from sympyapi import SympyApi, Access, jsend

app = Flask(__name__)
api = SympyApi()

### API VIEW ###

@app.route('/api/<string:method_name>', methods=['GET', 'POST'])
def api_view(method_name):
    return api.create_request(
        method_name,
        request.args,
        data=request.get_json(),
        access_code=session.get('access_code', None),
        method_type=request.method)
    

### API METHODS ###

@api.method('test', 'GET', 0)
def api_test(request):
    """
    => http://localhost:5000/api/test?a=1.2
    <= {"status": "success", "data": {"a": 1.2, "b": [1, 2, 3], "method": "GET"}}
    """
    data = {}
    data['a'] = request.get('a', argtype='float')
    data['b'] = request.get('b', [1, 2, 3], argtype='List[str]')
    print(type(data['b'][0]))
    data['method'] = request.method_type
    return jsend.success(data)

### API ACCESS CHECK ###

@api.get_access_code(token_arg='token') 
def _(token):
    command = 'SELECT access_code FROM users WHERE token=?'
    conn = sqlite.connect(DB_PATH)
    with conn:
        cursor = conn.cursor()
        cursor.execute(command, [token])
        fetch = cursor.fetchone()
    access_code = fetch[0] if fetch else 0
    return access_code

@api.check_access
def _(required_access_code, access_code):  # default
    return Access.check(required_access_code or 0, access_code or 0)

### API EXCEPTIONS ###

@api.exceptions.method('undefinedMethod')
def _(method_name):
    message = "Method '{}' doesn't exist.".format(method_name)
    return jsend.error(message, code=404)

@api.exceptions.method('missedArgument')
def _(method_name, arg):
    message = "Method '{}' missing required argument: '{}'.".format(
        method_name, arg)
    return jsend.error(message, code=400)

@api.exceptions.method('wrongValueType')
def _(method_name, arg, value, argtype):
    message = "Argument '{}' in method '{}' mast be '{}'.".format(
        arg, method_name, argtype)
    data = {arg: value} 
    return jsend.error(message, data=data, code=400)

@api.exceptions.method('wrongMethodType')
def _wrongMethodType(method_name, required_method_type, method_type):
    message = "Api method '{}' accepts {} HTTP methods. Got '{}'.".format(
        method_name, required_method_type, method_type)
    return jsend.error(message, code=400)

@api.exceptions.method('wrongAccessCode')
def _(method_name, required_access_code):
    message = "Method '{}' requiers access code {}.".format(
        method_name, required_access_code)
    return jsend.error(message, code=401)

### RUN APP ###

if __name__ == '__main__':
    app.run()