# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
import json

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
    """
    Return a simplified array of objects: 
    { roundNumber: X, awardA: Y }, to plot Round # vs. A's Winnings.
    """
    all_data = load_parsed_data()  # e.g. a list of RoundData dicts
    # Suppose each item is like:
    #   {
    #     "round_number": 1,
    #     "awards": {"A": 22, "B": -22},
    #     ...
    #   }
    # We'll transform it into a simpler format
    transformed = [
        {
            "roundNumber": rd["round_number"],
            "awardA": rd["winning_counts_end_round"]["A"]
        }
        for rd in all_data
    ]
    return jsonify(transformed)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5050)