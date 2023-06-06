window.onload = init

function init() {
    let params = new URL(document.location).searchParams;

    if (params.get("incorrect_game") === "none") {
        document.body.children.error.innerText = "incorrect game id (there was none)";
    } else if (params.get("incorrect_game") === "length") {
        document.body.children.error.innerText = "incorrect game id (incorrect length)";
    } else if (params.get("incorrect_game") === "id") {
        document.body.children.error.innerText = "game not found";
    } else if (params.get("incorrect_game") === "token") {
        document.body.children.error.innerText = "incorrect token";
    } else if (params.get("incorrect_game") != null) {
        document.body.children.error.innerText = "Unknown error occurred (" + params.get("incorrect_game").toString() + ")";
    }
}