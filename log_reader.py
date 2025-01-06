# import re
# from python_skeleton.skeleton.states import GameState, TerminalState, RoundState

# STARTING_STACK = 400

# def return_states_A():
#     pass

# def read_gamelog_A(filename):
#     with open(filename) as f:
#         raw_data_lines = f.readlines()

#     new_round_pattern = re.compile("Round #([0-9]*), ([A,B]) \((-?[0-9]*)\), ([A,B]) \((-?[0-9]*)\)")
#     hole_pattern = re.compile("([A-B]) dealt \[(.*)\]")
#     board_pattern = re.compile("(Flop|Turn|River|Run) \[(.*)\], ([A,B]) \((-?[0-9]*)\), ([A,B]) \((-?[0-9]*)\)")
#     check_pattern = re.compile("([A,B]) checks")
#     call_pattern = re.compile("([A,B]) calls")
#     fold_pattern = re.compile("([A,B]) folds")
#     raise_pattern = re.compile("([A-B]) (bets|raises to) ([0-9]*)")

#     player = {"A": 0, "B": 1}
    
#     small_blind_player = 0
#     big_blind_player = 1
#     curr_player = 0

#     game_state_A = GameState()
#     round_state_A = RoundState()

#     game_state_A.bankroll = 0
#     game_state_A.round_num = 0

#     active = 0
#     round_state_A.hands = [[], []]
#     round_state_A.deck = []
#     round_state_A.street = 0
#     round_state_A.pips = [0, 0]
#     contribution = [0, 0]
#     round_state_A.stacks = [STARTING_STACK, STARTING_STACK]

#     for line in raw_data_lines:
#         new_round_search = re.search(new_round_pattern, line)
#         hole_search = re.search(hole_pattern, line)
#         board_search = re.search(board_pattern, line)
#         check_search = re.search(check_pattern, line)
#         call_search = re.search(call_pattern, line)
#         fold_search = re.search(fold_pattern, line)
#         raise_search = re.search(raise_pattern, line)

#         # Basic setup 
#         if new_round_search:
#             if new_round_search.group(2) == 'A':
#                 game_state_A.bankroll = new_round_search.group(3)
#             elif new_round_search.group(4) == 'A':
#                 game_state_A.bankroll = new_round_search.group(5)
#             game_state_A.round_num = new_round_search.group(1)

#             if new_round_search.group(2) == 'A':
#                 active = 0
#             elif new_round_search.group(4) == 'A':
#                 active = 1

#             round_state_A.hands = [[], []]
#             round_state_A.deck = []
#             round_state_A.street = 0
#             round_state_A.pips[0] = 1
#             round_state_A.pips[0] = 2
#             contribution = [1, 2]
#             round_state_A.stacks[0] = STARTING_STACK - contribution[0]
#             round_state_A.stacks[1] = STARTING_STACK - contribution[1]

#         elif hole_search:
#             if hole_search.group(1) == 'A':
#                 round_state_A.hands[active] = (hole_search.group(2)).split(' ')
        
#         elif board_search:
#             round_state_A.deck = (board_search.group(2)).split(' ')
#             round_state_A.street = len(round_state_A.deck)
#             round_state_A.pips = [0, 0]
#             contribution = [int(board_search.group(4)), int(board_search.group(6))]
#             round_state_A.stacks[0] = STARTING_STACK - contribution[0]
#             round_state_A.stacks[1] = STARTING_STACK - contribution[1]

#         elif call_search:
#             curr_player = call_search.group(1)
#             if curr_player == 'A':
#                 round_state_A.pips[active] = round_state_A.pips[1 - active]
#                 contribution[active] = contribution[1 - active]
#             elif curr_player == 'B':
#                 round_state_A.pips[1 - active] = round_state_A.pips[active]
#                 contribution[1 - active] = contribution[active]

#             round_state_A.stacks[0] = STARTING_STACK - contribution[0]
#             round_state_A.stacks[1] = STARTING_STACK - contribution[1]

#         elif check_search:
#             curr_player = check_search.group(1)

#             return_states_A()

#         elif fold_search:
#             curr_player = fold_search.group(1)

#             return_states_A()

#         elif raise_search:
#             curr_player = raise_search.group(1)

#             if curr_player == 'A':
#                 round_state_A.pips[active] = int(raise_search.group(3))
#                 contribution[active] 
#             elif curr_player == 'B':
#                 round_state_A.pips[1 - active] = round_state_A.pips[active]
#                 contribution[1 - active] = contribution[active]

#             round_state_A.stacks[0] = STARTING_STACK - contribution[0]
#             round_state_A.stacks[1] = STARTING_STACK - contribution[1]
#             pips[curr_player] = int(raise_search.group(3))
#             # Comentar esta linea si contribution != pips + stack
#             contribution[curr_player] += pips[curr_player]
#             stack[curr_player] = STARTING_STACK - contribution[curr_player]

#             return_states_A()


# if __name__ == "__main__":
#     read_gamelog_A("gamelog.txt")