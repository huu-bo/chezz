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

function init() {
    // TODO: different board sizes
    console.debug(window.board.style["--square-amount"]);
    for (let i = 0; i < getComputedStyle(window.board).getPropertyValue('--square-amount') ** 2; i++) {
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