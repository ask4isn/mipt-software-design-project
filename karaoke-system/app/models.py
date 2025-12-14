from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional, List
from uuid import uuid4

ID = str
Money = float

RoomStatus = Literal["FREE", "RESERVED", "OCCUPIED"]
BookingStatus = Literal["CREATED", "CONFIRMED", "CANCELLED"]
SessionStatus = Literal["ACTIVE", "CLOSED"]
OrderStatus = Literal["CREATED", "PREPARING", "DELIVERED", "CANCELLED"]
BillStatus = Literal["OPEN", "PAID"]

class Room(BaseModel):
    roomId: ID = Field(default_factory=lambda: str(uuid4()))
    name: str
    capacity: int
    status: RoomStatus = "FREE"

class BookingCreate(BaseModel):
    roomId: ID
    startTime: datetime
    endTime: datetime
    partySize: int
    customerName: str
    customerPhone: str

class Booking(BaseModel):
    bookingId: ID = Field(default_factory=lambda: str(uuid4()))
    roomId: ID
    startTime: datetime
    endTime: datetime
    partySize: int
    status: BookingStatus = "CREATED"
    customerName: str
    customerPhone: str
    estimatedPrice: Money

class SessionCreate(BaseModel):
    roomId: ID
    bookingId: Optional[ID] = None

class Session(BaseModel):
    sessionId: ID = Field(default_factory=lambda: str(uuid4()))
    roomId: ID
    bookingId: Optional[ID] = None
    startTime: datetime = Field(default_factory=datetime.utcnow)
    endTime: Optional[datetime] = None
    status: SessionStatus = "ACTIVE"

class SongEntryCreate(BaseModel):
    songId: ID
    addedBy: str

class SongEntry(BaseModel):
    entryId: ID = Field(default_factory=lambda: str(uuid4()))
    songId: ID
    position: int
    addedBy: str
    addedAt: datetime = Field(default_factory=datetime.utcnow)

class MenuItem(BaseModel):
    menuItemId: ID = Field(default_factory=lambda: str(uuid4()))
    name: str
    price: Money
    type: Literal["FOOD", "DRINK"]

class OrderItemCreate(BaseModel):
    menuItemId: ID
    quantity: int

class OrderItem(BaseModel):
    menuItemId: ID
    quantity: int
    price: Money

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class Order(BaseModel):
    orderId: ID = Field(default_factory=lambda: str(uuid4()))
    sessionId: ID
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    status: OrderStatus = "CREATED"
    items: List[OrderItem]
    total: Money

class Bill(BaseModel):
    billId: ID = Field(default_factory=lambda: str(uuid4()))
    sessionId: ID
    roomCharge: Money
    ordersTotal: Money
    discount: Money
    total: Money
    status: BillStatus = "OPEN"