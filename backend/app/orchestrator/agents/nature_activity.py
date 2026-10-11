"""Nature Activity Agent: Crafts tactile, sensory-rich outdoor steps and tasks."""
import json
import logging
from typing import Optional, List, Dict, Any
from backend.app.models.mission import MissionPreferenceRequest
from backend.app.models.provider import ProviderCompletionRequest
from backend.app.providers.base import ModelProvider
from backend.app.orchestrator.state import PlannerDraft, ActivityDraft
from backend.app.orchestrator.repair import clean_and_repair_json, MalformedModelOutputError

logger = logging.getLogger(__name__)

ACTIVITY_RESPONSE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "tagline": {"type": "string"},
        "theme": {"type": "string"},
        "sensory_prompt": {"type": "string"},
        "leave_no_trace_principle": {"type": "string"},
        "safety_notes": {
            "type": "array",
            "items": {"type": "string"},
        },
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_number": {"type": "integer"},
                    "title": {"type": "string"},
                    "instruction": {"type": "string"},
                    "sensory_type": {"type": "string", "enum": ["sight", "sound", "touch", "scent", "spatial"]},
                    "estimated_minutes": {"type": "integer"},
                },
                "required": ["step_number", "title", "instruction", "sensory_type", "estimated_minutes"],
            },
        },
    },
    "required": ["title", "tagline", "theme", "sensory_prompt", "leave_no_trace_principle", "safety_notes", "steps"],
}

SYSTEM_PROMPT = """You are the GreenQuest Nature Activity Crafting Agent.
You design screen-free, sensory-grounded micro-adventures for outdoor environments.
Rules:
1. Steps must be safe, respectful of nature, and strictly on designated public pathways.
2. NEVER instruct users to eat/taste plants, fungi, berries, or drink unpurified water.
3. NEVER instruct users to trespass, leave designated trails, climb dangerous cliffs, or harass wildlife.
4. Emphasize sight, sound, touch (bark/fallen leaves), scent, and open-air breathing.
5. Provide actionable Leave-No-Trace principles and safety reminders.
6. Keep each step instruction brief and actionable (20-35 words max).
Always respond strictly in valid JSON matching the schema with sequential items in the "steps" array.
"""


class NatureActivityAgent:
    def __init__(self, provider: ModelProvider):
        self.provider = provider

    async def generate_activities(
        self,
        prefs: MissionPreferenceRequest,
        plan: PlannerDraft,
        remediation_notes: Optional[List[str]] = None,
    ) -> ActivityDraft:
        remediation_block = ""
        if remediation_notes:
            remediation_block = (
                "\nCRITICAL FIXES REQUIRED FROM PREVIOUS AUDIT:\n- "
                + "\n- ".join(remediation_notes)
                + "\nYou must strictly avoid the above issues."
            )

        step_target = max(2, plan.target_step_count)
        prompt = (
            f"Generate an outdoor quest based on this plan:\n"
            f"- Theme: {plan.theme}\n"
            f"- Narrative Arc: {plan.narrative_arc}\n"
            f"- Environment: {prefs.environment.value}\n"
            f"- Duration: {prefs.duration_minutes} minutes across {step_target} steps\n"
            f"- Mood: {prefs.mood.value}\n"
            f"- Energy: {prefs.energy_level.value}\n"
            f"- Senses to focus on: {', '.join(s.value for s in prefs.sensory_focus)}\n"
            f"- Context: {prefs.notes or 'None'}\n"
            f"{remediation_block}\n"
            f"Instructions must be 20-35 words each. Populate exactly {step_target} items in the 'steps' array."
        )

        request = ProviderCompletionRequest(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            json_mode=True,
            response_schema=ACTIVITY_RESPONSE_SCHEMA,
            temperature=0.5,
            max_tokens=650,
        )

        raw_output = await self.provider.generate(request)
        data = clean_and_repair_json(raw_output)

        raw_steps = data.get("steps", [])
        if not isinstance(raw_steps, list) or len(raw_steps) == 0:
            raise MalformedModelOutputError("Model returned empty or non-list steps array.")

        return ActivityDraft(
            title=str(data.get("title", f"{prefs.environment.value.capitalize()} Exploration")),
            tagline=str(data.get("tagline", "Tune into nature's quiet patterns.")),
            theme=str(data.get("theme", plan.theme)),
            sensory_prompt=str(data.get("sensory_prompt", "Awaken your senses in the fresh air.")),
            leave_no_trace_principle=str(data.get("leave_no_trace_principle", "Stay on marked trails and pack out what you carry in.")),
            safety_notes=list(data.get("safety_notes", ["Stay alert to path obstacles and changing weather."])),
            steps=raw_steps,
        )

