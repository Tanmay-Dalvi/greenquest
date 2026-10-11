"""Unit tests for deterministic safety guardrails."""
from backend.app.orchestrator.rules import evaluate_mission_safety


def test_safety_passes_clean_outdoor_activities():
    title = "Mindful Woodland Walk"
    steps = [
        {"title": "Tree Gaze", "instruction": "Observe the tree bark texture with your fingers gently.", "estimated_minutes": 5},
        {"title": "Wind Listening", "instruction": "Listen to the breeze rustling high branches for 2 minutes.", "estimated_minutes": 5},
    ]
    leave_no_trace = "Stay strictly on public paths and carry out all belongings."
    safety_notes = ["Watch footing for damp roots and loose gravel."]

    review = evaluate_mission_safety(title, steps, leave_no_trace, safety_notes)
    assert review.is_safe is True
    assert len(review.violations) == 0


def test_safety_rejects_ingestion_and_foraging():
    title = "Wild Berry Hunt"
    steps = [
        {"title": "Foraging", "instruction": "Eat some wild berries along the fence line.", "estimated_minutes": 5},
        {"title": "Resting", "instruction": "Rest quietly on the park bench.", "estimated_minutes": 5},
    ]
    leave_no_trace = "Respect nature and leave no trace behind."
    safety_notes = ["Be careful."]

    review = evaluate_mission_safety(title, steps, leave_no_trace, safety_notes)
    assert review.is_safe is False
    assert any("ingest" in v.lower() or "eat" in v.lower() for v in review.violations)


def test_safety_rejects_mushroom_interaction():
    title = "Fungi Study"
    steps = [
        {"title": "Mushroom Check", "instruction": "Touch and inspect this wild mushroom carefully.", "estimated_minutes": 5},
        {"title": "Trail Walk", "instruction": "Walk slowly along the gravel trail.", "estimated_minutes": 5},
    ]
    leave_no_trace = "Leave no trace on the forest trails."
    safety_notes = ["Stay safe."]

    review = evaluate_mission_safety(title, steps, leave_no_trace, safety_notes)
    assert review.is_safe is False
    assert any("mushroom" in v.lower() for v in review.violations)


def test_safety_rejects_trespassing_and_fence_climbing():
    title = "Shortcut Exploration"
    steps = [
        {"title": "Hop Over", "instruction": "Climb fence into private property to see the old orchard.", "estimated_minutes": 10},
        {"title": "Walk", "instruction": "Walk quietly along the ditch edge.", "estimated_minutes": 5},
    ]
    leave_no_trace = "Leave no trash behind."
    safety_notes = ["Be stealthy."]

    review = evaluate_mission_safety(title, steps, leave_no_trace, safety_notes)
    assert review.is_safe is False
    assert any("private" in v.lower() or "fence" in v.lower() for v in review.violations)


def test_safety_rejects_drinking_wild_water():
    title = "River Refreshment"
    steps = [
        {"title": "Water Taste", "instruction": "Kneel by the river and drink the water directly.", "estimated_minutes": 5},
        {"title": "Rest", "instruction": "Sit quietly on the bank pebbles.", "estimated_minutes": 5},
    ]
    leave_no_trace = "Keep water clean."
    safety_notes = ["Watch footing."]

    review = evaluate_mission_safety(title, steps, leave_no_trace, safety_notes)
    assert review.is_safe is False
    assert any("drink" in v.lower() for v in review.violations)


def test_safety_rejects_wildlife_harassment():
    title = "Critter Encounter"
    steps = [
        {"title": "Duck Feeding", "instruction": "Feed the duck some bread and touch the animal.", "estimated_minutes": 5},
        {"title": "Watching", "instruction": "Watch the pond ripples for two minutes.", "estimated_minutes": 5},
    ]
    leave_no_trace = "Stay on trail."
    safety_notes = ["Be watchful."]

    review = evaluate_mission_safety(title, steps, leave_no_trace, safety_notes)
    assert review.is_safe is False
    assert any("wildlife" in v.lower() or "animal" in v.lower() for v in review.violations)


def test_safety_enforces_leave_no_trace():
    title = "Sensory Exploration"
    steps = [
        {"title": "Step 1", "instruction": "Look at the leaf shapes above you.", "estimated_minutes": 5},
        {"title": "Step 2", "instruction": "Listen to the birds in the distance.", "estimated_minutes": 5},
    ]
    leave_no_trace = ""  # Missing!
    safety_notes = ["Stay alert."]

    review = evaluate_mission_safety(title, steps, leave_no_trace, safety_notes)
    assert review.is_safe is False
    assert any("leave-no-trace" in v.lower() for v in review.violations)
