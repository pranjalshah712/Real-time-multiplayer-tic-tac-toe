var socketio = io.connect("http://127.0.0.1:6543/start")

socketio.on('connect', () => {
            console.log('Connected to server');
        });


function validateForm() {

    var isvalid = true;
    var name = document.getElementById('name').value;
    if (name === ''){
         document.getElementById('name_error').innerHTML = 'Please Enter a Name!'
         setTimeout(function(){
            document.getElementById('name_error').style.display = 'none';
         }, 1500);
         isvalid = false;
    }
    return isvalid
}

var player = document.getElementById('player').value;
console.log(player)
var player_name = document.getElementById('player_name').value;
console.log(player_name)

function handleClick(square, username){
    socketio.emit('move', {'player':player, 'square_number':square, 'username':username})
}

var allMoves = [];

socketio.on('current_move', (move) => {
    var player = move.player;
    var square = move.square_number;
    var square = document.getElementById(`square${square}`);

//
    if (player == 1){
        var current_player = 'o';
    }
    else {
        var current_player = 'x';
    }
//
    if (square.textContent !== ''){
        return;
    }
    square.textContent = current_player;
    var moveData = {'square':move.square_number, 'current_player':current_player}
    allMoves.push(moveData)
    localStorage.setItem('all_moves', JSON.stringify(allMoves));
});

socketio.on('win', (win_info) => {
    var player = win_info.player;
    var win_square = win_info.square;
    var win_user = win_info.username;

    var current_player;

    if (player == 1) {
        current_player = 'o';
    } else {
        current_player = 'x';
    }
    document.getElementById('winner').style.display = 'block';
    document.getElementById('winner').innerHTML = `Congratulations ${win_user} you won!`;

    var squares = document.querySelectorAll('.square');
    squares.forEach(function(square) {
    square.onclick = null;
    });
});

socketio.on('loss', (loss_info) => {
    var player = loss_info.player;
    var loss_user = loss_info.username;

    var current_player;

    if (player == 1) {
        current_player = 'o';
    } else {
        current_player = 'x';
    }
    document.getElementById('loser').style.display = 'block';
    document.getElementById('loser').innerHTML = `Sorry, ${loss_user} you loss!`;

    var squares = document.querySelectorAll('.square');
    squares.forEach(function(square) {
    square.onclick = null;
    });
});


socketio.on('end_move', (move) => {
    var player = move.player;
    var square = move.square_number;
    var square = document.getElementById(`square${square}`);
//
    if (player == 1){
        var current_player = 'o';
    }
    else {
        var current_player = 'x';
    }
//
    document.getElementById('end').style.display = 'block';
    document.getElementById('end').innerHTML = 'Game Ended In Draw!';
    if (square.textContent !== ''){
        return;
    }
    square.textContent = current_player;

});

document.addEventListener('DOMContentLoaded', function() {
            reload();
        });

function reload(){

     var all_moves =  JSON.parse(localStorage.getItem('all_moves'));

     if (Array.isArray(all_moves)) {
          all_moves.forEach(function(move) {
              const squareId = `square${move.square}`;
              const square = document.getElementById(squareId);
              if (square) {
                  square.textContent = move.current_player;
                  }
              else {
                   console.warn(`Element with ID ${squareId} not found.`);
                }
              });
     }
     else {
           console.warn('No moves data found or data is not an array.');
     };
};


function restartButton() {

    localStorage.clear();
    location.reload();
};