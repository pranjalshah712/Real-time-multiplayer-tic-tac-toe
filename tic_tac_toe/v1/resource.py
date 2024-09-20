from flask import render_template, make_response, redirect, url_for, request
from flask_restful import Resource
from flask_socketio import Namespace, emit
from tic_tac_toe import redis_ob
import random
import json
from string import ascii_uppercase

rooms = []


def generate_room_code():
    while True:
        code = ""
        for _ in range(5):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            rooms.append(code)
            break
    return code


class Home(Resource):

    def get(self):
        return make_response(render_template('home.html'))

    def post(self):
        name = request.form.get('name')
        room_code = request.form.get('room_code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if join is False:
            new_room_code = generate_room_code()
            return redirect(url_for('game', room_code=new_room_code, username=name, player=1))

        if create is False and room_code == '':
            return make_response(render_template('home.html', error=True, username=name))
        else:
            try:
                rooms.remove(room_code)
                return redirect(url_for('game', room_code=room_code, username=name, player=2))
            except:
                return make_response(render_template('home.html', error_max=True, username=name))


class Game(Resource):
    def get(self, room_code, username, player):
        return make_response(render_template('game.html', room_code=room_code, username=username, player=player))


def set_square_numbers(user, square_numbers):
    redis_ob.set(user, json.dumps(square_numbers))


def get_square_numbers(user, move):
    square_numbers = json.loads(redis_ob.get(user))
    square_numbers.append(move['square_number'])
    square_numbers.sort()
    return square_numbers


class GameStart(Namespace):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = []
        self.user1 = ''
        self.user2 = ''
        self.loser = ''
        self.flag = True
        self.swap_user = ['0']
        self.count = 0
        self.win_conditions = [
            [1, 2, 3], [1, 4, 7], [4, 5, 6], [2, 5, 8],
            [7, 8, 9], [3, 6, 9], [1, 5, 9], [3, 5, 7]
        ]

    def on_connect(self):
        set_square_numbers('user1', [])
        set_square_numbers('user2', [])
        self.count = 0
        # self.user1.clear()
        # self.user2.clear()
        self.flag = True
        self.swap_user = ['0']
        print('user_connect')

    def on_move(self, move):
        if move['player'] != self.swap_user[-1]:

            if self.user1 == '':
                self.user1 = move['username']
            if self.user1 != move['username'] and self.user2 == '':
                self.user2 = move['username']
            loser = '2' if move['player'] == '1' else '1'
            if self.user1 == move['username']:
                self.loser = self.user2
            else:
                self.loser = self.user1

            if move['player'] == str(1):
                square_numbers = get_square_numbers('user1', move)
                print(square_numbers)
                set_square_numbers('user1', square_numbers)
                self.current_user = square_numbers
                # self.user1.append(move['square_number'])
                # self.user1.sort()
                # self.current_user = self.user1

            else:
                square_numbers = get_square_numbers('user2', move)
                print(square_numbers)
                set_square_numbers('user2', square_numbers)
                self.current_user = square_numbers
                # self.user2.append(move['square_number'])
                # self.user2.sort()
                # self.current_user = self.user1

            if len(self.current_user) > 2:

                for i in range(len(self.current_user) - 2):
                    for j in range(i + 1, len(self.current_user) - 1):
                        if [self.current_user[i], self.current_user[j], self.current_user[j + 1]] in self.win_conditions:
                            emit('current_move', move, broadcast=True)
                            emit('win', {'player': move['player'],
                                         'square': [self.current_user[i], self.current_user[j],
                                                    self.current_user[j + 1]],
                                         'username': move['username']}, broadcast=True)

                            emit('loss', {'player': loser, 'username': self.loser}, broadcast=True)
                            self.flag = False
                            break

            if self.flag is True:
                self.count += 1
                if self.count == 9:
                    print(self.count)
                    emit('end_move', move, broadcast=True)
                else:
                    print(self.count)
                    emit('current_move', move, broadcast=True)
            else:
                emit('current_move', move, broadcast=True)

            self.swap_user.append(move['player'])

            # if len(self.user1) > 2:
            #     try:
            #         for i in range(len(self.user1) - 2):
            #             if flag is False:
            #                 break
            #             for j in range(i + 1, len(self.user1)):
            #                 if [self.user1[i], self.user1[j], self.user1[j + 1]] in self.win_conditions:
            #                     emit('current_move', move, broadcast=True)
            #                     emit('win', {'player': move['player'],
            #                                  'square': [self.user1[i], self.user1[j], self.user1[j + 1]],
            #                                  'username': move['username']}, broadcast=True)
            #                     flag = False
            #                     break
            #     except IndexError as e:
            #         pass
            # if len(self.user2) > 2:
            #     try:
            #         for i in range(len(self.user2) - 2):
            #             if flag is False:
            #                 break
            #             for j in range(i + 1, len(self.user2)):
            #                 if [self.user2[i], self.user2[j], self.user2[j + 1]] in self.win_conditions:
            #                     emit('current_move', move, broadcast=True)
            #
            # emit('win', {'player': move['player'], 'square': [self.user2[i], self.user2[j], self.user2[j + 1]],
            # 'username': move['username']}, broadcast=True) flag = False break except IndexError as e: pass

            # if len(self.current_user) > 2:
            #     # try:
            #     for i in range(len(self.current_user) - 2):
            #         # if self.flag is False:
            #         #     break
            #         for j in range(i + 1, len(self.current_user) - 1):
            #             if [self.current_user[i], self.current_user[j], self.current_user[j + 1]] in self.win_conditions:
            #                 emit('current_move', move, broadcast=True)
            #                 emit('win', {'player': move['player'],
            #                             'square': [self.current_user[i], self.current_user[j], self.current_user[j + 1]],
            #                             'username': move['username']}, broadcast=True)
            #                 self.flag = False
            #                 break
            #     # except IndexError as e:
            #     #     print(e)
