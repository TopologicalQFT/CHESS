"""Pydantic schemas for inbound WebSocket messages.

Outbound messages are plain dicts; see docs/Overall Plan/Website Design/
WebSocket Protocol.md for the full protocol.
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CreateRoomMsg(BaseModel):
    type: Literal["create_room"]
    player_name: str = Field(min_length=1, max_length=30)
    color: Literal["w", "b", "random"] = "random"
    # Seconds per player; None = no clock. UI offers 300/600.
    time_control: Optional[int] = Field(default=None, ge=1, le=7200)


class JoinRoomMsg(BaseModel):
    type: Literal["join_room"]
    room_id: str
    player_name: str = Field(min_length=1, max_length=30)


class MoveMsg(BaseModel):
    type: Literal["move"]
    from_sq: str = Field(alias="from", min_length=2, max_length=2)
    to_sq: str = Field(alias="to", min_length=2, max_length=2)
    promotion: Optional[Literal["q", "r", "b", "n"]] = None

    def uci(self) -> str:
        return self.from_sq + self.to_sq + (self.promotion or "")


class ReconnectMsg(BaseModel):
    type: Literal["reconnect"]
    room_id: str
    color: Literal["w", "b"]
