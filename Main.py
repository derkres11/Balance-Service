from fastapi import FastAPI, HTTPException
from models import DepositRequest, DepositResponse, BalanceResponse, ReserveRequest, Reservation, Transaction
from service import deposit, get_balance, reserve_funds, recognize_transaction
from service import balances, transactions, reservations
from datetime import datetime
from fastapi import Query
import logging


logging.basicConfig(
    filename="balance_service.log",
    level=logging.INFO,          
    format="%(asctime)s - %(levelname)s - %(message)s"
)


app = FastAPI(title="User Balance Service", version="1.0")


@app.post("/deposit", response_model=DepositResponse)
def deposit_endpoint(request: DepositRequest):
    """
    Deposit money to a user's account.
    Validates that the amount is greater than zero.
    """
    if request.user_id not in balances:
        logging.error(f"Deposit failed: User {request.user_id} not found")
        raise HTTPException(status_code=404, detail="User not found") 
           
    new_balance = deposit(request.user_id, request.amount)

    logging.info(f"Deposit successful: User {request.user_id}, Amount {request.amount}, New Balance {new_balance}")

    return DepositResponse(
        user_id=request.user_id,
        new_balance=new_balance,
        message="Deposit successful"
    )


@app.get("/balance/{user_id}", response_model=BalanceResponse)
def balance_endpoint(user_id: int):
    """
    Get current balance for a user.
    Returns 0.0 if the user does not exist.
    """
    balance = get_balance(user_id)
    return BalanceResponse(user_id=user_id, balance=balance)


@app.post("/reserve", response_model=Reservation)
def reserve_endpoint(request: ReserveRequest):
    """
    Money reservation for the transaction.
    """
    if request.user_id not in balances:
        logging.error(f"Reservation failed: User {request.user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    if balances[request.user_id] < request.amount:
        logging.warning(f"Reservation failed: Insufficient balance for user {request.user_id}")
        raise HTTPException(status_code=400, detail="Insufficient balance")

    balances[request.user_id] -= request.amount
    reservation = Reservation(
        user_id=request.user_id,
        service_id=request.service_id,
        order_id=request.order_id,
        amount=request.amount,
        status="reserved"
    )
    reservations[(request.user_id, request.order_id)] = reservation
    logging.info(f"Reservation successful: User {request.user_id}, Order {request.order_id}, Amount {request.amount}")
    return {"message": "Reservation successful", "reservation": reservation}


@app.post("/recognize", response_model=Transaction)
def recognize_payment_endpoint(request: ReserveRequest):
    """Recognize a reserved payment and create a final transaction record."""

    key = (request.user_id, request.order_id)
    if key not in reservations:
        logging.error(f"Recognition failed: User {request.user_id} not found")
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation = reservations[key]

    if reservation.status != "reserved":
        logging.warning(f"Recognition failed:  wrong status for {request.user_id}")
        raise HTTPException(status_code=400, detail="Reservation already "
                                                    "recognized or cancelled")

    transaction = Transaction(
        user_id=reservation.user_id,
        service_id=reservation.service_id,
        order_id=reservation.order_id,
        amount=reservation.amount,
        timestamp=datetime.now()
    )

    transactions.append(transaction)

    reservation.status = "recognized"

    logging.info(f"Transaction recognized: User {reservation.user_id}, Order {reservation.order_id}, Amount {reservation.amount}")

    return {"message": "Transaction recognized successfully", "transaction": transaction}


@app.get("/transactions/{user_id}")
def transactions_endpoint(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("timestamp"),
    order: str = Query("desc")
):
    # Filter transactions
    user_transactions = [t for t in transactions if t.user_id == user_id]

    # Sort transactions
    reverse = True if order == "desc" else False
    if sort_by == "timestamp":
        user_transactions.sort(key=lambda t: t.timestamp, reverse=reverse)
    elif sort_by == "amount":
        user_transactions.sort(key=lambda t: t.amount, reverse=reverse)

    # Apply pagination
    paginated = user_transactions[skip : skip + limit]

    return {"user_id": user_id, "transactions": paginated}
