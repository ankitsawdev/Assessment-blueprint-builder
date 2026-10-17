
import json
import re
from pathlib import Path

from backend.database.mongodb import get_all_questions
from backend.schemas.question_schema import (
    Question,
    QuestionGap,
    QuestionRetrievalResponse,
)


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "questions.json"
)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def load_json_questions() -> list[Question]:
    """Load the original local JSON question bank."""
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        raw_questions = json.load(file)

    questions = []

    for item in raw_questions:
        try:
            questions.append(Question(**item))
        except Exception:
            continue

    return questions


def load_questions() -> list[Question]:
    """Combine JSON and MongoDB questions and remove duplicates."""
    json_questions = load_json_questions()
    database_questions = get_all_questions()

    unique_questions = []
    seen_ids = set()
    seen_texts = set()

    for question in json_questions + database_questions:
        question_text = normalize(question.question)

        if (
            question.id in seen_ids
            or question_text in seen_texts
        ):
            continue

        seen_ids.add(question.id)
        seen_texts.add(question_text)
        unique_questions.append(question)

    return unique_questions


def retrieve_questions(
    blueprint: dict,
) -> QuestionRetrievalResponse:
    skills = blueprint.get("skills", [])
    selected_questions = []
    gaps = []
    used_ids = set()

    # Questions are now retrieved from both sources.
    question_bank = load_questions()

    for skill_plan in skills:
        skill_name = skill_plan.get("skill", "").strip()
        required_count = skill_plan.get("question_count", 0)
        allocations = skill_plan.get("allocations", [])

        if not skill_name or required_count <= 0:
            continue

        skill_questions = [
            question
            for question in question_bank
            if normalize(question.skill) == normalize(skill_name)
        ]

        retrieved_for_skill = 0

        for allocation in allocations:
            desired_type = allocation.get("question_type")
            desired_difficulty = allocation.get("difficulty")
            desired_count = allocation.get("count", 1)

            candidates = [
                question
                for question in skill_questions
                if question.id not in used_ids
                and question.question_type == desired_type
                and question.difficulty == desired_difficulty
            ]

            # First fallback: match question type.
            if len(candidates) < desired_count:
                candidate_ids = {q.id for q in candidates}

                extra_candidates = [
                    q
                    for q in skill_questions
                    if q.id not in used_ids
                    and q.id not in candidate_ids
                    and q.question_type == desired_type
                ]

                candidates.extend(extra_candidates)

            # Second fallback: match difficulty.
            if len(candidates) < desired_count:
                candidate_ids = {q.id for q in candidates}

                extra_candidates = [
                    q
                    for q in skill_questions
                    if q.id not in used_ids
                    and q.id not in candidate_ids
                    and q.difficulty == desired_difficulty
                ]

                candidates.extend(extra_candidates)

            chosen = candidates[:desired_count]

            for question in chosen:
                selected_questions.append(question)
                used_ids.add(question.id)
                retrieved_for_skill += 1

        missing = max(0, required_count - retrieved_for_skill)

        if missing > 0:
            gaps.append(
                QuestionGap(
                    skill=skill_name,
                    required=required_count,
                    retrieved=retrieved_for_skill,
                    missing=missing,
                )
            )

    return QuestionRetrievalResponse(
        selected_questions=selected_questions,
        gaps=gaps,
        total_retrieved=len(selected_questions),
    )
