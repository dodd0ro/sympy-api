import inspect, json
from .exceptions import ApiExeptionHelper
from operator import attrgetter

class ApiRequest:
    DEFAULT =  object()

    def __init__(self, args, data, method_type=None):
        self.args = args
        self.data = data
        if method_type:
            self.method_type = method_type
        else:
            self.method_type = 'POST' if data else 'GET'

    def get(self, arg_name, default=DEFAULT, argtype=DEFAULT):
        '''
        argtype - проверка и преобразование не касаются default

        '''
        if arg_name in self.args:
            arg = self.args[arg_name]
            if arg == '':  #BAD?
                if default != self.DEFAULT:
                    return default
                else:
                    raise ApiExeptionHelper('wrongValueType', arg_name, None, argtype)
        elif default != self.DEFAULT:
            return default
        else:
            raise ApiExeptionHelper('missedArgument', arg_name)

        if argtype != self.DEFAULT:
            arg = to_type(arg, arg_name, argtype)
        return arg

    def get_data(self, key=None, default=DEFAULT, argtype=None):
        if key:
            try:
                if key in self.data:
                    try:
                        data = self.data[key]
                        if data == '':  #bad can be ['']
                            if default != self.DEFAULT:
                                return default
                            else:
                                raise ApiExeptionHelper(
                                    'wrongValueType',
                                    'POST_DATA[{}]'.format(key),
                                    None,
                                    argtype)
                    except TypeError:  # if data not dict
                        self.__raise_data_is_not_dict()
                elif default != self.DEFAULT:
                    return default
                else: # hgj 
                    raise ApiExeptionHelper('missedArgument',
                                            'POST_DATA[{}]'.format(key))
            except TypeError:  # if data is not dict
                self.__raise_data_is_not_dict()
        else:
            
            data = self.data
                
        if argtype:
            data = to_type(data, 'POST_DATA', argtype)

        return data

    def __raise_data_is_not_dict(self):
        raise ApiExeptionHelper(
            'wrongValueType', 'POST_DATA', self.data, 'dict')
    
    
def to_type(arg, arg_name, argtype):
    try:
        return _arg_types[argtype](arg)
    except:
        raise ApiExeptionHelper(
            'wrongValueType', arg_name, arg, argtype)
    


_arg_types = {
    'str': lambda x: str(x), #? и так всегда str
    'int': lambda x: int(x),
    'float': lambda x: float(x),
    'json': lambda x: json.loads(x),
    'List[str]': lambda x: [str(val) for val in _det_list(x)],
    'List[int]': lambda x: [int(val) for val in _det_list(x)],
    'List[float]': lambda x: [float(val) for val in _det_list(x)]
}     
            
def _det_list(val):
    return json.loads(val) if isinstance(val, str) else val
    
    
