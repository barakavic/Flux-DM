from textual.screen import ModalScreen
from textual.containers import Grid
from textual.widgets import Button, Label, Select
from engine import DownloadEngine

class SaveAsModal(ModalScreen):
    def compose(self):
        engine = DownloadEngine()

        options = []

        for loc in engine.get_save_locations():
            info = engine.get_disk_usage(loc)
            options.append((f"{loc} ({info['free']}GB Free)", loc))

            with Grid(id="modal-grid"):
                yield Label("Where would you like to save this file", id="question")
                yield Select(options, prompt="Choose a Disk/folder", id="dir-select")
                yield Button("Start Download", variant="success", id="start")
                yield Button("Cancel", variant="error", id="cancel")
    
    def on_button_pressed(self, event):
        if event.button.id == "start":
            selected_path = self.query_one("dir-select").value
            self.dismiss(selected_path)

        else:
            self.dismiss(None)