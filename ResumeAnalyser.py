import streamlit as st
import time
import requests
from google import genai
from pypdf import PdfReader



# SerpAPI for fetching job reviews
SERP_API_KEY = "20bcd02bdd65e4daa468dd8869b43cfb26b08aebc22dbedbc07de39a7d63b33e"  # Move to st.secrets for security

def get_job_reviews(job_title, company_name):
    """Fetch job reviews using SerpAPI from Glassdoor, Indeed, and other sources."""
    search_query = f"{job_title} {company_name} job reviews site:glassdoor.com OR site:indeed.com"
    
    params = {
        "engine": "google",
        "q": search_query,
        "api_key": SERP_API_KEY
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    
    reviews = []
    for result in data.get("organic_results", []):
        reviews.append(f"[{result['title']}]({result['link']})")
    
    return reviews if reviews else ["No reviews found."]


def AI(resume_text, job_title, company_name):
    """Analyze Resume using Google Gemini API"""
    prompt = f"""Analyze the following extracted resume text and evaluate the candidate’s suitability for a specific job role in a given company. Provide a structured breakdown along with an estimated probability of acceptance.

    **Input Resume Text:**
    {resume_text}

    **Target Job Role & Company:**
    - Job Title: {job_title}
    - Company Name: {company_name}

    **Output Requirements:**
    1. **Candidate Overview**
    2. **Education Details**
    3. **Work Experience**
    4. **Skills Analysis**
    5. **Projects & Contributions**
    6. **Role Suitability Analysis**
    7. **Acceptance Probability Calculation**
    8. **AI Insights & Recommendations**

    Be strict in acceptance probability calculation.
    """

    client = genai.Client(api_key="AIzaSyDAlgnjMS54hi0S1zbbhScRi5BYZZ1dLVU")  # Move to st.secrets for security
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    
    response_text = response.text.replace("*", "")

    # Generating job suggestions
    response2 = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"This was the analysis {response_text} Now suggest 5 more related jobs and why."
    )
    
    response2_text = response2.text.replace("*", "")
    return response_text, response2_text


# Streamlit UI
st.title("📄 Resume Analyzer")

# Form input
with st.form("job_form"):
    st.write("📌 **Enter Job Details**")
    job_title = st.text_input("Job Title:")
    company_name = st.text_input("Company Name:")
    submit = st.form_submit_button("Submit")
    if submit:
        st.success("✅ Form Submitted!")

# File upload
resume = st.file_uploader("📂 Upload Your Resume (PDF)")
if resume:
    progress = st.progress(0)
    for i in range(1, 5):
        time.sleep(0.5)
        progress.progress(25 * i)

    reader = PdfReader(resume)
    resume_text = reader.pages[0].extract_text()

    st.success("✅ Resume Uploaded!")

    # AI Analysis
    result, result2 = AI(resume_text, job_title, company_name)

    # Fetch Job Reviews
    job_reviews = get_job_reviews(job_title, company_name)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Analyzed Resume", "🌎 Job Reviews", "🔎 Suggested Jobs"])

    with tab1:
        st.header("📊 Resume Analysis")
        for chunk in result.splitlines():
            st.write(chunk)
            time.sleep(0.5)  # Streaming effect

    with tab2:
        st.header("🌎 Job Reviews from the Web")
        for review in job_reviews:
            st.markdown(f"- {review}")

    with tab3:
        st.header("🔎 Suggested Jobs")
        for chunk in result2.splitlines():
            st.write(chunk)
            time.sleep(0.5)
