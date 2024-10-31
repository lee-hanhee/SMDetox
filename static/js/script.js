let userClass = null;

async function makePrediction() {
    const appUsage = document.getElementById("appUsage").value;
    const screenTime = document.getElementById("screenTime").value;
    const dataUsage = document.getElementById("dataUsage").value;

    const data = {
        "App Usage Time": parseInt(appUsage),
        "Screen On Time": parseFloat(screenTime),
        "Data Usage": parseInt(dataUsage)
    };

    const response = await fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();
    if (response.ok) {
        userClass = result.predicted_class;
        document.getElementById("result").innerText = `Predicted Class: ${userClass}`;
        startChatbot();
    } else {
        document.getElementById("result").innerText = `Error: ${result.error}`;
    }
}

function startChatbot() {
    document.getElementById("prediction-section").style.display = "none";
    document.getElementById("chatbot-section").style.display = "block";
    displayMessage("Bot", "Hello! How can I help you with your screen time?");
}

async function sendMessage() {
    const userMessage = document.getElementById("userMessage").value;
    displayMessage("You", userMessage);

    const response = await fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_class: userClass, message: userMessage })
    });

    const result = await response.json();
    displayMessage("Bot", result.response);
}

function displayMessage(sender, message) {
    const chatLog = document.getElementById("chat-log");
    const newMessage = document.createElement("p");
    newMessage.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatLog.appendChild(newMessage);
    document.getElementById("userMessage").value = "";
}

async function setReminder() {
    const interval = prompt("Enter the reminder interval in minutes:");
    if (interval && !isNaN(interval)) {
        const reminderMessage = `remind me every ${interval} minutes`;

        const response = await fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_class: userClass, message: reminderMessage })
        });

        const result = await response.json();
        displayMessage("Bot", result.response);
    } else {
        alert("Please enter a valid number for the interval.");
    }
}

async function requestEducationalContent() {
    const response = await fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_class: userClass, message: "educational content" })
    });

    const result = await response.json();
    displayMessage("Bot", result.response);
}
