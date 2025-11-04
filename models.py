from pydantic import BaseModel, Field
from datetime import datetime


class Transaction(BaseModel):
    user_id: int
    service_id: int
    order_id: int
    amount: float
    timestamp: datetime


class DepositRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID must be greater than 0")
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")


class DepositResponse(BaseModel):
    user_id: int
    new_balance: float
    message: str


class ReserveRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID must be greater than 0")
    service_id: int = Field(..., gt=0, description="Service ID must be greater than 0")
    order_id: int = Field(..., gt=0, description="Order ID must be greater than 0")
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")


class BalanceResponse(BaseModel):
    user_id: int
    balance: float


class Reservation(BaseModel):
    user_id: int
    service_id: int
    order_id: int
    amount: float
    status: str


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    service_id: int
    order_id: int
    amount: float
    timestamp: str

    class Config:
        orm_mode = True