"""Robust JSON cleaning, defect repair, and schema extraction for LLM outputs."""
import re
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MalformedModelOutputError(Exception):
    """Raised when model output cannot be repaired into valid JSON or schema."""
    pass


def clean_and_repair_json(raw_text: str) -> Dict[str, Any]:
    """
    Cleans and repairs common open-weight LLM JSON defects:
    - Strips markdown fences (```json ... ```)
    - Trims preamble and postamble commentary / junk tokens
    - Fixes unicode curly quotes (“, ”) and quotation hallucination delimiters
    - Fixes trailing commas
    - Balances unclosed brackets/braces from length truncation
    - Employs regex field recovery as a last resort
    """
    if not raw_text or not raw_text.strip():
        raise MalformedModelOutputError("Model returned empty output.")

    text = raw_text.strip()

    # 1. Remove markdown fences
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()

    # 2. Slice boundary to outermost braces
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]

    # 3. Direct parse attempt
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 4. Repair known open-weight model defects
    repaired = text

    # Gemma 3 delimiter hallucination inside strings: .”}, {","sensory_type":
    repaired = re.sub(r'[”"]\s*\}\s*,\s*\{\s*"\s*,\s*', '", ', repaired)
    # Gemma 3 final step close hallucination: .”} ]}
    repaired = re.sub(r'[”"]\s*\}\s*\]\s*\}', '"}]}', repaired)
    # Convert all smart quotes to standard ASCII double quotes
    repaired = repaired.replace('“', '"').replace('”', '"')
    # Remove trailing commas before closing braces/brackets
    repaired = re.sub(r',\s*([}\]])', r'\1', repaired)

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # 5. Handle truncated output (unclosed quotes and braces)
    truncated = repaired
    # If ends with an open quote without closing quote
    open_quotes = truncated.count('"') - truncated.count(r'\"')
    if open_quotes % 2 != 0:
        truncated += '"'

    # Balance unclosed braces and brackets
    open_brackets = truncated.count('[') - truncated.count(']')
    if open_brackets > 0:
        truncated += ']' * open_brackets

    open_braces = truncated.count('{') - truncated.count('}')
    if open_braces > 0:
        truncated += '}' * open_braces

    # Clean trailing commas in balanced string
    truncated = re.sub(r',\s*([}\]])', r'\1', truncated)

    try:
        return json.loads(truncated)
    except json.JSONDecodeError:
        pass

    # 6. Fallback: Heuristic Regex Field Extraction
    extracted = _regex_extract_fields(text)
    if extracted:
        logger.info("Successfully recovered mission data via regex extraction")
        return extracted

    raise MalformedModelOutputError(f"Unable to parse or repair model output: {raw_text[:200]}...")


def _regex_extract_fields(text: str) -> Optional[Dict[str, Any]]:
    """Emergency heuristic extractor for semi-structured text containing mission keys."""
    data: Dict[str, Any] = {}

    # Extract scalar string fields
    for field in ["title", "tagline", "theme", "sensory_prompt", "leave_no_trace_principle", "narrative_arc", "difficulty"]:
        match = re.search(rf'"{field}"\s*:\s*"([^"]+)"', text, re.IGNORECASE)
        if match:
            data[field] = match.group(1).strip()

    # Extract integer fields
    for int_field in ["target_step_count", "allocated_minutes"]:
        match = re.search(rf'"{int_field}"\s*:\s*(\d+)', text, re.IGNORECASE)
        if match:
            data[int_field] = int(match.group(1))

    # Extract safety notes
    safety_matches = re.findall(r'"safety_notes"\s*:\s*\[(.*?)\]', text, re.DOTALL | re.IGNORECASE)
    if safety_matches:
        notes = re.findall(r'"([^"]{5,})"', safety_matches[0])
        if notes:
            data["safety_notes"] = notes

    # Extract steps
    steps: List[Dict[str, Any]] = []
    # Match step object chunks
    step_chunks = re.findall(r'\{[^{}]*"step_number"[^{}]*\}', text, re.DOTALL)
    for i, chunk in enumerate(step_chunks, start=1):
        step_obj: Dict[str, Any] = {"step_number": i}
        title_m = re.search(r'"title"\s*:\s*"([^"]+)"', chunk)
        step_obj["title"] = title_m.group(1).strip() if title_m else f"Step {i}"

        inst_m = re.search(r'"instruction"\s*:\s*"([^"]+)"', chunk)
        step_obj["instruction"] = inst_m.group(1).strip() if inst_m else "Observe your surroundings carefully."

        sensory_m = re.search(r'"sensory_type"\s*:\s*"([^"]+)"', chunk)
        step_obj["sensory_type"] = sensory_m.group(1).strip() if sensory_m else "sight"

        mins_m = re.search(r'"estimated_minutes"\s*:\s*(\d+)', chunk)
        step_obj["estimated_minutes"] = int(mins_m.group(1)) if mins_m else 5

        steps.append(step_obj)

    if steps:
        data["steps"] = steps

    # Require at least title or theme to be considered a valid recovery
    if "title" in data or "theme" in data:
        return data

    return None

