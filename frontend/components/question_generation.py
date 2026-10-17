
import requests
import streamlit as st

from frontend.services.api_client import generate_missing_questions


def render_question_generation():
    if "retrieval_result" not in st.session_state:
        return

    st.divider()
    st.subheader("Step 4: Generate Missing Questions")

    retrieval_result = st.session_state["retrieval_result"]
    gaps = retrieval_result.get("gaps", [])

    total_missing = sum(
        gap.get("missing", 0)
        for gap in gaps
    )

    st.metric("Questions Missing from Bank", total_missing)

    if total_missing == 0:
        st.success(
            "No missing questions reported. You can proceed to assembly."
        )
        return

    st.write(
        "Gemini will generate questions for the requirements "
        "that could not be fulfilled from the existing question bank."
    )

    if st.button(
        "Generate Missing Questions with AI",
        type="primary",
        use_container_width=True,
    ):
        if "blueprint" not in st.session_state:
            st.warning("Generate the assessment blueprint first.")
            return

        try:
            with st.spinner("Generating questions with Gemini..."):
                result = generate_missing_questions(
                    blueprint=st.session_state["blueprint"],
                    retrieval_result=retrieval_result,
                )

            st.session_state["generation_result"] = result
            st.success("AI question generation completed!")

        except requests.RequestException as exc:
            st.error("Could not generate missing questions.")

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

    if "generation_result" in st.session_state:
        result = st.session_state["generation_result"]

        st.divider()
        st.subheader("AI Generation Results")

        st.metric(
            "Questions Generated",
            result.get("total_generated", 0),
        )

        generated_questions = result.get("generated_questions", [])

        if generated_questions:
            st.markdown("#### Generated Questions")
            st.json(generated_questions)
        else:
            st.info("No questions were generated.")

        remaining_gaps = result.get("remaining_gaps", [])

        st.markdown("#### Remaining Gaps After Generation")

        if remaining_gaps:
            st.warning("Some requirements still need attention.")
            st.json(remaining_gaps)
        else:
            st.success("No remaining gaps reported by the generation API.")
