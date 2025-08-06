from flask import Flask, request, Response
from openai import OpenAI
from dotenv import load_dotenv
from collections import defaultdict
import time
import os

load_dotenv()

# Constants
SESSION_TIMEOUT = 15 * 60  # 15 minutes
MAX_MESSAGES = 20  # Prevent message list from getting too long

# In-memory session store
user_sessions = defaultdict(lambda: {"messages": [], "last_seen": time.time()})

# Setup OpenAI with environment variable
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from the Consulate Bot 👋"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.form
    sender = data.get("From", "")
    user_message = data.get("Body", "")
    now = time.time()

    # Reset session if it timed out
    if now - user_sessions[sender]["last_seen"] > SESSION_TIMEOUT:
        user_sessions[sender]["messages"] = []

    user_sessions[sender]["last_seen"] = now

    # Load guide and initialize session if it's new
    if not user_sessions[sender]["messages"]:
        guide_text = open("guide.txt", "r", encoding="utf-8").read()
        user_sessions[sender]["messages"].append({
            "role": "system",
            "content": f"You are a helpful consulate assistant. Only answer based on the following guide:\n\n{guide_text}"
        })

    # Append user message
    user_sessions[sender]["messages"].append({"role": "user", "content": user_message})

    # ✅ Anti-spam: trim history if too long
    if len(user_sessions[sender]["messages"]) > MAX_MESSAGES:
        user_sessions[sender]["messages"] = [user_sessions[sender]["messages"][0]] + user_sessions[sender]["messages"][-(MAX_MESSAGES - 1):]

    try:
        # Call OpenAI
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=user_sessions[sender]["messages"]
        )

        reply = response.choices[0].message.content.strip()

        # Save bot response
        user_sessions[sender]["messages"].append({"role": "assistant", "content": reply})

        # Optional fallback
        if "I'm not sure" in reply or "I cannot find" in reply:
            reply += "\n\n📄 Sorry, this info doesn't appear in the official guide. Please contact the consulate directly."

    except Exception as e:
        print(f"OpenAI Error: {e}")
        reply = "⚠️ Sorry, there was an error processing your request."

    # TwiML XML Response
    twiml = f"""
        <Response>
            <Message>{reply}</Message>
        </Response>
    """
    return Response(twiml, mimetype='application/xml')
