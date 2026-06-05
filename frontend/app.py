import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8001"

st.set_page_config(page_title="Gaceella AI Hiring Assistant", layout="wide")

st.markdown("""
<style>
.header {
    background: linear-gradient(135deg, #534AB7, #1D9E75);
    padding: 1.5rem; border-radius: 12px; text-align: center; margin-bottom: 1.5rem;
}
.header h1 { color: white; margin: 0; font-size: 2rem; }
.header p  { color: rgba(255,255,255,0.85); margin: 4px 0 0; }
</style>
<div class="header">
    <h1>Gaceella AI Hiring Assistant</h1>
    <p>by gaceella &nbsp;·&nbsp; Powered by Groq + Llama 3</p>
</div>
""", unsafe_allow_html=True)

if "job_id"  not in st.session_state: st.session_state.job_id  = None
if "ranked"  not in st.session_state: st.session_state.ranked  = None

tab1, tab2, tab3 = st.tabs(["Step 1: Job Description", "Step 2: Upload CVs", "Step 3: Results"])

with tab1:
    st.subheader("Enter Job Details")
    groq_key     = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    job_title    = st.text_input("Job Title", placeholder="e.g. Senior Python Developer")
    experience   = st.number_input("Years of Experience Required", min_value=0, max_value=20, value=3)
    skills_input = st.text_area("Required Skills (one per line)", placeholder="Python\nFastAPI\nDocker", height=120)
    job_desc     = st.text_area("Job Description", placeholder="Describe the role...", height=150)

    if st.button("Create Job Posting", type="primary", use_container_width=True):
        if not groq_key.startswith("gsk_"):
            st.error("Please enter a valid Groq API key.")
        elif not job_title or not job_desc:
            st.error("Please fill in job title and description.")
        else:
            skills = [s.strip() for s in skills_input.split("\n") if s.strip()]
            try:
                resp = requests.post(f"{API_URL}/jobs/create", json={
                    "title": job_title, "description": job_desc,
                    "required_skills": skills, "experience_years": experience,
                })
                if resp.status_code == 200:
                    st.session_state.job_id   = resp.json()["job_id"]
                    st.session_state.groq_key = groq_key
                    st.success(f"Job created! ID: **{st.session_state.job_id}** — Go to Step 2")
                else:
                    st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"Cannot connect to backend. Make sure it is running.\n{e}")

with tab2:
    st.subheader("Upload Candidate CVs")
    if not st.session_state.job_id:
        st.warning("Complete Step 1 first.")
    else:
        st.info(f"Job ID: **{st.session_state.job_id}**")
        uploaded_files = st.file_uploader("Upload PDF CVs", type=["pdf"], accept_multiple_files=True)

        if uploaded_files and st.button("Process CVs", type="primary", use_container_width=True):
            with st.spinner(f"Processing {len(uploaded_files)} CVs with AI..."):
                files = [("files", (f.name, f.read(), "application/pdf")) for f in uploaded_files]
                try:
                    resp = requests.post(
                        f"{API_URL}/jobs/{st.session_state.job_id}/upload-cvs",
                        files=files,
                        headers={"x-api-key": st.session_state.groq_key},
                    )
                    if resp.status_code == 200:
                        st.success(f"Processed {resp.json()['uploaded']} CVs! Go to Step 3.")
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

with tab3:
    st.subheader("Candidate Rankings")
    if not st.session_state.job_id:
        st.warning("Complete Steps 1 and 2 first.")
    else:
        if st.button("Rank Candidates with AI", type="primary", use_container_width=True):
            with st.spinner("AI is ranking all candidates..."):
                try:
                    resp = requests.get(
                        f"{API_URL}/jobs/{st.session_state.job_id}/rank",
                        headers={"x-api-key": st.session_state.groq_key},
                    )
                    if resp.status_code == 200:
                        st.session_state.ranked = resp.json()["candidates"]
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.ranked:
            for c in st.session_state.ranked:
                score = c.get("score", 0)
                color = "green" if score >= 70 else "orange" if score >= 50 else "red"
                with st.expander(f"#{c.get('rank')} — {c.get('name')} — Score: {score}/100 — {c.get('recommendation')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Score:** :{color}[{score}/100]")
                        st.markdown(f"**Summary:** {c.get('summary','')}")
                        if c.get("matching_skills"):
                            st.markdown("**Matching Skills:** " + ", ".join(c["matching_skills"]))
                    with col2:
                        if c.get("strengths"):
                            st.markdown("**Strengths:**")
                            for s in c["strengths"]: st.markdown(f"- {s}")
                        if c.get("missing_skills"):
                            st.markdown("**Missing Skills:** " + ", ".join(c["missing_skills"]))

                    if st.button(f"Generate Interview Questions", key=f"q_{c.get('name')}"):
                        with st.spinner("Generating questions..."):
                            try:
                                qresp = requests.get(
                                    f"{API_URL}/jobs/{st.session_state.job_id}/candidates/{c.get('name')}/questions",
                                    headers={"x-api-key": st.session_state.groq_key},
                                )
                                if qresp.status_code == 200:
                                    for i, q in enumerate(qresp.json()["questions"], 1):
                                        st.markdown(f"{i}. {q}")
                            except Exception as e:
                                st.error(f"Error: {e}")
