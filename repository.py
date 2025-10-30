# repository.py

# temporary storage
_balances = {}


def get_balance(user_id: int) -> float:
    """Return current balance or 0 if user not exists"""
    return _balances.get(user_id, 0.0)


def update_balance(user_id: int, amount: float) -> float:
    """Update balance and return new value"""
    if user_id not in _balances:
        _balances[user_id] = 0.0
    _balances[user_id] += amount
    return _balances[user_id]
