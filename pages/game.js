let params = new URL(document.location).searchParams;
game_id = params.get("game-id")

if (game_id == null) {
    window.location.href = "/?incorrect_game";
} else {
    console.log("stfu")
}

window.onload = init;

function init() {
    // TODO: different board sizes
    for (let i = 0; i < 9*9; i++) {
        let e = document.createElement("div");

        let color;
        if (i % 2 == 0) {
            color = "#EEEED2";
        } else {
            color = "#769656";
        }
        e.style.backgroundColor = color;

        e.className = "square"
        window.board.append(e);
    }
}