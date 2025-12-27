#! /usr/bin/env python
"""Multiplayer menu UI for online pool games."""

from __future__ import annotations

from direct.gui.DirectGui import (
    DGG,
    DirectButton,
    DirectEntry,
    DirectFrame,
    DirectLabel,
    DirectScrolledList,
)
from panda3d.core import TextNode

from pooltool.ani.fonts import load_font
from pooltool.ani.globals import Global
from pooltool.ani.menu._datatypes import (
    BUTTON_FONT,
    BUTTON_TEXT_SCALE,
    BaseMenu,
    MenuButton,
    MenuInput,
    MenuTitle,
    TEXT_COLOR,
    TITLE_FONT,
)
from pooltool.ani.menu._registry import MenuNavigator
from pooltool.multiplayer import MultiplayerClient
from pooltool.multiplayer.protocol import RoomInfo


class MultiplayerMenu(BaseMenu):
    """Main multiplayer menu for browsing and joining games."""

    name: str = "multiplayer"

    def __init__(self) -> None:
        super().__init__()

        self.client: MultiplayerClient | None = None
        self.room_list_frame: DirectScrolledList | None = None
        self.status_label: DirectLabel | None = None
        self.rooms: list[dict] = []

        self.title = MenuTitle.create(text="Online Multiplayer")
        self.back_button = MenuButton.create(
            text="Back",
            command=self._go_back,
            description="Return to main menu",
        )

    def populate(self) -> None:
        self.add_title(self.title)

        # Connection status
        self._create_status_label()

        # Server connection section
        self._create_connection_section()

        # Room browser section
        self._create_room_browser()

        # Action buttons
        self._create_action_buttons()

        self.add_button(self.back_button)

    def _create_status_label(self) -> None:
        """Create connection status indicator."""
        self.status_label = DirectLabel(
            text="Not Connected",
            scale=BUTTON_TEXT_SCALE * 0.8,
            relief=None,
            text_fg=(0.8, 0.3, 0.3, 1),
            text_align=TextNode.ALeft,
            text_font=load_font(TITLE_FONT),
            parent=self.area.getCanvas(),
        )
        self.status_label.setPos(-0.7, 0, 0.55)

    def _create_connection_section(self) -> None:
        """Create server connection input fields."""
        font = load_font(BUTTON_FONT)

        # Host input
        host_label = DirectLabel(
            text="Server:",
            scale=BUTTON_TEXT_SCALE * 0.7,
            relief=None,
            text_fg=TEXT_COLOR,
            text_align=TextNode.ALeft,
            text_font=load_font(TITLE_FONT),
            parent=self.area.getCanvas(),
        )
        host_label.setPos(-0.7, 0, 0.4)

        self.host_entry = DirectEntry(
            text="",
            scale=BUTTON_TEXT_SCALE * 0.6,
            width=12,
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 0.7),
            text_fg=TEXT_COLOR,
            text_font=font,
            initialText="localhost",
            numLines=1,
            parent=self.area.getCanvas(),
        )
        self.host_entry.setPos(-0.35, 0, 0.4)

        # Port input
        port_label = DirectLabel(
            text="Port:",
            scale=BUTTON_TEXT_SCALE * 0.7,
            relief=None,
            text_fg=TEXT_COLOR,
            text_align=TextNode.ALeft,
            text_font=load_font(TITLE_FONT),
            parent=self.area.getCanvas(),
        )
        port_label.setPos(0.25, 0, 0.4)

        self.port_entry = DirectEntry(
            text="",
            scale=BUTTON_TEXT_SCALE * 0.6,
            width=6,
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 0.7),
            text_fg=TEXT_COLOR,
            text_font=font,
            initialText="7777",
            numLines=1,
            parent=self.area.getCanvas(),
        )
        self.port_entry.setPos(0.48, 0, 0.4)

        # Name input
        name_label = DirectLabel(
            text="Name:",
            scale=BUTTON_TEXT_SCALE * 0.7,
            relief=None,
            text_fg=TEXT_COLOR,
            text_align=TextNode.ALeft,
            text_font=load_font(TITLE_FONT),
            parent=self.area.getCanvas(),
        )
        name_label.setPos(-0.7, 0, 0.25)

        self.name_entry = DirectEntry(
            text="",
            scale=BUTTON_TEXT_SCALE * 0.6,
            width=15,
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 0.7),
            text_fg=TEXT_COLOR,
            text_font=font,
            initialText="Player",
            numLines=1,
            parent=self.area.getCanvas(),
        )
        self.name_entry.setPos(-0.35, 0, 0.25)

        # Connect button
        self.connect_button = DirectButton(
            text="Connect",
            text_align=TextNode.ACenter,
            text_font=font,
            scale=BUTTON_TEXT_SCALE * 0.8,
            relief=DGG.RIDGE,
            frameColor=(0.3, 0.7, 0.3, 1),
            command=self._connect_to_server,
            parent=self.area.getCanvas(),
        )
        self.connect_button.setPos(0.55, 0, 0.25)

    def _create_room_browser(self) -> None:
        """Create room browser list."""
        font = load_font(BUTTON_FONT)

        # Room list header
        room_header = DirectLabel(
            text="Available Rooms:",
            scale=BUTTON_TEXT_SCALE * 0.8,
            relief=None,
            text_fg=TEXT_COLOR,
            text_align=TextNode.ALeft,
            text_font=load_font(TITLE_FONT),
            parent=self.area.getCanvas(),
        )
        room_header.setPos(-0.7, 0, 0.05)

        # Room list frame
        self.room_list_frame = DirectScrolledList(
            decButton_pos=(0.35, 0, 0.53),
            decButton_text="^",
            decButton_text_scale=0.04,
            decButton_borderWidth=(0.005, 0.005),
            incButton_pos=(0.35, 0, -0.02),
            incButton_text="v",
            incButton_text_scale=0.04,
            incButton_borderWidth=(0.005, 0.005),
            frameSize=(-0.75, 0.75, -0.45, 0.0),
            frameColor=(0.1, 0.1, 0.1, 0.5),
            pos=(0, 0, -0.15),
            numItemsVisible=5,
            forceHeight=0.08,
            itemFrame_frameSize=(-0.7, 0.65, -0.4, 0.0),
            itemFrame_pos=(0, 0, 0),
            parent=self.area.getCanvas(),
        )

        # Placeholder message
        self.no_rooms_label = DirectLabel(
            text="Connect to server to see rooms",
            scale=BUTTON_TEXT_SCALE * 0.6,
            relief=None,
            text_fg=(0.6, 0.6, 0.6, 1),
            text_font=font,
            parent=self.area.getCanvas(),
        )
        self.no_rooms_label.setPos(0, 0, -0.3)

    def _create_action_buttons(self) -> None:
        """Create action buttons for room management."""
        font = load_font(BUTTON_FONT)

        # Create room button
        self.create_room_button = DirectButton(
            text="Create Room",
            text_align=TextNode.ACenter,
            text_font=font,
            scale=BUTTON_TEXT_SCALE * 0.8,
            relief=DGG.RIDGE,
            frameColor=(0.3, 0.5, 0.8, 1),
            command=self._show_create_room_dialog,
            parent=self.area.getCanvas(),
            state=DGG.DISABLED,
        )
        self.create_room_button.setPos(-0.4, 0, -0.7)

        # Refresh button
        self.refresh_button = DirectButton(
            text="Refresh",
            text_align=TextNode.ACenter,
            text_font=font,
            scale=BUTTON_TEXT_SCALE * 0.8,
            relief=DGG.RIDGE,
            frameColor=(0.5, 0.5, 0.5, 1),
            command=self._refresh_rooms,
            parent=self.area.getCanvas(),
            state=DGG.DISABLED,
        )
        self.refresh_button.setPos(0.4, 0, -0.7)

    def _connect_to_server(self) -> None:
        """Connect to the multiplayer server."""
        host = self.host_entry.get()
        try:
            port = int(self.port_entry.get())
        except ValueError:
            port = 7777
        name = self.name_entry.get() or "Player"

        # Create client if needed
        if self.client is None:
            self.client = MultiplayerClient()
            self.client.on_connected = self._on_connected
            self.client.on_disconnected = self._on_disconnected
            self.client.on_room_list = self._on_room_list
            self.client.on_room_update = self._on_room_update
            self.client.on_game_start = self._on_game_start
            self.client.on_error = self._on_error

        # Connect
        self.client.connect(host, port, name)
        self._update_status("Connecting...", (0.8, 0.8, 0.3, 1))

        # Start update task
        Global.task_mgr.add(self._update_client, "multiplayer_client_update")

    def _update_client(self, task):
        """Update client to process messages."""
        if self.client:
            self.client.update()
        return task.cont

    def _on_connected(self, player_id: str) -> None:
        """Handle successful connection."""
        self._update_status("Connected", (0.3, 0.8, 0.3, 1))
        self.connect_button["text"] = "Disconnect"
        self.connect_button["command"] = self._disconnect
        self.connect_button["frameColor"] = (0.8, 0.3, 0.3, 1)

        # Enable buttons
        self.create_room_button["state"] = DGG.NORMAL
        self.refresh_button["state"] = DGG.NORMAL

        # Request room list
        self._refresh_rooms()

    def _on_disconnected(self) -> None:
        """Handle disconnection."""
        self._update_status("Disconnected", (0.8, 0.3, 0.3, 1))
        self.connect_button["text"] = "Connect"
        self.connect_button["command"] = self._connect_to_server
        self.connect_button["frameColor"] = (0.3, 0.7, 0.3, 1)

        # Disable buttons
        self.create_room_button["state"] = DGG.DISABLED
        self.refresh_button["state"] = DGG.DISABLED

        # Clear room list
        self._clear_room_list()

        # Stop update task
        Global.task_mgr.remove("multiplayer_client_update")

    def _on_room_list(self, rooms: list[dict]) -> None:
        """Handle room list update."""
        self.rooms = rooms
        self._update_room_list()

    def _on_room_update(self, room: RoomInfo) -> None:
        """Handle room update - navigate to lobby."""
        MenuNavigator.go_to_menu("multiplayer_lobby")()

    def _on_game_start(self, game_state) -> None:
        """Handle game start."""
        # Transition to game
        Global.base.messenger.send("enter-game")

    def _on_error(self, error: str) -> None:
        """Handle error message."""
        self._update_status(f"Error: {error}", (0.8, 0.3, 0.3, 1))

    def _update_status(self, text: str, color: tuple) -> None:
        """Update status label."""
        if self.status_label:
            self.status_label["text"] = text
            self.status_label["text_fg"] = color

    def _disconnect(self) -> None:
        """Disconnect from server."""
        if self.client:
            self.client.disconnect()

    def _refresh_rooms(self) -> None:
        """Request room list refresh."""
        if self.client and self.client.is_connected:
            self.client.request_room_list()

    def _clear_room_list(self) -> None:
        """Clear the room list display."""
        if self.room_list_frame:
            self.room_list_frame.removeAndDestroyAllItems()
        self.rooms = []
        if self.no_rooms_label:
            self.no_rooms_label["text"] = "Connect to server to see rooms"
            self.no_rooms_label.show()

    def _update_room_list(self) -> None:
        """Update the room list display."""
        if not self.room_list_frame:
            return

        self.room_list_frame.removeAndDestroyAllItems()

        if not self.rooms:
            if self.no_rooms_label:
                self.no_rooms_label["text"] = "No rooms available"
                self.no_rooms_label.show()
            return

        if self.no_rooms_label:
            self.no_rooms_label.hide()

        font = load_font(BUTTON_FONT)

        for room in self.rooms:
            room_id = room.get("room_id", "")
            room_name = room.get("room_name", "Unknown")
            player_count = room.get("player_count", 0)
            max_players = room.get("max_players", 2)
            game_type = room.get("game_type", "8ball")

            # Create room entry button
            text = f"{room_name} ({player_count}/{max_players}) - {game_type}"
            btn = DirectButton(
                text=text,
                text_align=TextNode.ALeft,
                text_font=font,
                scale=BUTTON_TEXT_SCALE * 0.6,
                relief=DGG.RIDGE,
                frameColor=(0.2, 0.2, 0.2, 0.8),
                frameSize=(-0.1, 1.3, -0.03, 0.05),
                command=self._join_room,
                extraArgs=[room_id],
            )
            self.room_list_frame.addItem(btn)

    def _join_room(self, room_id: str) -> None:
        """Join a room."""
        if self.client and self.client.is_connected:
            self.client.join_room(room_id)

    def _show_create_room_dialog(self) -> None:
        """Navigate to room creation menu."""
        MenuNavigator.go_to_menu("create_room")()

    def _go_back(self) -> None:
        """Return to main menu."""
        if self.client and self.client.is_connected:
            self.client.disconnect()
        Global.task_mgr.remove("multiplayer_client_update")
        MenuNavigator.go_to_menu("main_menu")()

    def hide(self) -> None:
        """Clean up when hiding menu."""
        super().hide()
        # Don't disconnect - keep connection alive


