from fastapi import FastAPI
from dotenv import load_dotenv
from backend.routes.jd_routes import router as jd_router

from backend.routes.assessment_routes import (
    router as assessment_router,
)

from backend.routes.question_routes import (
    router as question_router,
)
from backend.routes.assembly_routes import router as assembly_router

from backend.routes.validation_routes import router as validation_router

load_dotenv()

app = FastAPI(
    title="AI Assessment Blueprint Builder",
    description="Generate job-specific assessments using AI",
    version="1.0.0"
)


app.include_router(jd_router)
app.include_router(assessment_router)
app.include_router(question_router)
app.include_router(assembly_router)
app.include_router(validation_router)

@app.get("/")
def home():
    return {
        "message": "AI Assessment Blueprint Builder API is running"
    }

