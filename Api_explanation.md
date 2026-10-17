# AI Assessment Blueprint Builder --- Documentation

## 1. Project ka purpose

AI Assessment Blueprint Builder HR ko job description (JD) ke basis par
technical assessment banane mein help karta hai.

Ab tak ka flow:

``` text
JD Text / PDF
    ↓
1. JD Extraction
    ↓
2. Assessment Blueprint
    ↓
3. Question Retrieval ← backend/data/questions.json
    ↓
4. AI Question Generation
    ↓
5. Assessment Assembly
    ↓
Complete Assessment Response
```

Yeh documentation conversation mein implement/confirm kiye gaye code ke
basis par hai. Local code mein agar changes hain, toh local files final
source of truth hongi.

## 2. Project structure

``` text
assessment-blueprint-builder/
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── jd_routes.py
│   │   ├── assessment_routes.py
│   │   ├── question_routes.py
│   │   └── assembly_routes.py
│   ├── schemas/
│   │   ├── jd_schema.py
│   │   ├── assessment_schema.py
│   │   ├── question_schema.py
│   │   └── assembly_schema.py
│   ├── services/
│   │   ├── jd_service.py
│   │   ├── assessment_service.py
│   │   ├── question_service.py
│   │   ├── question_generation_service.py
│   │   └── assembly_service.py
│   ├── data/
│   │   └── questions.json
│   └── .env
└── requirements.txt
```

### Folder ka role

-   `routes/`: API endpoints receive aur route karte hain.
-   `schemas/`: Pydantic models; request/response fields validate karte
    hain.
-   `services/`: Actual business logic, AI calls, retrieval aur
    calculations.
-   `data/`: Existing question bank.
-   `.env`: Secret configuration, jaise Google API key.
-   `requirements.txt`: Python dependencies.

## 3. `backend/main.py`

FastAPI app create karta hai aur routers register karta hai. Har route
module ka router `app.include_router(...)` ke through include hota hai.

Project root se application run karo:

``` powershell
python -m uvicorn backend.main:app --reload
```

Swagger UI:

`http://127.0.0.1:8000/docs`

## 4. Feature 1 --- JD Extraction

### Files

-   `backend/routes/jd_routes.py`
-   `backend/schemas/jd_schema.py`
-   `backend/services/jd_service.py`
-   `backend/.env`

### Endpoints

  Method   Endpoint                   Input
  -------- -------------------------- -----------------------------------
  POST     `/job-descriptions/text`   Form field `jd_text`
  POST     `/job-descriptions/pdf`    Uploaded PDF file in `file` field

Text endpoint par `jd_text` ek form field hai, JSON body nahi, kyunki
route `Form(...)` use karta hai. PDF endpoint par user PDF upload karta
hai.

### `jd_schema.py`

`JobDescriptionResponse` structured JD fields define karta hai:

-   `job_title`
-   `experience_required`
-   `employment_type`
-   `job_location`
-   `required_skills`
-   `preferred_skills`
-   `responsibilities`
-   `qualifications`
-   `other_details`

### `jd_service.py`

-   PDF se text nikalne ke liye `pypdf` use karta hai.
-   `.env` se `GOOGLE_API_KEY` read karta hai.
-   LangChain `ChatGoogleGenerativeAI` ke through `gemini-2.5-flash`
    call karta hai.
-   Extracted details ko `JobDescriptionResponse` format mein return
    karta hai.

Flow: User text/PDF → `jd_routes.py` → `jd_service.py` → Gemini →
structured JD response.

## 5. Feature 2 --- Assessment Blueprint

### Files

-   `backend/routes/assessment_routes.py`
-   `backend/schemas/assessment_schema.py`
-   `backend/services/assessment_service.py`

### Endpoint

`POST /assessments/blueprint`

### Request body

Is endpoint ko `job_description` (Feature 1 ka response) aur `config`
(HR ki assessment settings) chahiye.

Illustrative example:

