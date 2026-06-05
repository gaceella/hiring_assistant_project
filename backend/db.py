import sqlite3, json
from pathlib import Path

DB_PATH = "data/hiring.db"

def init_db():
    Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS jobs (job_id TEXT PRIMARY KEY, data TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL, data TEXT NOT NULL)")
    conn.commit(); conn.close()

def save_job(job_id, job_data):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR REPLACE INTO jobs VALUES (?, ?)", (job_id, json.dumps(job_data)))
    conn.commit(); conn.close()

def get_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT data FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def save_candidate(job_id, candidate_data):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO candidates (job_id, data) VALUES (?, ?)", (job_id, json.dumps(candidate_data)))
    conn.commit(); conn.close()

def get_candidates(job_id):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT data FROM candidates WHERE job_id = ?", (job_id,)).fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]
