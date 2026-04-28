# ContractKavach 🛡️

**कांट्रैक्ट कवच — Your contract, decoded.**

An AI safety net for Indian migrant workers signing Gulf employment contracts.

> *Theme: Economic Empowerment & Education*

---

## The Problem

Every year, 100,000+ Indians sign employment contracts to work in the Gulf — and most can't read what they're signing.

- **₹85,000** average recruitment fee paid (legal cap under the Indian Emigration Act: **₹30,000**)
- **92%** of contracts are in English or Arabic
- Result: passport seizure, wage theft, kafala bondage

The contract is the first line of defense. Most workers can't read it.

---

## What ContractKavach Does

A worker photographs their contract. ContractKavach reads it, checks it against Indian and international labour law, and explains every red flag — in their own language, with the offending clause shown as proof.

### The 4-Step Pipeline
[1] UPLOAD   → Worker drops a photo or PDF (multipage supported)
[2] EXTRACT  → Claude Sonnet 4.5 vision reads English + Arabic + Hindi natively
[3] DETECT   → 8-rule engine checks against Indian Emigration Act + ILO standards
[4] WARN     → Bilingual flags + native Hindi voice playback


---

## Features

| Feature | What it does |
|---|---|
| 🌐 **Native multipage PDF/image vision** | Sent directly to Claude Sonnet 4.5 — no separate OCR. Reads stamps, mixed scripts. |
| ⚖️ **8-rule legal engine** | Recruitment-fee cap (₹30,000), passport surrender, kafala lock-in, ILO working-hour standards, more |
| 🔄 **Bilingual output** | Every flag rendered in English AND Hindi — title, explanation, exact quoted clause |
| 🔊 **Native Hindi voice playback** | Browser SpeechSynthesis reads critical flags aloud in Hindi |
| 📄 **Evidence-based highlighting** | Click any flag → contract scrolls to that page → offending clause appears in a yellow callout |
| ⚡ **One-click sample contracts** | Three pre-built demos: Worst Case (8 flags), Sneaky (4 flags), Mostly Fair (1 flag) |

---

## The 8 Red-Flag Rules

| ID | Rule | Severity | Source |
|---|---|---|---|
| RF01 | Recruitment fee > ₹30,000 | 🔴 Critical | Indian Emigration Act, 1983 |
| RF02 | Employer holds worker's passport | 🔴 Critical | Indian + ILO law |
| RF03 | Wage below destination minimum | 🔴 Critical | Per-country wage tables |
| RF04 | Working hours > ILO standards | 🟠 High | ILO Convention No. 1 |
| RF05 | Deductions > 25% of wage | 🟠 High | Wage-theft pattern indicator |
| RF06 | Only employer can terminate | 🟠 High | Power-asymmetry indicator |
| RF07 | No grievance mechanism | 🟡 Medium | MEA / Indian Embassy access |
| RF08 | Sponsor change forbidden (kafala) | 🔴 Critical | Modern slavery indicator |

---

## Tech Stack

| Layer | Tech |
|---|---|
| AI Vision | **Claude Sonnet 4.5** (multipage PDF + image, structured JSON output) |
| Backend | FastAPI · Python 3.11+ · uvicorn |
| Frontend | Next.js 14 (App Router) · React · Tailwind CSS |
| PDF rendering | pypdfium2 (page-to-image for evidence highlighting) |
| Voice | Browser SpeechSynthesis API · Hindi (hi-IN) |
| Built with | Claude Code in VS Code |

---

## Project Structure
contract-kavach/
├── backend/
│   ├── main.py               # FastAPI app + 3 endpoints
│   ├── claude_vision.py      # Claude API integration + extraction prompt
│   ├── rules.py              # 8-rule bilingual flag engine
│   ├── requirements.txt
│   └── uploads/              # User-uploaded contracts (gitignored)
├── frontend/
│   ├── app/
│   │   ├── page.js           # Single-page UI: upload, flags, viewer
│   │   ├── layout.js
│   │   └── globals.css
│   ├── next.config.mjs       # API proxy to backend
│   └── package.json
├── mock_contracts/
│   ├── worst_case.pdf        # UAE domestic worker — triggers all 8 flags
│   ├── sneaky.pdf            # Saudi construction — buries red flags on page 2
│   └── mostly_fair.pdf       # Qatar domestic — only 1 flag (food deduction)
├── generate_mock_contracts.py
├── ARCHITECTURE.md
├── PLAN.md
├── CLAUDE.md
└── README.md

---

## Running Locally

### Prerequisites
- Python 3.11+
- Node.js 20+
- An Anthropic API key

### Setup

```bash
# Clone
git clone https://github.com/SokaIsHatless/contract-kavach.git
cd contract-kavach

# Backend
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip install pypdfium2 reportlab    # dev dependencies for mock generation
```

Create a `.env` at the project root:
ANTHROPIC_API_KEY= YOUR KEY HERE


Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` and click any sample button.

---

## API Reference

### `POST /api/analyze`
Upload contract files (image or PDF), receive structured contract terms + red flags.

**Body:** multipart form with one or more `files`
**Returns:** `{ contract, flags, source_id, total_pages, is_pdf }`

### `GET /api/samples/{name}`
Run the analysis pipeline against a pre-built sample contract.
Valid names: `worst_case`, `sneaky`, `mostly_fair`

### `GET /api/page-image/{source_id}/{page_num}`
Render a specific page of the analyzed contract as PNG (for the evidence viewer).

---

## Demo Flow

1. Open the app → click **🔴 Worst Case (UAE domestic)**
2. Wait ~8 seconds — Claude Sonnet 4.5 reads the multipage PDF
3. **8 red flags appear**, each with English + Hindi titles + the exact contract clause that triggered it
4. Click **🔊 Listen to top critical flags in Hindi** — browser speaks the warnings in Hindi
5. Click any flag → contract image jumps to that page → yellow callout highlights the offending clause

---

## What's Next

- **WhatsApp / Telegram bot** — same pipeline, accessible from a 2G feature phone
- **Bhashini integration** — Tamil, Bengali, Malayalam, Marathi voice
- **Recruiter rating database** — crowdsourced fee + accuracy data from past workers
- **Direct grievance filing** — auto-submit to MEA / Indian Embassy

---



## License

none for now
