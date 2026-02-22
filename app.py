from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Footer, Header, Input, Label

from engine import DownloadEngine
from ui_components import SaveAsModal


def human_bytes_per_second(value: float) -> str:
    if value <= 0:
        return "-"
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    size = value
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return "-"


class FluxDM(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("n", "focus_url", "New Download"),
    ]

    CSS = """
    #input-container {
        padding: 1;
        height: 5;
    }
    #url-input {
        width: 100%;
    }
    #downloads-label {
        padding-left: 1;
        padding-top: 1;
    }
    #download-table {
        height: 1fr;
        margin: 0 1 1 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.engine = DownloadEngine()
        self.pending_url: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="input-container"):
            yield Label("Enter URL and press Enter")
            yield Input(placeholder="https://example.com/file.iso", id="url-input")
        yield Label("Downloads", id="downloads-label")
        yield DataTable(id="download-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#download-table", DataTable)
        table.add_columns("ID", "File", "Status", "Progress", "Speed", "Save Path")
        self.set_interval(0.5, self.refresh_table)

    def action_focus_url(self) -> None:
        self.query_one("#url-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "url-input":
            return

        url = event.value.strip()
        if not url:
            self.notify("URL cannot be empty", severity="warning")
            return

        self.pending_url = url
        default_name = self.engine.guess_filename(url)
        self.push_screen(SaveAsModal(default_name), self.begin_download)

    def begin_download(self, save_info: dict | None) -> None:
        if not save_info or not self.pending_url:
            self.notify("Download cancelled", severity="warning")
            return

        task = self.engine.create_task(
            url=self.pending_url,
            save_dir=save_info["save_path"],
            file_name=save_info.get("file_name") or None,
        )
        self.engine.start_task(task.task_id)

        self.query_one("#url-input", Input).value = ""
        self.notify(f"Started download #{task.task_id}: {task.file_name}")

    def refresh_table(self) -> None:
        table = self.query_one("#download-table", DataTable)
        table.clear()

        for task in self.engine.get_tasks():
            if task.total_bytes:
                progress_text = f"{task.progress:.1f}%"
            elif task.status == "completed":
                progress_text = "100%"
            else:
                progress_text = "-"

            status = task.status
            if task.status == "failed" and task.error:
                status = f"failed: {task.error[:36]}"

            table.add_row(
                str(task.task_id),
                task.file_name,
                status,
                progress_text,
                human_bytes_per_second(task.speed_bps),
                task.save_dir,
            )


if __name__ == "__main__":
    FluxDM().run()
