# ContractKavach — 24h Plan

## What it does
User uploads photos of their contract → AI extracts key terms → flags exploitative clauses against Indian Emigration Act + ILO standards → reads top red flags aloud in Hindi.

## Target user
Indian migrant workers heading to Gulf, signing Arabic/English contracts they can't read.

## The 4 features
1. Multi-page contract image upload
2. Claude vision extraction of structured contract terms
3. Red-flag detection (8 hardcoded rules)
4. Hindi voice playback of top red flags

## Wow moment for demo
When user clicks a red flag, the original contract image scrolls to that page and highlights the relevant region.

## Out of scope (DO NOT BUILD)
- WhatsApp integration
- User accounts / auth
- Database (use in-memory or filesystem)
- Multi-language voice (Hindi only)
- Mobile app
- Email/SMS notifications
- Recruiter rating database
- RAG over legal corpus (rules are hardcoded)