``` json
{
  "job_description": {
    "job_title": "Backend Developer",
    "experience_required": "2+ years",
    "employment_type": "Full-time",
    "job_location": "Remote",
    "required_skills": ["Python", "FastAPI", "SQL"],
    "preferred_skills": ["Docker"],
    "responsibilities": ["Build APIs"],
    "qualifications": ["Technical experience"],
    "other_details": []
  },
  "config": {
    "total_questions": 10,
    "duration_minutes": 60,
    "total_marks": 50,
    "difficulty": "mixed",
    "question_types": ["mcq", "coding", "short_answer"]
  }
}
```

Actual request mein `job_description` ke andar JD endpoint ka real
response bhejna hai. `config` values HR/user set karta hai.

### Schema aur service ka kaam

`assessment_schema.py` mein `AssessmentConfig`, `AssessmentRequest`,
`BlueprintPlan`, `SkillDistribution`, `QuestionAllocation`,
`SkillBlueprint` aur `AssessmentBlueprint` jaise models hain. Supported
question types: `mcq`, `coding`, `short_answer`, `scenario_based`.
Difficulty values: `easy`, `medium`, `hard`.

`assessment_service.py` Gemini se structured plan banwata hai,
skill-wise questions/types allocate karta hai, difficulty/marks/time
estimates set karta hai aur estimated duration configured duration se
zyada hone par error raise kar sakta hai.

Blueprint response next retrieval, generation aur assembly stages mein
use hota hai.

## 6. Feature 3 --- Question Bank & Retrieval

### Files

-   `backend/routes/question_routes.py`
-   `backend/schemas/question_schema.py`
-   `backend/services/question_service.py`
-   `backend/data/questions.json`

### Endpoint

`POST /questions/retrieve`

### Request body

Is endpoint ko `blueprint` key ke andar complete blueprint response
chahiye.

``` json
{
  "blueprint": {
    "...": "Paste the complete blueprint response here"
  }
}
```

`...` sirf placeholder hai. Actual request mein poora real blueprint
JSON paste karo.

### `questions.json`

Existing question records yahan stored hain. Sample topics mein Python
lists/tuples, decorators, FastAPI, SQL, REST pagination aur HTTP status
codes shamil hain. Question record mein `id`, `question`, `skill`,
`difficulty`, `question_type`, `marks` hote hain;
options/answer/explanation optional ho sakte hain.

### `question_service.py`

1.  JSON question bank load karta hai.
2.  Blueprint ki skill-wise allocations read karta hai.
3.  Skill, type aur difficulty ke basis par questions match karta hai.
4.  Zaroorat par type/difficulty fallback try karta hai.
5.  Duplicate questions avoid karta hai.
6.  Selected questions aur per-skill gaps return karta hai.

Retrieval response ki important keys: - `selected_questions` - `gaps` -
`total_retrieved`

Example gap: `{"skill":"Docker","required":2,"retrieved":1,"missing":1}`
ka matlab 2 Docker questions chahiye the, 1 mila aur 1 missing hai.

## 7. Feature 4 --- AI Question Generation

### Files

-   `backend/routes/question_routes.py`
-   `backend/schemas/question_schema.py`
-   `backend/services/question_generation_service.py`
-   `.env`

### Endpoint

`POST /questions/generate`

### Request body mein 2 keys zaroori hain

1.  `blueprint`: `/assessments/blueprint` ka complete response.
2.  `retrieval_result`: `/questions/retrieve` ka complete response.

``` json
{
  "blueprint": {
    "...": "Complete blueprint response"
  },
  "retrieval_result": {
    "selected_questions": [],
    "gaps": [
      {
        "skill": "Docker",
        "required": 1,
        "retrieved": 0,
        "missing": 1
      }
    ],
    "total_retrieved": 0
  }
}
```

Yeh example structure hai; `blueprint` placeholder ko actual JSON se
replace karo. Agar retrieval mein questions mile hain toh unhe
`selected_questions` mein include karo.

### `question_generation_service.py`

-   Google API key check karta hai.
-   Retrieval ke `gaps` se missing questions identify karta hai.
-   Blueprint allocations aur existing questions ka context Gemini ko
    deta hai.
-   `gemini-2.5-flash` se structured question output mangta hai.
-   Duplicate text reject karta hai, generated IDs assign karta hai aur
    MCQs ke options/answer validate karta hai.
