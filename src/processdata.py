import os
from pathlib import Path
import re

import yaml
import json
import pandas as pd

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load configuration and environment variables
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = yaml.safe_load((BASE_DIR / "config.yaml").read_text(encoding="utf-8"))
INPUT_CSV = BASE_DIR / CONFIG.get("input_csv_path", "data/leads.csv")
OUTPUT_JSON = BASE_DIR / CONFIG.get("output_json_path", "outputs/enriched_leads.json")
DEFAULT_TEAM = CONFIG.get("default_assigned_team", "Unassigned")
MODEL_NAME = CONFIG.get("gemini", {}).get("model", "gemini-2.5-flash")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def enrich_lead(job_title: str, comment: str) -> dict:
    # print("Job Title:", job_title)
    # print("Comment:", comment)
    system_prompt = (
        """You are an AI marketing assistant that classifies inbound business leads for a B2B software company.
        Your task is to analyze the lead's job title and comment and return a structured JSON object with the following fields:
        {
        "urgency": "High | Medium | Low",
        "persona_type": "Decision Maker | Practitioner | Other",
        "summary": "<one-sentence summary of the lead's intent>"
        }

        Definitions:
        - urgency:
        - High → clear buying intent, immediate request for contact or meeting.
        - Medium → exploring options or requesting demo without urgency.
        - Low → students, researchers, or general curiosity.
        - persona_type:
        - Decision Maker → senior execs, heads, directors, C-levels, VPs.
        - Practitioner → technical implementers (analysts, engineers, specialists).
        - Other → students, interns, journalists, or non-business contexts.

        Always return valid JSON and nothing else.
        """
    )
    user_prompt = (
        f"""Lead details:
        Job Title: {job_title}
        Comment: {comment}
        Return the analysis strictly in JSON format."""
    )
    # print("System Prompt:", system_prompt)
    # print("User Prompt:", user_prompt)
    response = client.models.generate_content(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
            ),
        contents= user_prompt
    )
    # print("Gemini Response:", response.text)
    cleaned = re.sub(r"```(?:json)?", "", response.text, flags=re.IGNORECASE).strip()
    # print("Cleaned Response:", cleaned)
    return json.loads(cleaned)


def assign_team(urgency: str | None, persona: str | None) -> str:
    #if no values provided, set to empty string
    Curr_urgency = (urgency or "").strip().title() 
    Curr_persona = (persona or "").strip().title() 

    # Group Assignment logic
    if Curr_urgency == "High" and Curr_persona == "Decision Maker":
        return "Strategic Sales"
    if Curr_urgency == "High" and Curr_persona == "Practitioner":
        return "Enterprise Sales"
    if Curr_urgency == "Medium":
        return "Sales Development"
    if Curr_urgency == "Low":
        return "Nurture Campaign"
    return DEFAULT_TEAM


def main() -> None:
    leads = pd.read_csv(INPUT_CSV)
    results = []
    for _, row in leads.iterrows():
        enriched = enrich_lead(str(row["job_title"]), str(row["comment"]))
        results.append(
            {
                "email": str(row["email"]),
                "job_title": str(row["job_title"]),
                "comment": str(row["comment"]),
                **enriched, # Merge enriched fields
                "assigned_team": assign_team(enriched.get("urgency"), enriched.get("persona_type")),
            }
        )
        print(f"Total leads processed: {len(results)}")

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} leads to {OUTPUT_JSON}")
    


if __name__ == "__main__":
    main()
