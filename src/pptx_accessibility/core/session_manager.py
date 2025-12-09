"""Session management for file uploads and processing."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger


class SessionManager:
    """Manages upload sessions and file storage."""

    def __init__(self, storage_root: Path | str) -> None:
        """Initialize session manager.

        Args:
            storage_root: Root directory for storage
        """
        self.storage_root = Path(storage_root)
        self.uploads_dir = self.storage_root / "uploads"
        self.processed_dir = self.storage_root / "processed"
        self.sessions_dir = self.storage_root / "sessions"
        self.reports_dir = self.storage_root / "reports"

        # Create directories if they don't exist
        for directory in [
            self.uploads_dir,
            self.processed_dir,
            self.sessions_dir,
            self.reports_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    async def create_session(
        self, filename: str, file_content: bytes, file_size: int
    ) -> tuple[str, str]:
        """Create new session and save uploaded file.

        Args:
            filename: Original filename
            file_content: File bytes
            file_size: File size in bytes

        Returns:
            Tuple of (session_id, file_type)
        """
        session_id = str(uuid.uuid4())

        # Detect file type
        file_type = self._detect_file_type(filename, file_content)

        # Create session directory
        session_upload_dir = self.uploads_dir / session_id
        session_upload_dir.mkdir(exist_ok=True)

        # Save uploaded file
        upload_path = session_upload_dir / f"original.{file_type}"
        upload_path.write_bytes(file_content)

        # Create session data
        session_data: dict[str, Any] = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "status": "uploaded",
            "filename": filename,
            "file_type": file_type,
            "metadata": {
                "file_size": file_size,
                "upload_path": str(upload_path),
            },
        }

        await self._save_session(session_id, session_data)

        logger.info(f"Created session {session_id} for file {filename} (type: {file_type})")
        return session_id, file_type

    def _detect_file_type(self, filename: str, content: bytes) -> str:
        """Detect file type from filename and content.

        Args:
            filename: Original filename
            content: File bytes

        Returns:
            'pptx' or 'pdf'

        Raises:
            ValueError: If file type is not supported
        """
        filename_lower = filename.lower()

        # Check by extension first
        if filename_lower.endswith(".pptx"):
            # Verify it's actually a ZIP (PPTX is a ZIP archive)
            if content[:4] == b"PK\x03\x04":
                return "pptx"
        elif filename_lower.endswith(".pdf"):
            # Verify PDF magic bytes
            if content[:4] == b"%PDF":
                return "pdf"

        # Fallback: Check by magic bytes
        if content[:4] == b"PK\x03\x04":
            return "pptx"
        elif content[:4] == b"%PDF":
            return "pdf"

        raise ValueError(f"Unsupported file type: {filename}")

    async def get_session(self, session_id: str) -> dict[str, Any]:
        """Retrieve session data.

        Args:
            session_id: Session identifier

        Returns:
            Session data dictionary

        Raises:
            FileNotFoundError: If session doesn't exist
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            raise FileNotFoundError(f"Session {session_id} not found")

        with open(session_file, "r", encoding="utf-8") as f:
            return json.load(f)

    async def update_session(self, session_id: str, updates: dict[str, Any]) -> None:
        """Update session data.

        Args:
            session_id: Session identifier
            updates: Dictionary of updates to merge
        """
        session_data = await self.get_session(session_id)
        session_data.update(updates)
        await self._save_session(session_id, session_data)

        logger.debug(f"Updated session {session_id}")

    async def _save_session(self, session_id: str, session_data: dict[str, Any]) -> None:
        """Save session data to disk.

        Args:
            session_id: Session identifier
            session_data: Complete session data
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

    async def delete_session(self, session_id: str) -> None:
        """Delete session and all associated files.

        Args:
            session_id: Session identifier
        """
        # Delete session file
        session_file = self.sessions_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()

        # Delete uploaded files
        upload_dir = self.uploads_dir / session_id
        if upload_dir.exists():
            for file in upload_dir.iterdir():
                file.unlink()
            upload_dir.rmdir()

        # Delete processed files
        processed_dir = self.processed_dir / session_id
        if processed_dir.exists():
            for file in processed_dir.iterdir():
                file.unlink()
            processed_dir.rmdir()

        # Delete reports
        report_dir = self.reports_dir / session_id
        if report_dir.exists():
            for file in report_dir.iterdir():
                file.unlink()
            report_dir.rmdir()

        logger.info(f"Deleted session {session_id}")

    def get_upload_path(self, session_id: str, file_type: str) -> Path:
        """Get path to uploaded file.

        Args:
            session_id: Session identifier
            file_type: 'pptx' or 'pdf'

        Returns:
            Path to uploaded file
        """
        return self.uploads_dir / session_id / f"original.{file_type}"

    def get_processed_path(self, session_id: str, file_type: str) -> Path:
        """Get path for processed file.

        Args:
            session_id: Session identifier
            file_type: 'pptx' or 'pdf'

        Returns:
            Path for processed file
        """
        processed_dir = self.processed_dir / session_id
        processed_dir.mkdir(exist_ok=True)
        return processed_dir / f"accessible.{file_type}"

    def get_report_path(self, session_id: str, format: str = "html") -> Path:
        """Get path for report file.

        Args:
            session_id: Session identifier
            format: Report format ('html' or 'pdf')

        Returns:
            Path for report file
        """
        report_dir = self.reports_dir / session_id
        report_dir.mkdir(exist_ok=True)
        return report_dir / f"report.{format}"
