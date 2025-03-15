import os
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.dependencies import get_current_user
from app.models.user import User
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/user/style-reference", status_code=status.HTTP_201_CREATED)
async def upload_user_style_reference(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file to analyze the specialist's writing style.
    Accepts PDF, DOCX, and TXT files.
    """
    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX, and TXT files are allowed"
        )
    
    # Prepare file path with timestamp to avoid overwrites
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = FileService.get_user_files_path(current_user.email, "style_reference") / filename
    
    # Save file
    await file.seek(0)
    FileService.save_binary_file(file_path, file.file)
    
    return {
        "filename": filename,
        "content_type": file.content_type,
        "size": os.path.getsize(file_path)
    }


@router.post("/client/{client_id}/reference-content", status_code=status.HTTP_201_CREATED)
async def upload_client_reference_content(
    client_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file to analyze the client's past content.
    Accepts PDF, DOCX, and TXT files.
    """
    # Validate client exists
    client_path = FileService.get_client_path(current_user.email, client_id)
    if not os.path.exists(client_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX, and TXT files are allowed"
        )
    
    # Prepare file path with timestamp to avoid overwrites
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = FileService.get_client_files_path(current_user.email, client_id, "reference_content") / filename
    
    # Save file
    await file.seek(0)
    FileService.save_binary_file(file_path, file.file)
    
    return {
        "filename": filename,
        "content_type": file.content_type,
        "size": os.path.getsize(file_path)
    }


@router.get("/user/style-reference", response_model=List[str])
async def list_user_style_references(
    current_user: User = Depends(get_current_user)
):
    """
    List all style reference files for the current specialist.
    """
    return FileService.list_user_files(current_user.email, "style_reference")


@router.get("/client/{client_id}/reference-content", response_model=List[str])
async def list_client_reference_content(
    client_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    List all reference content files for a specific client.
    """
    # Validate client exists
    client_path = FileService.get_client_path(current_user.email, client_id)
    if not os.path.exists(client_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    return FileService.list_client_files(current_user.email, client_id, "reference_content")


@router.get("/user/style-reference/{filename}")
async def download_user_style_reference(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a specific style reference file.
    """
    file_path = FileService.get_user_files_path(current_user.email, "style_reference") / filename
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.get("/client/{client_id}/reference-content/{filename}")
async def download_client_reference_content(
    client_id: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a specific client reference content file.
    """
    # Validate client exists
    client_path = FileService.get_client_path(current_user.email, client_id)
    if not os.path.exists(client_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    file_path = FileService.get_client_files_path(current_user.email, client_id, "reference_content") / filename
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.delete("/user/style-reference/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_style_reference(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific style reference file.
    """
    file_path = FileService.get_user_files_path(current_user.email, "style_reference") / filename
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )
    
    os.remove(file_path)
    return None


@router.delete("/client/{client_id}/reference-content/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_reference_content(
    client_id: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific client reference content file.
    """
    # Validate client exists
    client_path = FileService.get_client_path(current_user.email, client_id)
    if not os.path.exists(client_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    file_path = FileService.get_client_files_path(current_user.email, client_id, "reference_content") / filename
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )
    
    os.remove(file_path)
    return None