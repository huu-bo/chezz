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
        img.className = "piece"
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
}