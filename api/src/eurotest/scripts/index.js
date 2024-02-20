// TODO 
// - [ ] Create scripts by domain

// globals
const Events = {
	CONNECTION: "connect",
	UPDATE_USER_LIST: "update-user-list",
}

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
const userP = document.getElementById("user-p");


// events
loginButton.addEventListener("click", () => {
	// TODO 
	// - [ ] Can't be empty
	// - [ ] Try catch this boi or get errors from the websocket connection
	connectSocket(userInput.value);

	// Update the user connected
	userP.innerText = userInput.value

	// Clear the inputs if the connection is accepted
	userInput.value = "";
	loginButton.disabled = true;
	userInput.disbled = true;
});

// functions
const connectSocket = (userName) => {
	const ws = new WebSocket("ws://localhost:5000/ws");

	// notify admin to add to active users list
	ws.onopen = () => {
	  ws.send(JSON.stringify({type: Events.CONNECTION, message: userName}));
	}

	ws.onmessage = ({ data }) => {
		jsonData = JSON.parse(data);
		datatype = jsonData.type
		message = jsonData.message

		switch (datatype) {
			case Events.UPDATE_USER_LIST: 
				// REFACTOR only append the new user, not all the users connected
				connectedUsersList.innerHTML = "";
				message.forEach((userName) => {
						const user = document.createElement("li");
						user.textContent = userName;
						connectedUsersList.appendChild(user);
				});
		}

	}

}

const vote = () => {}

const refreshRanking = () => {}

