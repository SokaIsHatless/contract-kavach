"""Claude vision integration for contract analysis."""

import os
import base64
import json
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Find .env relative to THIS file's location, not the working directory
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Fail loudly if the key didn't load
if not os.environ.get("ANTHROPIC_API_KEY"):
    raise RuntimeError(f"ANTHROPIC_API_KEY not found. Looked in: {ENV_PATH}")

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-5"

EXTRACTION_PROMPT = """You are a contract analyst specializing in Indian migrant worker employment contracts. You read contracts in English, Arabic, Hindi, or any mix, including handwritten amendments and stamps.

Your job: extract structured information from the contract images provided. The user is an Indian worker who may not read the language fluently. Accuracy matters — workers will make decisions based on this.

Return ONLY a valid JSON object matching this exact schema:

{
  "language_detected": "english" | "arabic" | "mixed",
  "wage": {"amount": <number>, "currency": "<3-letter code>", "period": "monthly"|"daily"},
  "working_hours_per_day": <number or null>,
  "working_days_per_week": <number or null>,
  "recruitment_fee_paid": {"amount": <number>, "currency": "<code>"} or null,
  "passport_handling": "worker_keeps" | "employer_holds" | "unspecified",
  "deductions": [{"type": "<string>", "amount_or_percent": "<string>", "page": <int>}],
  "termination": "either_party" | "employer_only" | "worker_only" | "unspecified",
  "grievance_mechanism": "<string or null>",
  "sponsor_change_allowed": <true | false | null>,
  "destination_country": "<string or null>",
  "key_clauses": [
    {"text": "<exact quoted clause>", "page": <int>, "concern_level": "info"|"caution"|"critical"}
  ]
}

RULES:
- If a field is not stated in the contract, use null. Do not guess.
- For `key_clauses`, surface 3-7 clauses that most affect the worker's rights, money, or freedom.
- `evidence_page` is 1-indexed (page 1 = first image).
- Quote text exactly as it appears, including any awkward phrasing.
- For wages or fees in INR/AED/SAR/QAR, return the numeric amount only — no commas, no currency symbols inside the number.
- Output ONLY the JSON. No preamble. No markdown fences. No explanation.
"""


def _image_to_block(image_path: str) -> dict:
    """Convert a local image file to an Anthropic image content block."""
    path = Path(image_path)
    suffix = path.suffix.lower().lstrip(".")
    media_type = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "gif": "image/gif",
    }.get(suffix, "image/jpeg")

    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": data,
        },
    }


def analyze_contract(image_paths: list[str]) -> dict:
    """
    Send contract images to Claude vision and return structured JSON.
    image_paths: list of local file paths, ordered page 1, page 2, ...
    """
    content = [_image_to_block(p) for p in image_paths]
    content.append({"type": "text", "text": "Analyze these contract pages."})

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=EXTRACTION_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    raw = response.content[0].text.strip()
    # Strip code fences if Claude added them despite instructions
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


if __name__ == "__main__":
    # Quick smoke test — call with: python claude_vision.py path/to/contract.png
    import sys
    if len(sys.argv) > 1:
        result = analyze_contract(sys.argv[1:])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Usage: python claude_vision.py <image1> [image2] ...")