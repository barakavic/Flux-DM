from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem

class DownloadItem(Static):
    def render(self) -> str:
        return "Filename.zip | []60% | 2MB/s"
    
class FluxDM(App):

    BINDINGS = [("q", "quit", "Quit"), ("a", "add", "Add Download")]
    CSS = """
    Screen{
    align: center middle;
    }
    DownloadItem{
        background: $boost;
        margin: 1;
        padding: 1;
        border: solid green;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ListView(
            ListItem(DownloadItem()),
            ListItem(DownloadItem()),
            id="download-list"
        )
        yield Footer()

    def action_add(self) -> None:
        self.notify("Download link detected!")

if __name__ == "__main__":
    app = FluxDM()
    app.run()