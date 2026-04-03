"""Light theme defaults and reusable styles for NebulaTk widgets."""

DEFAULTS = {
    "default_text_color": "#101010",
    "default_fill": "#ffffff",
    "default_border": "#222222",
    # -1 keeps default-bound widgets auto-sized by NebulaTk.
    "default_font": ("Helvetica", -1, "normal"),
    "default_window_background": "#f4f7ff",
}

STYLES = {
    "controller_frame": {
        "fill": "#ffffff",
    },
    "surface": {
        "fill": "#f4f7ff",
    },
    "label_transparent": {
        "fill": "#00000000",
        "text_color": "default",
        "font": "default",
    },
    "toggle_button": {
        "fill": "#d7e8ff",
        "hover_fill": "#bfd6f3",
        "active_fill": "#e9f6d2",
        "active_hover_fill": "#d2e9b8",
        "text_color": "#112244",
        "border": "#4477aa",
        "border_width": 2,
        "font": ("Helvetica", 13, "bold"),
    },
    "settings_backdrop": {
        "fill": "#0f172a3A",
        "border_width": 0,
    },
    "settings_panel": {
        "fill": "#ffffff",
        "border": "#4477aa",
        "border_width": 2,
    },
    "settings_entry": {
        "fill": "#ffffff",
        "border": "#4477aa",
        "border_width": 2,
        "text_color": "default",
        "font": ("Helvetica", 13, "normal"),
    },
    "settings_dropdown": {
        "fill": "#d7e8ff",
        "border": "#4477aa",
        "border_width": 2,
    },
    "settings_dropdown_list": {
        "fill": "#ffffff",
        "border": "#4477aa",
        "border_width": 2,
    },
    "dropdown_option": {
        "fill": "#00000000",
        "hover_fill": "#d7e8ff",
        "text_color": "#112244",
        "font": ("Helvetica", 13, "normal"),
    },
    "button_accent": {
        "extends": "toggle_button",
        "fill": "#4d84c4",
        "hover_fill": "#3f72ad",
        "active_fill": "#3f72ad",
        "active_hover_fill": "#4d84c4",
        "text_color": "#ffffff",
    },
    "button_neutral": {
        "extends": "toggle_button",
        "fill": "#d7e8ff",
        "hover_fill": "#bfd6f3",
        "active_fill": "#d7e8ff",
        "active_hover_fill": "#bfd6f3",
    },
    "message_error": {
        "fill": "#00000000",
        "text_color": "#b00020",
        "font": ("Helvetica", 10, "normal"),
    },
    "overlay_label": {
        "fill": "#f4f7ffC8",
        "text_color": "default",
        "font": ("Helvetica", 20, "bold"),
    },
}
