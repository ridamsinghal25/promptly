from fastapi import APIRouter, Request, Path, Body, UploadFile, File, HTTPException
from src.queue.connection import queue
from src.queue.workers.text_worker import process_text
from src.queue.workers.upload_pdf_worker import upload_pdf
from src.queue.workers.pdf_worker import process_query
import os


router = APIRouter()

MAX_FILE_SIZE = 1024 * 1024 * 5


@router.post("/process-text")
async def process_text_query(request: Request, query: str = Body(..., description="Query")):

    # Add the job to the queue
    job = queue.enqueue(process_text, query)

    # Return the job ID
    return {
        "status": "success",
        "message": "User query added to the queue",
        "job_id": job.id
    }


@router.post("/upload-pdf")
async def upload_user_pdf(file: UploadFile = File(..., description="PDF file")):
    # File path
    file_path = f'src/uploads/{file.filename}'

    print(file.content_type)
    if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are allowed."
        )

    # To keep track of file size
    total_size = 0

    # Save file to disk
    with open(file_path, "wb") as f:
        # Read the uploaded file in small parts (1MB)
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB
            if not chunk:
                break  # Stop when no more data

            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                os.remove(file_path)
                raise HTTPException(
                    status_code=413,
                    detail="File too large (max 5 MB allowed)"
                )

            f.write(chunk)  # Write chunk to file

    # Add the job to the queue
    job = queue.enqueue(upload_pdf, file_path)

    return {
        "status": "success",
        "message": "File uploaded successfully",
        "job_id": job.id
    }


@router.post("/process-pdf")
async def process_pdf(query: str = Body(..., description="The user query")):

    # Add the job to the queue
    job = queue.enqueue(process_query, query)

    # Return the job ID
    return {
        "status": "success",
        "message": "User query added to the queue",
        "job_id": job.id
    }


@router.get("/result/{job_id}")
def get_result(
    job_id: str = Path(..., description="Job ID")
):
    # Get the result from the queue
    job = queue.fetch_job(job_id=job_id)

    # Return the result
    result = job.return_value()

    return {
        "status": "success",
        "message": "Job result",
        "result": result
    }
