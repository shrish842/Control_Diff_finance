from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from controldiff.api.deps import get_db
from controldiff.config import settings
from controldiff.domain.enums import ReviewDecisionType
from controldiff.services.regulation_service import get_run, list_runs
from controldiff.services.report_service import build_report
from controldiff.services.review_service import apply_review_decision

WEB_DIR = Path(__file__).resolve().parents[2] / "web"
TEMPLATES = Jinja2Templates(directory=str(WEB_DIR / "templates"))

router = APIRouter(prefix="/ui", tags=["ui"], include_in_schema=False)


def _mode_label() -> str:
    return "OpenAI Mode" if settings.openai_api_key else "Local Demo"


def _status_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


@router.get("/runs", response_class=HTMLResponse)
def runs_dashboard(request: Request, session: Session = Depends(get_db)) -> HTMLResponse:
    run_cards: list[dict[str, object]] = []

    for run in list_runs(session):
        report = build_report(session, run)
        regulation = report.get("regulation", {})
        run_cards.append(
            {
                "id": run.id,
                "title": regulation.get("title", "Untitled regulation"),
                "source": regulation.get("source", "unknown"),
                "status": _status_value(run.status),
                "confidence": float(run.confidence or 0.0),
                "review_required": bool(run.review_required),
                "obligations_count": len(report.get("obligations", [])),
                "mappings_count": len(report.get("mappings", [])),
            }
        )

    summary = {
        "total_runs": len(run_cards),
        "review_required": sum(1 for item in run_cards if item["review_required"]),
        "approved": sum(1 for item in run_cards if item["status"] == "approved"),
    }

    return TEMPLATES.TemplateResponse(
        request=request,
        name="runs.html",
        context={
            "page_title": "ControlDiff Analyst Desk",
            "mode_label": _mode_label(),
            "summary": summary,
            "runs": run_cards,
        },
    )


@router.get("/runs/{run_id}", response_class=HTMLResponse)
def run_detail_page(run_id: str, request: Request, session: Session = Depends(get_db)) -> HTMLResponse:
    run = get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    report = build_report(session, run)
    payload = report.get("payload", {})

    regulation = report.get(
        "regulation",
        {
            "id": getattr(run.regulation, "id", ""),
            "title": getattr(run.regulation, "title", "Untitled regulation"),
            "source": getattr(run.regulation, "source", "unknown"),
            "body_text": getattr(run.regulation, "body_text", ""),
        },
    )

    return TEMPLATES.TemplateResponse(
        request=request,
        name="run_detail.html",
        context={
            "page_title": f"Run {run.id}",
            "mode_label": _mode_label(),
            "run": {
                "id": run.id,
                "status": _status_value(run.status),
                "confidence": float(run.confidence or 0.0),
                "review_required": bool(run.review_required),
                "final_report": str(report.get("final_report", "")),
            },
            "regulation": regulation,
            "obligations": report.get("obligations", []),
            "mappings": report.get("mappings", []),
            "critic_notes": report.get("critic_notes", payload.get("critic_notes", [])),
            "replay_summary": report.get("replay_summary", payload.get("replay_summary", {})),
            "diffs": report.get("diffs", payload.get("diffs", [])),
            "reviews": report.get("reviews", []),
            "can_review": _status_value(run.status) not in {"approved", "rejected"},
        },
    )


@router.post("/runs/{run_id}/review")
def submit_review(
    run_id: str,
    reviewer: str = Form(...),
    decision: ReviewDecisionType = Form(...),
    notes: str = Form(""),
    session: Session = Depends(get_db),
) -> RedirectResponse:
    run = get_run(session, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    apply_review_decision(
        session=session,
        run=run,
        reviewer=reviewer,
        decision=decision,
        notes=notes,
    )
    return RedirectResponse(url=f"/ui/runs/{run_id}", status_code=303)
