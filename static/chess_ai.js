
function get_board_state() {
    $.ajax({
        type: "GET",
        url: SCRIPT_ROOT + 'get_position',
        async: false,
        success : function(data) {
            position = data['position'];
        }
    });

    return position;
}

var board_state = get_board_state();
var board = new ChessBoard('board', board_state);

var INTERVAL = 5000;

setInterval( function () {
    console.log( "Setting position!");
    new_state = get_board_state();
    board.position(new_state);
    }, INTERVAL);


