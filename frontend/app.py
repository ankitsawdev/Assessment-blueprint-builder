
import streamlit as st

from frontend.components.jd_form import render_jd_form
from frontend.components.assessment_form import render_assessment_form
from frontend.components.question_retrieval import render_question_retrieval
from frontend.components.question_generation import render_question_generation
from frontend.components.assessment_assembly import render_assessment_assembly
from frontend.components.assessment_validation import render_assessment_validation
from frontend.components.assessment_export import render_assessment_export


st.set_page_config(
    page_title="AI Assessment Blueprint Builder",
    page_icon="📝",
    layout="wide",
)

st.title("AI Assessment Blueprint Builder")
st.write(
    "Generate structured technical assessments from job descriptions using AI."
)

st.divider()

render_jd_form()
render_assessment_form()
render_question_retrieval()
render_question_generation()
render_assessment_assembly()
render_assessment_validation()
render_assessment_export()
