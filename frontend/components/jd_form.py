
import streamlit as st
import requests

from frontend.services.api_client import (
    extract_jd_from_text,
    extract_jd_from_pdf,
)


def render_jd_form():
    st.subheader("Step 1: Job Description")

    input_method = st.radio(
        "Choose input method",
        ["Paste Text", "Upload PDF"],
        horizontal=True,
    )

    if input_method == "Paste Text":
        jd_text = st.text_area(
            "Job Description",
            placeholder="Paste the complete job description here...",
            height=250,
        )

        if st.button("Extract Job Details", type="primary"):
            if not jd_text.strip():
                st.warning("Please enter a job description.")
                return

            try:
                with st.spinner("Extracting job details..."):
                    result = extract_jd_from_text(jd_text)

                st.session_state["job_description"] = result
                st.success("Job details extracted successfully!")

            except requests.RequestException as exc:
                st.error("Could not connect to the backend or extract JD.")
                st.caption(str(exc))

    else:
        uploaded_file = st.file_uploader(
            "Upload Job Description PDF",
            type=["pdf"],
        )

        if st.button("Extract Job Details", type="primary"):
            if uploaded_file is None:
                st.warning("Please upload a PDF file.")
                return

            try:
                with st.spinner("Extracting job details from PDF..."):
                    result = extract_jd_from_pdf(
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                    )

                st.session_state["job_description"] = result
                st.success("Job details extracted successfully!")

            except requests.RequestException as exc:
                st.error("Could not connect to the backend or extract JD.")
                st.caption(str(exc))

    if "job_description" in st.session_state:
        st.divider()
        st.subheader("Extracted Job Details")
        st.json(st.session_state["job_description"])