-   Jo gaps solve nahi hue, unhe `remaining_gaps` mein return karta hai.

Response keys: `generated_questions`, `total_generated`,
`remaining_gaps`.

## 8. Feature 5 --- Assessment Assembly

### Files

-   `backend/routes/assembly_routes.py`
-   `backend/schemas/assembly_schema.py`
-   `backend/services/assembly_service.py`

### Endpoint

`POST /assessments/assemble`

### Request body mein 3 keys

1.  `blueprint`: blueprint endpoint ka complete response.
2.  `retrieval_result`: retrieval endpoint ka complete response.
3.  `generation_result`: generation endpoint ka complete response.

``` json
{
  "blueprint": {
    "...": "Complete blueprint response"
  },
  "retrieval_result": {
    "...": "Complete retrieval response"
  },
  "generation_result": {
    "...": "Complete generation response"
  }
}
```

Placeholders ko actual responses se replace karna hai.

### `assembly_service.py`

-   Retrieved aur generated questions combine karta hai.
-   Normalized question text aur IDs ke basis par duplicates remove
    karta hai.
-   Total questions aur actual total marks calculate karta hai.
-   Question type, difficulty aur skill distributions calculate karta
    hai.
-   Generation response ke remaining gaps return karta hai.

Assembly response fields: - `assessment_title` - `duration_minutes` -
`total_questions` - `total_marks` - `questions` -
`question_type_distribution` - `difficulty_distribution` -
`skill_distribution` - `remaining_gaps`

Note: `total_marks` assembled questions ke actual marks ka sum hai.
Duration blueprint se `duration_minutes` field ke through read hoti hai,
agar woh field available ho. Abhi assembly planned marks ko
automatically enforce nahi karti.

## 9. `question_schema.py` --- shared question models

`Question` ek question ka format define karta hai, jisme `id`,
`question`, `skill`, `difficulty`, `question_type`, `marks`, `options`,
`correct_answer`, `explanation` fields hain.

Related models: - `QuestionRetrievalRequest`: blueprint input. -
`QuestionGap`: required/retrieved/missing counts. -
`QuestionRetrievalResponse`: selected questions aur gaps. -
`QuestionGenerationRequest`: blueprint + retrieval response. -
`GeneratedQuestionList`: AI output ka structured format. -
`QuestionGenerationResponse`: generated questions aur remaining gaps.

## 10. `.env` aur dependencies

`.env` mein Google API key rakhi jaati hai:

``` text
GOOGLE_API_KEY=your_google_api_key
```

Actual key ko public GitHub repository mein commit mat karna; `.env` ko
`.gitignore` mein ignore karna chahiye.

`requirements.txt` mein use hone wali important dependencies: -
`fastapi[standard]` - `uvicorn` - `python-dotenv` - `pypdf` -
`python-multipart` - `langchain-core` - `langchain-google-genai`

Local requirements file mein exact versions/additional dependencies alag
ho sakti hain.

## 11. Endpoint quick reference

  -------------------------------------------------------------------------------------
  Step              Method            Endpoint                   Required input
  ----------------- ----------------- -------------------------- ----------------------
  JD text           POST              `/job-descriptions/text`   Form field `jd_text`

  JD PDF            POST              `/job-descriptions/pdf`    PDF upload field
                                                                 `file`

  Blueprint         POST              `/assessments/blueprint`   `job_description` +
                                                                 `config`

  Retrieval         POST              `/questions/retrieve`      `blueprint`

  Generation        POST              `/questions/generate`      `blueprint` +
                                                                 `retrieval_result`

  Assembly          POST              `/assessments/assemble`    `blueprint` +
                                                                 `retrieval_result` +
                                                                 `generation_result`
  -------------------------------------------------------------------------------------

Swagger UI: `http://127.0.0.1:8000/docs`

## 12. End-to-end request flow

1.  JD text/PDF submit karo aur structured JD response lo.
2.  JD response ko blueprint request ke `job_description` mein bhejo;
    assessment settings `config` mein do.
