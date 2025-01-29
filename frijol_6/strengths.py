import eval7
import numpy as np
import csv
import itertools
import time
from tqdm import tqdm

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

def get_strengths_2():
    deck = eval7.Deck()
    N = 52

    holes = []
    for hole1 in range(N):
        for hole2 in range(hole1 + 1, N):
            holes.append((hole1, hole2))

    with open('strengths.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = ['Flop']
        for hole1, hole2 in holes:
            header.append(f"{deck[hole1]}{deck[hole2]}")
        writer.writerow(header)
        csvfile.flush()   # ensure the header is saved

        pbar = tqdm(total=22100)
        counter = 0
        for flop1 in range(N):
            flop1_card = deck[flop1]
            for flop2 in range(flop1 + 1, N):
                flop2_card = deck[flop2]
                for flop3 in range(flop2 + 1, N):
                    pbar.update(1)

                    flop3_card = deck[flop3]
                    strengths = {}
                    
                    hole_indexes = {}
                    for turn in range(N):
                        if turn in [flop1, flop2, flop3]:
                            continue
                        turn_card = deck[turn]
                        for river in range(turn + 1, N):
                            if river in [flop1, flop2, flop3]:
                                continue
                            river_card = deck[river]
                                
                            values = []
                            for hole1 in range(N):
                                if hole1 in [flop1, flop2, flop3, turn, river]:
                                    continue
                                hole1_card = deck[hole1]
                                for hole2 in range(hole1 + 1, N):
                                    if hole2 in [flop1, flop2, flop3, turn, river]:
                                        continue
                                    hole2_card = deck[hole2]

                                    value = eval7.evaluate([flop1_card, flop2_card, flop3_card, turn_card, river_card, hole1_card, hole2_card])
                                    values.append([hole1, hole2, value])
                            
                            values = sorted(values, key=lambda x: x[2])
                            for idx, (hole1, hole2, value) in enumerate(values):
                                try:
                                    hole_indexes[(hole1, hole2)].append(idx)
                                except:
                                    hole_indexes[(hole1, hole2)] = [idx]
                    
                    for ((hole1, hole2), indices) in hole_indexes.items():
                        avg_index = np.average(indices)/1326 if indices else -1
                        # Store the average index for the hand combination
                        strengths[(hole1, hole2)] = avg_index
                    
                    # Write the strengths to a CSV file
                    row = [f"{deck[flop1]}{deck[flop2]}{deck[flop3]}"]
                    for hole1, hole2 in holes:
                        avg_strength = strengths.get((hole1, hole2), -1)
                        row.append(f"{avg_strength:.4f}")
                    writer.writerow(row)

                csvfile.flush()

if __name__ == "__main__":
    get_strengths_2()