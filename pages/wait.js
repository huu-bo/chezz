let params = new URL(document.location).searchParams;
game_id = params.get("game-id");
token = params.get("token");

if (game_id == null) {
    window.location.href = "/?incorrect_game=none";
} else if (game_id.length != 8) {
    window.location.href = "/?incorrect_game=length";
}

if (token == null) {
//    window.location.href = "/?incorrect_game=token";
}

window.onload = init;

function init() {
    if (token == null) {
        const query = new URLSearchParams({
            "game-id": game_id
        });

        const request = new Request("/api/join?" + query.toString());
        fetch(request)
        .then((response) => {
            if (response.status === 200) {
                return response.text();
            } else {
                throw new Error("Something went wrong on API server!");
            }
        })
        .then((response) => {
            if (response.length != 64) {
                if (response == 'id') {
                    document.body.children.error.innerText += "No game-ID\n";
                } else if (response == 'u-id') {
                    document.body.children.error.innerText += "Unknown game-ID\n";
                } else if (response == 'uninit') {
                    document.body.children.error.innerText += "Game is not initialised\n";
                } else if (response == 'full') {
                    document.body.children.error.innerText += "Game is full\n";
                } else {
                    document.body.children.error.innerText += response + "\n";
                }

                throw new Error("error " + response);  // TODO: redundant
            } else {
                token = response;
                setup_timer();
            }
        })
        .catch((error) => {
            console.error(error);
            document.body.children.error.innerText += "Api error (join)\n";
        });
    }

    document.body.children.game_id.innerText = game_id;
    if (token != null) {
        setup_timer();
    }

    const query = new URLSearchParams({
            "game-id": game_id
        });

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
            console.debug(response);
            document.getElementById("max_player_amount").innerText = response["max_players"];
        })
        .catch((error) => {
            console.error(error);
            document.body.children.error.innerText += "Api error (rules)\n";
        });
}

function check_players() {
    const query = new URLSearchParams({
        "game-id": game_id,
        "token": token
    });

    const request = new Request("/api/players?" + query.toString());
    fetch(request)
    .then((response) => {
        if (response.status === 200) {
            return response.text();
        } else {
            throw new Error("Something went wrong on API server!");
        }
    })
    .then((response) => {
        if (response == "id") {
            window.location.href = "/?incorrect_game=id";
        } else if (response == "start") {
            const query = new URLSearchParams({
                "game-id": game_id,
                "token": token
            });
            document.body.children.error.innerText += "starting\n";
            window.location.href = "/game.html" + query.toString();
        }

        console.debug("players:", +response);

        document.getElementById("player_amount").innerText = response;
    })
    .catch((error) => {
        console.error(error);
        document.body.children.error.innerText += "Api error (players)\n";
    })
}

function setup_timer() {
    check_players();
    window.setInterval(check_players, 2000);
}
