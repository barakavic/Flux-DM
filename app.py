from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, ProgressBar, Label
from textual.containers import Container, Vertical


class FluxDM(App):

    BINDINGS = [("q", "quit", "Quit"), ("n", "new_download", "New")]
    CSS = """
    #input-container {
        height: auto;
        margin: 1;
    }
    #download-area{
        border: tall $primary;
        margin: 1;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="input-container"):
            yield Label("Enter URL to Download:")
            yield Input(placeholder="https//:example.com.file.zip", id="url-input")
        
        with Container(id="download-area"):
            yield Label("Active Downloads:")

            yield ProgressBar(total=100, show_eta=True, id="test-bar")

        yield Footer()
    
    def on_mount(self) -> None:
        self.query_one('#url-input').focus()

if __name__ == "__main__":
    app = FluxDM()
    app.run()