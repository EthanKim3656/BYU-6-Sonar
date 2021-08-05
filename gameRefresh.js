// Check if players have chosen sonar 
// counts every 5 seconds
let int;
int = setInterval(() => {

	// Send 'GET' request to '/game'
	const xhr = new XMLHttpRequest();
	xhr.open('GET', '/game');
	xhr.onload = () => {
		const {response} = xhr;
			clearInterval(int);
			window.location.reload();
	};
	xhr.send();
}, 5000);

// No script tags,
// that's HTML