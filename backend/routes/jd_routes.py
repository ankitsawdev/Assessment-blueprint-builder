
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.schemas.jd_schema import JobDescriptionResponse
from backend.services.jd_service import (
    extract_jd_information,
    extract_text_from_pdf,
)

router = APIRouter(
    prefix="/job-descriptions",
    tags=["Job Descriptions"],
)


@router.post("/text", response_model=JobDescriptionResponse)
def submit_jd_text(jd_text: str = Form(...)):
    try:
        return extract_jd_information(jd_text)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="AI extraction failed. Check API configuration and try again.",
        ) from exc


@router.post("/pdf", response_model=JobDescriptionResponse)
async def submit_jd_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Please upload a PDF file.",
            )

        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty.",
            )

        jd_text = extract_text_from_pdf(file_bytes)
        return extract_jd_information(jd_text)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="JD extraction failed. Check the PDF and AI configuration.",
        ) from exc

    finally:
        await file.close()
