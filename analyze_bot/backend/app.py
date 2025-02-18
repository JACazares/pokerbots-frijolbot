# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from analysis.round import get_round_data

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://10.29.251.249:3000"}})

# Suppose you have a function that reads your parsed data (JSON or DB)
def load_parsed_data():
    # For demonstration, maybe read from a local file
    with open("data/parsed.json", "r") as f:
        data = json.load(f)
    return data  # This data might be an array of rounds

@app.route("/analysis/rounds", methods=["GET"])
def get_rounds():
    # Get all parsed data
    all_data = load_parsed_data()

    # Get the `street` filter from the query parameters
    street_filter = request.args.get("street", "ALL").lower()

    return get_round_data(all_data, street_filter)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5050)