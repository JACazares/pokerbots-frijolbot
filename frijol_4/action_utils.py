from frijol_4.skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from helper_bot import FrijolBot

def CheckFold(bot: FrijolBot):
    """
    Determines the appropriate action (Check or Fold) based on the available legal actions.

    Args:
        bot (FrijolBot): The current bot in the game, which includes the legal actions.

    Returns:
        Action: Returns a CheckAction if it is in the list of legal actions, otherwise returns a FoldAction.
    """
    print(CheckAction)
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
        return RaiseAction(int(raise_amount))

    return CheckCall(bot)
