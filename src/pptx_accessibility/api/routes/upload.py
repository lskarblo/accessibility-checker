"""Upload endpoints for file handling."""

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a PPTX or PDF file for accessibility checking.

    Args:
        file: Uploaded file (must be .pptx or .pdf)

    Returns:
        Session information including session_id and file_type
    """
    from pptx_accessibility.api.app import session_manager

    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    filename_lower = file.filename.lower()
    if not (filename_lower.endswith(".pptx") or filename_lower.endswith(".pdf")):
        raise HTTPException(
            status_code=400,
            detail="Only .pptx and .pdf files are supported",
        )

    # Read file content
    try:
        content = await file.read()
        file_size = len(content)

        # Create session
        session_id, file_type = await session_manager.create_session(
            filename=file.filename,
            file_content=content,
            file_size=file_size,
        )

        logger.info(
            f"File uploaded: {file.filename} ({file_size} bytes, type: {file_type}, "
            f"session: {session_id})"
        )

        return {
            "session_id": session_id,
            "filename": file.filename,
            "file_type": file_type,
            "file_size": file_size,
            "status": "uploaded",
        }

    except ValueError as e:
        logger.error(f"File type detection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information.

    Args:
        session_id: Session identifier

    Returns:
        Session data
    """
    from pptx_accessibility.api.app import session_manager

    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    try:
        session_data = await session_manager.get_session(session_id)
        return session_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except Exception as e:
        logger.error(f"Failed to retrieve session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete session and all associated files.

    Args:
        session_id: Session identifier

    Returns:
        Confirmation message
    """
    from pptx_accessibility.api.app import session_manager

    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    try:
        await session_manager.delete_session(session_id)
        return {"message": f"Session {session_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
