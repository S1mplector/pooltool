from collections.abc import Callable

from pooltool.ani.globals import Global
from pooltool.ani.menu._datatypes import (
    BaseMenu,
    MenuBackButton,
    MenuHeader,
    MenuTitle,
    MenuDropdown,
)
from pooltool.ani.menu._factory import create_elements_from_dataclass
from pooltool.ani.menu._registry import MenuNavigator
from pooltool.config import settings
from panda3d.core import WindowProperties


def _fps_wrap(func: Callable[[str], None]) -> Callable[[str], None]:
    def inner(value: str) -> None:
        if int(float(value)) < 5:
            value = "5"

        func(value)
        Global.clock.setFrameRate(settings.graphics.fps)

    return inner


class SettingsMenu(BaseMenu):
    name: str = "settings"

    def __init__(self) -> None:
        super().__init__()

        self.title = MenuTitle.create(text="Settings")
        self.back_button = MenuBackButton.create(MenuNavigator.go_to_menu("main_menu"))

    def populate(self) -> None:
        self.add_back_button(self.back_button)
        self.add_title(self.title)

        self.add_header(MenuHeader.create(text="Graphics"))
        for element, field in create_elements_from_dataclass(settings.graphics):
            if field.name == "fps":
                # Patch the FPS function
                entry = element.direct_entry
                entry["command"] = _fps_wrap(entry["command"])

            self.add_element(element)

        self.add_header(MenuHeader.create(text="Window"))

        aspect = settings.system.aspect_ratio
        widths = [1024, 1280, 1400, 1440, 1600, 1920, 2560]
        options = [f"{w} x {int(w / aspect)}" for w in widths]

        current_w = settings.system.window_width
        try:
            initial = f"{current_w} x {int(current_w / aspect)}"
        except Exception:
            initial = options[0]

        def _on_resolution_select(value: str) -> None:
            try:
                w = int(value.split("x")[0].strip())
            except Exception:
                return

            h = int(w / settings.system.aspect_ratio)

            with settings.write() as s:
                s.system.window_width = w

            try:
                props = WindowProperties()
                try:
                    win_props = Global.base.win.getProperties()
                    if win_props.hasOrigin():
                        props.setOrigin(win_props.getXOrigin(), win_props.getYOrigin())
                except Exception:
                    pass
                props.setSize(w, h)
                Global.base.win.requestProperties(props)
            except Exception:
                pass

        res_dropdown = MenuDropdown.create(
            name="Resolution",
            options=options,
            initial_selection=initial if initial in options else options[0],
            description="",
            command=_on_resolution_select,
        )

        self.add_dropdown(res_dropdown)
