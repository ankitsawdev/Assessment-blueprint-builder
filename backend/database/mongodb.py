
import hashlib
import os
import re
from datetime import datetime, timezone
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from backend.schemas.question_schema import Question

load_dotenv()


def normalize(text: str) -> str:
    """Normalize question text for duplicate detection."""
    return re.sub(r"\s+", " ", text.strip()).casefold()


def create_fingerprint(question_text: str) -> str:
    """Create a stable fingerprint from normalized question text."""
    normalized_text = normalize(question_text)
    return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient:
    """Create and reuse one MongoDB client."""
    uri = os.getenv("MONGODB_URI")

    if not uri:
        raise RuntimeError(
            "MONGODB_URI is missing. Configure it in backend/.env."
        )

    return MongoClient(
        uri,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
    )


def get_question_collection() -> Collection:
    """Return the questions collection and ensure unique fingerprints."""
    database_name = os.getenv(
        "MONGODB_DATABASE",
        "assessment_blueprint_builder",
    )

    client = get_mongo_client()
    collection = client[database_name]["questions"]

    # Verify that Atlas is reachable.
    client.admin.command("ping")

    # MongoDB prevents two documents from having the same fingerprint.
    collection.create_index(
        [("fingerprint", 1)],
        unique=True,
        name="unique_question_fingerprint",
    )

    # Useful for filtering questions by skill.
    collection.create_index(
        [("skill_normalized", 1)],
        name="skill_normalized_index",
    )

    return collection


def get_all_questions() -> list[Question]:
    """Load saved questions from MongoDB."""
    collection = get_question_collection()
    saved_questions = []

    for document in collection.find(
        {},
        {
            "_id": 0,
            "id": 1,
            "question": 1,
            "skill": 1,
            "difficulty": 1,
            "question_type": 1,
            "marks": 1,
            "options": 1,
            "correct_answer": 1,
            "explanation": 1,
        },
    ):
        try:
            saved_questions.append(Question(**document))
        except Exception:
            # Ignore old or malformed records instead of breaking retrieval.
            continue

    return saved_questions


def save_generated_questions(
    questions: list[Question],
) -> int:
    """
    Save generated questions without inserting duplicate question text.
    Returns the number of newly inserted questions.
    """
    if not questions:
        return 0

    collection = get_question_collection()
    inserted_count = 0

    for question in questions:
        fingerprint = create_fingerprint(question.question)

        document = question.model_dump()
        document.update(
            {
                "fingerprint": fingerprint,
                "skill_normalized": normalize(question.skill),
                "source": "gemini_generated",
                "created_at": datetime.now(timezone.utc),
            }
        )

        try:
            result = collection.update_one(
                {"fingerprint": fingerprint},
                {"$setOnInsert": document},
                upsert=True,
            )

            if result.upserted_id is not None:
                inserted_count += 1

        except DuplicateKeyError:
            # Another concurrent request may have inserted it first.
            continue

    return inserted_count
