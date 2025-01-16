def generate_hole_card_strengths(output_file, iters=200):
    """
    Generates the strength for each pair of hole cards and outputs a CSV file.
    """
    rank_combinations = []

    # Generate all unique pairs of hole cards
    for i, rank1 in enumerate(constants.ranks):
        for rank2 in constants.ranks[i:]:
            for bounty in constants.ranks:
                if rank1 == rank2:
                    # Pairs (off suit, obviously)
                    rank_combinations.append((rank1 + "s", rank2 + "h", bounty))
                else:
                    # Suited combinations
                    rank_combinations.append((rank1 + "s", rank2 + "s", bounty))

                    # Offsuit combinations
                    rank_combinations.append((rank1 + "s", rank2 + "h", bounty))

    # Evaluate the strength of each pair
    mock_bot = FrijolBot()
    mock_bot.opponent_bounty_distribution = np.ones(13) / 13

    results = []
    for combo in tqdm(rank_combinations):
        strength = estimate_strength(combo[:2], iters=iters, my_bounty=combo[2])
        results.append(
            {"C1": combo[0], "C2": combo[1], "Bounty": combo[2], "Strength": strength}
        )

    # Sort by strength
    results.sort(key=lambda x: x["Strength"], reverse=True)

    # Write to CSV
    with open(output_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["C1", "C2", "Bounty", "Strength"])
        writer.writeheader()
        writer.writerows(results)

    print(f"CSV file '{output_file}' generated successfully!")