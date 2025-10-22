# AI-Powered Lead Enrichment & Routing

## Overview
Automates enrichment and routing of inbound leads using Google Gemini to extract urgency, persona type, and a concise summary before assigning the lead to the right team.

### Workflow
1. Load `leads.csv`
2. Enrich via Gemini (urgency, persona_type, summary)
3. Apply routing rules
4. Export JSON results

### Folder Structure
```
config.yaml      # editable paths, Gemini model, default team
data/            # contains leads.csv
outputs/         # enriched_leads.json (created after runs)
src/             # Python scripts (lead_router.py, processdata.py, ...)
```

### Setup
1. Create `.env` with `GEMINI_API_KEY=your_key`.
2. Adjust any paths or Gemini settings in `config.yaml` as needed.
3. Install dependencies: `pip install -r requirements.txt`

### Run
MVP pipeline (one-command flow):
```
python src/processdata.py
```

Alternate entry point (modular script):
```
python src/lead_router.py
```
