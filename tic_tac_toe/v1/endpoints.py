from tic_tac_toe import api, socketio
from tic_tac_toe.v1.resource import Home, Game, GameStart

api.add_resource(Home, '/')
api.add_resource(Game, '/game/<string:room_code>/<string:username>/<int:player>')

socketio.on_namespace(GameStart('/start'))
