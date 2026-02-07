import shutil
import os

class DownloadEngine:
    @staticmethod
    def get_disk_usage(path="/"):
        """ Disk Info in Gigs """
        usage = shutil.disk_usage(path)
        return {
            "path": path,
            "total": usage.total // (1024**3),
            "free": usage.free // (1024**3),
            "percent": round((usage.used / usage.total) *100, 1)
        }
    
    @staticmethod
    def get_save_locations():
        """ Ubuntu save paths """
        user = os.getenv("USER")
        locations = ["/", f"/home/{user}"]

        """ External mounted media """
        media_path = f"/media/{user}"
        if os.path.exists(media_path):
            for drive in os.listdir(media_path):
                locations.append(os.path.join(media_path, drive))
        return locations

