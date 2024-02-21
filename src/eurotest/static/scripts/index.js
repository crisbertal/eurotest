// TODO 
// - [ ] Create scripts by domain
// - [ ] Serve HTML and JS with http-server or something like that with NodeJS

const Events = {
	CONNECTION: "connect",
	UPDATE_USER_LIST: "update-user-list",
    NEXT_COUNTRY: "next-country",
};

// Global State
let user = {};
let country = "es";

// components
// buttons
const loginButton = document.getElementById("login-button");
const voteButton = document.getElementById("vote-button");
const refreshRankingButton = document.getElementById("refresh-ranking-button");

// inputs
const userInput = document.getElementById("user-input");
const performanceInput = document.getElementById("performance-input");
const memeInput = document.getElementById("meme-input");

// ulist
const rankingList = document.getElementById("ranking-list");
const connectedUsersList = document.getElementById("connected-users-list");

// text
const currentCountryTitle = document.getElementById("current-country");
const userP = document.getElementById("user-p");


// events
loginButton.addEventListener("click", () => {
	// TODO 
	// - [ ] Can't be empty
	// - [ ] Try catch this boi or get errors from the websocket connection

	user = {
		name: userInput.value,
		vote: false,
	};

	connectSocket(user);

	// Update the user connected
	userP.innerText = userInput.value

	// Clear the inputs if the connection is accepted
	userInput.value = "";
	loginButton.disabled = true;
	userInput.disbled = true;
});


voteButton.addEventListener("click", () => {
	// TODO for the current country
	fetch("http://localhost:5000/vote", {
		method: "POST",
		mode: "cors",
		// REFACTOR all in the body or change endpoint /{country}/vote/
		body: JSON.stringify({
			username: user.name,
			// TODO, get current country from the backend
			country: "es",
			performance: parseInt(performanceInput.value),
			meme: parseInt(memeInput.value)
		}),
		headers: {
			"Content-type": "application/json; charset=UTF-8"
		}
	});
});


refreshRankingButton.addEventListener("click", async () => {
	response = await fetch("http://localhost:5000/ranking", {
		method: "GET",
		headers: {
			"Content-type": "application/json; charset=UTF-8"
		}
	});

	ranking = await response.json();
	rankingList.innerHTML = "";
	// only get countries with vote counts from back
	ranking.forEach((score) => {
		const rankingElement = document.createElement("li");
		rankingElement.textContent = `${score.country}: Performance: ${score.mean_performance} | Meme: ${score.mean_meme}`
		rankingList.appendChild(rankingElement);
	});
});


// functions
const connectSocket = () => {
	const ws = new WebSocket("ws://localhost:5000/ws");

	// notify admin to add to active users list
	ws.onopen = () => {
		const message = {
			type: Events.CONNECTION,
			message: user
		}
		ws.send(JSON.stringify(message));
	}

	ws.onmessage = async ({ data }) => {
		jsonData = await JSON.parse(data);
		datatype = jsonData.type;
		// REFACTOR esto es un poco mierda... Como que al pasar serializado el
		// mensaje en el websocket, hay que volver a parsearlo aqui
		message = await JSON.parse(jsonData.message);

		switch (datatype) {
			// on user connected to the lobby
			case Events.UPDATE_USER_LIST: 
				// REFACTOR only append the new user, not all the users connected
				connectedUsersList.innerHTML = "";
				message.forEach((userConnected) => {
					const userElement = document.createElement("li");
					const color = userConnected.vote ? "green" : "red";
					userElement.style.color = color;
					userElement.textContent = userConnected.name;
					connectedUsersList.appendChild(userElement);
				});
				break;
			case Events.NEXT_COUNTRY:
				currentCountryTitle.innerHTML = `Pais actual: ${message.name}`;
		}

	}

}

const refreshRanking = () => {}
