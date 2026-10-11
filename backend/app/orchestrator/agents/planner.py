"""Planner Agent: Designs overarching outdoor theme, narrative arc, and step pacing."""
import json
import logging
from typing import Dict, Any
from backend.app.models.mission import MissionPreferenceRequest
from backend.app.models.provider import ProviderCompletionRequest
from backend.app.providers.base import ModelProvider
from backend.app.orchestrator.state import PlannerDraft
from backend.app.orchestrator.repair import clean_and_repair_json

logger = logging.getLogger(__name__)

PLANNER_RESPONSE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "theme": {"type": "string"},
        "narrative_arc": {"type": "string"},
        "target_step_count": {"type": "integer"},
        "difficulty": {"type": "string"},
        "allocated_minutes": {"type": "integer"},
    },
    "required": ["theme", "narrative_arc", "target_step_count", "difficulty", "allocated_minutes"],
}

SYSTEM_PROMPT = """You are the GreenQuest Outdoor Adventure Planner.
Your goal is to get people off their screens and immersed in nature (parks, gardens, forests, neighborhoods).
Given user preferences (environment, duration, mood, energy, companions, senses), produce a high-level plan.
Always respond strictly in valid JSON matching this schema:
{
  "theme": "A poetic, inspiring 3-6 word theme name",
  "narrative_arc": "One sentence explaining the progression from arrival to grounding to departure",
  "target_step_count": 3,
  "difficulty": "easy",
  "allocated_minutes": 30
}
Do not include any explanation or markdown formatting outside the JSON object.
"""


class PlannerAgent:
    def __init__(self, provider: ModelProvider):
        self.provider = provider

    async def plan(self, prefs: MissionPreferenceRequest) -> PlannerDraft:
        target_steps = 2 if prefs.duration_minutes <= 15 else (3 if prefs.duration_minutes <= 40 else 4)

        prompt = (
            f"Plan an outdoor micro-adventure with these parameters:\n"
            f"- Environment: {prefs.environment.value}\n"
            f"- Duration: {prefs.duration_minutes} minutes\n"
            f"- Mood: {prefs.mood.value}\n"
            f"- Energy Level: {prefs.energy_level.value}\n"
            f"- Companion: {prefs.companion_type.value}\n"
            f"- Sensory Focus: {', '.join(s.value for s in prefs.sensory_focus)}\n"
            f"- Notes / Context: {prefs.notes or 'None'}\n"
            f"- Target step count: {target_steps}\n"
            f"Respond with exact JSON."
        )

        request = ProviderCompletionRequest(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            json_mode=True,
            response_schema=PLANNER_RESPONSE_SCHEMA,
            temperature=0.3,
            max_tokens=350,
        )

        raw_output = await self.provider.generate(request)
        try:
            data = clean_and_repair_json(raw_output)
            return PlannerDraft(
                theme=str(data.get("theme", f"{prefs.mood.value.capitalize()} {prefs.environment.value.capitalize()} Quest")),
                narrative_arc=str(data.get("narrative_arc", "Arrive, observe surroundings, and reflect in the open air.")),
                target_step_count=int(data.get("target_step_count", target_steps)),
                difficulty=str(data.get("difficulty", "easy")),
                allocated_minutes=prefs.duration_minutes,
            )
        except Exception as exc:
            logger.warning("Planner JSON parsing failed (%s), using structured default", str(exc))
            return PlannerDraft(
                theme=f"{prefs.mood.value.capitalize()} {prefs.environment.value.capitalize()} Quest",
                narrative_arc="Transition from screen time to sensory exploration and departure.",
                target_step_count=target_steps,
                difficulty="easy",
                allocated_minutes=prefs.duration_minutes,
            )

