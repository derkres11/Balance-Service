#models_db.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)

    balances = relationship("Balance", back_populates="user", cascade="all, delete")
    reservations = relationship("Reservation", back_populates="user", cascade="all, delete")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete")


class Balance(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, default=0.0)

    user = relationship("User", back_populates="balances")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, nullable=False)
    order_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="reserved")

    user = relationship("User", back_populates="reservations")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, nullable=False)
    order_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


class TransactionResponse(Base):
    id: int
    user_id: int
    service_id: int
    order_id: int
    amount: float
    timestamp: str

    class Config:
        orm_mode = True