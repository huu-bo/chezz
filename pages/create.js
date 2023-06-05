window.onload = init

const request = new Request("/api/game-id");
let game_id = null;

fetched = fetch(request)
  .then((response) => {
    if (response.status === 200) {
      return response.text();
    } else {
      throw new Error("Something went wrong on API server!");
    }
  });


function init() {
    fetched.then((response) => {
        console.debug("game ID", response);
        game_id = response;
        document.body.children.game_id.innerText = game_id;
        document.getElementById('game-id-form').value = game_id;
    })
    .catch((error) => {
        console.error(error);
        game_id = 0;
        document.body.children.error.innerText += "Api error";
    })
}