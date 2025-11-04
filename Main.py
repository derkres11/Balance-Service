from fastapi import FastAPI, HTTPException
from models import TransactionResponse, DepositRequest, DepositResponse, BalanceResponse, ReserveRequest, Reservation, Transaction
from service import deposit, get_balance, reserve_funds, recognize_transaction
from service import balances, transactions, reservations
from datetime import datetime
from fastapi import Query
import logging
from models_db import User, Balance
from sqlalchemy.orm import Session



logging.basicConfig(
    filename="balance_service.log",
    level=logging.INFO,          
    format="%(asctime)s - %(levelname)s - %(message)s"
    
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



app = FastAPI(title="User Balance Service", version="1.0")


"""@app.post("/deposit", response_model=DepositResponse)
def deposit_endpoint(request: DepositRequest):
    """

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
    )"""


@app.get("/balance/{user_id}", response_model=BalanceResponse)
def balance_endpoint(user_id: int):
    """
    Get current balance for a user.
    Returns 0.0 if the user does not exist.
    """
    balance = get_balance(user_id)
    return BalanceResponse(user_id=user_id, balance=balance)


"""@app.post("/reserve", response_model=Reservation)
def reserve_endpoint(request: ReserveRequest):
    """
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
    return {"message": "Reservation successful", "reservation": reservation}"""

@app.post("/reserve")
def reserve_endpoint(request: ReserveRequest, db: Session = Depends(get_db)):
    """
    Reserve money for an order (stored in DB).
    """
    try:
        with db.begin():  
            user = db.query(User).filter(User.id == request.user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            balance = db.query(Balance).filter(Balance.user_id == request.user_id).first()
            if not balance or balance.amount < request.amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")

            new_balance = balance.amount - request.amount
            if new_balance < 0:
                raise HTTPException(status_code=400, detail="Balance cannot be negative")

            balance.amount = new_balance

            reservation = Reservation(
                user_id=request.user_id,
                service_id=request.service_id,
                order_id=request.order_id,
                amount=request.amount,
                status="reserved"
            )
            db.add(reservation)

            logging.info(f"Reservation successful: user={request.user_id}, order={request.order_id}, amount={request.amount}")

        db.commit()
        return {"message": "Reservation successful", "reservation_id": reservation.id}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Reservation failed for user={request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Reservation failed: {e}")



@app.post("/deposit", response_model=DepositResponse)
def deposit_endpoint(request: DepositRequest, db: Session = Depends(get_db)):
    """
    Deposit money to a user's account.
    """
    with db.begin():
        balance = db.query(Balance).filter(Balance.user_id == request.user_id).first()
        if not balance:
            user = db.query(User).filter(User.id == request.user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            balance = Balance(user_id=request.user_id, amount=0.0)
            db.add(balance)
            db.flush() 
        balance.amount += request.amount
        db.commit()

        return DepositResponse(
            user_id=request.user_id,
            new_balance=balance.amount,
            message="Deposit successful"
        )


"""@app.get("/transactions/{user_id}")
def transactions_endpoint(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("timestamp"),
    order: str = Query("desc")
):
    user_transactions = [t for t in transactions if t.user_id == user_id]

    reverse = True if order == "desc" else False
    if sort_by == "timestamp":
        user_transactions.sort(key=lambda t: t.timestamp, reverse=reverse)
    elif sort_by == "amount":
        user_transactions.sort(key=lambda t: t.amount, reverse=reverse)

    paginated = user_transactions[skip : skip + limit]

    return {"user_id": user_id, "transactions": paginated}"""


@app.get("/balance/{user_id}", response_model=BalanceResponse)
def balance_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Get current balance for a user from the database.
    """
    try:
        with db.begin():  # транзакция "на чтение"
            balance = db.query(Balance).filter(Balance.user_id == user_id).first()
            if not balance:
                raise HTTPException(status_code=404, detail="User balance not found")

        return BalanceResponse(user_id=user_id, balance=balance.amount)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error fetching balance: {e}")


