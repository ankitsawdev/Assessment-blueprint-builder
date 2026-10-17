
from backend.schemas.assembly_schema import (
    AssessmentAssemblyRequest,
    AssessmentAssemblyResponse,
)


def assemble_assessment(
    request: AssessmentAssemblyRequest,
) -> AssessmentAssemblyResponse:

    blueprint = request.blueprint
    retrieval = request.retrieval_result
    generation = request.generation_result

    all_questions = (
        retrieval.selected_questions
        + generation.generated_questions
    )

    unique_questions = []
    seen_texts = set()
    seen_ids = set()

    for question in all_questions:
        normalized_text = " ".join(
            question.question.strip().casefold().split()
        )

        if normalized_text in seen_texts or question.id in seen_ids:
            continue

        seen_texts.add(normalized_text)
        seen_ids.add(question.id)
        unique_questions.append(question)

    type_distribution = {}
    difficulty_distribution = {}
    skill_distribution = {}

    for question in unique_questions:
        type_distribution[question.question_type] = (
            type_distribution.get(question.question_type, 0) + 1
        )

        difficulty_distribution[question.difficulty] = (
            difficulty_distribution.get(question.difficulty, 0) + 1
        )

        skill_distribution[question.skill] = (
            skill_distribution.get(question.skill, 0) + 1
        )

    title = (
        blueprint.get("assessment_title")
        or blueprint.get("role")
        or blueprint.get("job_title")
        or "Technical Assessment"
    )

    return AssessmentAssemblyResponse(
        assessment_title=title,
        duration_minutes=blueprint.get("duration_minutes"),
        total_questions=len(unique_questions),
        total_marks=sum(q.marks for q in unique_questions),
        questions=unique_questions,
        question_type_distribution=type_distribution,
        difficulty_distribution=difficulty_distribution,
        skill_distribution=skill_distribution,
        remaining_gaps=generation.remaining_gaps,
    )
