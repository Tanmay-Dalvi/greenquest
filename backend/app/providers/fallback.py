import hashlib
import time
from datetime import datetime, timezone
from typing import List, Dict, Any
from backend.app.models.mission import (
    EnvironmentType,
    MoodType,
    EnergyLevel,
    SensoryType,
    DifficultyLevel,
    MissionPreferenceRequest,
    MissionResponse,
    MissionStep,
    GeneratorInfo,
)
from backend.app.models.provider import ProviderCompletionRequest, ProviderStatus
from backend.app.providers.base import ModelProvider


# Procedural templates mapped to environments and moods
ENVIRONMENT_THEMES: Dict[EnvironmentType, Dict[str, Any]] = {
    EnvironmentType.PARK: {
        "title_prefix": "Green Haven",
        "taglines": [
            "Observe the subtle choreography of open lawns, tree canopies, and park visitors.",
            "Find calm in the communal greens: notice light dancing through manicured branches."
        ],
        "leave_no_trace": "Pack out any trash you carry in and keep dogs on marked park trails.",
        "safety_notes": [
            "Stick to paved or established gravel pathways.",
            "Be mindful of bicycles, runners, and other park visitors.",
            "Do not consume any park plants, berries, or standing pond water."
        ],
        "step_templates": [
            ("Sensory Grounding", "Stand beside a mature park tree for 2 minutes. Close your eyes and tune in to the ambient birdcalls above traffic sounds.", SensoryType.SOUND),
            ("Leaf Texture Contrast", "Collect two fallen leaves from the ground. Compare the smoothness of the top side against the ribbed veins on the underside.", SensoryType.TOUCH),
            ("Canopy Light Gradient", "Look upward into the branch canopy. Identify three distinct shades of green shifting from sunlight to shadow.", SensoryType.SIGHT),
            ("Earth Scent Inhale", "Kneel near damp mulch or open soil. Take three deep breaths and note the earthy petrichor scent.", SensoryType.SCENT),
            ("Reflective Cool Down", "Find a park bench or grassy verge. Rest for 3 minutes while noticing how your breath syncs with the rustle of leaves.", SensoryType.SPATIAL),
        ]
    },
    EnvironmentType.FOREST: {
        "title_prefix": "Canopy Whisper",
        "taglines": [
            "Step beneath the ancient canopy and let the forest floor ground your senses.",
            "Trace the age-old dialogue between moss, decaying timber, and soaring trunks."
        ],
        "leave_no_trace": "Stay strictly on designated trails to protect delicate root systems and soil biomes.",
        "safety_notes": [
            "Stay on marked trails and maintain trail awareness at all times.",
            "Never consume wild mushrooms, fungi, or unknown forest berries.",
            "Watch footing for exposed roots, loose rocks, and slippery moss."
        ],
        "step_templates": [
            ("Threshold Silence", "Stop at the forest edge for 90 seconds. Listen to the sudden dampening of outside noises under the tree canopy.", SensoryType.SOUND),
            ("Bark Texture Expedition", "Gently press your fingertips against the bark of two different tree species. Feel the furrowed valleys and smooth ridges.", SensoryType.TOUCH),
            ("Moss Micro-World", "Locate a fallen nurse log or stone covered in moss. Observe the miniature landscape of tiny sporophytes.", SensoryType.SIGHT),
            ("Pine & Resin Aroma", "Rub a dry fallen conifer needle between your fingers. Inhale the aromatic resin.", SensoryType.SCENT),
            ("Canopy Window Search", "Gaze straight up and search for a gap in the crown where sky peeks through like stained glass.", SensoryType.SPATIAL),
        ]
    },
    EnvironmentType.GARDEN: {
        "title_prefix": "Botanical Wonder",
        "taglines": [
            "Immerse yourself in intentional flora, pollinator highways, and soil rhythms.",
            "Slow down to witness the quiet industry of community garden beds and blooming borders."
        ],
        "leave_no_trace": "Admire blooms with your eyes and camera; never pick living flowers or vegetable crops.",
        "safety_notes": [
            "Walk cautiously on narrow garden paths and flagstones.",
            "Observe bees and wasps from a respectful distance without swatting.",
            "Do not harvest or sample garden plants without explicit gardener consent."
        ],
        "step_templates": [
            ("Petal Geometry", "Examine a single flower closely. Count its petals or note the spiral symmetry of its center seeds.", SensoryType.SIGHT),
            ("Herbal Scent Awakening", "Hover your nose near aromatic foliage like rosemary, lavender, or mint without tearing the stem.", SensoryType.SCENT),
            ("Pollinator Tracker", "Observe a flowering patch for 3 minutes without moving. Count how many winged pollinators arrive.", SensoryType.SIGHT),
            ("Leaf Velvet Check", "Find a fuzzy leaf (like lamb's ear or sage) and brush the tip of your index finger across its surface.", SensoryType.TOUCH),
            ("Garden Wind Chimes", "Close your eyes and listen for gentle rustling stems or buzzing insects.", SensoryType.SOUND),
        ]
    },
    EnvironmentType.WATERFRONT: {
        "title_prefix": "Shoreline Rhythms",
        "taglines": [
            "Synchronize your breathing with the rhythm of lapping water and shoreline winds.",
            "Witness the dynamic boundary where solid earth meets liquid movement."
        ],
        "leave_no_trace": "Keep trash far away from water banks; protect nesting shoreline waterfowl.",
        "safety_notes": [
            "Remain at a safe distance from steep or slippery embankments.",
            "Do not enter unknown or moving water currents.",
            "Never drink untreated surface or river water."
        ],
        "step_templates": [
            ("Water Cadence Listening", "Stand near the bank and close your eyes. Tune your breathing to match the tempo of ripples or waves.", SensoryType.SOUND),
            ("Pebble Smoothness", "Pick up a dry water-smoothed stone from the path edge. Feel the cool polished surface in your palm.", SensoryType.TOUCH),
            ("Reflection Watching", "Observe the mirrored surface of the water. Notice how wind fractures the reflected sky into mosaic patterns.", SensoryType.SIGHT),
            ("Aquatic Breeze Inhale", "Face into the wind blowing off the water. Feel the cool humidity and catch the fresh aquatic scent.", SensoryType.SCENT),
            ("Horizon Expansion", "Look across the widest expanse of water visible. Allow your vision to relax into peripheral awareness.", SensoryType.SPATIAL),
        ]
    },
    EnvironmentType.TRAIL: {
        "title_prefix": "Pathfinder's Stride",
        "taglines": [
            "Navigate the subtle twists of the dirt pathway with conscious, grounded strides.",
            "Follow the contour of the earth and reconnect with forward momentum in open air."
        ],
        "leave_no_trace": "Stick to the center of the trail to prevent trail widening and soil erosion.",
        "safety_notes": [
            "Check trail markers regularly to avoid losing orientation.",
            "Yield to uphill hikers and maintain sturdy footing on loose gravel.",
            "Carry sufficient hydration and be alert to changing weather."
        ],
        "step_templates": [
            ("Grounded Footstrike", "Walk the first 100 paces with intentional focus on your heel-to-toe roll against the dirt.", SensoryType.TOUCH),
            ("Trail Vista Spotting", "Pause at the first bend or elevation rise. Survey the landscape contours in front of you.", SensoryType.SIGHT),
            ("Wind Direction Check", "Turn your face until you feel the breeze evenly on both cheeks. Note which direction the air flows.", SensoryType.TOUCH),
            ("Bird Flight Observation", "Scan the tree line for birds darting between branches. Track one bird's trajectory.", SensoryType.SIGHT),
            ("Silent Stride Minute", "Walk for one full minute making as little footstep sound as humanly possible.", SensoryType.SOUND),
        ]
    },
    EnvironmentType.NEIGHBORHOOD: {
        "title_prefix": "Urban Naturalist",
        "taglines": [
            "Discover resilient pockets of biodiversity nestled in sidewalk cracks and front yards.",
            "Re-enchant familiar streets by seeking out the wild organisms sharing your block."
        ],
        "leave_no_trace": "Respect private property boundaries; observe sidewalk gardens from public pathways.",
        "safety_notes": [
            "Always use marked pedestrian crossings and watch for vehicular traffic.",
            "Stay entirely on public sidewalks and easements; do not trespass.",
            "Avoid touching unknown residential plants or pet animals without permission."
        ],
        "step_templates": [
            ("Sidewalk Crack Sprout", "Locate a resilient plant growing between pavement cracks. Marvel at its tenacity.", SensoryType.SIGHT),
            ("Street Tree Canopy", "Look up at the next street tree you pass. Notice how its branches adapt to telephone poles and roofs.", SensoryType.SPATIAL),
            ("City Bird Listening", "Filter out motor sounds and identify two distinct urban bird vocalizations (sparrows, crows, doves).", SensoryType.SOUND),
            ("Sun-Warmed Brick", "Touch an exterior brick or stone wall warmed by the sun. Feel the stored solar thermal energy.", SensoryType.TOUCH),
            ("Pocket Greenery Gratitude", "Find a front lawn flower or ornamental shrub and spend 30 seconds appreciating its splash of color.", SensoryType.SIGHT),
        ]
    }
}


