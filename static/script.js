async function analyzePassword() {

    // Get password input value
    const password = document.getElementById('password').value;

    // Send password to Flask backend
    const response = await fetch('/analyze', {

        method: 'POST',

        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            password: password
        })
    });

    // Receive response data
    const data = await response.json();

    // Display password strength
    document.getElementById('strength').innerText =
        `Strength: ${data.strength}`;

    // Display score
    document.getElementById('score').innerText =
        `Score: ${data.score}/5`;

    // Display password reuse message
    document.getElementById('reuse').innerText =
        data.reuse_message;

    // Display generated strong password
    document.getElementById('generated-password').innerText =
        data.generated_password;

    // Display suggestions
    const suggestionsList =
        document.getElementById('suggestions');

    suggestionsList.innerHTML = '';

    data.suggestions.forEach(item => {

        const li = document.createElement('li');

        li.innerText = item;

        suggestionsList.appendChild(li);
    });
}
