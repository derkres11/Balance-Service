# service.py
from datetime import datetime
from models import Reservation, Transaction
# Temporary storage for user balances
balances = {}
reservations = {}
transactions = []


def deposit(user_id: int, amount: float) -> float:
    """
    Deposit money to a user's account.
    Returns the new balance.
    """
    if user_id not in balances:
        balances[user_id] = 0.0
    balances[user_id] += amount
    return balances[user_id]


def get_balance(user_id: int) -> float:
    """
    Get the current balance of a user.
    Returns 0.0 if the user does not exist.
    """
    return balances.get(user_id, 0.0)


def reserve_funds(request) -> Reservation:
    """
    Reserve money for an order.
    """
    if request.user_id not in balances:
        raise ValueError("User not found")

    if balances[request.user_id] < request.amount:
        raise ValueError("Insufficient balance")

    balances[request.user_id] -= request.amount
    reservation = Reservation(
        user_id=request.user_id,
        service_id=request.service_id,
        order_id=request.order_id,
        amount=request.amount,
        status="reserved"
    )
    reservations[(request.user_id, request.order_id)] = reservation
    return reservation


def recognize_transaction(request) -> Transaction:
    """
    Finalize reserved funds and create a transaction record.
    """
    key = (request.user_id, request.order_id)
    if key not in reservations:
        raise ValueError("Reservation not found")

    reservation = reservations[key]
    if reservation.status != "reserved":
        raise ValueError("Reservation already recognized or cancelled")

    transaction = Transaction(
        user_id=reservation.user_id,
        service_id=reservation.service_id,
        order_id=reservation.order_id,
        amount=reservation.amount,
        timestamp=datetime.now()
    )
    transactions.append(transaction)
    reservation.status = "recognized"

    return transaction