class CreateRoomMenu(BaseMenu):
    """Menu for creating a new multiplayer room."""

    name: str = "create_room"

    def __init__(self) -> None:
        super().__init__()
        self.title = MenuTitle.create(text="Create Room")

    def populate(self) -> None:
        self.add_title(self.title)

        font = load_font(BUTTON_FONT)

        # Room name input
        name_label = DirectLabel(
            text="Room Name:",
            scale=BUTTON_TEXT_SCALE * 0.8,
            relief=None,
            text_fg=TEXT_COLOR,
            text_align=TextNode.ALeft,
            text_font=load_font(TITLE_FONT),
            parent=self.area.getCanvas(),
        )
        name_label.setPos(-0.7, 0, 0.5)

        self.room_name_entry = DirectEntry(
            text="",
            scale=BUTTON_TEXT_SCALE * 0.6,
            width=20,
            relief=DGG.SUNKEN,
            frameColor=(1, 1, 1, 0.7),
            text_fg=TEXT_COLOR,
            text_font=font,
            initialText="My Room",
            numLines=1,
            parent=self.area.getCanvas(),
        )
        self.room_name_entry.setPos(-0.2, 0, 0.5)

        # Game type selection
        type_label = DirectLabel(
            text="Game Type:",
            scale=BUTTON_TEXT_SCALE * 0.8,
            relief=None,
            text_fg=TEXT_COLOR,
            text_align=TextNode.ALeft,
            text_font=load_font(TITLE_FONT),
            parent=self.area.getCanvas(),
        )
        type_label.setPos(-0.7, 0, 0.3)

        # Game type buttons
        self.game_type = "8ball"
        self.type_buttons = {}

        for i, game_type in enumerate(["8ball", "9ball", "snooker"]):
            btn = DirectButton(
                text=game_type,
                text_align=TextNode.ACenter,
                text_font=font,
                scale=BUTTON_TEXT_SCALE * 0.7,
                relief=DGG.RIDGE,
                frameColor=(0.3, 0.5, 0.8, 1) if i == 0 else (0.3, 0.3, 0.3, 1),
                command=self._select_game_type,
                extraArgs=[game_type],
                parent=self.area.getCanvas(),
            )
            btn.setPos(-0.4 + i * 0.4, 0, 0.3)
            self.type_buttons[game_type] = btn

        # Create button
        create_btn = DirectButton(
            text="Create Room",
            text_align=TextNode.ACenter,
            text_font=font,
            scale=BUTTON_TEXT_SCALE,
            relief=DGG.RIDGE,
            frameColor=(0.3, 0.7, 0.3, 1),
            command=self._create_room,
            parent=self.area.getCanvas(),
        )
        create_btn.setPos(0, 0, 0.0)

        # Back button
        back_btn = DirectButton(
            text="Back",
            text_align=TextNode.ACenter,
            text_font=font,
            scale=BUTTON_TEXT_SCALE * 0.8,
            relief=DGG.RIDGE,
            frameColor=(0.5, 0.5, 0.5, 1),
            command=MenuNavigator.go_to_menu("multiplayer"),
            parent=self.area.getCanvas(),
        )
        back_btn.setPos(0, 0, -0.2)

    def _select_game_type(self, game_type: str) -> None:
        """Select a game type."""
        self.game_type = game_type
        for gt, btn in self.type_buttons.items():
            if gt == game_type:
                btn["frameColor"] = (0.3, 0.5, 0.8, 1)
            else:
                btn["frameColor"] = (0.3, 0.3, 0.3, 1)

    def _create_room(self) -> None:
        """Create the room."""
        from pooltool.ani.menu._registry import MenuRegistry

        mp_menu = MenuRegistry.get_menu("multiplayer")
        if mp_menu and hasattr(mp_menu, "client") and mp_menu.client:
            room_name = self.room_name_entry.get() or "My Room"
            mp_menu.client.create_room(room_name, self.game_type)