3.  Blueprint response ko retrieval request ke `blueprint` mein bhejo.
4.  Blueprint aur retrieval ke complete responses ko generation request
    mein bhejo.
5.  Blueprint, retrieval aur generation ke complete responses ko
    assembly request mein respective keys ke saath bhejo.

``` text
JD input → JD response → Blueprint response → Retrieval response
        → Generation response → Final assembly response
```

Har next API ko previous API ka **complete JSON response** bhejna
chahiye, jab tak schema explicitly partial input allow na kare. `422`
validation error aaye toh request body ke field names aur types check
karo.

## 13. Current status

-   [x] JD text/PDF extraction
-   [x] Assessment configuration aur blueprint planning
-   [x] JSON question bank retrieval
-   [x] AI question generation
-   [x] Assessment assembly
-   [ ] Assessment validation --- planned next
-   [ ] PDF/Excel export --- planned next

Current implemented scope API-based backend flow hai. Is document mein
frontend UI, database persistence, authentication, assessment
publishing, candidate attempts ya candidate evaluation ko implemented
nahi maana gaya hai.




---

## 14. Feature 6 — Assessment Validation

### Purpose

Assessment Validation ka kaam final assembled assessment ko check karna hai ki woh blueprint ki requirements follow karta hai ya nahi.

Ye feature assessment ke errors identify karta hai aur validation report return karta hai. Abhi ye automatically assessment ko correct nahi karta.

### Related files

```text
backend/
├── routes/
│   └── validation_routes.py
├── schemas/
│   └── validation_schema.py
└── services/
    └── validation_service.py
```

### 14.1 `validation_schema.py`

Is file mein validation API ke request aur response models define kiye gaye hain.

**`AssessmentValidationRequest`**

Do inputs receive karta hai:

- `blueprint`: Assessment Blueprint API ka complete response.
- `assessment`: Assessment Assembly API ka complete response.

**`ValidationCheck`**

Har individual validation ka result store karta hai:

- `name`: Validation check ka naam.
- `passed`: Check pass hua ya fail.
- `message`: Check ka result ya failure ka reason.

**`AssessmentValidationResponse`**

Final validation report return karta hai:

- `is_valid`: Assessment saare implemented checks pass karta hai ya nahi.
- `checks`: Individual validation results.
- `errors`: Failed checks ke error messages.
- `warnings`: Non-blocking warnings.

### 14.2 `validation_routes.py`

Is file mein validation API endpoint define kiya gaya hai.

**Endpoint:** `POST /assessments/validate`

Request body mein do keys bhejni hoti hain:

```json
{
  "blueprint": {
    "...": "Complete blueprint response"
  },
  "assessment": {
    "...": "Complete assembly response"
  }
}
```

Yahan `...` sirf placeholder hai. Actual request mein respective APIs ke complete JSON responses bhejne hain.

Route request ko `AssessmentValidationRequest` schema se validate karta hai aur phir `validate_assessment()` service function call karta hai. Successful validation processing ke baad `AssessmentValidationResponse` return hota hai.

### 14.3 `validation_service.py`

Is file mein actual validation logic implement ki gayi hai.

Abhi ye checks perform hote hain:

| Check | Purpose |
|---|---|
| `question_count` | Blueprint mein expected questions aur assembled assessment mein actual questions ki count compare karta hai. |
| `total_marks` | Blueprint ke planned total marks ko assembled questions ke actual marks ke sum se compare karta hai. |
| `duplicate_questions` | Duplicate question text aur duplicate question IDs check karta hai. |
| `question_fields` | Question marks positive hain ya nahi, aur MCQ mein kam-se-kam 2 options aur valid correct answer hai ya nahi, check karta hai. |
| `skill_distribution` | Blueprint ke skill-wise expected question counts ko actual counts se compare karta hai. |
| `remaining_gaps` | Check karta hai ki generation response mein koi missing questions report hue hain ya nahi. |

Assessment duration ke liye ek warning check bhi hai. Agar duration missing ya invalid hai, toh warning return hoti hai.

### 14.4 Validation result ko kaise samjhein?

Example response:

