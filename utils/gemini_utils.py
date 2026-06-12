import json
import os

from dotenv import load_dotenv
from google import genai

from state import FinancialData
from prompts.extraction import EXTRACTION_PROMPT

load_dotenv()


def extract_financial_data(
    context: str
) -> FinancialData:

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = EXTRACTION_PROMPT.format(
        context=context
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw = response.text.strip()

    raw = raw.replace(
        "```json",
        ""
    )

    raw = raw.replace(
        "```",
        ""
    )

    raw = raw.strip()

    data = json.loads(raw)

    return FinancialData.model_validate(
        data
    )