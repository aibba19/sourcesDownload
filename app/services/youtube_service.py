from collections.abc import Callable
from pathlib import Path

from yt_dlp import YoutubeDL

from app.domain.models import VideoMetadata
from app.utils.filename import sanitize_filename


class YouTubeService:
    def __init__(self, output_dir: Path, max_height: int = 1080):
        self.output_dir = output_dir
        self.max_height = max_height

    def extract_metadata(self, url: str) -> VideoMetadata:
        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
        }

        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        title = info.get("title") or "youtube_video"
        file_name = f"{sanitize_filename(title)}.mp4"
        channel_url = info.get("uploader_url")
        channel_id = info.get("channel_id")

        if not channel_url and channel_id:
            channel_url = f"https://www.youtube.com/channel/{channel_id}"

        return VideoMetadata(
            video_id=info.get("id") or "",
            title=title,
            video_url=info.get("webpage_url") or url,
            channel_name=info.get("channel") or info.get("uploader") or "Unknown channel",
            channel_url=channel_url or "",
            duration_seconds=info.get("duration"),
            upload_date=info.get("upload_date"),
            description=info.get("description"),
            output_file_name=file_name,
            output_file_path=self.output_dir / file_name,
        )

    def download_mp4(self, metadata: VideoMetadata, progress_callback: Callable[[float], None] | None = None) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        def report_progress(download_status: dict):
            if progress_callback is None:
                return

            status = download_status.get("status")
            if status == "finished":
                progress_callback(100.0)
                return

            if status != "downloading":
                return

            downloaded = download_status.get("downloaded_bytes")
            total = download_status.get("total_bytes") or download_status.get("total_bytes_estimate")

            if not downloaded or not total:
                return

            percentage = (downloaded / total) * 100
            progress_callback(percentage)

        output_template = str(self.output_dir / "%(title)s.%(ext)s")
        options = {
            "outtmpl": output_template,
            "format": f"bestvideo[height<={self.max_height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={self.max_height}][ext=mp4]/best",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": False,
            "restrictfilenames": False,
            "progress_hooks": [report_progress],
        }

        with YoutubeDL(options) as ydl:
            ydl.download([metadata.video_url])

        if metadata.output_file_path.exists():
            return metadata.output_file_path

        candidates = sorted(self.output_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            raise FileNotFoundError("Download completed but no MP4 file found in output directory.")

        latest = candidates[0]
        return latest
