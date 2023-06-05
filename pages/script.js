window.onload = init

function init() {
    let params = new URL(document.location).searchParams;

    if (params.get("incorrect_game") === "none") {
        document.body.children.error.innerText = "incorrect game id (there was none)";
    } else if (params.get("incorrect_game") === "length") {
        document.body.children.error.innerText = "incorrect game id (incorrect length)";
    }
}