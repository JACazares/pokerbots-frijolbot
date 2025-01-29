import sys
import json
from poker_parser.parser_logic import PokerLogParser

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <path_to_gamelog.txt> <path_to_saved_json.json>")
        sys.exit(1)

    filepath = sys.argv[1]
    parser = PokerLogParser()
    data = parser.parse_file(filepath)

    # Write to JSON
    with open(sys.argv[2], "w") as outfile:
        json.dump(data, outfile, indent=2)

    print(f"Parsing complete. Output in {sys.argv[2]}")

if __name__ == "__main__":
    main()