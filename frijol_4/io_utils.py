import csv
import numpy as np
import eval7

def read_csv_table(filename):
    """Reads a CSV file and returns a dictionary mapping a tuple of the first columns to the last column."""
    
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        table = {tuple(row[:-1]): row[-1] for row in reader}

    return table

def read_starting_ranges(filename):
    with open('my_starting_ranges.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        rowlist=[]
        for idx, row in enumerate(reader):
            if idx % 15 != 0 and idx%15 != 1:
                rowlist.append([float(num) for num in row[1:14]]+[float(num) for num in row[15:]])
        BTN_opening_range=np.array(rowlist[0:13])
        BB_call_range_vs_open=np.array(rowlist[13:26])
        BB_3bet_range_vs_open=np.array(rowlist[26:39])
        BB_fold_range_vs_open=np.array(rowlist[39:52])
        BTN_call_range_vs_3bet=np.array(rowlist[52:65])
        BTN_4bet_range_vs_3bet=np.array(rowlist[65:78])
        BTN_fold_range_vs_3bet=np.array(rowlist[78:91])
        BB_call_range_vs_4bet=np.array(rowlist[91:104])
        BB_5bet_range_vs_4bet=np.array(rowlist[104:119])
    return BTN_opening_range, BB_call_range_vs_open, BB_3bet_range_vs_open, BTN_call_range_vs_3bet, BTN_4bet_range_vs_3bet, BB_call_range_vs_4bet, BB_5bet_range_vs_4bet

def simplify_hole(hole):
    '''
        Given a pair of hole cards, returns the row and column in a traditional poker ranges table
    '''
    hole_cards=[eval7.Card(s) for s in hole]
    if hole_cards[0].suit==hole_cards[1].suit: #Suited
        sortedcards=sorted(hole_cards, key=lambda x : x.rank)
        row=12-sortedcards[1].rank
        column=12-sortedcards[0].rank
    else:
        sortedcards=sorted(hole_cards, key=lambda x : x.rank)
        row=12-sortedcards[0].rank
        column=12-sortedcards[1].rank
    return row, column



if __name__=="__main__":
    print(simplify_hole(['Ac', '2s']))
    BTN_opening_range, BB_call_range_vs_open, BB_3bet_range_vs_open, BTN_call_range_vs_3bet, BTN_4bet_range_vs_3bet, BB_call_range_vs_4bet, BB_5bet_range_vs_4bet = read_starting_ranges("my_starting_ranges.csv")
    print(np.shape(BTN_call_range_vs_3bet))
    print(np.shape(BB_call_range_vs_open))
    print(np.shape(BB_call_range_vs_4bet))
    