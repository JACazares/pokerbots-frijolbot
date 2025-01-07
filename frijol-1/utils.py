import scipy.special
import math
import numpy as np

def compute_checkfold_winprob(rounds_left, bankroll, big_blind):
    bounties_to_win=math.ceil((bankroll-3*rounds_left/2-(rounds_left%2)*(int(big_blind)-0.5))/11)-1
    if bounties_to_win>rounds_left:
        bounties_to_win=rounds_left
    if bounties_to_win<0:
        bounties_to_win=0
    winning_cases=np.arange(bounties_to_win+1)
    success_rate=1-48*47/(52*51)
    probabilities=np.array([scipy.special.comb(rounds_left, case, exact=True) for case in winning_cases])
    probabilities=probabilities*(success_rate**winning_cases)*(1-success_rate)**(rounds_left-winning_cases)
    return np.sum(probabilities)

print(compute_checkfold_winprob(50, 200, False))