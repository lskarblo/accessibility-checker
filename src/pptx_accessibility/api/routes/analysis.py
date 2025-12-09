"""Analysis API routes."""

from typing import Any

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from pptx_accessibility.core.analyzer import AccessibilityAnalyzer
from pptx_accessibility.pptx_access.reader import PPTXReader

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """Request model for analysis."""

    enabled_rules: list[str] | None = None
    config: dict[str, Any] = {}


class AnalyzeResponse(BaseModel):
    """Response model for analysis."""

    session_id: str
    status: str
    total_findings: int
    scores: dict[str, Any]
    findings_by_severity: dict[str, int]
    metadata: dict[str, Any]


@router.post("/{session_id}/analyze", response_model=AnalyzeResponse)
async def analyze_presentation(
    session_id: str,
    request: AnalyzeRequest,
) -> dict[str, Any]:
    """Run accessibility analysis on uploaded presentation.

    Args:
        session_id: Session ID from upload
        request: Analysis configuration

    Returns:
        Analysis results with findings and scores
    """
    from pptx_accessibility.api.app import session_manager

    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    # Get session
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["file_type"] != "pptx":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not yet supported for {session['file_type']} files",
        )

    logger.info(f"Starting analysis for session {session_id}")

    # Get uploaded file path
    file_path = session_manager.storage_root / "uploads" / session_id / session["filename"]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    try:
        # Load presentation
        reader = PPTXReader(file_path)

        # Create analyzer
        analyzer = AccessibilityAnalyzer()

        # Run analysis
        results = await analyzer.analyze_presentation(
            presentation=reader,
            enabled_rules=request.enabled_rules,
            context=request.config,
        )

        # Update session with analysis results
        session["status"] = "analyzed"
        session["analysis"] = results
        await session_manager.update_session(session_id, session)

        logger.info(
            f"Analysis complete: {results['total_findings']} findings, "
            f"score: {results['scores']['overall_score']}"
        )

        return {
            "session_id": session_id,
            "status": "analyzed",
            "total_findings": results["total_findings"],
            "scores": results["scores"],
            "findings_by_severity": results["findings_by_severity"],
            "metadata": results["metadata"],
        }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/{session_id}/findings")
async def get_findings(
    session_id: str,
    severity: str | None = None,
    slide_number: int | None = None,
) -> dict[str, Any]:
    """Get detailed findings from analysis.

    Args:
        session_id: Session ID
        severity: Optional filter by severity (critical, high, medium, low, info)
        slide_number: Optional filter by slide number

    Returns:
        List of findings with optional filtering
    """
    from pptx_accessibility.api.app import session_manager

    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    # Get session
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["status"] != "analyzed":
        raise HTTPException(
            status_code=400, detail="No analysis results available. Run analysis first."
        )

    analysis = session.get("analysis", {})
    findings = analysis.get("findings", [])

    # Apply filters
    if severity:
        findings = [f for f in findings if f["severity"] == severity]

    if slide_number is not None:
        findings = [f for f in findings if f["slide_number"] == slide_number]

    return {
        "session_id": session_id,
        "total_findings": len(findings),
        "findings": findings,
    }


@router.get("/{session_id}/scores")
async def get_scores(
    session_id: str,
) -> dict[str, Any]:
    """Get accessibility scores for a session.

    Args:
        session_id: Session ID

    Returns:
        Accessibility scores and metrics
    """
    from pptx_accessibility.api.app import session_manager

    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    # Get session
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["status"] != "analyzed":
        raise HTTPException(
            status_code=400, detail="No analysis results available. Run analysis first."
        )

    analysis = session.get("analysis", {})

    return {
        "session_id": session_id,
        "scores": analysis.get("scores", {}),
        "metadata": analysis.get("metadata", {}),
    }


@router.get("/rules")
async def get_available_rules() -> dict[str, Any]:
    """Get list of available accessibility rules.

    Returns:
        Dictionary of available rules with descriptions
    """
    analyzer = AccessibilityAnalyzer()
    rules = analyzer.get_available_rules()

    return {
        "total_rules": len(rules),
        "rules": rules,
    }
