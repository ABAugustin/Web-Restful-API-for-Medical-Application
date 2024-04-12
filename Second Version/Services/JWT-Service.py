from flask import Flask, jsonify, request
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'alabalaportocala12'

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if data['username'] == 'example' and data['password'] == 'password':

        token = jwt.encode({'username': data['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                          app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token.decode('UTF-8')})

    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'message': 'Welcome, ' + data['username']})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401