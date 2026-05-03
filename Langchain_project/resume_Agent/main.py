import streamlit as st
import os
from pathlib import Path

from pdfoperation import pdf_loader, split_text
from chroma_db import add_resume, delete_resume, query_search, get_all_resumes
from models import embeddings

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

import dotenv

dotenv.load_dotenv()


if "show_manage" not in st.session_state:
    st.session_state.show_manage = False

if "show_all_resumes" not in st.session_state:
    st.session_state.show_all_resumes = False

if "llm" not in st.session_state:
    st.session_state.llm = init_chat_model(
        model="openai/gpt-oss-120b",
        model_provider="openai",
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("groq_api"),
    )

llm = st.session_state.llm


def deduplicate(docs, metas, dists):
    seen = set()
    results = []

    for doc, meta, dist in zip(docs, metas, dists):
        rid = meta.get("resume_id")
        if rid and rid not in seen:
            seen.add(rid)
            results.append({"doc": doc, "meta": meta, "dist": dist})

    return results


def explain_match(job_desc, resume_chunk):
    messages = [
        SystemMessage(
            content="You are an HR assistant. Explain why the resume matches the job."
        ),
        HumanMessage(
            content=f"""
Job Description:
{job_desc}

Resume Snippet:
{resume_chunk}

Explain in 3–4 bullet points.
"""
        ),
    ]
    return llm.invoke(messages).content




st.set_page_config(layout="wide")
st.title("📄 Resume RAG & ATS Shortlisting")


with st.sidebar:
    st.header("Resume Management")

    file = st.file_uploader("Upload Resume (PDF)", type="pdf")

    if file:
        path = f"_temp_{file.name}"
        with open(path, "wb") as f:
            f.write(file.getbuffer())

        if st.button("Index Resume", use_container_width=True):
            text, meta = pdf_loader(path)
            chunks = split_text(text)

            texts = [f"search_document: {c}" for c in chunks]
            embed = embeddings(texts)

            resume_id = Path(file.name).stem

            metadatas = [
                {
                    "resume_id": resume_id,
                    "source": meta["source"],
                    "page_count": meta["page_count"],
                    "chunk_index": i,
                }
                for i in range(len(chunks))
            ]

            add_resume(resume_id, chunks, embed, metadatas)
            st.success("✅ Resume indexed")

    if st.button("View All Resumes", use_container_width=True):
        st.session_state.show_all_resumes = True


if st.session_state.show_all_resumes:
    st.subheader("All Indexed Resumes")

    data = get_all_resumes()
    metas = data.get("metadatas", [])

    seen = set()
    for meta in metas:
        rid = meta["resume_id"]
        if rid not in seen:
            seen.add(rid)
            st.write(f"📌 Resume ID: {rid}")


st.divider()
st.subheader("Shortlist Candidates")

job_description = st.text_area("Paste Job Description", height=220)
top_k = st.slider("Candidates to shortlist", 1, 10, 5)

if st.button("Shortlist"):
    if not job_description.strip():
        st.warning("Enter job description")
    else:
        results = query_search(job_description, top_k=top_k * 3)

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]

        final = deduplicate(docs, metas, dists)[:top_k]

        for i, item in enumerate(final, 1):
            st.subheader(f"Candidate {i}")
            st.write(f"Resume ID: {item['meta']['resume_id']}")
            st.write(f"Relevance Score: {1 - item['dist']:.2f}")

            with st.expander("Matching Content"):
                st.write(item["doc"])

            with st.expander("AI Explanation"):
                st.write(explain_match(job_description, item["doc"]))
                recent=explain_match(job_description, item["doc"])
            
            

