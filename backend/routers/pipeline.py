"""Pipeline router."""

from __future__ import annotations

from fastapi import APIRouter

from schemas import PipelineRunSummary
from services.pipeline_service import get_pipeline_run_summary

router = APIRouter(tags=["pipeline"])


@router.get("/api/pipeline", response_model=PipelineRunSummary)
@router.get("/api/pipeline/run-summary", response_model=PipelineRunSummary)
def pipeline_run_summary() -> PipelineRunSummary:
    """Return pipeline summary for dashboard showcase."""
    return PipelineRunSummary(**get_pipeline_run_summary())
