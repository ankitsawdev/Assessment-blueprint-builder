
import requests
import streamlit as st

from frontend.services.api_client import retrieve_questions


def render_question_retrieval():
    if "blueprint" not in st.session_state:
        return

    st.divider()
    st.subheader("Step 3: Retrieve Questions")

    st.write(
        "Retrieve relevant questions from the existing question bank "
        "using the generated assessment blueprint."
    )

    if st.button(
        "Retrieve Questions from Question Bank",
        type="primary",
        use_container_width=True,
    ):
        try:
            with st.spinner("Retrieving relevant questions..."):
                result = retrieve_questions(
                    st.session_state["blueprint"]
                )

            st.session_state["retrieval_result"] = result
            st.success("Question retrieval completed!")

        except requests.RequestException as exc:
            st.error("Could not retrieve questions.")

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

    if "retrieval_result" in st.session_state:
        result = st.session_state["retrieval_result"]

        st.divider()
        st.subheader("Retrieval Results")

        col1, col2 = st.columns(2)

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Questions Retrieved",
                result.get("total_retrieved", 0),
            )

        with col2:
            total_missing = sum(
                gap.get("missing", 0)
                for gap in result.get("gaps", [])
            )

            st.metric(
                "Missing Questions",
                total_missing,
            )

        st.markdown("#### Retrieved Questions")
        questions = result.get("selected_questions", [])

        if questions:
            st.json(questions)
        else:
            st.info("No matching questions were retrieved.")

        st.markdown("#### Missing Question Requirements")
        gaps = result.get("gaps", [])

        if gaps:
            st.warning(
                "Some requirements could not be fulfilled "
                "from the existing question bank."
            )
            st.json(gaps)
        else:
            st.success(
                "No remaining gaps were reported by retrieval."
            )
