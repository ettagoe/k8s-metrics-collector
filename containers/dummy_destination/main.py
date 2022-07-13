import os
import json

from flask import Flask, request

OUTPUT_DIR = '/app/output'

app = Flask(__name__)
app.secret_key = b"\xf9\x19\x8d\xd2\xb7N\x84\xae\x16\x0f'`U\x88x&\nF\xa2\xe9\xa1\xd7\x8b\t"


@app.route('/api/v1/metrics', methods=['POST'])
def to_file():
    # if request.args.get('token') and request.args.get('token') == 'incorrect_token':
    #     return json.dumps({'errors': ['Data collection token is invalid']}), 401
    data = request.json
    if data and len(data) > 0:
        _write_to_file(_extract_file_name(), data)
    return json.dumps({'errors': []})


def _write_to_file(file_name: str, data):
    file_path = os.path.join(OUTPUT_DIR, file_name)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            if existing_data := json.load(f):
                data = existing_data + data
    with open(file_path, 'w') as f:
        json.dump(data, f)


def _extract_file_name():
    # todo
    return 'node.json'


if __name__ == '__main__':
    app.run()
