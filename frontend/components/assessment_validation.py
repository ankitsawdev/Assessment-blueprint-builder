
import streamlit as st
import requests

from frontend.services.api_client import (
    validate_assessment,
    generate_missing_questions,
    assemble_assessment,
)


def render_assessment_validation():
    st.header("7. Assessment Validation")

    st.write(
        "Validate the assessment and try to fix missing questions automatically."
    )

    blueprint = st.session_state.get("blueprint")
    retrieval_result = st.session_state.get("retrieval_result")
    assessment = st.session_state.get("assembled_assessment")

    if not blueprint:
        st.info("First, create an assessment blueprint.")
        return

    if not assessment:
        st.info("First, assemble the assessment.")
        return

    st.caption(
        f"Questions: {assessment.get('total_questions', 0)} | "
        f"Marks: {assessment.get('total_marks', 0)} | "
        f"Duration: {assessment.get('duration_minutes', 0)} minutes"
    )

    col1, col2 = st.columns(2)

    with col1:
        validate_clicked = st.button(
            "Validate Assessment",
            type="primary",
            use_container_width=True,
        )

    with col2:
        fix_clicked = st.button(
            "Fix Issues & Revalidate",
            use_container_width=True,
        )

    if validate_clicked:
        try:
            with st.spinner("Validating assessment..."):
                result = validate_assessment(
                    blueprint=blueprint,
                    assessment=assessment,
                )

            st.session_state["validation_result"] = result
            st.rerun()

        except requests.RequestException as exc:
            st.error(f"Validation request failed: {exc}")

    if fix_clicked:
        if not retrieval_result:
            st.error(
                "Retrieval data not found. Run question retrieval again first."
            )
        else:
            try:
                with st.spinner(
                    "Generating missing questions, assembling and validating..."
                ):
                    generation_result = generate_missing_questions(
                        blueprint=blueprint,
                        retrieval_result=retrieval_result,
                    )

                    st.session_state["generation_result"] = generation_result

                    updated_assessment = assemble_assessment(
                        blueprint=blueprint,
                        retrieval_result=retrieval_result,
                        generation_result=generation_result,
                    )

                    st.session_state["assembled_assessment"] = (
                        updated_assessment
                    )

                    result = validate_assessment(
                        blueprint=blueprint,
                        assessment=updated_assessment,
                    )

                    st.session_state["validation_result"] = result

                st.rerun()

            except requests.RequestException as exc:
                st.error(
                    "Could not fix and revalidate the assessment. "
                    "Check the backend and API response."
                )

                if exc.response is not None:
                    try:
                        st.json(exc.response.json())
                    except ValueError:
                        st.code(exc.response.text)
                else:
                    st.caption(str(exc))

            except Exception as exc:
                st.error(f"Unexpected error: {exc}")

    result = st.session_state.get("validation_result")

    if not result:
        return

    st.divider()
    st.subheader("Validation Results")

    if result.get("is_valid", False):
        st.success("Assessment passed all validation checks.")
    else:
        st.error(
            "Assessment still has issues. Review the failed checks below."
        )

    checks = result.get("checks", [])

    passed_count = sum(
        1 for check in checks if check.get("passed", False)
    )
    failed_count = len(checks) - passed_count

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Checks", len(checks))
    col2.metric("Passed", passed_count)
    col3.metric("Failed", failed_count)

    st.subheader("Individual Checks")

    for check in checks:
        name = check.get("name", "Unnamed check")
        passed = check.get("passed", False)
        message = check.get("message", "")

        with st.container(border=True):
            left, right = st.columns([1, 5])

            with left:
                if passed:
                    st.success("PASS")
                else:
                    st.error("FAIL")

            with right:
                st.markdown(f"**{name.replace('_', ' ').title()}**")
                st.write(message)

    errors = result.get("errors", [])
    warnings = result.get("warnings", [])

    if errors:
        st.subheader("Errors")
        for error in errors:
            st.error(error)

    if warnings:
        st.subheader("Warnings")
        for warning in warnings:
            st.warning(warning)

    with st.expander("View complete validation response"):
        st.json(result)
