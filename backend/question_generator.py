from groq import Groq

QUESTIONS_PROMPT = """You are an expert technical recruiter in Pakistan.
Generate 8 personalized interview questions for this candidate.

JOB: {job_title}
REQUIRED SKILLS: {required_skills}
CANDIDATE: {candidate_name}
THEIR SKILLS: {candidate_skills}
EXPERIENCE: {experience_years} years

Generate exactly 8 questions:
- 3 technical questions based on required skills
- 2 behavioral questions
- 2 questions about experience gaps
- 1 Pakistan-specific situational question

Format as numbered list 1. 2. 3. etc."""

def generate_interview_questions(job: dict, candidate: dict, api_key: str) -> list:
    try:
        client = Groq(api_key=api_key)
        prompt = QUESTIONS_PROMPT.format(
            job_title=job.get("title", ""),
            required_skills=", ".join(job.get("required_skills", [])),
            candidate_name=candidate.get("name", ""),
            candidate_skills=", ".join(candidate.get("skills", [])),
            experience_years=candidate.get("experience_years", 0),
        )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600,
        )

        text      = response.choices[0].message.content
        lines     = text.strip().split("\n")
        questions = []
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit() and ". " in line:
                questions.append(line.split(". ", 1)[1].strip())
        return questions[:8]

    except Exception as e:
        return [f"Error generating questions: {str(e)}"]
