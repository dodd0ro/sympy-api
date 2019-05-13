from .exceptions import ApiExeptions, ApiExeptionHelper
from .request import ApiRequest
from .access import Access
from functools import wraps


class SympyApi:

    def __init__(self):
        self.exceptions = ApiExeptions()
        self.methods_dict = {}

        self._check_access = lambda *args, **kwargs: True
        self._token_arg_name = None

    def method(self, method_name, access_code=0):  # decorator
        ''' '''
        def decorator(function):
            if method_name in self.methods_dict:
                raise Exception("Duplicated methods names")
            
            function.access_code = access_code
            self.methods_dict[method_name] = function

        return decorator

    def check_access(self, token_name='token'):  # decorator
        def decorator(function):
            self._check_access = function
            self._token_arg_name = token_name
        return decorator

    def create_request(self, method_name, args,
                       data=None, forced_access_code=None):
        try:
            method = self.methods_dict[method_name]
        except KeyError:
            return self.exceptions.get('undefinedMethod')(method_name)

        if not self._check_access(method.access_code,
                                  args.get(self._token_arg_name, None),
                                  forced_access_code):
            return self.exceptions.get('wrongAccessCode')(
                method_name, method.access_code)

        try:
            request = ApiRequest(args, data)
            return method(request)
        except ApiExeptionHelper as error:
            if error.name in self.exceptions.methods:
                return self.exceptions.get(error.name)(
                    method_name, *error.args, **error.kwargs)  #! method_name
            else:
                raise

        

