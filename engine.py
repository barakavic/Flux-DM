import os
import shutil
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, unquote
from urllib.request import Request, urlopen


@dataclass
class DownloadTask:
    task_id: int
    url: str
    save_dir: str
    file_name: str
    status: str = "queued"
    progress: float = 0.0
    speed_bps: float = 0.0
    total_bytes: Optional[int] = None
    downloaded_bytes: int = 0
    error: Optional[str] = None
    cancel_requested: bool = False
    started_at: float = field(default_factory=time.time)


class DownloadEngine:
    def __init__(self):
        self._lock = threading.Lock()
        self._tasks: dict[int, DownloadTask] = {}
        self._next_id = 1

    @staticmethod
    def get_disk_usage(path: str = "/") -> dict:
        usage = shutil.disk_usage(path)
        return {
            "path": path,
            "total": usage.total // (1024**3),
            "free": usage.free // (1024**3),
            "percent": round((usage.used / usage.total) * 100, 1),
        }

    @staticmethod
    def get_save_locations() -> list[str]:
        user = os.getenv("USER", "")
        locations = ["/", f"/home/{user}"] if user else ["/"]

        if user:
            media_path = f"/media/{user}"
            if os.path.exists(media_path):
                for drive in os.listdir(media_path):
                    locations.append(os.path.join(media_path, drive))

        deduped = []
        for location in locations:
            if os.path.exists(location) and location not in deduped:
                deduped.append(location)
        return deduped

    @staticmethod
    def guess_filename(url: str) -> str:
        parsed = urlparse(url)
        candidate = unquote(Path(parsed.path).name)
        return candidate or "download.bin"

    def create_task(self, url: str, save_dir: str, file_name: Optional[str] = None) -> DownloadTask:
        chosen_name = (file_name or self.guess_filename(url)).strip() or self.guess_filename(url)
        with self._lock:
            task = DownloadTask(
                task_id=self._next_id,
                url=url,
                save_dir=save_dir,
                file_name=chosen_name,
            )
            self._tasks[self._next_id] = task
            self._next_id += 1
            return task

    def start_task(self, task_id: int) -> None:
        worker = threading.Thread(target=self._download_worker, args=(task_id,), daemon=True)
        worker.start()

    def cancel_task(self, task_id: int) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.status in {"queued", "downloading"}:
                task.cancel_requested = True

    def get_tasks(self) -> list[DownloadTask]:
        with self._lock:
            return [DownloadTask(**vars(task)) for task in self._tasks.values()]

    def _download_worker(self, task_id: int) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            task.status = "downloading"

        try:
            os.makedirs(task.save_dir, exist_ok=True)
            destination = os.path.join(task.save_dir, task.file_name)
            req = Request(task.url, headers={"User-Agent": "FluxDM/0.1"})

            with urlopen(req, timeout=30) as response, open(destination, "wb") as out_file:
                content_length = response.headers.get("Content-Length")
                with self._lock:
                    task.total_bytes = int(content_length) if content_length and content_length.isdigit() else None

                chunk_size = 64 * 1024
                last_sample_at = time.time()
                last_sample_bytes = 0

                while True:
                    with self._lock:
                        if task.cancel_requested:
                            task.status = "cancelled"
                            break

                    chunk = response.read(chunk_size)
                    if not chunk:
                        break

                    out_file.write(chunk)

                    now = time.time()
                    with self._lock:
                        task.downloaded_bytes += len(chunk)

                        if task.total_bytes:
                            task.progress = min(100.0, (task.downloaded_bytes / task.total_bytes) * 100)

                        elapsed = now - last_sample_at
                        if elapsed >= 1.0:
                            interval_bytes = task.downloaded_bytes - last_sample_bytes
                            task.speed_bps = interval_bytes / elapsed
                            last_sample_at = now
                            last_sample_bytes = task.downloaded_bytes

                with self._lock:
                    if task.status == "cancelled":
                        task.progress = 0.0
                        if os.path.exists(destination):
                            os.remove(destination)
                    else:
                        task.progress = 100.0
                        task.status = "completed"
                        task.speed_bps = 0.0

        except Exception as exc:  # noqa: BLE001
            with self._lock:
                task.status = "failed"
                task.error = str(exc)
                task.speed_bps = 0.0
