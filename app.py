
import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from anthropic import Anthropic

# SETUP
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# MAIN WEBSITE: ONE IDEA GENERATOR
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "one-idea (5).html")


# SOLO ACTIVITY GENERATOR
@app.route("/api/idea", methods=["POST"])
def create_idea():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Please enter a city."}), 400

        city = data.get("city", "").strip()
        avoid = data.get("avoid", [])

        if not city:
            return jsonify({"error": "Please enter a city."}), 400

        avoidance = ""
        if avoid:
            avoidance = (
                " Do not repeat these already-given ideas: "
                + " | ".join(avoid[-4:])
            )

        prompt = (
            f"Give ONE short, fun, specific thing for a solo traveler "
            f"to do today in {city}. "
            "Maximum 12 words. Casual, upbeat, playful tone. "
            "Must name a real, specific place. "
            "You may add one fitting emoji. "
            "No quotes, no preamble, just the tip."
            + avoidance
            + ' Examples: "Hop the train to Howth and hike the cliffs 🌊" '
            '"Grab strawberries at Borough Market".'
        )

        message = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=60,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        idea = ""

        for block in message.content:
            if block.type == "text":
                idea += block.text

        idea = idea.strip().strip('"').strip("'")

        if not idea:
            return jsonify({
                "error": "Claude returned an empty idea."
            }), 500

        return jsonify({
            "success": True,
            "idea": idea
        })

    except Exception:
        app.logger.exception("Activity generation failed")
        return jsonify({
            "error": "We couldn't generate an idea. Please try again."
        }), 500


# RUN WEBSITE
if __name__ == "__main__":
    app.run(debug=True, port=5000)
