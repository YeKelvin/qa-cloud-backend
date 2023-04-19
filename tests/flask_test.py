#!/usr/bin/ python3
# @File    : flask_test.py
# @Time    : 2019/11/13 17:59
# @Author  : Kelvin.Ye
from flask import Flask
from flask import request


app = Flask(__name__)


@app.route('/test', methods=['GET', 'POST'])
def test():
    print(f'url={request.url}')
    print(f'base_url={request.base_url}')
    print(f'method={request.method}')
    print(f'type={type(request.data)}, request.data={request.data}')
    print(f'type={type(request.args)}, request.args={request.args}')
    print(f'type={type(request.form)}, request.form={request.form}')
    print(f'type={type(request.values)}, request.values={request.values}')
    print(f'type={type(request.is_json)}, request.is_json={request.is_json}')
    print(f'type={type(request.json)}, request.json={request.json}')
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
