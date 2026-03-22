import asyncio
import os
import shutil
import uuid
from pathlib import Path
from typing import Final

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from download_utils import (
    has_downloaded_files,
    is_valid_pinterest_url,
    resolve_download_file,
    safe_remove_file,
)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DOWNLOADS_DIR = BASE_DIR / "downloads"
MAX_PINS: Final[int] = 500
ZIP_EXTENSION: Final[str] = ".zip"

# Mount static files under /static.
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Create downloads folder if it doesn't exist.
DOWNLOADS_DIR.mkdir(exist_ok=True)


class DownloadRequest(BaseModel):
    board_url: str


async def _scrape_and_download(board_url: str, folder_path: Path) -> list:
    """Use pinterest-dl to scrape and download pins from a board."""
    from pinterest_dl import PinterestDL

    def _run():
        scraper = PinterestDL.with_api(timeout=30, verbose=False)
        return scraper.scrape_and_download(
            url=board_url,
            output_dir=str(folder_path),
            num=MAX_PINS,
            download_streams=True,
        )

    return await asyncio.to_thread(_run)


async def _make_zip_archive(folder_path: Path) -> Path:
    zip_file_path = await asyncio.to_thread(
        shutil.make_archive, str(folder_path), "zip", str(folder_path)
    )
    return Path(zip_file_path)


@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse(path=STATIC_DIR / "index.html")


@app.post("/download")
async def download_pinterest_board(payload: DownloadRequest):
    board_url = payload.board_url.strip()
    if not is_valid_pinterest_url(board_url):
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid Pinterest board URL.",
        )

    session_id = str(uuid.uuid4())
    folder_path = DOWNLOADS_DIR / session_id
    folder_path.mkdir(parents=True, exist_ok=True)

    try:
        results = await _scrape_and_download(board_url, folder_path)
    except Exception as exc:
        shutil.rmtree(folder_path, ignore_errors=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download board: {exc}",
        ) from exc

    if not results or not has_downloaded_files(folder_path):
        shutil.rmtree(folder_path, ignore_errors=True)
        raise HTTPException(
            status_code=404, detail="No downloadable media found for this board."
        )

    try:
        zip_file_path = await _make_zip_archive(folder_path)
    finally:
        shutil.rmtree(folder_path, ignore_errors=True)

    return {"download_url": f"/downloads/{zip_file_path.name}"}


@app.get("/downloads/{filename}")
async def get_download(filename: str, background_tasks: BackgroundTasks):
    file_path = resolve_download_file(DOWNLOADS_DIR, filename, ZIP_EXTENSION)
    if file_path is None:
        raise HTTPException(status_code=400, detail="Invalid file name.")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    background_tasks.add_task(safe_remove_file, file_path)
    return FileResponse(file_path, media_type="application/zip", filename=file_path.name)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
