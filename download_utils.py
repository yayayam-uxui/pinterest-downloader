import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


def is_valid_pinterest_url(raw_url: str) -> bool:
    parsed = urlparse(raw_url.strip())
    if parsed.scheme not in {"http", "https"}:
        return False

    host = parsed.netloc.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]

    if host != "pinterest.com" and not host.endswith(".pinterest.com"):
        return False

    return bool(parsed.path.strip("/"))


def resolve_download_file(
    downloads_dir: Path, filename: str, zip_extension: str = ".zip"
) -> Optional[Path]:
    normalized_name = Path(filename).name
    if normalized_name != filename or "\\" in filename:
        return None

    if not normalized_name.endswith(zip_extension):
        return None

    try:
        uuid.UUID(Path(normalized_name).stem)
    except ValueError:
        return None

    return downloads_dir / normalized_name


def has_downloaded_files(folder_path: Path) -> bool:
    return any(item.is_file() for item in folder_path.rglob("*"))


def safe_remove_file(file_path: Path) -> None:
    try:
        file_path.unlink()
    except FileNotFoundError:
        pass
