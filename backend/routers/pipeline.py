"""Pipeline router."""

from fastapi import APIRouter

from services.pipeline_service import get_pipeline_run_summary

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.get("/run-summary")
def pipeline_run_summary():
    """Return pipeline run summary for frontend Databricks showcase."""
    return get_pipeline_run_summary()
