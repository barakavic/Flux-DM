from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, ProgressBar, Label
from textual.containers import Container, Vertical
from ui_components import SaveAsModal


class FluxDM(App):

    BINDINGS = [("q", "quit", "Quit"), ("n", "new_download", "New")]
    CSS = """
    #modal-grid {
        grid-size: 2;
        grid-gutter: 1;
        padding: 1;
        width: 60;
        height: 15;
        border: thick $accent;
        background: $surface;
        align: center middle;
    }
    #question { column-span: 2; height: 1fr; content-align: center middle; }
    #dir-select { column-span: 2; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="input-container"):
            yield Label("Enter URL to Download:")
            yield Input(placeholder="https//:example.com.file.zip", id="url-input")
        
        with Vertical(id="download-area"):
            yield ProgressBar(total=100, show_eta=True, id="test-bar")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted):
        if event.value:
            self.push_screen(SaveAsModal(), self.begin_download)

    def begin_download(self, save_path: str | None):
        if save_path:
            self.notify(f"Downloading to {save_path}...")

        else:
            self.notify("Download cancelled", severity="warning")

if __name__ == "__main__":
    app = FluxDM()
    app.run()