# AI-Powered Lead Enrichment & Routing

## 1. Business Summary (for Marketing Operations)
Marketing receives hundreds of "Contact Us" leads that currently need manual review. This tool automates that triage. It skims each lead's message, classifies how urgent the request is, identifies who is reaching out, and sends it to the right team. Teams save several hours every week and respond faster to high-value opportunities, especially when senior decision makers reach out.

## 2. How It Works (Plain Language)
1. Reads new leads from the `leads.csv` spreadsheet.
2. Sends the job title and comment to Google's Gemini AI to understand urgency, persona type, and intent.
3. Applies business rules to select the best follow-on team.
4. Writes all details - including the AI summary and assigned team - to a shareable JSON file.

## 3. Technical Deep Dive

### Architecture
- **Data ingestion:** `pandas.read_csv` loads the structured CSV file.
- **AI enrichment:** The Gemini `gemini-2.5-flash` model analyzes each lead. A structured system prompt frames the task as a marketing assistant classifying inbound leads. A simple regex removes optional Markdown fences before parsing the JSON payload.
- **Routing logic:** A deterministic helper picks the team based on urgency/persona output, defaulting to `Unassigned` if the AI response is incomplete.
- **Persistence:** Enriched results are written to `outputs/enriched_leads.json` for auditing or downstream automation.

### Prompt Rationale
The system prompt:
- Sets the context (B2B software inbound leads).
- Lists the exact JSON keys expected.
- Defines urgency and persona choices in plain language.

This minimizes hallucinations, keeps responses consistent, and ensures we can parse valid JSON every time. The user prompt injects the specific job title and comment so Gemini has the full context to classify correctly.

## 4. Setup & Run Instructions

### Prerequisites
- Python 3.10 or newer.
- Google Gemini API key stored in a `.env` file.

### Steps
1. Clone or download this repository.
2. Create and activate a virtual environment, then install dependencies:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate           # Windows
   source .venv/bin/activate          # macOS / Linux
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with:
   ```ini
   GEMINI_API_KEY=your_api_key_here
   ```
4. Optional: adjust `config.yaml` if you want different input/output paths or a different Gemini model.
5. Run the pipeline:
   ```bash
   python src/processdata.py
   ```
6. Review the enriched leads stored at `outputs/enriched_leads.json`.

## 5. Future Improvements
- **Robust error handling and retries:** capture API failures, malformed JSON, or empty responses and retry or log for manual follow-up.
- **Cost and performance optimization:** cache repeat analyses, batch requests, or add rate limiting to control spend.
- **Additional data sources:** ingest leads directly from Salesforce or Marketo instead of relying on a manual CSV export.
- **Confidence signals:** expose Gemini confidence scores to help humans decide when to override.
- **Operational dashboard:** surface trend metrics (for example, number of high-urgency decision makers) for Marketing Ops in real time.
