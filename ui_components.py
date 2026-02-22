from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select

from engine import DownloadEngine


class SaveAsModal(ModalScreen):
    CSS = """
    #modal-grid {
        grid-size: 2;
        grid-gutter: 1;
        padding: 1;
        width: 76;
        height: 16;
        border: thick $accent;
        background: $surface;
        align: center middle;
    }
    #question {
        column-span: 2;
        height: 1fr;
        content-align: center middle;
    }
    #dir-select {
        column-span: 2;
    }
    #file-name {
        column-span: 2;
    }
    """

    def __init__(self, default_filename: str):
        super().__init__()
        self.default_filename = default_filename

    def compose(self):
        options = []
        for loc in DownloadEngine.get_save_locations():
            info = DownloadEngine.get_disk_usage(loc)
            label = f"{loc} ({info['free']}GB free)"
            options.append((label, loc))

        with Grid(id="modal-grid"):
            yield Label("Where should this file be saved?", id="question")
            yield Select(options, prompt="Choose a disk/folder", id="dir-select")
            yield Input(value=self.default_filename, placeholder="File name", id="file-name")
            yield Button("Start Download", variant="success", id="start")
            yield Button("Cancel", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "start":
            selected_path = self.query_one("#dir-select", Select).value
            file_name = self.query_one("#file-name", Input).value.strip()
            if selected_path:
                self.dismiss({"save_path": selected_path, "file_name": file_name})
                return
        self.dismiss(None)
