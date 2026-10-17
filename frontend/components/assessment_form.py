
import requests
import streamlit as st

from frontend.services.api_client import create_assessment_blueprint


QUESTION_TYPE_LABELS = {
    "mcq": "Multiple Choice (MCQ)",
    "coding": "Coding",
    "short_answer": "Short Answer",
    "scenario_based": "Scenario Based",
}

DEFAULT_DURATIONS = {
    "mcq": 0.5,
    "coding": 1.0,
    "short_answer": 2.0,
    "scenario_based": 2.0,
}


def render_assessment_form():
    if "job_description" not in st.session_state:
        st.info("First, extract a Job Description in Step 1.")
        return

    st.divider()
    st.subheader("Step 2: Assessment Configuration")

    with st.form("assessment_configuration_form"):
        col1, col2 = st.columns(2)

        with col1:
            total_questions = st.number_input(
                "Total Questions",
                min_value=1,
                max_value=100,
                value=20,
                step=1,
            )

            total_marks = st.number_input(
                "Total Marks",
                min_value=1,
                value=100,
                step=5,
            )

            duration_minutes = st.number_input(
                "Assessment Duration (minutes)",
                min_value=5,
                max_value=300,
                value=240,
                step=5,
            )

        with col2:
            difficulty = st.selectbox(
                "Difficulty",
                options=["easy", "medium", "hard", "mixed"],
                index=3,
            )

        st.markdown("#### Question Type Distribution")
        st.caption(
            "Set how many questions you want for each type. "
            "The counts must add up to Total Questions."
        )

        count_columns = st.columns(4)

        question_type_counts = {}

        defaults = {
            "mcq": 10,
            "coding": 10,
            "short_answer": 0,
            "scenario_based": 0,
        }

        for index, question_type in enumerate(QUESTION_TYPE_LABELS):
            with count_columns[index]:
                question_type_counts[question_type] = st.number_input(
                    QUESTION_TYPE_LABELS[question_type],
                    min_value=0,
                    max_value=100,
                    value=defaults[question_type],
                    step=1,
                    key=f"count_{question_type}",
                )

        st.markdown("#### Estimated Time per Question (minutes)")

        duration_columns = st.columns(4)
        question_durations = {}

        for index, question_type in enumerate(QUESTION_TYPE_LABELS):
            with duration_columns[index]:
                question_durations[question_type] = st.number_input(
                    QUESTION_TYPE_LABELS[question_type],
                    min_value=0.5,
                    max_value=180.0,
                    value=DEFAULT_DURATIONS[question_type],
                    step=0.5,
                    key=f"duration_{question_type}",
                )

        st.markdown("#### Mixed Difficulty Distribution")
        st.caption(
            "These percentages apply only when difficulty is Mixed. "
            "Their total must equal 100%."
        )

        difficulty_columns = st.columns(3)

        with difficulty_columns[0]:
            easy_percentage = st.number_input(
                "Easy (%)",
                min_value=0,
                max_value=100,
                value=30,
                step=5,
            )

        with difficulty_columns[1]:
            medium_percentage = st.number_input(
                "Medium (%)",
                min_value=0,
                max_value=100,
                value=50,
                step=5,
            )

        with difficulty_columns[2]:
            hard_percentage = st.number_input(
                "Hard (%)",
                min_value=0,
                max_value=100,
                value=20,
                step=5,
            )

        submitted = st.form_submit_button(
            "Generate Assessment Blueprint",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        # Keep only question types with a positive count.
        selected_counts = {
            question_type: int(count)
            for question_type, count in question_type_counts.items()
            if count > 0
        }

        if not selected_counts:
            st.warning("At least one question type must have a question.")
            return

        if sum(selected_counts.values()) != int(total_questions):
            st.error(
                f"Question counts add up to {sum(selected_counts.values())}, "
                f"but Total Questions is {int(total_questions)}. "
                "Please make both totals equal."
            )
            return

        if total_marks < total_questions:
            st.warning(
                "Total Marks must be at least equal to Total Questions."
            )
            return

        difficulty_distribution = {
            "easy": int(easy_percentage),
            "medium": int(medium_percentage),
            "hard": int(hard_percentage),
        }

        if sum(difficulty_distribution.values()) != 100:
            st.warning(
                "Easy, Medium and Hard percentages must total 100%."
            )
            return

        config = {
            "total_questions": int(total_questions),
            "duration_minutes": int(duration_minutes),
            "total_marks": int(total_marks),
            "difficulty": difficulty,
            "question_types": list(selected_counts.keys()),
            "question_type_counts": selected_counts,
            "question_duration_minutes": question_durations,
            "mixed_difficulty_distribution": difficulty_distribution,
        }

        try:
            with st.spinner("Generating assessment blueprint with AI..."):
                blueprint = create_assessment_blueprint(
                    job_description=st.session_state["job_description"],
                    config=config,
                )

            st.session_state["blueprint"] = blueprint
            st.success("Assessment blueprint generated successfully!")

        except requests.RequestException as exc:
            st.error("Could not generate the assessment blueprint.")

            if exc.response is not None:
                st.caption(
                    f"Backend response: {exc.response.status_code}"
                )

                try:
                    st.json(exc.response.json())
                except ValueError:
                    st.code(exc.response.text)
            else:
                st.caption(str(exc))

        except Exception as exc:
            st.error("An unexpected error occurred.")
            st.caption(str(exc))

    if "blueprint" in st.session_state:
        st.divider()
        st.subheader("Generated Assessment Blueprint")
        st.json(st.session_state["blueprint"])
