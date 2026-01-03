from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid

from app.services.storage_service import StorageService

router = APIRouter(prefix="/storage")


@router.post("/upload")
def upload_file_to_s3(file: UploadFile = File(...)):
    """Upload a file to S3 and return the file URL."""
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # preserve extension if present
    ext = ""
    if file.filename and "." in file.filename:
        ext = "." + file.filename.rsplit(".", 1)[1]

    filename = f"{uuid.uuid4().hex}{ext}"
    url = StorageService.upload_to_s3(file, filename)
    return {"url": url}
