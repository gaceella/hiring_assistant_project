import json
from groq import Groq

RANKING_PROMPT = """You are an expert HR recruiter in Pakistan.
Analyze the candidate CV against the job description and provide evaluation.

JOB:
Title: {job_title}
Description: {job_description}
Required Skills: {required_skills}
Experience Required: {experience_years} years

CANDIDATE:
Name: {candidate_name}
Skills: {candidate_skills}
Experience: {candidate_experience} years
Education: {candidate_education}
Summary: {candidate_summary}

Return ONLY this JSON:
{{
    "score": <0-100>,
    "recommendation": "<STRONG_YES / YES / MAYBE / NO>",
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "strengths": ["strength1", "strength2"],
    "concerns": ["concern1"],
    "summary": "<2-3 sentence evaluation>"
}}"""

def rank_candidates(job: dict, candidates: list, api_key: str) -> list:
    client = Groq(api_key=api_key)
    ranked = []

    for candidate in candidates:
        try:
            prompt = RANKING_PROMPT.format(
                job_title=job.get("title", ""),
                job_description=job.get("description", ""),
                required_skills=", ".join(job.get("required_skills", [])),
                experience_years=job.get("experience_years", 0),
                candidate_name=candidate.get("name", "Unknown"),
                candidate_skills=", ".join(candidate.get("skills", [])),
                candidate_experience=candidate.get("experience_years", 0),
                candidate_education=candidate.get("education", ""),
                candidate_summary=candidate.get("summary", ""),
            )

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500,
            )

            text  = response.choices[0].message.content
            start = text.find("{")
            end   = text.rfind("}") + 1
            evaluation = json.loads(text[start:end])

            ranked.append({
                "name":            candidate.get("name", "Unknown"),
                "email":           candidate.get("email", ""),
                "filename":        candidate.get("filename", ""),
                "score":           evaluation.get("score", 0),
                "recommendation":  evaluation.get("recommendation", "NO"),
                "matching_skills": evaluation.get("matching_skills", []),
                "missing_skills":  evaluation.get("missing_skills", []),
                "strengths":       evaluation.get("strengths", []),
                "concerns":        evaluation.get("concerns", []),
                "summary":         evaluation.get("summary", ""),
            })

        except Exception as e:
            ranked.append({
                "name": candidate.get("name", "Unknown"),
                "score": 0, "recommendation": "ERROR",
                "summary": f"Error: {str(e)}",
            })

    ranked.sort(key=lambda x: x.get("score", 0), reverse=True)
    for i, c in enumerate(ranked):
        c["rank"] = i + 1
    return ranked
