from flask import Flask, request, session
from sympyapi import SympyApi, Access, jsend
app = Flask(__name__)
api = SympyApi()

### API VIEW ###

@app.route('/api/<string:method_name>', methods=['GET', 'POST'])
def api_view(method_name):
    args = request.args.to_dict()  #bad!

    user_access_code = session.get('access_code', None)

    user_id = session.get('user_id', None)
    args.update({'user_id':user_id})

    if request.method == 'POST':
        return api.create_request(
            method_name, args,
            data=request.get_json(),
            forced_access_code=user_access_code)
    
    elif request.method == 'GET':
        return api.create_request(
            method_name, args,
            forced_access_code=user_access_code)

### API METHODS ###

@api.method('test')
def api_test(request):
    a = request.get('a', 'ff', argtype='List[int]')
    b = request.get('b', [1,2,3], argtype='List[str]')
    message = 'TEST {} {}'.format(a, b)
    return jsend.success(message)

### API ACCESS CHECK ###

@api.check_access(token_name='token')
def _(required_access_code, token, forced_access_code=None):
    if forced_access_code:
        user_access_code = forced_access_code
    else:
        if not token:
            user_access_code = 0
        else:
            command = 'SELECT access_code FROM users WHERE token=?'
            conn = sqlite3.connect(DB_PATH)
            with conn:
                cursor = conn.cursor()
                cursor.execute(command, [token])
                fetch = cursor.fetchone()
            user_access_code = fetch[0] if fetch else 0
            
    is_accessed = Access.check(required_access_code, user_access_code)
    return is_accessed

### API EXCEPTIONS ###

@api.exceptions.method('undefinedMethod')
def _(method_name):
    message = "Method '{}' doesn't exist.".format(method_name)
    return jsend.error(message, code=404)


@api.exceptions.method('missedArgument')
def _(method_name, argument_name):
    message = "Method '{}' missing required argument: '{}'.".format(
        method_name, argument_name)
    return jsend.error(message, code=400)


@api.exceptions.method('wrongValueType')
def _(method_name, arg_name, arg, right_arg_type):
    message = "Argument '{}' in method '{}' mast be '{}'.".format(
        arg_name, method_name, right_arg_type)
    data = {arg_name: arg} 
    return jsend.error(message, data=data, code=400)


@api.exceptions.method('wrongAccessCode')
def _(method_name, target_access_code):
    message = "Method '{}' requiers access code {}.".format(
        method_name, target_access_code)
    return jsend.error(message, code=401)

### RUN APP ###

if __name__ == '__main__':
    app.run()