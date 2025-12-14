from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List

from .models import (
    Room, BookingCreate, Booking,
    SessionCreate, Session,
    SongEntryCreate, SongEntry,
    OrderCreate, Order, OrderItem,
    Bill
)
from . import storage

app = FastAPI(title="karaoke-prototype")

@app.on_event("startup")
def _startup():
    storage.seed()

def estimate_price(start: datetime, end: datetime) -> float:
    hours = max((end - start).total_seconds() / 3600.0, 0.0)
    return round(hours * 1000.0, 2)

@app.get("/rooms", response_model=List[Room])
def list_rooms():
    return list(storage.rooms.values())

@app.get("/rooms/availability", response_model=List[Room])
def availability(startTime: datetime, endTime: datetime, partySize: int):
    if endTime <= startTime:
        raise HTTPException(400, "endTime must be after startTime")

    res = []
    for r in storage.rooms.values():
        if r.capacity < partySize:
            continue
        busy = False
        for b in storage.bookings.values():
            if b.roomId == r.roomId and b.status != "CANCELLED":
                if storage.overlaps(startTime, endTime, b.startTime, b.endTime):
                    busy = True
                    break
        if not busy:
            res.append(r)
    return res

@app.post("/bookings", response_model=Booking, status_code=201)
def create_booking(payload: BookingCreate):
    if payload.endTime <= payload.startTime:
        raise HTTPException(400, "endTime must be after startTime")
    room = storage.rooms.get(payload.roomId)
    if not room:
        raise HTTPException(404, "Room not found")
    if room.capacity < payload.partySize:
        raise HTTPException(400, "partySize exceeds room capacity")

    for b in storage.bookings.values():
        if b.roomId == payload.roomId and b.status != "CANCELLED":
            if storage.overlaps(payload.startTime, payload.endTime, b.startTime, b.endTime):
                raise HTTPException(409, "Room is not available for this time slot")

    booking = Booking(
        roomId=payload.roomId,
        startTime=payload.startTime,
        endTime=payload.endTime,
        partySize=payload.partySize,
        customerName=payload.customerName,
        customerPhone=payload.customerPhone,
        estimatedPrice=estimate_price(payload.startTime, payload.endTime),
    )
    storage.bookings[booking.bookingId] = booking
    return booking

@app.get("/bookings/{bookingId}", response_model=Booking)
def get_booking(bookingId: str):
    b = storage.bookings.get(bookingId)
    if not b:
        raise HTTPException(404, "Booking not found")
    return b

@app.post("/sessions", response_model=Session, status_code=201)
def open_session(payload: SessionCreate):
    s = Session(roomId=payload.roomId, bookingId=payload.bookingId)
    storage.sessions[s.sessionId] = s
    storage.queues[s.sessionId] = []
    return s

@app.post("/sessions/{sessionId}/songs", response_model=SongEntry, status_code=201)
def add_song(sessionId: str, payload: SongEntryCreate):
    s = storage.sessions.get(sessionId)
    if not s:
        raise HTTPException(404, "Session not found")
    if s.status != "ACTIVE":
        raise HTTPException(400, "Session is not active")
    q = storage.queues.get(sessionId, [])
    entry = SongEntry(songId=payload.songId, addedBy=payload.addedBy, position=len(q) + 1)
    q.append(entry)
    storage.queues[sessionId] = q
    return entry

@app.post("/sessions/{sessionId}/close", response_model=Session)
def close_session(sessionId: str):
    s = storage.sessions.get(sessionId)
    if not s:
        raise HTTPException(404, "Session not found")
    if s.status != "ACTIVE":
        raise HTTPException(400, "Session already closed")
    s.endTime = datetime.utcnow()
    s.status = "CLOSED"
    storage.sessions[sessionId] = s
    return s

@app.get("/menu")
def get_menu():
    return list(storage.menu.values())

@app.post("/sessions/{sessionId}/orders", response_model=Order, status_code=201)
def create_order(sessionId: str, payload: OrderCreate):
    s = storage.sessions.get(sessionId)
    if not s:
        raise HTTPException(404, "Session not found")
    if s.status != "ACTIVE":
        raise HTTPException(400, "Session is not active")

    items: List[OrderItem] = []
    total = 0.0
    for it in payload.items:
        mi = storage.menu.get(it.menuItemId)
        if not mi:
            raise HTTPException(404, f"MenuItem not found: {it.menuItemId}")
        if it.quantity <= 0:
            raise HTTPException(400, "quantity must be > 0")
        oi = OrderItem(menuItemId=mi.menuItemId, quantity=it.quantity, price=mi.price)
        items.append(oi)
        total += mi.price * it.quantity

    order = Order(sessionId=sessionId, items=items, total=round(total, 2))
    storage.orders[order.orderId] = order
    return order

@app.get("/sessions/{sessionId}/bill", response_model=Bill)
def get_bill(sessionId: str):
    for b in storage.bills.values():
        if b.sessionId == sessionId:
            return b

    s = storage.sessions.get(sessionId)
    if not s or not s.endTime:
        raise HTTPException(400, "Session must be closed to calculate bill")

    hours = (s.endTime - s.startTime).total_seconds() / 3600.0
    room_charge = round(max(hours, 0.0) * 1000.0, 2)

    orders_total = 0.0
    for o in storage.orders.values():
        if o.sessionId == sessionId and o.status != "CANCELLED":
            orders_total += o.total
    orders_total = round(orders_total, 2)

    discount = 0.0
    total = round(room_charge + orders_total - discount, 2)

    bill = Bill(
        sessionId=sessionId,
        roomCharge=room_charge,
        ordersTotal=orders_total,
        discount=discount,
        total=total,
        status="OPEN"
    )
    storage.bills[bill.billId] = bill
    return bill

@app.post("/bills/{billId}/pay")
def pay_bill(billId: str):
    b = storage.bills.get(billId)
    if not b:
        raise HTTPException(404, "Bill not found")
    b.status = "PAID"
    storage.bills[billId] = b
    return {"billId": billId, "status": b.status}