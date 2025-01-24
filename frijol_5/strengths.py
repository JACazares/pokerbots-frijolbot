import eval7 
import numpy as np
import csv
import pandas as pd 
import time
from itertools import combinations

def get_stengths():
    deck = eval7.Deck()
    print(deck)
    matrix=-np.ones([22100, 1326])
    matrix_row=0
    row_headers=[]
    column_headers=['']
    for idx_1, flop1 in enumerate(deck):
        for idx_2, flop2 in enumerate(deck):
            for idx_3, flop3 in enumerate(deck):
                if idx_1<idx_2 and idx_2<idx_3:  #For each flop
                    row_headers.append(str(flop1) + str(flop2) + str(flop3))
                    if idx_3>5:
                        break
                    averages = -np.ones([52, 52])
                    start_time=time.time()
                    for idx_turn, turn in enumerate(deck):
                        for idx_river, river in enumerate(deck):
                            if (idx_turn not in [idx_1, idx_2, idx_3]) and (idx_river not in [idx_1, idx_2, idx_3]) and (idx_turn < idx_river):
                                values = []
                                hole_values = -np.ones([52, 52, 52, 52])
                                for idx_hole1, hole1 in enumerate(deck):
                                    for idx_hole2, hole2 in enumerate(deck):
                                        if idx_hole1<idx_hole2 and (idx_hole1 not in [idx_1, idx_2, idx_3, idx_turn, idx_river]) and (idx_hole2 not in [idx_1, idx_2, idx_3, idx_turn, idx_river]):
                                            value = eval7.evaluate([flop1, flop2, flop3, turn, river, hole1, hole2])
                                            values.append([idx_hole1, idx_hole2, value])
                                values.sort(key = lambda item: item[2])
                                for idx, item in enumerate(values):
                                    hole_values[item[0], item[1], idx_turn, idx_river]=idx
                    print(time.time()-start_time)
                    for idx_hole1, hole1 in enumerate(deck):
                        for idx_hole2, hole2 in enumerate(deck): 
                            if idx_hole1<idx_hole2:
                                order_sum=0
                                order_num=0
                                for idx_turn in range(52):
                                    for idx_river in range(52):
                                        if idx_turn<idx_river and hole_values[idx_hole1, idx_hole2, idx_turn, idx_river]!=-1: 
                                            order_sum+=hole_values[idx_hole1, idx_hole2, idx_turn, idx_river]
                                            order_num+=1
                                if order_num == 0: 
                                    averages[idx_hole1, idx_hole2] = -1
                                else: 
                                    averages[idx_hole1, idx_hole2]=order_sum/order_num
                    triu_avg = np.triu(averages, k=1)
                    flat_triu_av = triu_avg[np.triu_indices_from(triu_avg, k=1)]
                    matrix[matrix_row, :] = flat_triu_av
                    matrix_row +=1
                    print(idx_1, idx_2, idx_3)
        for idx_hole1, hole1 in enumerate(deck):
            for idx_hole2, hole2 in enumerate(deck): 
                if idx_hole1<idx_hole2:
                    column_headers.append(str(hole1) + str(hole2))
        
        with open('strengths.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
    
        # Write the column headers
            writer.writerow(column_headers)
    
        # Write the data rows with row headers
            for i, row in enumerate(matrix):
                writer.writerow([row_headers[i]] + list(row))

get_stengths()