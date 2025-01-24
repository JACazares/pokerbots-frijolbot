import eval7
import numpy as np
import csv
import itertools
import time



def get_strengths():
    deck = eval7.Deck()
    matrix = -np.ones([22100, 1326])
    matrix_row = 0
    row_headers = []
    column_headers = ['']
    counter=0

    # Generate all 3-card combinations for flops
    flops = list(itertools.combinations(deck, 3))
    for flop in flops: 
        row_headers.append("".join(map(str, flop)))
    for flop in flops:
        counter+=1
        averages = -np.ones([52,52])
        start_time = time.time()

        # Generate all valid turn and river combinations
        remaining_cards = set(deck) - set(flop)
        turn_river_combinations = list(itertools.combinations(remaining_cards, 2))

        # Precompute hand rankings
        hole_values = -np.ones([52, 52, 1326])
        for idx_tr, (turn, river) in enumerate(turn_river_combinations):
            values = []
            remaining_after_tr = remaining_cards - {turn, river}

            # Generate all valid hole card combinations
            hole_combinations = list(itertools.combinations(remaining_after_tr, 2))
            for idx_hc, (hole1, hole2) in enumerate(hole_combinations):
                value = eval7.evaluate(list(flop)+[turn, river, hole1, hole2])  
                values.append((hole1, hole2, value))

            # Sort and rank hole card values
            values.sort(key=lambda item: item[2])
            list_deck=list(deck)
            for rank, (hole1, hole2, _) in enumerate(values):
                hole_values[list_deck.index(hole1), list_deck.index(hole2), idx_tr] = rank

        print(f"Flop {str(flop[0]) + str(flop[1]) + str(flop[2])} processed in {time.time() - start_time:.2f} seconds.")

        # Calculate averages for each pair of hole cards
        for idx_hole1, hole1 in enumerate(deck):
            for idx_hole2, hole2 in enumerate(deck):
                if idx_hole1 < idx_hole2:
                    rankings = hole_values[idx_hole1, idx_hole2, :]
                    valid_rankings = rankings[rankings != -1]
                    if len(valid_rankings) > 0:
                        averages[idx_hole1, idx_hole2] = np.mean(valid_rankings)/1326

        # Flatten the upper triangle of the averages matrix
        triu_avg = np.triu(averages, k=1)
        flat_triu_avg = triu_avg[np.triu_indices_from(triu_avg, k=1)]
        matrix[matrix_row, :] = flat_triu_avg
        matrix_row += 1

    # Generate column headers
        if counter %5 ==0:
            for idx_hole1, hole1 in enumerate(deck):
                for idx_hole2, hole2 in enumerate(deck):
                    if idx_hole1 < idx_hole2:
                        column_headers.append(f"{hole1}{hole2}")

        # Save the matrix to a CSV file
            with open('strengths.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(column_headers)  # Write column headers
                for i, row in enumerate(matrix):  # Write data rows with row headers
                    writer.writerow([row_headers[i]] + list(row))


get_strengths()