"""Nature Activity Agent: Crafts tactile, sensory-rich outdoor steps and tasks."""
import json
import logging
from typing import Optional, List
from backend.app.models.mission import MissionPreferenceRequest
from backend.app.models.provider import ProviderCompletionRequest
from backend.app.providers.base import ModelProvider
from backend.app.orchestrator.state import PlannerDraft, ActivityDraft

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the GreenQuest Nature Activity Crafting Agent.
You design screen-free, sensory-grounded micro-adventures for outdoor environments.
Rules:
1. Steps must be safe, respectful of nature, and non-destructive.
2. NEVER instruct users to eat/taste plants, fungi, berries, or drink unpurified water.
3. NEVER instruct users to trespass, leave designated trails, climb dangerous cliffs, or harass wildlife.
4. Emphasize sight, sound, touch (bark/fallen leaves), scent, and open-air breathing.
5. Provide actionable Leave-No-Trace principles and safety reminders.

Always respond in strictly valid JSON matching this schema:
{
  "title": "Inspiring adventure title (e.g. Whispers of the Canopy)",
  "tagline": "Poetic sensory teaser sentence",
  "theme": "Theme description",
  "sensory_prompt": "Guidance on which senses to awaken",
  "leave_no_trace_principle": "Concrete stewardship guideline",
  "safety_notes": ["Safety note 1", "Safety note 2"],
  "steps": [
    {
      "step_number": 1,
      "title": "Short title",
      "instruction": "Concrete, safe action to do in nature (20-40 words)",
      "sensory_type": "sight",
      "estimated_minutes": 5
    }
  ]
}
Do not write markdown or commentary outside the JSON block.
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
                "\nCRITICAL FIXES REQUIRED FROM PREVIOUS SAFETY AUDIT:\n- "
                + "\n- ".join(remediation_notes)
                + "\nYou must strictly avoid the above safety violations."
            )

        prompt = (
            f"Generate an outdoor quest based on this plan:\n"
            f"- Theme: {plan.theme}\n"
            f"- Narrative Arc: {plan.narrative_arc}\n"
            f"- Environment: {prefs.environment.value}\n"
            f"- Duration: {prefs.duration_minutes} minutes across {plan.target_step_count} steps\n"
            f"- Mood: {prefs.mood.value}\n"
            f"- Energy: {prefs.energy_level.value}\n"
            f"- Senses to focus on: {', '.join(s.value for s in prefs.sensory_focus)}\n"
            f"- Context: {prefs.notes or 'None'}\n"
            f"{remediation_block}\n"
            f"Produce exact JSON with {plan.target_step_count} sequential steps."
        )

        request = ProviderCompletionRequest(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            json_mode=True,
            temperature=0.7,
            max_tokens=700,
        )

        raw_output = await self.provider.generate(request)
        clean_json = raw_output.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()

        data = json.loads(clean_json)

        return ActivityDraft(
            title=str(data.get("title", f"{prefs.environment.value.capitalize()} Exploration")),
            tagline=str(data.get("tagline", "Tune into nature's quiet patterns.")),
            theme=str(data.get("theme", plan.theme)),
            sensory_prompt=str(data.get("sensory_prompt", "Awaken your senses in the fresh air.")),
            leave_no_trace_principle=str(data.get("leave_no_trace_principle", "Stay on marked trails and pack out what you carry in.")),
            safety_notes=list(data.get("safety_notes", ["Stay alert to path obstacles and changing weather."])),
            steps=list(data.get("steps", [])),
        )
