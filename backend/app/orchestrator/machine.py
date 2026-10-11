"""State Machine Orchestrator for GreenQuest Mission Generation.
Manages multi-agent workflow, bounded retries, deterministic safety validation,
observable execution logging, and automated fallback triggering.
"""
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List
from backend.app.config import settings
from backend.app.models.mission import (
    MissionPreferenceRequest,
    MissionResponse,
    MissionStep,
    GeneratorInfo,
    DifficultyLevel,
    SensoryType,
)
from backend.app.providers.base import (
    ModelProvider,
    ProviderUnavailableError,
    ProviderTimeoutError,
    ProviderError,
)
from backend.app.providers.fallback import DeterministicFallbackProvider
from backend.app.orchestrator.state import (
    OrchestrationState,
    OrchestrationPhase,
    LogStatus,
    ActivityDraft,
)
from backend.app.orchestrator.agents.planner import PlannerAgent
from backend.app.orchestrator.agents.nature_activity import NatureActivityAgent
from backend.app.orchestrator.agents.safety import SafetyValidatorAgent

logger = logging.getLogger(__name__)


class OrchestrationStateMachine:
    """Finite State Machine coordinating agents and fallback safeguards."""

    def __init__(
        self,
        provider: ModelProvider,
        fallback_provider: Optional[DeterministicFallbackProvider] = None,
        max_retries: Optional[int] = None,
    ):
        self.provider = provider
        self.fallback_provider = fallback_provider or DeterministicFallbackProvider()
        self.max_retries = max_retries or settings.MAX_SAFETY_RETRIES

        self.planner_agent = PlannerAgent(self.provider)
        self.activity_agent = NatureActivityAgent(self.provider)
        self.safety_agent = SafetyValidatorAgent()

    async def execute(self, prefs: MissionPreferenceRequest) -> MissionResponse:
        """Execute mission generation lifecycle with observability and error bounds."""
        overall_start = time.perf_counter()
        state = OrchestrationState(
            preferences=prefs,
            max_retries=self.max_retries,
        )

        # 0. Check forced fallback
        if settings.FORCE_FALLBACK or self.provider.name == "fallback":
            return self._trigger_fallback(state, overall_start, "Fallback provider requested / forced")

        try:
            # 1. PLANNING PHASE
            state.current_phase = OrchestrationPhase.PLANNING
            plan_start = time.perf_counter()
            plan_draft = await self.planner_agent.plan(prefs)
            plan_ms = int((time.perf_counter() - plan_start) * 1000)
            state.planner_draft = plan_draft
            state.add_log(
                agent_name="PlannerAgent",
                phase=OrchestrationPhase.PLANNING,
                status=LogStatus.SUCCESS,
                duration_ms=plan_ms,
                summary=f"Planned theme '{plan_draft.theme}' with {plan_draft.target_step_count} steps",
                details=plan_draft.model_dump(),
            )

            # 2. ACTIVITY CRAFTING & SAFETY VALIDATION LOOP
            remediation: Optional[List[str]] = None
            activity_draft: Optional[ActivityDraft] = None

            while state.retry_count <= self.max_retries:
                state.current_phase = OrchestrationPhase.ACTIVITY_GENERATION
                act_start = time.perf_counter()
                try:
                    activity_draft = await self.activity_agent.generate_activities(
                        prefs=prefs,
                        plan=plan_draft,
                        remediation_notes=remediation,
                    )
                except (ProviderUnavailableError, ProviderTimeoutError):
                    raise
                except Exception as exc:
                    act_ms = int((time.perf_counter() - act_start) * 1000)
                    logger.warning(
                        "Activity generation parsing/model error (attempt %d/%d): %s",
                        state.retry_count + 1,
                        self.max_retries,
                        str(exc),
                    )
                    state.retry_count += 1
                    state.add_log(
                        agent_name="NatureActivityAgent",
                        phase=OrchestrationPhase.ACTIVITY_GENERATION,
                        status=LogStatus.RETRY,
                        duration_ms=act_ms,
                        summary=f"Model output format defect: {str(exc)}",
                    )
                    if state.retry_count > self.max_retries:
                        return self._trigger_fallback(
                            state,
                            overall_start,
                            f"Activity generation failed after {self.max_retries} attempts: {str(exc)}",
                        )
                    remediation = [
                        f"Previous output had format error ({str(exc)}). Ensure strictly valid JSON matching schema."
                    ]
                    continue

                act_ms = int((time.perf_counter() - act_start) * 1000)
                state.activity_draft = activity_draft
                state.add_log(
                    agent_name="NatureActivityAgent",
                    phase=OrchestrationPhase.ACTIVITY_GENERATION,
                    status=LogStatus.SUCCESS,
                    duration_ms=act_ms,
                    summary=f"Generated draft '{activity_draft.title}' with {len(activity_draft.steps)} steps",
                )

                # 3. SAFETY VALIDATION PHASE
                state.current_phase = OrchestrationPhase.SAFETY_VALIDATION
                safe_start = time.perf_counter()
                safety_review = self.safety_agent.validate(activity_draft)
                safe_ms = int((time.perf_counter() - safe_start) * 1000)
                state.safety_review = safety_review

                if safety_review.is_safe:
                    state.add_log(
                        agent_name="SafetyValidatorAgent",
                        phase=OrchestrationPhase.SAFETY_VALIDATION,
                        status=LogStatus.SUCCESS,
                        duration_ms=safe_ms,
                        summary="Mission passed all deterministic safety guardrails",
                        details=safety_review.model_dump(),
                    )
                    break
                else:
                    # Safety violation detected
                    state.retry_count += 1
                    remediation = safety_review.violations + safety_review.recommendations
                    state.add_log(
                        agent_name="SafetyValidatorAgent",
                        phase=OrchestrationPhase.SAFETY_VALIDATION,
                        status=LogStatus.RETRY,
                        duration_ms=safe_ms,
                        summary=f"Safety violations found (attempt {state.retry_count}/{self.max_retries}): {len(safety_review.violations)} issues",
                        details={"violations": safety_review.violations},
                    )

                    if state.retry_count > self.max_retries:
                        return self._trigger_fallback(
                            state,
                            overall_start,
                            f"Safety guardrails failed after {self.max_retries} attempts: {'; '.join(safety_review.violations)}",
                        )

            # Assemble final mission
            mission = self._assemble_mission(state, activity_draft, overall_start)
            state.final_mission = mission
            state.current_phase = OrchestrationPhase.COMPLETED
            return mission

        except (ProviderUnavailableError, ProviderTimeoutError, ProviderError) as exc:
            return self._trigger_fallback(state, overall_start, f"Provider error: {str(exc)}")
        except Exception as exc:
            logger.exception("Unexpected exception in orchestrator: %s", str(exc))
            return self._trigger_fallback(state, overall_start, f"Internal orchestration error: {str(exc)}")

    def _assemble_mission(
        self,
        state: OrchestrationState,
        draft: ActivityDraft,
        overall_start: float,
    ) -> MissionResponse:
        """Transform activity draft into validated MissionResponse."""
        elapsed_ms = int((time.perf_counter() - overall_start) * 1000)
        mission_id = f"gq-{state.preferences.environment.value}-{uuid.uuid4().hex[:6]}"

        target_total_mins = state.preferences.duration_minutes
        step_count = len(draft.steps)
        if step_count > 0:
            raw_mins = [max(1, int(s.get("estimated_minutes", 5))) for s in draft.steps]
            raw_sum = sum(raw_mins)
            if raw_sum > 0 and abs(raw_sum - target_total_mins) > 2:
                allocated_mins = []
                remaining = target_total_mins
                for idx, rm in enumerate(raw_mins):
                    if idx == step_count - 1:
                        allocated_mins.append(max(2, remaining))
                    else:
                        share = max(2, round((rm / raw_sum) * target_total_mins))
                        share = min(share, max(2, remaining - (2 * (step_count - idx - 1))))
                        allocated_mins.append(share)
                        remaining -= share
            else:
                allocated_mins = raw_mins
        else:
            allocated_mins = []

        parsed_steps: List[MissionStep] = []
        for i, s in enumerate(draft.steps, start=1):
            raw_sensory = str(s.get("sensory_type", "sight")).lower()
            try:
                sensory_type = SensoryType(raw_sensory)
            except ValueError:
                sensory_type = SensoryType.SIGHT

            step_mins = allocated_mins[i - 1] if i - 1 < len(allocated_mins) else 5

            parsed_steps.append(
                MissionStep(
                    step_number=i,
                    title=str(s.get("title", f"Step {i}")),
                    instruction=str(s.get("instruction", "Observe your surroundings carefully.")),
                    sensory_type=sensory_type,
                    estimated_minutes=max(2, min(60, step_mins)),
                    completed=False,
                )
            )

        return MissionResponse(
            id=mission_id,
            title=draft.title,
            tagline=draft.tagline,
            environment=state.preferences.environment,
            estimated_duration_minutes=state.preferences.duration_minutes,
            difficulty=DifficultyLevel.EASY,
            theme=draft.theme,
            sensory_prompt=draft.sensory_prompt,
            leave_no_trace_principle=draft.leave_no_trace_principle,
            safety_notes=draft.safety_notes,
            steps=parsed_steps,
            generator_info=GeneratorInfo(
                provider=self.provider.name,
                model=self.provider.model_name,
                fallback_used=False,
                generation_time_ms=elapsed_ms,
                safety_validated=True,
            ),
            created_at=datetime.now(timezone.utc),
        )

    def _trigger_fallback(
        self,
        state: OrchestrationState,
        overall_start: float,
        reason: str,
    ) -> MissionResponse:
        """Gracefully switch to deterministic fallback generator."""
        fallback_start = time.perf_counter()
        state.current_phase = OrchestrationPhase.FALLBACK
        state.fallback_used = True
        state.fallback_reason = reason

        mission = self.fallback_provider.generate_mission_sync(state.preferences)
        total_ms = int((time.perf_counter() - overall_start) * 1000)

        mission.generator_info.generation_time_ms = total_ms
        mission.generator_info.fallback_used = True

        state.add_log(
            agent_name="DeterministicFallbackProvider",
            phase=OrchestrationPhase.FALLBACK,
            status=LogStatus.FALLBACK_TRIGGERED,
            duration_ms=int((time.perf_counter() - fallback_start) * 1000),
            summary=f"Triggered fallback generation: {reason}",
            details={"fallback_reason": reason},
        )

        state.final_mission = mission
        state.current_phase = OrchestrationPhase.COMPLETED
        return mission
