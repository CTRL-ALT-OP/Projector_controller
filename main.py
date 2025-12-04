import contextlib
import json
from typing import List, Dict

import nebulatk as ntk

from projector import Projector


WINDOW_BACKGROUND = "#181818"
FRAME_BACKGROUND = "#242424"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#569e6a"
ACCENT_COLOR_HOVER = "#3e734c"
DISABLED_COLOR = "#6e6e6e"
DISABLED_COLOR_HOVER = "#4a4a4a"

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 120
FRAME_SPACING = 8
FRAME_WIDTH = WINDOW_WIDTH - FRAME_SPACING * 2
FRAME_HEIGHT = WINDOW_HEIGHT - FRAME_SPACING * 2


BUTTON_SPACING = 4
BUTTON_WIDTH = ((FRAME_WIDTH - 70) / 4) - BUTTON_SPACING
BUTTON_HEIGHT = 30


class ProjectorControllerFrame(ntk.Frame):
    """
    One UI controller for a single projector.

    Sections (top to bottom):
      - Name label (projector_type or friendly name)
      - Source buttons
      - Feature toggle buttons
      - Power button (icon), reflecting initial power state
    """

    def __init__(self, master, proj: Projector, meta: Dict, *args, **kwargs):
        super().__init__(master, fill=FRAME_BACKGROUND, *args, **kwargs)
        self.hide()
        self.proj = proj
        self.meta = meta

        # Pre-load power icon images (off/on with hover variants)
        self.power_icon_off = ntk.image_manager.Image("images/power.png")
        self.power_icon_off.recolor(DISABLED_COLOR)
        self.power_icon_off_hover = ntk.image_manager.Image("images/power.png")
        self.power_icon_off_hover.recolor(DISABLED_COLOR_HOVER)

        self.power_icon_on = ntk.image_manager.Image("images/power.png")
        self.power_icon_on.recolor(ACCENT_COLOR)
        self.power_icon_on_hover = ntk.image_manager.Image("images/power.png")
        self.power_icon_on_hover.recolor(ACCENT_COLOR_HOVER)

        self._build_ui()
        self._sync_initial_state()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # Name section
        # Prefer a stored custom name; otherwise derive a human-friendly default
        # from the projector type (e.g. "test_projector" -> "Test Projector").
        name = self.meta.get("name")
        if not name:
            proj_type = self.meta.get("projector_type", "Projector")
            name = proj_type.replace("_", " ").title()
        self.name_label = ntk.Entry(
            self,
            text=name,
            font=("Arial", 12, "bold"),
            text_color=TEXT_COLOR,
            fill="#00000000",
        )
        self.name_label.place(x=8, y=6)
        self.name_label.cursor.fill = "#ffffff"
        self.name_label.cursor_animation.stop()
        self.name_label.cursor_animation = ntk.animation_controller.Animation(
            self.name_label.cursor,
            {
                "fill": "#ffffff00",  # Fade out completely
            },
            duration=0.4,  # Slightly slower blink for a more natural feel
            looping=True,
        )
        self.name_label.cursor_animation.start()

        self.max_font_size = 100
        for name, cmd in self.proj.projector_lib.commands.items():
            if cmd.get("type") not in ("source", "source_cycle", "feature", "toggle"):
                continue
            max_for_name = ntk.fonts_manager.get_max_font_size(
                self.master.root,
                ("Arial", 12, "bold"),
                BUTTON_WIDTH - 4,
                BUTTON_HEIGHT - 4,
                name,
            )
            if max_for_name < self.max_font_size:
                self.max_font_size = max_for_name

        # Source list section
        y = self._build_sources_section(y_start=30)

        # Feature list section
        self._build_features_section(y_start=y)

        # Power button on the right
        self._build_power_section(x_right=FRAME_WIDTH - 6, y_center=60 + ((y - 70) / 2))

        self.height = y + 40

        self._update_children()

    def _build_sources_section(self, y_start: int):
        # Sources are commands where type == "source" or "source_cycle"
        commands = self.proj.projector_lib.commands
        self.source_buttons = []

        x = 8

        def build_button(x, name, cmd):
            btn = ntk.Button(
                self,
                text=name,
                font=("Arial", self.max_font_size, "bold"),
                width=BUTTON_WIDTH,
                height=BUTTON_HEIGHT,
                border=DISABLED_COLOR_HOVER,
                border_width=2,
                fill=DISABLED_COLOR,
                hover_fill=DISABLED_COLOR_HOVER,
                active_fill=ACCENT_COLOR,
                active_hover_fill=ACCENT_COLOR_HOVER,
                text_color=TEXT_COLOR,
                mode="toggle",
            )

            def make_handler(command_name: str):
                def handler():
                    # Use high-level set_source where possible so Epson
                    # cycle keys behave as expected for human labels.
                    try:
                        self.proj.set_source(command_name)
                        self._radio_switch(btn)
                    except Exception:
                        # Fallback to raw command if mapping fails
                        try:
                            self.proj.toggle(command_name)
                            self._radio_switch(btn)
                        except Exception as e:
                            btn.state = True
                            ntk.standard_methods.toggle_object_toggle(btn)
                            print(e, "reached iamanexception")

                return handler

            btn.command = make_handler(name)
            btn.place(x=x, y=y_start)
            self.source_buttons.append(btn)
            return btn

        for name, cmd in commands.items():
            if cmd.get("type") not in ("source", "source_cycle"):
                continue

            if cmd.get("type") == "source_cycle":
                for target in self.proj.get_targets(name):
                    build_button(x, target, cmd)
                    if x >= (BUTTON_SPACING + BUTTON_WIDTH) * 3:
                        x = FRAME_SPACING
                        y_start += BUTTON_SPACING + BUTTON_HEIGHT
                    else:
                        x += BUTTON_SPACING + BUTTON_WIDTH

            else:
                build_button(x, name, cmd)
                x += BUTTON_SPACING + BUTTON_WIDTH
        return y_start + BUTTON_SPACING + BUTTON_HEIGHT

    def _radio_switch(self, new_active_button: ntk.Button):
        for button in self.source_buttons:
            if (
                button == new_active_button
                and button.state != True
                or button != new_active_button
                and button.state != False
            ):
                ntk.standard_methods.toggle_object_toggle(button)

    def _build_features_section(self, y_start: int):
        # Features are commands where type == "feature" or "toggle"
        commands = self.proj.projector_lib.commands
        self.feature_buttons = []

        x = 8
        for name, cmd in commands.items():
            if cmd.get("type") not in ("feature", "toggle"):
                continue

            btn = ntk.Button(
                self,
                text=name,
                font=("Arial", self.max_font_size, "bold"),
                width=BUTTON_WIDTH,
                height=BUTTON_HEIGHT,
                fill=DISABLED_COLOR,
                border=DISABLED_COLOR_HOVER,
                border_width=2,
                hover_fill=DISABLED_COLOR_HOVER,
                active_fill=ACCENT_COLOR,
                active_hover_fill=ACCENT_COLOR_HOVER,
                text_color=TEXT_COLOR,
                mode="toggle",
            )

            def make_handler(command_name: str):
                def handler():
                    try:
                        self.proj.toggle(command_name)
                    except Exception as e:
                        print(e, "iamanexception")
                        ntk.standard_methods.toggle_object_toggle(btn)

                return handler

            btn.command = make_handler(name)
            btn.place(x=x, y=y_start)
            self.feature_buttons.append(btn)
            x += BUTTON_SPACING + BUTTON_WIDTH

    def _build_power_section(self, x_right: int, y_center: int):
        # Frame width assumed 240; power button sized 48x48
        size = 48
        self.power_button = ntk.Button(
            self,
            image=self.power_icon_off,
            active_image=self.power_icon_on,
            hover_image=self.power_icon_off_hover,
            active_hover_image=self.power_icon_on_hover,
            width=size,
            height=size,
            mode="toggle",
            bounds_type="box",
        )

        def on_power():
            # Button's active state determines desired power
            if self.power_button.state:
                self.proj.on()
            else:
                self.proj.off()

            self._sync_initial_state()

        self.power_button.command = on_power
        self.power_button.place(x=x_right - size, y=y_center - size // 2)

    # ----------------------------------------------------------------- State
    def _sync_initial_state(self):
        """
        Query the projector and update power button and any other default state.
        """
        try:
            is_on = self.proj.status()
        except Exception:
            is_on = False

        if is_on and not self.power_button.state:
            # Toggle to "on" without triggering callback
            ntk.standard_methods.toggle_object_toggle(self.power_button)
        elif (not is_on) and self.power_button.state:
            ntk.standard_methods.toggle_object_toggle(self.power_button)

        try:
            current_source = self.proj.source()
        except Exception as e:
            print(e, "iamanexception")
            current_source = None
        print(current_source)
        if current_source:
            for button in self.source_buttons:
                if button.text.lower().replace(
                    " ", ""
                ) == current_source.lower().replace(" ", ""):
                    self._radio_switch(button)
                    break


def load_projectors_from_json(path: str = "data.json") -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Only use resolved projectors for full control
    return data.get("resolved", [])


def create_app():
    # Load projector definitions
    projector_defs = load_projectors_from_json()

    # Simple layout: vertical stack of controller frames
    frames = []
    frame_height = FRAME_HEIGHT
    window_height = max(frame_height * len(projector_defs), frame_height)
    window_width = WINDOW_WIDTH

    window = ntk.Window(
        title="Projector Controller", width=window_width, height=window_height
    )

    background = ntk.Frame(
        window, fill=WINDOW_BACKGROUND, width=window_width, height=window_height
    )
    background.place()

    for idx, meta in enumerate(projector_defs):
        ip = meta["ip"]
        proj_type = meta["projector_type"]

        proj = Projector(ip, proj_type)

        frame = ProjectorControllerFrame(
            background,
            proj,
            meta,
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
        )
        frames.append(frame)
        window_height += frame.height - FRAME_HEIGHT + FRAME_SPACING * 2

        window.resize(window_width, window_height)
        background.configure(height=window_height)
        frame.place(
            x=FRAME_SPACING, y=FRAME_SPACING + idx * (FRAME_HEIGHT + FRAME_SPACING)
        )
        frame.show()

    def _save_names_and_close():
        """
        Persist any edited projector names back to data.json before closing.
        """
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

        resolved = data.get("resolved", [])

        # Update entries in order; if the JSON has fewer entries than frames,
        # update only what exists.
        for idx, frame in enumerate(frames):
            if idx >= len(resolved):
                break
            name_value = frame.name_label.get()

            if name_value:
                resolved[idx]["name"] = str(name_value)

        data["resolved"] = resolved

        with contextlib.suppress(Exception):
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        window.root.destroy()

    # Ensure that closing the window saves any edited names.
    with contextlib.suppress(Exception):
        window.root.protocol("WM_DELETE_WINDOW", _save_names_and_close)
    return window


if __name__ == "__main__":
    app = create_app()
