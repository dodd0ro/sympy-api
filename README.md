
# Что это?
sympyApi - мини-фреймворк для создания api на python, который поможет:
- уменьшить количество повторяющегося кода
- автоматически возвращать ответы на исключения
- проверять и преобразовывать типы аргументов запроса
- производить авторизацию


# Краткое руководство

<!-- TOC -->


- [Подготовка](#подготовка)
- [Методы API](#методы-api)
- [HTTP методы](#http-методы)
- [Аргументы](#аргументы)
- [Авторизация](#авторизация)
    - [Пользовательский способ авторизации](#пользовательский-способ-авторизации)
    - [Пользовательский способ аутентификации](#пользовательский-способ-аутентификации)
- [Обработка исключений](#обработка-исключений)
    - [Стандартные исключения](#стандартные-исключения)
    - [Пользовательские исключения](#пользовательские-исключения)
- [Работа с Flask:](#работа-с-flask)
- [Допольнительные инструменты](#допольнительные-инструменты)
    - [jsend](#jsend)
    - [Access](#access)

<!-- /TOC -->


## Подготовка
<sup>[[к оглавлению]](#Краткое-руководство)</sup>


```python 
from sympyapi import SympyApi

api = SympyApi()
```


## Методы API 
<sup>[[к оглавлению]](#Краткое-руководство)</sup>


```python
@api.method('foo')
def foo(request):
    return 'hello world'
```
```python
foo_response = api.create_request('foo')
print(foo_response)  # "hello world"

bar_response = api.create_request('bar')
print(bar_response)  # "{"error": "Method 'bar' doesn't exist."}"
```


## HTTP методы
<sup>[[к оглавлению]](#Краткое-руководство)</sup>


```python
@api.method('foo', 'GET')
def foo_get(request):
    return request.get('x')

@api.method('foo', 'POST')
def foo_post(request):
    return request.get_data()
```
```python
response = api.create_request('foo', args={x: 'hello'}, method_type='GET')
print(response)  # "hello"

response = api.create_request('foo', data='world', method_type='POST')
print(response)  # "world"

response = api.create_request('foo', method_type='PUT')
print(response)  
# "{"error": "Api method 'foo' accepts ['GET', 'POST'] HTTP methods. Got 'PUT'."}"
```
```python
@api.method('bar', ['GET', 'POST'])
def bar(request):
    return request.get('x') + ' ' + request.get_data()

response = api.create_request('bar', {'x': 'hello'}, data='world')
print(response_bar)  # "hello world"
```

## Аргументы
<sup>[[к оглавлению]](#Краткое-руководство)</sup>


```python
@api.method('foo')
def foo(request):
    a = request.get('a')
    b = request.get('b', argtype='float')
    c = request.get('c', argtype='int', default=2) 
    return f"ac:{a * c} bc:{b * c}"
```
```python
response = api.create_request('foo', {'a': '2', 'b': '2', 'b': '3'})
print(response)  # "ac:222 bc:6.0"

response = api.create_request('foo', {'a': '2', 'b': '2'})
print(response)  # "ac:22 bc:4.0"

response = api.create_request('foo', {'a': '2', 'b': 'b'})
print(response)
# "{"error": "Argument 'b' in method 'foo' mast be 'float'."}"

response = api.create_request('foo', {'a': '2'})
print(response)
# "{"error": "Method 'foo' missing required argument: 'b'"}"
```

## Авторизация
<sup>[[к оглавлению]](#Краткое-руководство)</sup>


```python
@api.method('foo', access_code=6)
def foo(request):
    return 'hello world'
```
```python
response = api.create_request('foo', access_code=4)
print(response)  # "hello world" 

response = api.create_request('foo', {'token': 'abcde'})
print(response)  # "hello world" при успехе аутентификации

response = api.create_request('foo', access_code=1)
print(response)
# "{"error": "'error': "Method 'foo' requiers access code 6."}"
```
#### Пользовательский способ авторизации
```python
@api.check_access
def _(required_access_code, access_code): 
    return access_code in required_access_code
```
```python
@api.method('foo', access_code='ab')
def foo(request):
    return 'hello world'

response = api.create_request('foo', access_code='b')
print(response)  # "hello world"

response = api.create_request('foo', access_code='c')
print(response)
# "{"error": "'error': "Method 'foo' requiers access code 6."}"
```
#### Пользовательский способ аутентификации
```python
@api.get_access_code(token_arg='token')
def _(token):
    # пример кода сверки с базой данных
    command = 'SELECT access_code FROM users WHERE token=?'
    conn = sqlite3.connect(DB_PATH)
    with conn:
        cursor = conn.cursor()
        cursor.execute(command, [token])
        fetch = cursor.fetchone()
    access_code = fetch[0] if fetch else 0

    return access_code
```
```python
response = api.create_request('foo', {"token": "abcde"})
```
## Обработка исключений
<sup>[[к оглавлению]](#Краткое-руководство)</sup>


```python
@api.exceptions.method('errorType')
def errorType(method_name, *info):
    return 'message'
```
### Стандартные исключения

| Имя исключения  | Передаваемые аргументы                         | Описание                         |
| --------------- | ---------------------------------------------- | -------------------------------- |
| undefinedMethod | method_name                                    | несуществующий метод             |
| missedArgument  | method_name, arg                               | остутствует необходимый аргумент |
| wrongValueType  | method_name, arg, value, argtype               | неправильный тип аргумента       |
| wrongMethodType | method_name, required_method_type, method_type | неправильный HTTP метод          |
| wrongAccessCode | method_name, required_access_code              | ошибка авторизации               |


Пример формирования ответа при остутствии необходимого аргумента:
```python
@api.exceptions.method('missedArgument')
def _(method_name, arg):
    message = f"{method_name}() missing required argument: '{arg}'"
    return return json.dumps({"status": "fail", "message": message, "code": 400}) 
```
```
http://localhost:5000/api/test?a=2
{"status": "fail", "message": "test() missing required argument: 'b'", "code": 400}
```


### Пользовательские исключения

Предположим, мы хотим создать проверочню функцию `is_poitive`, которая при получении негативного числа прекратит выполнение сценария и вернет ответ на запрос, указывающий на ошибку. Для этого создадим и вызовим исключение с помощью `ApiExeptionHelper` и передадим в него выбранное нами название этой ошибки (например `notPositive`) и любую нужную информацию:
```python
from sympyapi import ApiExeptionHelper

def is_poitive(val):
    if x < 0:
        raise ApiExeptionHelper('notPositive', val)

@api.method('multiplyString')
def foo(request):
    s = request.get('s')
    x = is_poitive(request.get('x', argtype='int'))

    result = s * x
    return json.dumps({"status": "success", "data": result}) 
```

Теперь определим как должен формироваться ответ на эту ошибку:
```python
@api.exceptions.method('notPositive')
def notPositiveException(method_name, val):
    message = f"Value mast be positive, got: {val}"
    return json.dumps({"status": "fail", "message": message, "code": 400}) 
```
Проверяем:
```python
response = api.create_request('multiplyString', {s: 'hello ', x: 2})
print(response)  
# "{"status": "success", "data": "hello hello "}"

response = api.create_request('multiplyString', {s: 'hello ', x: -1})
print(response)
# "{"status": "fail", "message": "Value mast be positive, got: -1", "code": 400}"
```

## Работа с Flask:
<sup>[[к оглавлению]](#Краткое-руководство)</sup>


```python
from flask import Flask

app = Flask(__name__)

@app.route('api/<string:method_name>', methods=['GET', 'POST'])
def api_view(method_name):
    return api.flask_request(method_name)

```

```python
@api.method('join')
def api_join(request):
    x = request.get('x')
    y = request.get('y')
    result = ' '.join([x, y])
    jsend.success(result)  

# http://localhost/api/join?x=hello&y=world
# {"status": "success", "data": "hello world"}
```

```python
from flask import Flask, request, session

app = Flask(__name__)

@app.route('api/<string:method_name>', methods=['GET', 'POST'])
def api_view(method_name):
    return api.create_request(
        method_name,
        request.args,
        data=request.get_json(),
        access_code=session.get('access_code', None),
        method_type=request.method)
```
## Допольнительные инструменты
<sup>[[к оглавлению]](#Краткое-руководство)</sup>


### jsend
```python
from sympyapi import jsend

jsend.success()  
# "{"status": "success"}"

jsend.success({x: 1})  
# "{"status": "success", "data": {x: 1}}"

jsend.error('FAIL!!!', code=400, data={x: 1})    
# "{"status": "fail", "message": "FAIL!!!", "code": 400, "data": {x: 1}}"
```
### Access
```python
from simpyapi import Access

user_access = Access.calc(2, 4) 
print(user_access)  # 6

access = Access.check(user_access, 2)
print(access)  # True

access = Access.check(user_access, 3)
print(access)  # Flase
```
```python
codes = Access.create_codes(['CREATE', 'EDIT', 'DELETE']) 
# codes.CREATE = 1; codes.EDIT = 2; codes.DELETE = 4; 

user_access = Access.calc(codes.CREATE, codes.EDIT)
print(user_access)  # 3

access = Access.check(user_access, codes.EDIT)
print(access)  # True

access = Access.check(user_access, codes.DELETE)
print(access)  # Flase


```


# API

## class sympyapi.SympyApi()

### method()

### create_request()

### check_access()

### get_access_code()

### exceptions.get()

### exceptions.method()

## class sympyapi.ApiRequest(args, data, method_type=None)

### get(self, arg_name, default=DEFAULT, argtype=DEFAULT)

### get_data(self, key=None, default=DEFAULT, argtype=None)

### args

### data

### method_type

## class sympyapi.ApiExeptionHelper()

### name

### args

### kwargs


## sympyapi.Access

### Access.codes
### Access.calc
### Access.check

## sympyapi.jsend

### success()

### error()

