# ContractKavach — Hackathon Project

## CRITICAL CONTEXT
- This is a 24-HOUR HACKATHON PROTOTYPE. Solo developer.
- Goal: working demo, not production code.
- I am a first-time serious Claude Code user. Be explicit about what you're doing.

## STRICT RULES
- DO NOT write tests.
- DO NOT add error boundaries, retry logic, or defensive try/except beyond the bare minimum to not crash on stage.
- DO NOT refactor working code unless I explicitly ask.
- DO NOT suggest TypeScript strict mode, ESLint configs, or "best practices" cleanups.
- DO NOT add features I didn't ask for.
- DO use `claude-sonnet-4-5` for vision (NOT Opus — too expensive for iteration).
- DO commit after every working feature with a clear message.

## STACK (FIXED — DO NOT SUGGEST CHANGES)
- Backend: FastAPI (Python 3.11+)
- Frontend: Next.js 14 (app router) + Tailwind
- Vision: Anthropic claude-sonnet-4-5 via SDK
- TTS: Bhashini API (fallback: browser SpeechSynthesis)
- Storage: local filesystem (./uploads/)

## PROJECT STRUCTURE
contract-kavach/
├── backend/
│   ├── main.py           # FastAPI app
│   ├── claude_vision.py  # Claude API calls
│   ├── rules.py          # Red-flag rule engine
│   ├── tts.py            # Bhashini TTS
│   └── requirements.txt
├── frontend/
│   └── (Next.js 14 app router)
├── mock_contracts/       # PDF samples
├── PLAN.md
├── ARCHITECTURE.md
└── CLAUDE.md

## API CONTRACT (FIXED)
POST /api/analyze
  Body: multipart/form-data with one or more image files
  Response: see ARCHITECTURE.md for JSON schema

## WHEN STUCK
- If something doesn't work in 15 min, ask the user before going deeper.
- Time-box exploratory work.