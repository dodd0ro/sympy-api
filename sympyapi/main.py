from .exceptions import ApiExeptions, ApiExeptionHelper
from .request import ApiRequest
from .access import Access
from functools import wraps


class SympyApi:

    def __init__(self):
        self.exceptions = ApiExeptions()
        self.methods_dict = {}

        self._check_access = lambda ra, a: Access.check(ra or 0, a or 0)
        self._token_arg_name = None

    def method(self, method_name, method_types=None, access_code=None):  # decorator
        ''' '''
        if method_types and type(method_types) != list:
            method_types = [method_types]

        def decorator(function):
            if method_name in self.methods_dict:
                raise Exception("Duplicated methods names")

            self.methods_dict[method_name] = {
                'function': function,
                'access_code': access_code,
                'method_types': method_types }
            
        return decorator

    def check_access(self, function):  # decorator
        def decorator():
            self._check_access = function
        return decorator

    def get_access_code(self, token_arg='token'):  # decorator
        def decorator(function):
            self._token_arg_name = token_arg
            self._get_access_code = function
        return decorator

    def create_request(self, method_name, args,
                       data=None, access_code=None, method_type=None):
        try:
            method_data = self.methods_dict[method_name]
        except KeyError:
            return self.exceptions.get('undefinedMethod')(method_name)

        method = method_data['function']
        required_access_code = method_data['access_code']
        required_method_types = method_data['method_types']

        token = args.get(self._token_arg_name, None)
        if not access_code and token:
            access_code = self._get_access_code(token)

        if not self._check_access(required_access_code, access_code):
            return self.exceptions.get('wrongAccessCode')(
                method_name, required_access_code)

        if required_method_types and not method_type in required_method_types:
            return self.exceptions.get('wrongMethodType')(
                method_name, required_method_types, method_type)

        try:
            request = ApiRequest(args, data, method_type)
            return method(request)
        except ApiExeptionHelper as error:
            if error.name in self.exceptions.methods:
                return self.exceptions.get(error.name)(
                    method_name, *error.args, **error.kwargs)  #! method_name
            else:
                raise #BAD

        

