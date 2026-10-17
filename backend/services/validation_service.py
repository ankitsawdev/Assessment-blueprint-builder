
from collections import Counter

from backend.schemas.validation_schema import (
    AssessmentValidationRequest,
    AssessmentValidationResponse,
    ValidationCheck,
)


def validate_assessment(
    request: AssessmentValidationRequest,
) -> AssessmentValidationResponse:

    blueprint = request.blueprint
    assessment = request.assessment

    checks = []
    errors = []
    warnings = []

    def add_check(name: str, passed: bool, message: str):
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

    # 1. Validate total question count against the blueprint.
    expected_count = blueprint.get("total_questions")

    if expected_count is not None:
        add_check(
            "question_count",
            len(questions) == expected_count,
            (
                f"Expected {expected_count} questions; "
                f"found {len(questions)}."
            ),
        )
    else:
        warnings.append(
            "Blueprint mein total_questions field nahi mili; "
            "exact question count verify nahi kiya ja saka."
        )

    # 2. Validate total marks.
    expected_marks = blueprint.get("total_marks")

    if expected_marks is not None:
        add_check(
            "total_marks",
            assessment.total_marks == expected_marks,
            (
                f"Expected {expected_marks} marks; "
                f"actual marks are {assessment.total_marks}."
            ),
        )
    else:
        warnings.append(
            "Blueprint mein total_marks field nahi mili; "
            "planned marks verify nahi kiye ja sake."
        )

    # 3. Validate duplicate question text and IDs.
    normalized_texts = [
        " ".join(q.question.strip().casefold().split())
        for q in questions
    ]
    question_ids = [q.id for q in questions]

    duplicate_texts = len(normalized_texts) != len(set(normalized_texts))
    duplicate_ids = len(question_ids) != len(set(question_ids))

    add_check(
        "duplicate_questions",
        not duplicate_texts and not duplicate_ids,
        "Duplicate question text or question IDs found."
        if duplicate_texts or duplicate_ids
        else "No duplicate question text or IDs found.",
    )

    # 4. Validate question marks and MCQ structure.
    invalid_marks = [
        q.id for q in questions if q.marks < 1
    ]

    invalid_mcqs = [
        q.id
        for q in questions
        if q.question_type == "mcq"
        and (
            len(q.options) < 2
            or not q.correct_answer
            or q.correct_answer not in q.options
        )
    ]

    add_check(
        "question_fields",
        not invalid_marks and not invalid_mcqs,
        (
            f"Invalid marks for questions: {invalid_marks}. "
            f"Invalid MCQ options/answers for questions: {invalid_mcqs}."
            if invalid_marks or invalid_mcqs
            else "Question marks and MCQ options/answers are valid."
        ),
    )

    # 5. Validate skill-wise question counts when present in blueprint.
    skill_plans = blueprint.get("skills", [])
    actual_skill_counts = Counter(q.skill.casefold() for q in questions)
    skill_count_issues = []

    for skill_plan in skill_plans:
        skill = skill_plan.get("skill", "")
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
            skill.casefold(), 0
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

    # 6. Check whether question generation left any gaps.
    remaining_gaps = [
        gap for gap in assessment.remaining_gaps
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

    # 7. Duration information check.
    if not assessment.duration_minutes or assessment.duration_minutes <= 0:
        warnings.append(
            "Assessment duration missing or invalid hai."
        )

    # Warnings don't make an assessment invalid; failed checks do.
    return AssessmentValidationResponse(
        is_valid=not errors,
        checks=checks,
        errors=errors,
        warnings=warnings,
    )
