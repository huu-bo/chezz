let params = new URL(document.location).searchParams;
game_id = params.get("game-id");
token = params.get("token");

if (game_id == null) {
    window.location.href = "/?incorrect_game=none";
} else if (game_id.length != 8) {
    window.location.href = "/?incorrect_game=length";
} else {
    console.log("stfu");
}

if (token == null) {
    window.location.href = "/?incorrect_game=token";
}

window.onload = init;

function init() {
    document.body.children.game_id.innerText = game_id;
    window.setInterval(check_players, 1000);
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
