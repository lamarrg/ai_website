document.getElementById('ask-btn').addEventListener('click', function() {
    askQuestion();
});

document.getElementById('question').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();  // Prevent the default action (form submission)
        askQuestion();
    }
});

function askQuestion() {
    const question = document.getElementById('question').value;

    if (question) {
        // Hide the suggestion questions immediately
        document.querySelector('.question-container').classList.add('hidden');

        fetch('/ask_ollama', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            document.getElementById('response-container').innerHTML = `<p>${data.response}</p>`;
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('response-container').innerHTML = `<p>Error: ${error.message}</p>`;
        });
    } else {
        document.getElementById('response-container').innerHTML = "<p>Please enter a question.</p>";
    }
}