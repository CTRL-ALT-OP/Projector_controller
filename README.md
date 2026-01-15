# Projector Controller

## Adding a new projector type
- Create a new module in `projectors/` (e.g., `projectors/sony.py`). The filename becomes the projector type shown in the settings dropdown.
- Export the same pieces as the existing modules (`projectors/christie.py`, `projectors/epson.py`, `projectors/test_projector.py`):
  - `default_login`: `{"username": "...", "password": "..."}` used by auto-discovery and command URLs.
  - `control_page` and `req_headers`: paths/headers probed by `auto_discover.py` to identify the device.
  - `commands`: a dict of remote-control actions. Each entry needs `type` (`"power"`, `"source"`, `"source_cycle"`, `"feature"`, or `"toggle"`), HTTP `mode` (`"get"`/`"post"`), `duplicate` flag (send twice), `path`, `default_kvjoiner`, `default_kjoiner`, and `params` (list of `[key, value]`; use `"$$time"` to inject a timestamp).
  - `request_status(user, password, ip)` and `request_source(user, password, ip)` so the UI can sync state.
  - `time()` helper that returns a millisecond timestamp string.
- Optional helpers:
  - `TARGET_TO_CYCLE_COMMAND` mapping for cycle-based source buttons (see Epson).
  - `handle_command(command_name, projector_instance)` if the module should run in-process instead of issuing HTTP (see `projectors/test_projector.py`).
- Once the file exists, restart the app; `main.py` auto-lists modules in `projectors/` for the settings dropdown and auto-discovery.

## Changing projector settings at runtime
- Launch the app (e.g., `python main.py`). Each projector card shows its friendly name at the top (editable inline).
- Click the gear icon to open settings. You can update IP address, projector type (dropdown populated from the `projectors/` folder), and credentials.
- Click `Save` to apply changes to the running controller; `Cancel` to discard. Friendly names and updated metadata are written back to `data.json` when you close the window.

## Using the controls
- **Power**: The circular power icon on the right toggles on/off and tries to reflect the live status when the app loads.
- **Sources**: Source buttons on the left send direct or cycle-based input commands. The active source stays highlighted; cycle sources advance until the target matches the device’s reported source.
- **Features/Toggles**: Middle-row buttons (e.g., `MUTE`, `BLANK`, `FREEZE`) fire feature/toggle commands.
- A translucent “Loading…” overlay appears while commands are in flight so you know the request is still running.

## Updating
- Utilizes [https://github.com/CTRL-ALT-OP/AutoUpdate]. The frozen file inside the source `updater/` directory is the auto updater, and the entry point for the app. This checks for releases saved to the GitHub repo.

## Building
- Bump the version flag inside the main repo
- Run the `build.py` file. It will build using PyInstaller, so only run on Win11 machines for now, otherwise there will be a conflict in the build version of the updater script and the main executable.
	- The `build.py` file will generate 2 `.zip` files, named `windows_autoupdating.zip` and `windows.zip`.
	- These 2 `.zip` files will be uploaded to the corresponding versioned release on GitHub.
	- Note that the updater only cares about the release flagged as latest under GitHub, so downloading old versions will immediately update if downloaded as the auto-updating version.