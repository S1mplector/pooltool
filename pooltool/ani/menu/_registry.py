import sys
from collections.abc import Callable

from pooltool.ani.globals import Global
from pooltool.ani.menu._datatypes import BaseMenu


class MenuRegistry:
    _menus: dict[str, type[BaseMenu]] = {}
    _menu_instances: dict[str, BaseMenu] = {}
    _current_menu: BaseMenu | None = None

    @classmethod
    def register(cls, menu_class: type[BaseMenu]) -> None:
        cls._menus[menu_class.name] = menu_class

    @classmethod
    def get_menu_class(cls, name: str) -> type[BaseMenu]:
        if name not in cls._menus:
            raise KeyError(f"Menu '{name}' not registered")
        return cls._menus[name]

    @classmethod
    def create_menu(cls, name: str) -> BaseMenu:
        menu_class = cls.get_menu_class(name)
        return menu_class()

    @classmethod
    def get_or_create_menu(cls, name: str) -> BaseMenu:
        """Get existing menu instance or create a new one."""
        if name not in cls._menu_instances:
            cls._menu_instances[name] = cls.create_menu(name)
        return cls._menu_instances[name]

    @classmethod
    def show_menu(cls, name: str) -> None:
        if cls._current_menu:
            cls._current_menu.hide()

        # Use persistent instances for multiplayer menus to keep client state
        if name.startswith("multiplayer") or name == "create_room":
            cls._current_menu = cls.get_or_create_menu(name)
        else:
            cls._current_menu = cls.create_menu(name)

        assert cls._current_menu is not None
        cls._current_menu.show()

    @classmethod
    def hide_all(cls) -> None:
        if cls._current_menu:
            cls._current_menu.hide()
            cls._current_menu = None

    @classmethod
    def get_current_menu(cls) -> BaseMenu | None:
        return cls._current_menu

    @classmethod
    def get_menu(cls, name: str) -> BaseMenu | None:
        """Get a menu instance by name if it exists."""
        return cls._menu_instances.get(name)


class MenuNavigator:
    @staticmethod
    def go_to_menu(menu_name: str) -> Callable[[], None]:
        def navigate():
            MenuRegistry.show_menu(menu_name)

        return navigate

    @staticmethod
    def quit_application() -> None:
        sys.exit()

    @staticmethod
    def enter_game() -> None:
        Global.base.messenger.send("enter-game")
