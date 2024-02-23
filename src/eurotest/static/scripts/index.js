// REQUIREMENTS 
// - [ ] Admin buttons only visible for admin users
// - [ ] Cooldown for next_country button after clicked

// REFACTOR
// - [ ] Create scripts by domain

const Events = {
	CONNECTION: "connect",
	UPDATE_USER_LIST: "update-user-list",
    NEXT_COUNTRY: "next-country",
};

// Global State
let user = {};
let country = "es";
let ws_connection;

// components
// buttons
const loginButton = document.getElementById("login-button");
const voteButton = document.getElementById("vote-button");
const refreshRankingButton = document.getElementById("refresh-ranking-button");
const nextCountryButton = document.getElementById("next-country-button");

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
loginButton.addEventListener("click", async () => {
	// TODO 
	// - [ ] Can't be empty
	// - [ ] Try catch this boi or get errors from the websocket connection
	//

	user = {
		name: userInput.value,
		vote: false,
	};

	// REFACTOR try catch all fetch bois
	response = await fetch("http://localhost:5000/login", {
		method: "POST",
		mode: "cors",
		body: JSON.stringify(user),
		headers: {
			"Content-type": "application/json; charset=UTF-8"
		}
	});

	// TODO client need to get error messages 
	if (response.status !== 200) {
		console.error("Error");
		console.error(response);
	}

	body = await response.json();

	user = body.user;
	country = body.country;

	connectSocket(user);

	// Update the user connected
	userP.innerText = userInput.value

	// Clear the inputs if the connection is accepted
	userInput.value = "";
	loginButton.disabled = true;
	userInput.disbled = true;

	// Add current country label
	currentCountryTitle.innerHTML = `Pais actual: ${country}`;
});


voteButton.addEventListener("click", () => {
	fetch("http://localhost:5000/vote", {
		method: "POST",
		mode: "cors",
		// REFACTOR all in the body or change endpoint /{country}/vote/
		body: JSON.stringify({
			username: user.name,
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


nextCountryButton.addEventListener("click", () => {
	// TODO dont make this button visible if theres no websocket connection
	ws_connection.send(JSON.stringify({
		"type": Events.NEXT_COUNTRY,
		// only need the type
		"message": ""
	}));
});


// functions
const connectSocket = () => {
	const ws = new WebSocket("ws://localhost:5000/ws");
	// REFACTOR, use the same ws object, not ws_connection
	ws_connection = ws;

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