```json
{
  "is_valid": false,
  "checks": [
    {
      "name": "total_marks",
      "passed": false,
      "message": "Expected 100 marks; actual marks are 57."
    }
  ],
  "errors": [
    "Expected 100 marks; actual marks are 57."
  ],
  "warnings": []
}
```

Is result ka matlab hai ki assessment mein 57 marks hain, jabki blueprint mein 100 marks planned the.

- `is_valid: true` ka matlab hai ki saare implemented validation checks pass hue.
- `is_valid: false` ka matlab hai ki kam-se-kam ek validation fail hui.
- `errors` failed checks ke reasons batata hai.
- `warnings` aise issues batata hai jo current implementation mein validation ko automatically fail nahi karte.

**Important:** `is_valid: true` ka matlab ye nahi hai ki har question ka technical answer verified hai. Ye sirf implemented validation rules ke pass hone ko indicate karta hai.

### 14.5 Current limitations

Abhi validation feature mein:

- Marks mismatch detect hota hai, lekin marks automatically correct nahi hote.
- Invalid MCQ detect hota hai, lekin question bank ya generated question automatically update nahi hota.
- Difficulty distribution ki exact matching check nahi hoti.
- Duration ki availability check hoti hai; actual estimated duration ka detailed comparison nahi hota.
- Questions ki technical correctness aur job relevance ka independent verification nahi hota.
- Failed validation ke baad automatic retry ya correction loop implement nahi hai.

Marks mismatch fix karne ke liye question retrieval aur assessment assembly ke marks-allocation logic ko bhi blueprint ke according consistent banana hoga.

---

## 15. Current End-to-End Backend Workflow

Ab tak ke implemented backend features ka complete flow:

```text
1. JD Input
   Text / PDF
       |
       v
2. JD Extraction
   Gemini + LangChain
       |
       v
3. Assessment Blueprint
   User configuration + extracted JD
       |
       v
4. Question Retrieval
   Existing questions from questions.json
       |
       v
5. AI Question Generation
   Generate missing questions using Gemini
       |
       v
6. Assessment Assembly
   Combine retrieved + generated questions
       |
       v
7. Assessment Validation
   Check count, marks, duplicates, fields,
   skill counts and remaining gaps
       |
       v
8. Validation Report
   Validity status + checks + errors + warnings
```

### End-to-end API sequence

| Step | Endpoint | Required input |
|---|---|---|
| 1 | `POST /job-descriptions/text` or `POST /job-descriptions/pdf` | JD text or PDF |
| 2 | `POST /assessments/blueprint` | `job_description` + `config` |
| 3 | `POST /questions/retrieve` | `blueprint` |
| 4 | `POST /questions/generate` | `blueprint` + `retrieval_result` |
| 5 | `POST /assessments/assemble` | `blueprint` + `retrieval_result` + `generation_result` |
| 6 | `POST /assessments/validate` | `blueprint` + `assessment` |

Har endpoint ka response agle endpoint ki request mein use hota hai, jahan required ho.

---

## 16. Future Improvements — Not Yet Implemented

Ye improvements future scope mein hain; inhe current completed features nahi maana jana chahiye.

- **LangGraph workflow:** Retrieval, generation, assembly aur validation ko graph ke nodes ke roop mein connect karna.
- **Validation and correction loop:** Failed checks ke basis par assessment ko correct ya regenerate karke limited attempts ke saath revalidate karna.
- **PDF/Excel export:** Final assessment ko downloadable formats mein dena.
- **Database integration:** Assessments aur related data ko persist karna.
- **Frontend UI:** HR ke liye user-friendly interface banana.
- **Authentication:** HR login aur assessment management.
- **Candidate workflow:** Assessment attempts, answer submission aur evaluation.
- **Testing and deployment:** Automated tests, security checks aur production deployment.

### Current project status

Core backend prototype mein JD extraction, blueprint generation, question retrieval, AI question generation, assembly aur validation endpoints implement kiye gaye hain.

Assessment Validation feature abhi errors detect karta hai; automatic correction aur LangGraph orchestration future improvements hain. Marks allocation ki consistency ko bhi resolve karna baaki hai.


