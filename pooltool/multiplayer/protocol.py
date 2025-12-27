#! /usr/bin/env python
"""Network protocol definitions for multiplayer communication."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

import attrs


class MessageType(str, Enum):
    """Types of messages exchanged between server and clients."""

    # Connection
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"

    # Lobby
    CREATE_ROOM = "create_room"
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    ROOM_LIST = "room_list"
    ROOM_UPDATE = "room_update"
    PLAYER_READY = "player_ready"
    GAME_START = "game_start"

    # Gameplay
    SHOT_AIM = "shot_aim"
    SHOT_EXECUTE = "shot_execute"
    SHOT_RESULT = "shot_result"
    GAME_STATE = "game_state"
    TURN_CHANGE = "turn_change"
    GAME_OVER = "game_over"

    # Chat
    CHAT_MESSAGE = "chat_message"

    # Errors
    ERROR = "error"


@attrs.define
class PlayerInfo:
    """Information about a connected player."""

    player_id: str
    name: str
    is_ready: bool = False
    is_host: bool = False
    is_connected: bool = True


@attrs.define
class RoomInfo:
    """Information about a game room."""

    room_id: str
    room_name: str
    host_id: str
    players: list[PlayerInfo]
    max_players: int = 2
    game_type: str = "8ball"
    is_started: bool = False

    @property
    def is_full(self) -> bool:
        return len(self.players) >= self.max_players

    @property
    def player_count(self) -> int:
        return len(self.players)


@attrs.define
class CueState:
    """State of the cue stick for synchronization."""

    phi: float  # Horizontal angle
    theta: float  # Elevation angle
    V0: float  # Strike velocity
    a: float  # English horizontal
    b: float  # English vertical
    cue_ball_id: str


@attrs.define
class GameState:
    """Complete game state for synchronization."""

    room_id: str
    current_player_id: str
    turn_number: int
    shot_number: int
    ball_positions: dict[str, tuple[float, float, float]]
    ball_states: dict[str, str]  # ball_id -> state (e.g., "on_table", "pocketed")
    cue_state: CueState | None
    score: dict[str, int]
    is_game_over: bool = False
    winner_id: str | None = None


@attrs.define
class GameMessage:
    """A message exchanged between server and clients."""

    msg_type: MessageType
    sender_id: str
    data: dict[str, Any]
    timestamp: float

    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps({
            "msg_type": self.msg_type.value,
            "sender_id": self.sender_id,
            "data": self.data,
            "timestamp": self.timestamp,
        })

    @classmethod
    def from_json(cls, json_str: str) -> GameMessage:
        """Deserialize message from JSON string."""
        data = json.loads(json_str)
        return cls(
            msg_type=MessageType(data["msg_type"]),
            sender_id=data["sender_id"],
            data=data["data"],
            timestamp=data["timestamp"],
        )


def serialize_ball_positions(balls: dict) -> dict[str, tuple[float, float, float]]:
    """Extract ball positions from a balls dictionary."""
    positions = {}
    for ball_id, ball in balls.items():
        pos = ball.state.rvw[0]
        positions[ball_id] = (float(pos[0]), float(pos[1]), float(pos[2]))
    return positions


def serialize_ball_states(balls: dict) -> dict[str, str]:
    """Extract ball states from a balls dictionary."""
    states = {}
    for ball_id, ball in balls.items():
        states[ball_id] = ball.state.s.name
    return states
