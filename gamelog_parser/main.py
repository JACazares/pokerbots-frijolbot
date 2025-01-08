import sys
import json
from poker_parser.parser_logic import PokerLogParser

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_gamelog.txt>")
        sys.exit(1)

    filepath = sys.argv[1]
    parser = PokerLogParser()
    data = parser.parse_file(filepath)

    # Write to JSON
    with open("gamelog_enhanced.json", "w") as outfile:
        json.dump(data, outfile, indent=2)

    print("Parsing complete. Output in gamelog_enhanced.json")

if __name__ == "__main__":
    main()