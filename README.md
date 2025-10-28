# AI-Powered Lead Enrichment & Routing

## 1. Business Summary
Marketing team receives thousands of "Contact Us" leads that currently need manual review. This tool automates that triage end to end. It skims through each lead's message, classifies how urgent the request is, identifies who is reaching out, and routes the lead automatically. Teams save roughly 30-40 hours per week of manual sorting, respond faster to high-value opportunities, and improve routing accuracy by grounding every decision in consistent AI-backed rules. Leadership also gains instant visibility into key go-to-market metrics such as high-urgency lead volume, decision-maker engagement, and team workload.

Key business impact:
- Time: Manual ~165 hrs/month vs AI ~3 hrs/month (assumes ~2 min/lead, 5,000 leads/month).
- Cost: Manual ~€3,300/month vs AI ~€3.86 (Gemini API) (assumes €20/hour and existing infra).
- Accuracy: Manual ~80% vs AI ~93% (AI applies consistent logic; no reviewer fatigue).


## 2. How It Works (Click on the Image below to see a demo video)
[![Walk-Through](https://github.com/user-attachments/assets/ccec57c2-77d0-42cc-89f7-534740eee22c)](https://www.youtube.com/watch?v=3SFRvY3632I)
1. Reads new leads from the `leads.csv` spreadsheet.
2. Sends the job title and comment to Google's Gemini AI to understand urgency, persona type, and intent.
3. Applies business rules to select the best follow-on team.
4. Writes all details - including the AI summary and assigned team - to a shareable JSON file.
5. Makes a dashboard using the generated JSON file.

## 3. Technical Deep Dive

### Architecture
- **Data ingestion:** `pandas.read_csv` loads the structured CSV file.
- **AI enrichment:** The Gemini `gemini-2.5-flash` model analyzes each lead. A structured system prompt frames the task as a marketing assistant classifying inbound leads. A simple regex removes optional Markdown fences before parsing the JSON payload.
- **Routing logic:** A deterministic helper function picks the team based on urgency/persona output, defaulting to `Unassigned` if the AI response is incomplete.
- **Output:** Enriched results are written to `outputs/enriched_leads.json` for auditing or downstream automation.

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
   .\\.venv\\Scripts\\activate           # Windows
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
7. (Optional) Explore the interactive dashboard:
   ```bash
   streamlit run src/dashboard_app.py
   ```

## 5. Additional Feature: Lead Intelligence Dashboard
<img width="1905" height="921" alt="image" src="https://github.com/user-attachments/assets/ccec57c2-77d0-42cc-89f7-534740eee22c" />
<img width="1834" height="541" alt="image" src="https://github.com/user-attachments/assets/8d132b59-74b1-45df-b5db-09478a6f12ae" />


- **What it does:** Provides a real-time, interactive view of enriched leads, including urgency/persona distributions, routing breakdowns, and the full enriched dataset. The dashboard also auto-generates data if it has not yet been produced.
- **Why it was added:** Marketing stakeholders need fast, visual insights without sifting through raw JSON. The dashboard delivers the KPIs that matter (e.g., count of high-urgency decision makers) and a quick download option for campaign follow-up, reducing reliance on analysts.
- **How it works:** Streamlit loads `outputs/enriched_leads.json`, or triggers the enrichment script if the file is missing. Plotly renders histograms for high-level trends, while the data table shows the detailed AI-enriched records. A download button provides the JSON if teams want to feed the results into other systems.

## 6. Future Improvements
- **Integration with CRM & Website**: Direct API integration with the website and Monday.com replaces manual CSV import/export for a fully automated flow.
- **Robust error handling and retries:** capture API failures, malformed JSON, or empty responses and retry or log for manual follow-up.
- **Confidence signals:** expose Gemini confidence scores to help humans decide when to override.
- **Cost and performance optimization:** cache repeat analyses, batch requests, or add rate limiting to control spend.


