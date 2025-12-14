from typing import Dict, List
from datetime import datetime
from .models import Room, Booking, Session, SongEntry, MenuItem, Order, Bill

rooms: Dict[str, Room] = {}
bookings: Dict[str, Booking] = {}
sessions: Dict[str, Session] = {}
queues: Dict[str, List[SongEntry]] = {}
menu: Dict[str, MenuItem] = {}
orders: Dict[str, Order] = {}
bills: Dict[str, Bill] = {}

def seed():
    if rooms:
        return
    r1 = Room(name="Room A", capacity=4)
    r2 = Room(name="Room B", capacity=8)
    r3 = Room(name="VIP", capacity=10)
    for r in (r1, r2, r3):
        rooms[r.roomId] = r

    m1 = MenuItem(name="Cola 0.5", price=250.0, type="DRINK")
    m2 = MenuItem(name="Beer", price=350.0, type="DRINK")
    m3 = MenuItem(name="Pizza", price=700.0, type="FOOD")
    for m in (m1, m2, m3):
        menu[m.menuItemId] = m

def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return not (a_end <= b_start or a_start >= b_end)