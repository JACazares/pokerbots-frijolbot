import random
import numpy as np
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from helper_bot import FrijolBot
import eval7

def CheckFold(bot: FrijolBot):
    """
    Determines the appropriate action (Check or Fold) based on the available legal actions.

    Args:
        bot (FrijolBot): The current bot in the game, which includes the legal actions.

    Returns:
        Action: Returns a CheckAction if it is in the list of legal actions, otherwise returns a FoldAction.
    """
    if CheckAction in bot.get_legal_actions():
        return CheckAction()
    return FoldAction()


def CheckCall(bot: FrijolBot):
    """
    Determines whether to perform a check or call action based on the available legal actions.

    Args:
        bot (FrijolBot): The current bot in the game, which includes the legal actions.

    Returns:
        Action: The CheckAction if it is in the list of legal actions, otherwise the CallAction.
    """
    if CheckAction in bot.get_legal_actions():
        return CheckAction()

    return CallAction()


def RaiseCheckCall(bot: FrijolBot, raise_amount: float):
    """
    Determines the appropriate action (Raise, Check, or Call) based on the given parameters.

    Args:
        bot (FrijolBot): The current bot in the game, which includes the legal actions.
        raise_amount (float): The amount to raise by.

    Returns:
        Action: A RaiseAction with the appropriate raise amount if raising is legal, 
                otherwise a CheckCall action.
    """
    if RaiseAction in bot.get_legal_actions():
        min_raise, max_raise = bot.get_raise_bounds()
        raise_amount = min(raise_amount, max_raise)
        raise_amount = max(raise_amount, min_raise)
        bot.previously_raised = True
        return RaiseAction(int(raise_amount))

    return CheckCall(bot)


def mixed_strategy(bot: FrijolBot, fold_probability: float, call_probability: float, raise_amount: float = 1):
    """
    Does a randomized selection of actions depending on input probabilities

    Inputs:
    legal actions: The set of legal actions
    my_pip: Your total contribution of chips this betting round
    round_state: Round state object from RoundState
    checkfold: The probability with which it will choose check-fold action
    checkcall: The probabiity with which it will choose check-call action
    1-checkfold-checkcall will be the probability of raising.
    raise_amount: How much it will raise given that it chooses raise.

    Output: An action
    """

    action_probability = random.random()

    if action_probability < fold_probability:
        return CheckFold(bot)
    elif action_probability < fold_probability + call_probability:
        return CheckCall(bot)

    min_raise, max_rasie = bot.get_raise_bounds()
    raise_amount = min(max(raise_amount, min_raise), max_rasie)
    std_dev = (raise_amount - min_raise) / 10
    raise_amount = np.random.normal(raise_amount, std_dev)

    return RaiseCheckCall(bot, raise_amount)