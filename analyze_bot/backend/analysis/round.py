from flask import jsonify

def get_round_data(all_data, street_filter):
    # Filter data based on the last street
    if street_filter not in ["all", "showdown"]:
        all_data = [
            rd
            for rd in all_data
            if rd["streets"][-1]["street_name"].lower() == street_filter and not rd["showdown"]["went_to_showdown"]
        ]
    elif street_filter == "showdown":
        all_data = [rd for rd in all_data if rd["showdown"]["went_to_showdown"]]

    # Transform data for plotting
    transformed = [
        {
            "roundNumber": rd["round_number"],
            "awardA": rd["awards"]["A"],
        }
        for rd in all_data
    ]

    running_sum = 0
    for item in transformed:
        running_sum += item["awardA"]
        item["awardA"] = running_sum

    return jsonify(transformed)
