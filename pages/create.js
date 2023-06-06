window.onload = init

const request = new Request("/api/game-id");
let game_id = null;
let token = null;

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
        split = response.split('\n');

        if (split.length != 2) {
            console.log(split);
            console.log(response);
            throw new Error("did not get token and id");
        }

        console.debug("game ID", split[0]);

        game_id = split[0];
        token = split[1];
        document.body.children.game_id.innerText = game_id;
        document.getElementById('game-id-form').value = game_id;
    })
    .catch((error) => {
        console.error(error);
        game_id = 0;
        document.body.children.error.innerText += "Api error (id/token)";
    })
}

function check_rules() {
    const query = new URLSearchParams({
        "game-id": game_id,
        "token": token
    });

    const request = new Request("/api/rules?" + query.toString());
    fetch(request)
    .then((response) => {
        if (response.status === 200) {
            return response.text();
        } else {
            throw new Error("Something went wrong on API server!");
        }
    })
    .then((response) => {
        console.debug("rules response", response);
        document.body.children.error.innerText += response;
        if (response != "ok") {
            throw new Error("sending rules failed with message " + response);
        }

        const query = new URLSearchParams({
            "game-id": game_id,
            "token": token
        });
        window.location.href = "/wait.html?" + query.toString();
    })
    .catch((error) => {
        console.error(error);
        document.body.children.error.innerText += "Api error (rules)";
    });
}