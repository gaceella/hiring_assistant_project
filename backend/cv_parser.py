import json
from groq import Groq
from pypdf import PdfReader

CV_PARSE_PROMPT = """Extract structured information from this CV text.
Return ONLY valid JSON in this exact format:
{{
    "name": "<full name>",
    "email": "<email address>",
    "phone": "<phone number>",
    "skills": ["skill1", "skill2", "skill3"],
    "experience_years": <total years as number>,
    "education": "<highest degree and institution>",
    "current_role": "<current or most recent job title>",
    "current_company": "<current or most recent company>",
    "summary": "<2-3 sentence professional summary>"
}}

CV Text:
{cv_text}"""

def parse_cv(pdf_path: str, api_key: str) -> dict:
    try:
        reader  = PdfReader(pdf_path)
        cv_text = "\n".join(page.extract_text() for page in reader.pages)
        cv_text = cv_text[:3000]

        client   = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": CV_PARSE_PROMPT.format(cv_text=cv_text)}],
            temperature=0,
            max_tokens=400,
        )

        text   = response.choices[0].message.content
        start  = text.find("{")
        end    = text.rfind("}") + 1
        parsed = json.loads(text[start:end])
        parsed["raw_text"] = cv_text
        return parsed

    except Exception as e:
        return {
            "name": "Unknown", "email": "", "skills": [],
            "experience_years": 0, "education": "",
            "summary": f"Could not parse CV: {str(e)}", "raw_text": "",
        }
