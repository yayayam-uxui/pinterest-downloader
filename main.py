from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess, uuid, shutil, os
from fastapi import BackgroundTasks

app = FastAPI()

# Mount static files under /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create downloads folder if it doesn't exist
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Serve the homepage (index.html)
@app.get("/")
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# Handle the POST request to download Pinterest board
@app.post("/download")
async def download_pinterest_board(request: Request):
    try:
        data = await request.json()
        board_url = data.get("board_url")

        if not board_url:
            return JSONResponse(status_code=400, content={"detail": "Missing Pinterest board URL."})

        session_id = str(uuid.uuid4())
        folder_path = os.path.join(DOWNLOADS_DIR, session_id)
        os.makedirs(folder_path, exist_ok=True)

        # Run gallery-dl to download the board
        result = subprocess.run(["gallery-dl", "-d", folder_path, board_url], capture_output=True, text=True)

        if result.returncode != 0:
            return JSONResponse(status_code=500, content={"detail": "Gallery-dl error", "error": result.stderr})

        # Zip the downloaded folder
        zip_file_path = shutil.make_archive(folder_path, 'zip', folder_path)
        zip_filename = os.path.basename(zip_file_path)

        # Clean up original folder after zipping
        shutil.rmtree(folder_path)

        return {"download_url": f"/downloads/{zip_filename}"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# Serve the zip file for download
@app.get("/downloads/{filename}")
async def get_download(filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(DOWNLOADS_DIR, filename)
    
    if os.path.exists(file_path):
        # Schedule file cleanup after response is sent
        background_tasks.add_task(os.remove, file_path)
        
        return FileResponse(file_path, media_type="application/zip", filename=filename)

    return JSONResponse(status_code=404, content={"detail": "File not found"})



if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
