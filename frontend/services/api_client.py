
import requests

API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 120


def extract_jd_from_text(jd_text: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/job-descriptions/text",
        data={"jd_text": jd_text},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def extract_jd_from_pdf(file_name: str, file_bytes: bytes) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/job-descriptions/pdf",
        files={"file": (file_name, file_bytes, "application/pdf")},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()



def create_assessment_blueprint(
    job_description: dict,
    config: dict,
) -> dict:
    payload = {
        "job_description": job_description,
        "config": config,
    }

    response = requests.post(
        f"{API_BASE_URL}/assessments/blueprint",
        json=payload,
        timeout=TIMEOUT,
    )

    response.raise_for_status()
    return response.json()



def retrieve_questions(blueprint: dict) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/questions/retrieve",
        json={"blueprint": blueprint},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()



def generate_missing_questions(
    blueprint: dict,
    retrieval_result: dict,
) -> dict:
    payload = {
        "blueprint": blueprint,
        "retrieval_result": retrieval_result,
    }

    response = requests.post(
        f"{API_BASE_URL}/questions/generate",
        json=payload,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def assemble_assessment(
    blueprint: dict,
    retrieval_result: dict,
    generation_result: dict,
) -> dict:
    payload = {
        "blueprint": blueprint,
        "retrieval_result": retrieval_result,
        "generation_result": generation_result,
    }

    response = requests.post(
        f"{API_BASE_URL}/assessments/assemble",
        json=payload,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def validate_assessment(
    blueprint: dict,
    assessment: dict,
) -> dict:
    """Validate the assembled assessment through the backend."""
    response = requests.post(
        f"{API_BASE_URL}/assessments/validate",
        json={
            "blueprint": blueprint,
            "assessment": assessment,
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()