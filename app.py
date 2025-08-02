from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Setup OpenAI with environment variable
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from the Consulate Bot 👋"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.form  # <-- Twilio sends as form data, not JSON!
    user_message = data.get("Body", "")  # WhatsApp message body
    sender = data.get("From", "")  # Optional: who sent the message

    print(f"User ({sender}) said: {user_message}")

    # OpenAI Chat Completion
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )

    reply = response.choices[0].message.content
    print(f"Bot says: {reply}")

    # Twilio needs a specific XML (TwiML) format in response
    return f"""
        <Response>
            <Message>{reply}</Message>
        </Response>
    """, 200, {'Content-Type': 'application/xml'}


