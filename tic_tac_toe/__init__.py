from flask import Flask
from flask_socketio import SocketIO
import redis
import importlib
from flask_restful import Api

app = Flask(__name__, template_folder='../templates', static_folder='../static')
socketio = SocketIO(app)
redis_ob = redis.StrictRedis(host='localhost', port=6379, db=0)
api = Api(app)

importlib.import_module('tic_tac_toe.v1')
