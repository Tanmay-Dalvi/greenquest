"""Safety Agent: Combines deterministic guardrails with schema validation."""
from typing import List, Dict, Any
from backend.app.models.mission import SafetyReview
from backend.app.orchestrator.state import ActivityDraft
from backend.app.orchestrator.rules import evaluate_mission_safety


class SafetyValidatorAgent:
    """Zero-trust safety auditor. LLM output is always audited deterministically."""

    def validate(self, activity_draft: ActivityDraft) -> SafetyReview:
        # Run deterministic rule engine
        review = evaluate_mission_safety(
            title=activity_draft.title,
            steps=activity_draft.steps,
            leave_no_trace=activity_draft.leave_no_trace_principle,
            safety_notes=activity_draft.safety_notes,
        )

        return review