class MultiplayerLobbyMenu(BaseMenu):
    """Menu for the multiplayer game lobby."""

    name: str = "multiplayer_lobby"

    def __init__(self) -> None:
        super().__init__()
        self.title = MenuTitle.create(text="Game Lobby")

    def populate(self) -> None:
        from pooltool.ani.menu._registry import MenuRegistry

        self.add_title(self.title)

        font = load_font(BUTTON_FONT)

        # Get client from multiplayer menu
        mp_menu = MenuRegistry.get_menu("multiplayer")
        client = None
        if mp_menu and hasattr(mp_menu, "client"):
            client = mp_menu.client

        room = client.current_room if client else None

        # Room info
        room_name = room.room_name if room else "Unknown Room"
        room_info = DirectLabel(
            text=f"Room: {room_name}",
            scale=BUTTON_TEXT_SCALE * 0.9,
            relief=None,
            text_fg=TEXT_COLOR,
            text_align=TextNode.ALeft,
            text_font=load_font(TITLE_FONT),
            parent=self.area.getCanvas(),
        )
        room_info.setPos(-0.7, 0, 0.5)

        # Player list header
        player_header = DirectLabel(
            text="Players:",
            scale=BUTTON_TEXT_SCALE * 0.8,
            relief=None,
            text_fg=TEXT_COLOR,
            text_align=TextNode.ALeft,
            text_font=load_font(TITLE_FONT),
            parent=self.area.getCanvas(),
        )
        player_header.setPos(-0.7, 0, 0.3)

        # Player list
        if room:
            for i, player in enumerate(room.players):
                status = "Ready" if player.is_ready else "Not Ready"
                host_tag = " (Host)" if player.is_host else ""
                you_tag = " (You)" if client and player.player_id == client.player_id else ""

                player_label = DirectLabel(
                    text=f"{player.name}{host_tag}{you_tag} - {status}",
                    scale=BUTTON_TEXT_SCALE * 0.7,
                    relief=None,
                    text_fg=(0.3, 0.8, 0.3, 1) if player.is_ready else TEXT_COLOR,
                    text_align=TextNode.ALeft,
                    text_font=font,
                    parent=self.area.getCanvas(),
                )
                player_label.setPos(-0.5, 0, 0.15 - i * 0.1)

        # Ready button
        is_ready = False
        if client and room:
            for p in room.players:
                if p.player_id == client.player_id:
                    is_ready = p.is_ready
                    break

        ready_btn = DirectButton(
            text="Ready!" if not is_ready else "Not Ready",
            text_align=TextNode.ACenter,
            text_font=font,
            scale=BUTTON_TEXT_SCALE,
            relief=DGG.RIDGE,
            frameColor=(0.3, 0.7, 0.3, 1) if not is_ready else (0.7, 0.3, 0.3, 1),
            command=self._toggle_ready,
            parent=self.area.getCanvas(),
        )
        ready_btn.setPos(0, 0, -0.2)

        # Leave button
        leave_btn = DirectButton(
            text="Leave Room",
            text_align=TextNode.ACenter,
            text_font=font,
            scale=BUTTON_TEXT_SCALE * 0.8,
            relief=DGG.RIDGE,
            frameColor=(0.5, 0.5, 0.5, 1),
            command=self._leave_room,
            parent=self.area.getCanvas(),
        )
        leave_btn.setPos(0, 0, -0.4)

    def _toggle_ready(self) -> None:
        """Toggle ready status."""
        from pooltool.ani.menu._registry import MenuRegistry

        mp_menu = MenuRegistry.get_menu("multiplayer")
        if mp_menu and hasattr(mp_menu, "client") and mp_menu.client:
            client = mp_menu.client
            if client.current_room:
                for p in client.current_room.players:
                    if p.player_id == client.player_id:
                        client.set_ready(not p.is_ready)
                        break

    def _leave_room(self) -> None:
        """Leave the current room."""
        from pooltool.ani.menu._registry import MenuRegistry

        mp_menu = MenuRegistry.get_menu("multiplayer")
        if mp_menu and hasattr(mp_menu, "client") and mp_menu.client:
            mp_menu.client.leave_room()

        MenuNavigator.go_to_menu("multiplayer")()
