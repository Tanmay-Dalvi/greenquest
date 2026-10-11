"""Orchestrator state definitions and execution observability log types."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.models.mission import (
    MissionPreferenceRequest,
    MissionResponse,
    SafetyReview,
)


class OrchestrationPhase(str, Enum):
    INIT = "INIT"
    PLANNING = "PLANNING"
    ACTIVITY_GENERATION = "ACTIVITY_GENERATION"
    SAFETY_VALIDATION = "SAFETY_VALIDATION"
    FALLBACK = "FALLBACK"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class LogStatus(str, Enum):
    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    FAILED = "FAILED"
    FALLBACK_TRIGGERED = "FALLBACK_TRIGGERED"


class AgentExecutionLog(BaseModel):
    """Observable record of an agent step execution."""
    agent_name: str
    phase: OrchestrationPhase
    status: LogStatus
    duration_ms: int = Field(ge=0)
    summary: str
    details: Optional[Dict[str, Any]] = None


class PlannerDraft(BaseModel):
    """Output from the Planner Agent."""
    theme: str
    narrative_arc: str
    target_step_count: int
    difficulty: str
    allocated_minutes: int


class ActivityDraft(BaseModel):
    """Draft activities from Nature Activity Agent."""
    title: str
    tagline: str
    theme: str
    sensory_prompt: str
    leave_no_trace_principle: str
    safety_notes: List[str]
    steps: List[Dict[str, Any]]


class OrchestrationState(BaseModel):
    """Complete state snapshot of an ongoing mission generation run."""
    preferences: MissionPreferenceRequest
    current_phase: OrchestrationPhase = OrchestrationPhase.INIT
    retry_count: int = 0
    max_retries: int = 2
    planner_draft: Optional[PlannerDraft] = None
    activity_draft: Optional[ActivityDraft] = None
    safety_review: Optional[SafetyReview] = None
    final_mission: Optional[MissionResponse] = None
    execution_logs: List[AgentExecutionLog] = Field(default_factory=list)
    fallback_used: bool = False
    fallback_reason: Optional[str] = None

    def add_log(
        self,
        agent_name: str,
        phase: OrchestrationPhase,
        status: LogStatus,
        duration_ms: int,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.execution_logs.append(
            AgentExecutionLog(
                agent_name=agent_name,
                phase=phase,
                status=status,
                duration_ms=duration_ms,
                summary=summary,
                details=details,
            )
        )

