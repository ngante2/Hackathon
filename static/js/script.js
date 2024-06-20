async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (!userInput) return;

    // Display user's message
    const chatBox = document.getElementById('chat-box');
    const userMessage = document.createElement('p');
    userMessage.className = 'user-message';
    userMessage.innerText = userInput;
    chatBox.appendChild(userMessage);
    document.getElementById('user-input').value = '';

    // Send user's message to the backend
    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    });

    const data = await response.json();

    // Display bot's response as HTML
    const botMessage = document.createElement('div');
    botMessage.className = 'bot-response';
    botMessage.innerHTML = data.response;  // Use innerHTML to render HTML content
    chatBox.appendChild(botMessage);

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;
}
