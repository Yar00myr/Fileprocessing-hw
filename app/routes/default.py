import os
import uuid
import asyncio
from typing import List
from fastapi import APIRouter, UploadFile, BackgroundTasks, HTTPException
from ..logging import logger


MAX_FILE_SIZE = 5 * 1024 * 1024
UPLOAD_FOLDER = "saved_files/"
FORMATS = [
    "image/png",
    "image/jpg",
]
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

file_router = APIRouter(prefix="/file")


async def save_image(file_path: str, img: bytes):
    await asyncio.sleep(2)
    with open(file_path, "wb") as buffer:
        buffer.write(img)


@file_router.post("/upload")
async def upload(file: List[UploadFile], background_tasks: BackgroundTasks):
    file_id = str(uuid.uuid4())
    folder = os.path.join(UPLOAD_FOLDER, file_id)
    os.mkdir(folder)
    logger.info(f"Created folder for request: {folder}")

    img = []

    for images in file:
        if images.content_type in FORMATS and images.size < MAX_FILE_SIZE:
            img.append(f"{images.filename} {images.size} bytes")
            background_tasks.add_task(
                save_image,
                file_path=f"{folder}/{images.filename}",
                img=images.file.read(),
            )
    return {
        "filenames": img,
        "id": file_id,
    }


@file_router.get("/list_of_saved_files/{file_id}")
async def saved_files(file_id: str):
    folder = os.path.join(UPLOAD_FOLDER, file_id)

    if not os.path.exists(folder):
        logger.error(f"No folder found for file ID {file_id}")
        raise HTTPException(
            status_code=404,
            detail=f"No files found for file ID {file_id}.",
        )

    files = os.listdir(folder)
    if not files:
        logger.warning(f"No files found in folder: {folder}")
        raise HTTPException(status_code=404, detail="No files found in the directory.")

    logger.info(f"Files found: {files}")
    return {"files": files}
