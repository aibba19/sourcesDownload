from dataclasses import dataclass
from pathlib import Path


@dataclass
class VideoMetadata:
    video_id: str
    title: str
    video_url: str
    channel_name: str
    channel_url: str
    duration_seconds: int | None
    upload_date: str | None
    description: str | None
    output_file_name: str
    output_file_path: Path
