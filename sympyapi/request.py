import inspect, json
from .exceptions import ApiExeptionHelper
from operator import attrgetter

class ApiRequest:
    DEFAULT =  object()

    def __init__(self, args:dict, data):
        self._args = args
        self._data = data

    def get(self, arg_name, def_val=DEFAULT, argtype=DEFAULT):
        '''
        argtype - проверка и преобразование не касаются def_val

        '''
        if arg_name in self._args:
            arg = self._args[arg_name]
            if arg == '':  #bad?
                if def_val != self.DEFAULT:
                    return def_val
                else:
                    raise ApiExeptionHelper('wrongValueType', arg_name, None, argtype)
        elif def_val != self.DEFAULT:
            return def_val
        else:
            raise ApiExeptionHelper('missedArgument', arg_name)

        if argtype != self.DEFAULT:
            to_type(arg, arg_name, argtype)

        return arg

    def get_data(self, key=None, def_val=DEFAULT, argtype=None):
        if key:
            try:
                if key in self._data:
                    try:
                        data = self._data[key]
                        if data == '':  #bad can be ['']
                            if def_val != self.DEFAULT:
                                return def_val
                            else:
                                raise ApiExeptionHelper(
                                    'wrongValueType',
                                    'POST_DATA[{}]'.format(key),
                                    None,
                                    argtype)
                    except TypeError:  # if data not dict
                        self.__raise_data_is_not_dict()
                elif def_val != self.DEFAULT:
                    return def_val
                else: # hgj 
                    raise ApiExeptionHelper('missedArgument',
                                            'POST_DATA[{}]'.format(key))
            except TypeError:  # if data is not dict
                self.__raise_data_is_not_dict()
        else:
            
            data = self._data
                
        if argtype:
            data = to_type(data, 'POST_DATA', argtype)

        return data

    def __raise_data_is_not_dict(self):
        raise ApiExeptionHelper(
            'wrongValueType', 'POST_DATA', self._data, 'dict')
    
    
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
    
    
