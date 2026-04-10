import json
import asyncio
from typing import Any

from groq import Groq
import os 

from app.utils.schemas import RaceSummary
from config import get_settings


def _build_prompt(payload: dict[str, Any]) -> str:
    """Build structured prompt for LLM summary generation."""
    return (
        "You are an F1 race telemetry analyst. Produce JSON with keys: "
        "headline, key_events, driver_reports, technical_insights, alert_summary.\n"
        f"Input data:\n{json.dumps(payload, default=str)}"
    )


async def generate_race_summary(analysis_payload: dict[str, Any]) -> RaceSummary:
    """Generate race summary from aggregated analysis payload."""
    settings = get_settings()
    prompt = _build_prompt(analysis_payload)

    if not settings.groq_api_key:
        return RaceSummary(
            headline="Telemetry summary generated without external LLM.",
            key_events=["Groq API key not configured."],
            driver_reports={},
            technical_insights=["Configure GROQ_API_KEY to enable AI summaries."],
            alert_summary={"INFO": ["No grouped alerts available."]},
        )

    client = Groq(api_key=settings.groq_api_key)
    def generate_summary(analysis_data: dict) -> RaceSummary:
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": "You are an expert F1 race analyst..."},
                {"role": "user", "content": f"Analyse this race data: {analysis_data}"}
            ],
            max_tokens=2000,
        )
        return response.choices[0].message.content

    def _run_completion() -> str:
        completion = client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
        )
        content = completion.choices[0].message.content
        return content if isinstance(content, str) else str(content)

    text = await asyncio.to_thread(_run_completion)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = {
            "headline": "Unable to parse model output.",
            "key_events": [text[:500]],
            "driver_reports": {},
            "technical_insights": [],
            "alert_summary": {},
        }
    return RaceSummary.model_validate(parsed)
