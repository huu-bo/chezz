let params = new URL(document.location).searchParams;
game_id = params.get("game-id")

if (game_id == null) {
    window.location.href = "/?incorrect_game=none";
} else if (game_id.length != 8) {
    window.location.href = "/?incorrect_game=length";
} else {
    console.log("stfu")
}

window.onload = init;
pieces = {};
all_pieces = ["bb", "bk", "bn", "bp", "bq", "br",
              "wb", "wk", "wn", "wp", "wq", "wr"]; // TODO: get from rules
layout = null;

function init() {
    for (let i in all_pieces) {  // TODO: this loads sequentially
        piece = all_pieces[i];
        var img = document.createElement("img");
        img.src = "/assets/" + piece + ".png";
        img.className = "piece";
        img.style.cursor = "move";
        img.draggable = false;
        img.style.position = "absolute";
        pieces[piece] = img;
    }

    const query = new URLSearchParams({
        "game-id": game_id
    });

    let rules = null;

    const request = new Request("/api/get-rules?" + query.toString());
    fetch(request)
    .then((response) => {
        if (response.status === 200) {
            // TODO: error messages
            return response.json();
        } else {
            throw new Error("Something went wrong on API server!");
        }
    })
    .then((response) => {
        console.log(response);
        rules = response;

        square_amount = getComputedStyle(window.board).getPropertyValue('--square-amount');
        for (let i = 0; i < square_amount ** 2; i++) {
            rule_piece = rules["rules"]["board"][i];
            if (rule_piece != " ") {
                document.getElementsByClassName("square")[i].appendChild(pieces[rule_piece].cloneNode(false));
            }
        }
    })
    .catch((error) => {
        console.error(error);
        document.body.children.error.innerText += "Api error (rules)\n";
    });

    console.log(rules);

    square_amount = getComputedStyle(window.board).getPropertyValue('--square-amount');
    state = false;
    for (let i = 0; i < square_amount ** 2; i++) {
        let e = document.createElement("div");

        if (i % square_amount == 0) {
            state = !state;
        }
        let color;
        if (state) {
            color = "#EEEED2";
        } else {
            color = "#769656";
        }
        state = !state;

        e.style.backgroundColor = color;

        e.className = "square";

        window.board.append(e);
    }

    move_pieces();
}

function move_pieces() {
    board = document.getElementById("board");
    document.onmousemove = mouse_move;
    const board_rect = board.getBoundingClientRect();  // TODO: update on resize
    square_amount = getComputedStyle(window.board).getPropertyValue('--square-amount');
    squares = document.getElementsByClassName("square");
    const piece_size = getComputedStyle(squares[0]).getPropertyValue('width');
    drag_element = null;
    let i;
    let start_drag_i;
    document.onmousedown = drag_mouse_down;

    function mouse_move(e) {
        let x = (e.clientX - board_rect.x) / board_rect.width;
        let y = (e.clientY - board_rect.y) / board_rect.height;
        x = Math.floor(x * square_amount);
        y = Math.floor(y * square_amount);

        if (x >= 0 && x < square_amount) {
            if (y >= 0 && y < square_amount) {
                i = x + y * square_amount;
            } else {
                i = -1;
            }
        } else {
            i = -1;
        }

        if (drag_element != null) {
//            drag_element.style.left = (e.clientX - board_rect.x) + "px";
//            drag_element.style.top = (e.clientY - board_rect.y) + "px";

            let x = e.clientX;
            let y = e.clientY;

            drag_element.style.left = "calc(" + x + "px - (" + piece_size + ") / 2)";
            drag_element.style.top = "calc(" + y + "px - (" + piece_size + ") / 2)";
        }

//        if (i != -1) {
//            squares[i].style.backgroundColor = "black";
//        }
    }

    function drag_mouse_down(e) {
        console.debug(e);
        if (i != -1) {
            console.debug(squares[i].children);
            if (squares[i].children.length == 0) {
                console.debug("empty", i);
                return;
            }
            drag_element = squares[i].children[0];
            document.getElementById("board").children[i].removeChild(drag_element);
//            drag_element.detach();
            document.getElementById("board").appendChild(drag_element);
            drag_element.style.position = "absolute";
            start_drag_i = i;
            document.onmouseup = drag_mouse_up;

            mouse_move(e);
        }
    }

    // TODO: render valid moves
    // TODO: check if moves are valid
    // TODO: ask server about valid moves
    function drag_mouse_up(e) {
        if (start_drag_i == i && document.onmousedown != null) {
            document.onmousedown = null;
            return;
        }
        document.onmousedown = drag_mouse_down;

        try {
            document.getElementById("board-border").removeChild(drag_element);
        } catch {}
        drag_element.style.left = "0px";
        drag_element.style.top = "0px";
        drag_element.style.position = "static";

        console.log(drag_element, i);
        squares[i].appendChild(drag_element);
        drag_element = null;
        document.onmouseup = null;
    }
}
