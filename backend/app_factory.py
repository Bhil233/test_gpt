from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import shutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import DATA_IMAGE_DIR, SCRIPT_UPLOADER_WATCH_DIR
from routers import data_monitor_router, detect_router
from services.script_uploader import ScriptUploaderProcessManager


def _clear_directory_files(directory: Path) -> None:
    if not directory.exists():
        return

    for item in directory.iterdir():
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        else:
            try:
                item.unlink()
            except FileNotFoundError:
                pass


def create_app() -> FastAPI:
    uploader_manager = ScriptUploaderProcessManager()
    detected_frames_dir = (Path(__file__).resolve().parent / SCRIPT_UPLOADER_WATCH_DIR).resolve()
    data_image_dir = (Path(__file__).resolve().parent / DATA_IMAGE_DIR).resolve()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _clear_directory_files(detected_frames_dir)
        uploader_manager.start()
        try:
            yield
        finally:
            uploader_manager.stop()
            _clear_directory_files(detected_frames_dir)

    app = FastAPI(title="AI Fire Detection API", lifespan=lifespan)
    app.state.script_uploader_manager = uploader_manager
    detected_frames_dir.mkdir(parents=True, exist_ok=True)
    data_image_dir.mkdir(parents=True, exist_ok=True)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount(
        "/static/detected-frames",
        StaticFiles(directory=str(detected_frames_dir)),
        name="detected_frames",
    )
    app.mount(
        "/static/data-image",
        StaticFiles(directory=str(data_image_dir)),
        name="data_image",
    )
    app.include_router(detect_router)
    app.include_router(data_monitor_router)
    return app
