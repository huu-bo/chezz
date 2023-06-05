window.onload = init

function init() {
    let params = new URL(document.location).searchParams;

    if (params.get("incorrect_game") === "") {
        // window.location.href = "/?incorrect_game";
        document.body.children.error.innerText = "incorrect game id"
    }
}