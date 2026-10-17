AI ASSESSMENT BLUEPRINT BUILDER
Project Scope and Requirements Report

1. PROJECT OBJECTIVE
Build an AI-powered application that takes a Job Description (JD) and prepares a structured assessment tailored to the job role. The system should identify the required skills, find suitable questions from an existing question bank, generate questions when needed, and validate the final assessment before presenting it.

2. EXPECTED WORKFLOW
1. JD Input
   - Allow the user to paste a Job Description or upload it as a PDF.
   - Extract the JD text for further processing.

2. Skill and Competency Extraction
   - Identify responsibilities, mandatory skills, supporting skills, tools, seniority, experience requirements, and observable behaviours.
   - Normalize skill names, combine duplicates, and flag unclear or missing requirements for review.

3. Assessment Configuration
   - Allow configuration of question count, assessment duration, difficulty level, and question types.
   - Adjust question depth and difficulty based on role seniority and the importance of each responsibility.

4. Question Retrieval
   - Search the local question bank for questions relevant to the extracted skills.
   - Tag retrieved questions with skill, difficulty, cognitive level, job relevance, and expected response time.
   - Semantic search may use embeddings with FAISS or Chroma.

5. Question Generation
   - Generate new, scenario-based or work-sample questions when the question bank does not provide enough suitable coverage.
   - Send newly generated questions for human review before publication.

6. Assessment Validation
   - Check skill coverage, relevance, difficulty distribution, duration, and marks.
   - Detect duplicate concepts, excessive keyword overlap, uneven difficulty, and overrepresentation of any one skill.
   - Identify skills that are assessed insufficiently or are missing.

7. Final Output
   - Present the assessment with questions, question types, marks, difficulty, expected response time, total duration, and skill-wise coverage.
   - Provide an explainability report showing which JD evidence supports each extracted skill, blueprint weight, and question tag.

3. KEY FEATURES FROM THE PROJECT BRIEF
- JD Evidence Map: Connect phrases from the JD to extracted competencies and provide confidence scores.
- Adaptive Blueprint: Set question difficulty and depth according to role seniority and responsibility importance.
- Coverage Heatmap: Show assessed, under-assessed, and missing competencies before finalization.
- Semantic Tagging: Recommend relevant tags using embeddings and detect questions assigned to the wrong skill.
- Candidate Simulation: Test the assessment with synthetic response profiles to review duration, scoring spread, and whether proficiency levels can be distinguished.
- Feedback Loop: Use reviewer corrections and question performance data to improve future blueprints and tagging.

4. PROPOSED TECHNOLOGY
- Backend API: FastAPI
- LLM integration and prompt handling: LangChain
- Workflow and agent orchestration: LangGraph
- LLM provider: Gemini API (implementation choice)
- Data storage: A local question bank and competency taxonomy in JSON/CSV initially; a database can be selected for the implementation.
- Semantic retrieval: FAISS or Chroma with embeddings
- Input processing: PDF/text parsing
- Validation: Application logic plus LLM-assisted checks where appropriate

Note: FastAPI and Gemini are proposed implementation choices. The project brief specifies the capabilities and mentions a local competency taxonomy/question bank in CSV or JSON, with FAISS or Chroma as embedding options.

5. SUGGESTED AGENT / WORKFLOW RESPONSIBILITIES
- Job Description Analysis: Parse the JD and extract evidence.
- Competency Mapping: Normalize and map extracted skills to the competency taxonomy.
- Blueprint Design: Decide the skill-wise question distribution, difficulty, question count, and duration.
- Question Retrieval and Generation: Retrieve existing questions and generate questions for coverage gaps.
- Tagging and Quality Review: Apply tags, check quality, and flag issues for human review.

These are workflow responsibilities; they do not require every step to be implemented as a separate independent agent.

6. PROJECT BOUNDARIES
The core deliverable is an assessment blueprint builder, not a complete online examination platform. The initial version should focus on creating, validating, and displaying assessments. Candidate login, live test delivery, automated candidate grading, proctoring, and HR management features are outside the stated core scope unless separately approved.

7. ACCEPTANCE CRITERIA
The project will be considered complete when:
- A user can paste or upload a JD.
- The system extracts and normalizes skills and competencies.
- The user can configure assessment settings.
- Relevant questions can be retrieved from the local question bank.
- AI can generate questions for identified coverage gaps.
- The system validates coverage, relevance, difficulty, duration, and duplication.
- The output includes a structured assessment and skill-wise coverage.
- The system explains how JD evidence connects to extracted skills and selected questions.
- Newly generated questions can be flagged for human review.

8. IMPLEMENTATION PRIORITY
Phase 1: Build the basic end-to-end workflow: JD input, skill extraction, configuration, question retrieval/generation, validation, and final output.
Phase 2: Add competency normalization, duplicate detection, coverage heatmap, explainability, and human review.
Phase 3: Add candidate simulation and feedback-based improvement if time and data permit.

9. IMPORTANT CLARIFICATION
The system should not simply generate a list of questions from an LLM. It must use the JD to identify competencies, retrieve suitable existing questions, generate only where coverage is insufficient, validate the assessment, and show why the selected skills and questions are relevant.

This report defines the proposed scope based on the supplied project brief and the initial workflow research. Any changes to scope should be confirmed before implementation to avoid mid-project confusion.



python -m uvicorn backend.main:app --reload
python -m streamlit run frontend/app.py