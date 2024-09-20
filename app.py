from tic_tac_toe import app, socketio

if __name__ == '__main__':
    socketio.run(app, port=6543, debug=False, allow_unsafe_werkzeug=True)
