from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    user_message = data.get("message", "")

    print(f"User said: {user_message}")

    # Talk to GPT
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}],
    )

    reply = response.choices[0].message.content
    print(f"Bot says: {reply}")

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(port=5000)
