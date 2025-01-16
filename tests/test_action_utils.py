import pytest
from frijol_4.action_utils import CheckFold, CheckCall, RaiseCheckCall
from frijol_4.skeleton.actions import FoldAction, CheckAction, CallAction, RaiseAction
from frijol_4.helper_bot import FrijolBot

def test_check_fold_with_check_action(mocker):
    bot = mocker.MagicMock(spec=FrijolBot)
    bot.get_legal_actions.return_value = [CheckAction, FoldAction]

    print(bot.get_legal_actions())
    
    action = CheckFold(bot)
    
    assert isinstance(action, CheckAction)

def test_check_fold_without_check_action(mocker):
    bot = mocker.MagicMock(spec=FrijolBot)
    bot.get_legal_actions.return_value = [FoldAction]
    
    action = CheckFold(bot)
    
    assert isinstance(action, FoldAction)

def test_check_call_with_check_action(mocker):
    bot = mocker.MagicMock(spec=FrijolBot)
    bot.get_legal_actions.return_value = [CheckAction, CallAction]
    
    action = CheckCall(bot)
    
    assert isinstance(action, CheckAction)

def test_check_call_without_check_action(mocker):
    bot = mocker.MagicMock(spec=FrijolBot)
    bot.get_legal_actions.return_value = [CallAction]
    
    action = CheckCall(bot)
    
    assert isinstance(action, CallAction)

def test_raise_check_call_with_raise_action(mocker):
    bot = mocker.MagicMock(spec=FrijolBot)
    bot.get_legal_actions.return_value = [RaiseAction, CheckAction, CallAction]
    bot.get_raise_bounds.return_value = (10, 100)
    
    action = RaiseCheckCall(bot, 50)
    
    assert isinstance(action, RaiseAction)
    assert action.amount == 50

def test_raise_check_call_with_raise_action_above_max(mocker):
    bot = mocker.MagicMock(spec=FrijolBot)
    bot.get_legal_actions.return_value = [RaiseAction, CheckAction, CallAction]
    bot.get_raise_bounds.return_value = (10, 100)
    
    action = RaiseCheckCall(bot, 150)
    
    assert isinstance(action, RaiseAction)
    assert action.amount == 100

def test_raise_check_call_with_raise_action_below_min(mocker):
    bot = mocker.MagicMock(spec=FrijolBot)
    bot.get_legal_actions.return_value = [RaiseAction, CheckAction, CallAction]
    bot.get_raise_bounds.return_value = (10, 100)
    
    action = RaiseCheckCall(bot, 5)
    
    assert isinstance(action, RaiseAction)
    assert action.amount == 10

def test_raise_check_call_without_raise_action(mocker):
    bot = mocker.MagicMock(spec=FrijolBot)
    bot.get_legal_actions.return_value = [CheckAction, CallAction]
    
    action = RaiseCheckCall(bot, 50)
    
    assert isinstance(action, CheckAction)

def test_raise_check_call_with_floating_point_raise(mocker):
    bot = mocker.MagicMock(spec=FrijolBot)
    bot.get_legal_actions.return_value = [RaiseAction, CheckAction, CallAction]
    bot.get_raise_bounds.return_value = (10, 100)
    
    action = RaiseCheckCall(bot, 25.75)
    
    assert isinstance(action, RaiseAction)
    assert isinstance(action.amount, int)
    assert action.amount == 25