class DeterministicFallbackProvider(ModelProvider):
    """
    Guaranteed deterministic mission generator that requires zero internet connection,
    has zero hallucination risk, and strictly adheres to all safety rules and schemas.
    """

    @property
    def name(self) -> str:
        return "fallback"

    @property
    def model_name(self) -> str:
        return "deterministic-rule-engine-v1"

    async def generate(self, request: ProviderCompletionRequest) -> str:
        """Emulate provider text generation by outputting pre-validated JSON."""
        # This is called if orchestrator invokes provider interface directly
        # We return a formatted JSON payload
        mission = self.generate_mission_sync(MissionPreferenceRequest())
        return mission.model_dump_json()

    async def check_availability(self) -> ProviderStatus:
        return ProviderStatus(
            provider_name=self.name,
            is_available=True,
            model_name=self.model_name,
            latency_ms=0.5,
            message="Deterministic fallback generator is always available",
        )

    def generate_mission_sync(self, prefs: MissionPreferenceRequest) -> MissionResponse:
        """Procedurally generate a complete validated MissionResponse."""
        start_time = time.perf_counter()
        env_config = ENVIRONMENT_THEMES.get(prefs.environment, ENVIRONMENT_THEMES[EnvironmentType.PARK])

        # Generate unique mission ID
        seed_str = f"{prefs.environment.value}-{prefs.mood.value}-{prefs.duration_minutes}-{prefs.notes or ''}"
        hash_suffix = hashlib.md5(seed_str.encode("utf-8")).hexdigest()[:6]
        mission_id = f"gq-{prefs.environment.value}-{prefs.mood.value}-{hash_suffix}"

        # Determine step count based on duration (10m = 2 steps, 30m = 3-4 steps, 60m+ = 4-5 steps)
        if prefs.duration_minutes <= 15:
            step_count = 2
        elif prefs.duration_minutes <= 35:
            step_count = 3
        elif prefs.duration_minutes <= 60:
            step_count = 4
        else:
            step_count = 5

        # Select templates and apportion minutes
        available_steps = env_config["step_templates"]
        selected_templates = available_steps[:step_count]

        # Allocate time per step
        base_step_minutes = max(3, prefs.duration_minutes // step_count)
        remainder = prefs.duration_minutes - (base_step_minutes * step_count)

        steps: List[MissionStep] = []
        for i, (title, instruction, sensory_type) in enumerate(selected_templates):
            step_mins = base_step_minutes + (remainder if i == 0 else 0)
            steps.append(
                MissionStep(
                    step_number=i + 1,
                    title=f"{title}",
                    instruction=instruction,
                    sensory_type=sensory_type,
                    estimated_minutes=step_mins,
                    completed=False,
                )
            )

        # Title and tagline
        title = f"{env_config['title_prefix']}: {prefs.mood.value.capitalize()} Quest"
        tagline = env_config["taglines"][0] if env_config["taglines"] else "A mindful nature micro-adventure."

        # Sensory prompt
        primary_senses = ", ".join(s.value for s in prefs.sensory_focus)
        sensory_prompt = f"Focus your attention on {primary_senses}. Notice how slowing down sharpens each sensation."

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        difficulty_map = {
            EnergyLevel.LOW: DifficultyLevel.EASY,
            EnergyLevel.MODERATE: DifficultyLevel.MODERATE,
            EnergyLevel.BRISK: DifficultyLevel.CHALLENGING,
        }

        return MissionResponse(
            id=mission_id,
            title=title,
            tagline=tagline,
            environment=prefs.environment,
            estimated_duration_minutes=prefs.duration_minutes,
            difficulty=difficulty_map.get(prefs.energy_level, DifficultyLevel.EASY),
            theme=f"{prefs.mood.value.capitalize()} {prefs.environment.value.capitalize()} Exploration",
            sensory_prompt=sensory_prompt,
            leave_no_trace_principle=env_config["leave_no_trace"],
            safety_notes=env_config["safety_notes"],
            steps=steps,
            generator_info=GeneratorInfo(
                provider="fallback",
                model=self.model_name,
                fallback_used=True,
                generation_time_ms=elapsed_ms,
                safety_validated=True,
            ),
            created_at=datetime.now(timezone.utc),
        )
