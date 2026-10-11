"""Deterministic rule-based safety engine for GreenQuest outdoor missions.
Evaluates mission proposals with zero-trust validation before user presentation.
"""
import re
from typing import List, Dict, Any, Tuple
from backend.app.models.mission import SafetyReview


# Forbidden patterns that immediately disqualify an activity
HAZARDOUS_PATTERNS: List[Tuple[str, str]] = [
    # Ingestion & foraging risks
    (r"\b(eat|taste|chew|swallow|ingest|consume|sample)\b.*?\b(berry|berries|plant|leaf|mushroom|fungi|flower|seed)\b", "Encouraging ingestion of wild plants or fungi is forbidden."),
    (r"\b(eat|taste|chew|ingest)\b", "Instructions must not ask users to ingest or taste any natural objects."),
    (r"\b(mushroom|fungus|fungi)\b", "Direct interaction with wild mushrooms/fungi is barred to prevent toxic ingestion."),
    (r"\b(drink)\b.*?\b(water|river|pond|stream|creek|lake)\b", "Drinking unpurified wild water is strictly prohibited."),

    # Trespassing & property violations
    (r"\b(trespass|private property|private land|climb fence|hop fence|scale fence|enter yard)\b", "Entering private property, trespassing, or climbing fences is strictly prohibited."),
    (r"\b(off-trail|leave marked path|wander into brush)\b", "Going off-trail harms local biomes and risks disorientation."),

    # Dangerous terrain & water hazards
    (r"\b(climb|scale)\b.*?\b(cliff|steep rock|tall tree|electric|fence)\b", "High-altitude climbing without safety gear is prohibited."),
    (r"\b(swim|dive|wade deeply|cross)\b.*?\b(current|river|rapids|flood|waterfall)\b", "Entering moving or deep water currents is prohibited."),

    # Wildlife harassment
    (r"\b(touch|feed|catch|trap|grab|corner|chase)\b.*?\b(wildlife|animal|bird|duck|squirrel|raccoon|snake|nest)\b", "Harassing, feeding, or handling wild animals is prohibited."),
]

REQUIRED_SAFETY_KEYWORDS = [
    "path", "trail", "observe", "stay", "safe", "look"
]


def evaluate_mission_safety(
    title: str,
    steps: List[Dict[str, Any]],
    leave_no_trace: str,
    safety_notes: List[str],
) -> SafetyReview:
    """
    Run deterministic rule checks against the mission content.
    Returns SafetyReview indicating whether the mission passed and any violations.
    """
    violations: List[str] = []
    recommendations: List[str] = []

    # 1. Combine all text for text search
    all_text = f"{title}\n{leave_no_trace}\n" + "\n".join(safety_notes)
    for step in steps:
        step_title = step.get("title", "")
        step_inst = step.get("instruction", "")
        all_text += f"\n{step_title}: {step_inst}"

    text_lower = all_text.lower()

    # 2. Check forbidden hazardous patterns
    for pattern, explanation in HAZARDOUS_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            violations.append(explanation)

    # 3. Check Leave-No-Trace principle presence
    if not leave_no_trace or len(leave_no_trace.strip()) < 10:
        violations.append("Mission is missing a clear Leave-No-Trace outdoor stewardship principle.")
        recommendations.append("Include explicit guidance to protect trails, vegetation, and pack out waste.")

    # 4. Check Safety Notes presence
    if not safety_notes or len(safety_notes) < 1:
        violations.append("Mission must provide at least one outdoor safety note.")
        recommendations.append("Add situational safety guidance (e.g. footing, weather, boundaries).")

    # 5. Check Step Count
    if len(steps) < 2:
        violations.append(f"Mission has only {len(steps)} steps; minimum is 2 steps.")
        recommendations.append("Ensure mission has between 2 and 5 well-paced activities.")

    # 6. Check individual step quality
    for i, step in enumerate(steps, start=1):
        instruction = step.get("instruction", "")
        if len(instruction.strip()) < 10:
            violations.append(f"Step {i} instruction is too brief to be actionable or safe.")
        estimated_min = step.get("estimated_minutes", 0)
        if estimated_min <= 0 or estimated_min > 90:
            violations.append(f"Step {i} duration ({estimated_min}m) is invalid.")

    is_safe = len(violations) == 0
    return SafetyReview(
        is_safe=is_safe,
        violations=violations,
        recommendations=recommendations,
    )
