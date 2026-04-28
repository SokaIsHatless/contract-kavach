# Architecture

## Data flow
1. Frontend uploads N images to POST /api/analyze
2. Backend sends images to Claude vision with extraction prompt
3. Claude returns structured JSON of contract terms
4. Backend runs rules.py against JSON → list of red flags
5. Backend calls Bhashini TTS on top 3 flags → returns audio URL
6. Frontend renders flags + audio player + image viewer

## JSON schema returned by Claude vision
{
  "language_detected": "english" | "arabic" | "mixed",
  "wage": {"amount": number, "currency": "INR"|"AED"|"SAR"|..., "period": "monthly"|"daily"},
  "working_hours_per_day": number | null,
  "working_days_per_week": number | null,
  "recruitment_fee_paid": {"amount": number, "currency": string} | null,
  "passport_handling": "worker_keeps" | "employer_holds" | "unspecified",
  "deductions": [{"type": string, "amount_or_percent": string, "page": number}],
  "termination": "either_party" | "employer_only" | "worker_only" | "unspecified",
  "grievance_mechanism": string | null,
  "sponsor_change_allowed": boolean | null,
  "destination_country": string | null,
  "key_clauses": [{"text": string, "page": number, "concern_level": "info"|"caution"|"critical"}]
}

## Red-flag rule output
{
  "rule_id": "RF01",
  "severity": "critical" | "high" | "medium",
  "title_en": "Recruitment fee exceeds legal cap",
  "title_hi": "भर्ती शुल्क कानूनी सीमा से अधिक",
  "explanation_en": "...",
  "explanation_hi": "...",
  "evidence_page": number,
  "evidence_quote": string
}