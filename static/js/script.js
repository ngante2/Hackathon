"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
function handleDropdownChange() {
    const dropdown = document.getElementById('dropdown');
    const selectedValue = dropdown.value;
    console.log(`Selected value: ${selectedValue}`);
    // You can add any additional logic here, such as sending the selected value to the backend
}
function sendMessage() {
    return __awaiter(this, void 0, void 0, function* () {
        const userInput = document.getElementById('user-input').value;
        const dropdown = document.getElementById('dropdown');
        const selectedValue = dropdown.value;
        if (!userInput)
            return;
        // Display user's message
        const chatBox = document.getElementById('chat-box');
        const userMessage = document.createElement('p');
        userMessage.className = 'user-message';
        userMessage.innerText = userInput;
        chatBox.appendChild(userMessage);
        document.getElementById('user-input').value = '';
        // Send user's message to the backend
        const response = yield fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput, dropdown: selectedValue })
        });
        const data = yield response.json();
        // Display bot's response as HTML
        const botMessage = document.createElement('div');
        botMessage.className = 'bot-response';
        botMessage.innerHTML = data.response; // Use innerHTML to render HTML content
        chatBox.appendChild(botMessage);
        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}
