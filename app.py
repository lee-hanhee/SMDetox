from flask import Flask, request, jsonify, render_template
import torch
import torch.nn as nn
import numpy as np
import joblib
import os
import threading
import time

MODEL_PATH = os.path.join('models', 'best_model.pth')
SCALER_PATH = os.path.join('models', 'scaler.pkl')

# Load scaler and model
scaler = joblib.load(SCALER_PATH)

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(3, 64)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(64, 32)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(32, 5)

    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x

model = Net()
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

app = Flask(__name__)

# Global store for reminder intervals
user_reminders = {}

# Educational content
EDUCATIONAL_CONTENT = [
    "Did you know? Taking breaks from social media helps reduce stress and improve focus!",
    "Pro tip: Consider turning off notifications to minimize distractions.",
    "Try a new hobby offline, like reading or painting, as an alternative to screen time.",
    "Remember: Quality time spent offline can enhance your overall mental well-being."
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    required_fields = ["App Usage Time", "Screen On Time", "Data Usage"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Request must contain App Usage Time, Screen On Time, and Data Usage"}), 400

    features = np.array([[data["App Usage Time"], data["Screen On Time"], data["Data Usage"]]])
    features = scaler.transform(features)
    features_tensor = torch.tensor(features, dtype=torch.float32)

    with torch.no_grad():
        output = model(features_tensor)
        _, predicted_class = torch.max(output, 1)

    user_class = int(predicted_class.item() + 1)
    return jsonify({"predicted_class": user_class})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_class = request.json.get("user_class")
    user_message = request.json.get("message").lower()
    response = get_chatbot_response(user_class, user_message)
    return jsonify({"response": response})

def get_chatbot_response(user_class, message):
    # Define responses for each user class
    responses = {
        1: "Keep up the good work maintaining low screen time!",
        2: "Great balance! Would you like some tips to improve further?",
        3: "Let's set a goal to reduce screen time by 10% this week. Sound good?",
        4: "It seems you’re spending quite a bit of time on your device. How about some break reminders?",
        5: "Your usage is high. I recommend setting stricter goals and taking regular breaks."
    }
    
    # Add additional custom responses
    if "remind me every" in message:
        interval = int(message.split()[-1])  # Assume user specifies in minutes
        user_reminders[user_class] = interval
        start_reminder_thread(user_class, interval)
        return f"Reminder set! I’ll remind you every {interval} minutes to take a break from social media."

    elif "educational content" in message or "tips" in message:
        return np.random.choice(EDUCATIONAL_CONTENT)

    # Default response based on class
    return responses.get(user_class, "I'm here to help with personalized recommendations. Let me know what you need!")

# Background thread for sending reminders
def send_reminder(user_class):
    if user_class in user_reminders:
        print(f"Reminder for user class {user_class}: Take a break from social media!")  # In production, use notifications

def reminder_thread(user_class, interval):
    while user_class in user_reminders:
        time.sleep(interval * 60)  # Convert interval to seconds
        send_reminder(user_class)

def start_reminder_thread(user_class, interval):
    thread = threading.Thread(target=reminder_thread, args=(user_class, interval))
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    app.run(debug=True)