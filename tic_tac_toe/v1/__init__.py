from flask import Blueprint
from tic_tac_toe import app, api
from tic_tac_toe.v1 import endpoints

blue_ob = Blueprint('tic_tac_toe', __name__)
api.blueprint = blue_ob
api.blueprint_setup = blue_ob

app.register_blueprint(blue_ob)
