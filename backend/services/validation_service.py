
import re
from collections import Counter

from backend.schemas.validation_schema import (
    AssessmentValidationRequest,
    AssessmentValidationResponse,
    ValidationCheck,
)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def validate_assessment(
    request: AssessmentValidationRequest,
) -> AssessmentValidationResponse:
    blueprint = request.blueprint
    assessment = request.assessment

    checks = []
    errors = []
    warnings = []

    def add_check(name: str, passed: bool, message: str) -> None:
        checks.append(
            ValidationCheck(
                name=name,
                passed=passed,
                message=message,
            )
        )
        if not passed:
            errors.append(message)

    questions = assessment.questions

    # 1. Actual question count must match the blueprint.
    expected_count = blueprint.get("total_questions")
    actual_count = len(questions)

    if expected_count is not None:
        add_check(
            "question_count",
            actual_count == expected_count,
            (
                f"Expected {expected_count} questions; "
                f"found {actual_count}."
            ),
        )
    else:
        warnings.append(
            "Blueprint mein total_questions field nahi mili."
        )

    # Also check that the assembly summary matches its question list.
    add_check(
        "assembly_question_count",
        assessment.total_questions == actual_count,
        (
            f"Assembly reports {assessment.total_questions} questions, "
            f"but its question list contains {actual_count}."
        ),
    )

    # 2. Marks must match the target and the actual question marks.
    actual_marks = sum(question.marks for question in questions)

    add_check(
        "marks_calculation",
        assessment.total_marks == actual_marks,
        (
            f"Assembly reports {assessment.total_marks} marks, "
            f"but question marks sum to {actual_marks}."
        ),
    )

    expected_marks = blueprint.get("total_marks")

    if expected_marks is not None:
        add_check(
            "total_marks",
            actual_marks == expected_marks,
            (
                f"Expected {expected_marks} marks; "
                f"actual question marks total {actual_marks}."
            ),
        )
    else:
        warnings.append(
            "Blueprint mein total_marks field nahi mili."
        )

    # 3. Validate assessment duration.
    actual_duration = assessment.duration_minutes
    expected_duration = blueprint.get("duration_minutes")

    duration_valid = (
        isinstance(actual_duration, (int, float))
        and not isinstance(actual_duration, bool)
        and actual_duration > 0
    )

    if expected_duration is not None:
        duration_valid = (
            duration_valid
            and actual_duration == expected_duration
        )

        duration_message = (
            f"Expected duration {expected_duration} minutes; "
            f"actual duration is {actual_duration} minutes."
        )
    else:
        duration_message = (
            f"Assessment duration is {actual_duration} minutes."
        )

        if actual_duration is None:
            warnings.append(
                "Blueprint mein duration_minutes nahi mila; "
                "sirf assessment duration ki basic validity check ki gayi."
            )

    add_check(
        "duration",
        duration_valid,
        duration_message,
    )

    # 4. Check duplicate IDs and question text.
    normalized_texts = [
        normalize(question.question)
        for question in questions
    ]
    question_ids = [question.id for question in questions]

    duplicate_texts = len(normalized_texts) != len(set(normalized_texts))
    duplicate_ids = len(question_ids) != len(set(question_ids))

    add_check(
        "duplicate_questions",
        not duplicate_texts and not duplicate_ids,
        (
            "Duplicate question text or question IDs found."
            if duplicate_texts or duplicate_ids
            else "No duplicate question text or IDs found."
        ),
    )

    # 5. Validate question fields and MCQ answers.
    invalid_marks = [
        question.id
        for question in questions
        if question.marks < 1
    ]

    invalid_texts = [
        question.id
        for question in questions
        if not question.question.strip()
        or not question.skill.strip()
    ]

    invalid_mcqs = []

    for question in questions:
        if question.question_type != "mcq":
            continue

        normalized_options = [
            normalize(option)
            for option in question.options
        ]

        options_are_valid = (
            len(question.options) >= 2
            and len(normalized_options) == len(set(normalized_options))
            and all(option.strip() for option in question.options)
        )

        answer_is_valid = (
            bool(question.correct_answer)
            and question.correct_answer in question.options
        )

        if not options_are_valid or not answer_is_valid:
            invalid_mcqs.append(question.id)

    fields_valid = (
        not invalid_marks
        and not invalid_texts
        and not invalid_mcqs
    )

    add_check(
        "question_fields",
        fields_valid,
        (
            f"Invalid marks: {invalid_marks}; "
            f"empty question/skill: {invalid_texts}; "
            f"invalid MCQs: {invalid_mcqs}."
            if not fields_valid
            else "Question marks, text, skills and MCQ answers are valid."
        ),
    )

    # 6. Validate skill-wise question counts.
    skill_plans = blueprint.get("skills", [])
    actual_skill_counts = Counter(
        normalize(question.skill)
        for question in questions
    )
    skill_count_issues = []

    for skill_plan in skill_plans:
        skill = skill_plan.get("skill", "").strip()

        if not skill:
            continue

        expected_skill_count = skill_plan.get("question_count")

        if expected_skill_count is None:
            allocations = skill_plan.get("allocations", [])
            if allocations:
                expected_skill_count = sum(
                    allocation.get("count", 0)
                    for allocation in allocations
                )

        if expected_skill_count is None:
            continue

        actual_skill_count = actual_skill_counts.get(
            normalize(skill),
            0,
        )

        if actual_skill_count != expected_skill_count:
            skill_count_issues.append(
                f"{skill}: expected {expected_skill_count}, "
                f"found {actual_skill_count}"
            )

    add_check(
        "skill_distribution",
        not skill_count_issues,
        (
            "Skill count mismatch: " + "; ".join(skill_count_issues)
            if skill_count_issues
            else "Skill-wise question counts match the blueprint."
        ),
    )

    # 7. Check question generation gaps.
    remaining_gaps = [
        gap
        for gap in assessment.remaining_gaps
        if gap.missing > 0
    ]

    add_check(
        "remaining_gaps",
        not remaining_gaps,
        (
            "Questions are still missing: "
            + "; ".join(
                f"{gap.skill} ({gap.missing} missing)"
                for gap in remaining_gaps
            )
            if remaining_gaps
            else "No remaining question gaps reported."
        ),
    )

    return AssessmentValidationResponse(
        is_valid=not errors,
        checks=checks,
        errors=errors,
        warnings=warnings,
    )
