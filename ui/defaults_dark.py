"""Dark theme defaults and reusable styles for NebulaTk widgets."""

DEFAULTS = {
    "default_text_color": "#ffffff",
    "default_fill": "#242424",
    "default_border": "#3a3a3a",
    # -1 keeps default-bound widgets auto-sized by NebulaTk.
    "default_font": ("Arial", -1, "normal"),
    "default_window_background": "#181818",
}

STYLES = {
    "controller_frame": {
        "fill": "#242424",
    },
    "surface": {
        "fill": "#181818",
    },
    "label_transparent": {
        "fill": "#00000000",
        "text_color": "default",
        "font": "default",
    },
    "toggle_button": {
        "fill": "#6e6e6e",
        "hover_fill": "#4a4a4a",
        "active_fill": "#569e6a",
        "active_hover_fill": "#3e734c",
        "text_color": "default",
        "border": "#4a4a4a",
        "border_width": 2,
        "font": ("Arial", 13, "bold"),
    },
    "settings_backdrop": {
        "fill": "#00000088",
        "border_width": 0,
    },
    "settings_panel": {
        "fill": "#1e1e1e",
        "border": "#3a3a3a",
        "border_width": 2,
    },
    "settings_entry": {
        "fill": "#2c2c2c",
        "border": "#3a3a3a",
        "border_width": 2,
        "text_color": "default",
        "font": ("Arial", 13, "normal"),
    },
    "settings_dropdown": {
        "fill": "#6e6e6e",
        "border": "#4a4a4a",
        "border_width": 2,
    },
    "settings_dropdown_list": {
        "fill": "#1e1e1e",
        "border": "#3a3a3a",
        "border_width": 2,
    },
    "dropdown_option": {
        "fill": "#00000000",
        "hover_fill": "#4a4a4a",
        "text_color": "default",
        "font": ("Arial", 13, "normal"),
    },
    "button_accent": {
        "extends": "toggle_button",
        "fill": "#569e6a",
        "hover_fill": "#3e734c",
        "active_fill": "#3e734c",
        "active_hover_fill": "#569e6a",
    },
    "button_neutral": {
        "extends": "toggle_button",
        "active_fill": "#6e6e6e",
        "active_hover_fill": "#4a4a4a",
    },
    "message_error": {
        "fill": "#00000000",
        "text_color": "#d36c6c",
        "font": ("Arial", 10, "normal"),
    },
    "overlay_label": {
        "fill": "#1818188F",
        "text_color": "default",
        "font": ("Arial", 20, "bold"),
    },
}
