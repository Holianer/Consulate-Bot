from flask import Flask, request, Response
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
    # Twilio sends x-www-form-urlencoded data
    data = request.form
    user_message = data.get("Body", "")
    sender = data.get("From", "")

    print(f"User ({sender}) said: {user_message}")

    # Load guide
    try:
        guide_text = open("guide.txt", "r", encoding="utf-8").read()
    except Exception as e:
        print(f"Error loading guide: {e}")
        return Response("<Response><Message>Error loading guide.</Message></Response>", mimetype='application/xml')

    # OpenAI chat
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are a consulate assistant. Only answer based on the following guide:\n\n{guide_text}"},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()

        # Optional fallback message
        if "I'm not sure" in reply or "I cannot find" in reply:
            reply += "\n\n📄 Sorry, this info doesn't appear in the official guide. Please contact the consulate directly."

    except Exception as e:
        print(f"OpenAI Error: {e}")
        reply = "⚠️ Sorry, there was an error processing your request."

    # Return TwiML
    twiml = f"""
        <Response>
            <Message>{reply}</Message>
        </Response>
    """
    return Response(twiml, mimetype='application/xml')
