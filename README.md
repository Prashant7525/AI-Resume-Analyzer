# AI Resume Analyzer

A production-oriented Flask resume analysis and career optimization platform with ATS analysis, resume intelligence, job matching, AI-assisted writing, AI job tailoring, analysis history, PDF reports, and a professional V4.0 Resume Builder.

## Overview

AI Resume Analyzer helps users understand, improve, and tailor their resumes for real-world job applications.

The platform combines deterministic resume analysis with optional AI capabilities and a browser-based resume builder.

```text
Resume PDF
    │
    ▼
Resume Parsing
    │
    ├── ATS Analysis
    ├── Resume Quality
    ├── Resume Intelligence
    ├── Bullet Analysis
    ├── Achievement Analysis
    ├── Improvement Analysis
    └── Job Matching
             │
             ▼
       AI Job Tailoring
             │
             ▼
       Resume Builder
             │
             ▼
      Professional PDF
```

## Features

### Resume Analysis

- PDF resume upload
- PDF validation
- Resume text extraction
- Contact information detection
- Resume section detection
- ATS readiness scoring
- Resume quality scoring
- Resume structure analysis
- Resume improvement analysis
- Bullet-point analysis
- Achievement and metrics detection
- Section intelligence
- Score explanations
- Strengths and attention areas
- Action-oriented recommendations

### Job Matching

- Job description input
- Resume-to-job compatibility scoring
- Matched skills
- Missing skills
- Keyword coverage
- Keyword suggestions
- Job-specific recommendations

### AI Writing Assistant

AI-assisted resume writing for:

- Resume bullets
- Professional summaries
- Project descriptions
- Experience bullets

The application uses a centralized AI provider abstraction and validates AI input/output before presenting results.

AI functionality is optional. Core resume analysis and the Resume Builder remain usable without an AI API key.

### AI Job Tailoring

The V3.4 tailoring workflow compares a resume against a job description and produces:

- Job-match summary
- Missing skills
- Important keywords
- Tailored recommendations
- Matched keywords

Development mode also includes a deterministic fallback so the tailoring workflow can be exercised without a live AI provider.

The system is designed to avoid recommending false claims or invented skills, experience, qualifications, or achievements.

### Analysis History

- Save completed analyses
- Analysis history
- View previous analyses
- Delete saved analyses
- Saved job-match information
- Historical score information

### PDF Reports

Generate downloadable PDF analysis reports containing the resume analysis results, scores, recommendations, and analytics.

### V4.0 Resume Builder

The V4.0 Resume Builder provides a structured resume creation and editing workflow.

Supported sections:

- Personal Information
- Professional Summary
- Skills
- Experience
- Projects
- Education
- Certifications
- Achievements

Builder capabilities include:

- Multiple experience entries
- Multiple project entries
- Multiple education entries
- Bullet points for experience and projects
- Live resume preview
- Five professional resume templates
- Classic ATS
- Modern
- Minimal
- Executive
- Developer
- Local browser draft autosave
- Save draft controls
- JSON export
- JSON import
- Field validation
- Light mode
- Dark mode
- Back-to-top control
- Responsive layout
- Browser Print / Save as PDF
- A4 print formatting
- Analyzer-to-Builder resume import

### Analyzer → Builder Workflow

An analyzed resume can be transferred directly into the Resume Builder:

```text
Upload Resume
     ↓
Analyze Resume
     ↓
Review Results
     ↓
Open in Resume Builder
     ↓
Edit / Improve
     ↓
Choose Template
     ↓
Print / Save PDF
```

The import process only transfers information available from the analyzer and does not invent missing resume details.

## Project Structure

```text
AI-Resume-Analyzer/
│
├── app/
│   ├── ai/
│   │   ├── prompts.py
│   │   ├── provider.py
│   │   ├── validators.py
│   │   ├── writing_service.py
│   │   └── tailoring/
│   │       ├── prompts.py
│   │       ├── service.py
│   │       ├── validators.py
│   │       └── __init__.py
│   │
│   ├── builder/
│   │   ├── model.py
│   │   ├── service.py
│   │   ├── validators.py
│   │   └── __init__.py
│   │
│   ├── templates/
│   │   ├── builder.html
│   │   ├── error.html
│   │   ├── history.html
│   │   ├── index.html
│   │   ├── privacy.html
│   │   └── terms.html
│   │
│   ├── static/
│   │   ├── builder.js
│   │   ├── favicon.svg
│   │   └── style.css
│   │
│   ├── achievement_analyzer.py
│   ├── analytics.py
│   ├── ats_analyzer.py
│   ├── bullet_analyzer.py
│   ├── dashboard.py
│   ├── database.py
│   ├── job_matcher.py
│   ├── main.py
│   ├── report_generator.py
│   ├── resume_improvements.py
│   ├── resume_intelligence.py
│   ├── resume_parser.py
│   ├── resume_quality.py
│   ├── score_explanation.py
│   └── section_intelligence.py
│
├── tests/
│   ├── test_achievement_analyzer.py
│   ├── test_ai_provider.py
│   ├── test_ai_tailoring.py
│   ├── test_ai_writing_service.py
│   ├── test_analytics.py
│   ├── test_app.py
│   ├── test_ats_analyzer.py
│   ├── test_bullet_analyzer.py
│   ├── test_dashboard.py
│   ├── test_job_matcher.py
│   ├── test_report_generator.py
│   ├── test_resume_builder.py
│   ├── test_resume_improvements.py
│   ├── test_resume_improvements_v3.py
│   ├── test_resume_intelligence.py
│   ├── test_resume_quality.py
│   └── test_section_intelligence.py
│
├── Procfile
├── requirements.txt
├── .python-version
├── .gitignore
├── LICENSE
└── README.md
```

## Tech Stack

### Backend

- Python
- Flask
- Flask-WTF
- SQLite
- Gunicorn

### Resume Processing

- PyMuPDF
- Regular expressions
- Structured Python analysis services

### PDF Generation

- ReportLab
- Browser print / PDF export for Resume Builder

### AI

- OpenAI API through a provider abstraction
- Structured prompt and response validation
- Development fallback for job tailoring

### Frontend

- HTML
- CSS
- JavaScript
- Responsive UI
- LocalStorage for Resume Builder drafts

### Testing

- Pytest

## Local Setup

### Windows

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the application:

```powershell
python -m app.main
```

Open:

```text
http://127.0.0.1:5000
```

### Linux / WSL2

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Flask:

```bash
python -m app.main
```

For production-style local testing:

```bash
gunicorn app.main:app
```

The project has been tested with Gunicorn under Ubuntu/WSL2.

## AI Configuration

AI features are optional.

Configure the provider through environment variables appropriate to your deployment:

```text
OPENAI_API_KEY=your-key
OPENAI_MODEL=your-configured-model
OPENAI_TIMEOUT=30
```

Never commit API keys, `.env` files, or other credentials.

Example `.env` file:

```text
APP_ENV=development
SECRET_KEY=your-development-secret
OPENAI_API_KEY=your-key
OPENAI_MODEL=your-configured-model
OPENAI_TIMEOUT=30
```

## Resume Builder

Open:

```text
http://127.0.0.1:5000/builder
```

The builder works without an AI API key.

### Draft Storage

Builder drafts are stored locally in the browser using LocalStorage.

They are not automatically uploaded to the Flask server.

Use:

- **Save Draft** to explicitly save the current local draft
- **Export JSON** to create a portable backup
- **Import JSON** to restore a saved resume

### Templates

Five templates are available:

1. Classic ATS
2. Modern
3. Minimal
4. Executive
5. Developer

The templates are designed to remain readable and ATS-friendly while providing different visual styles.

### PDF Output

Use:

```text
Print / Save PDF
```

The builder uses print-specific CSS to:

- Hide the application interface
- Hide the editor
- Hide template controls
- Format the resume for A4
- Preserve template styling
- Control page breaks
- Produce a clean printable resume

Browser PDF headers and footers should be disabled when a completely clean PDF is desired.

## Security

The application includes several security and reliability measures:

- Upload size limits
- PDF signature validation
- Structural PDF validation
- Input sanitization
- Control-character removal
- CSRF protection
- Parameterized SQLite queries
- Safe database handling
- Production secret-key enforcement
- Secure session-cookie configuration in production
- Generic internal-error responses
- Debug configuration separation
- Environment-based configuration

Production mode requires:

```text
APP_ENV=production
SECRET_KEY=<strong-random-secret>
```

## Database

SQLite is used for local persistence and analysis history.

The runtime database is stored under the application's instance directory and is intentionally excluded from Git.

For a future multi-user deployment, the database layer can be migrated to a managed relational database such as PostgreSQL.

## Testing

Run the complete test suite:

```powershell
python -m pytest -q
```

Current regression suite:

```text
239 passed
```

Run only Resume Builder tests:

```powershell
python -m pytest -q tests/test_resume_builder.py
```

Run the test suite from Ubuntu/WSL2:

```bash
python -m pytest -q
```

The Resume Builder model, service, and validation layers are designed to be tested independently of the Flask web layer.

## Production

The repository includes a `Procfile` configured for Gunicorn:

```text
web: gunicorn app.main:app
```

Production environment variables should include at least:

```text
APP_ENV=production
SECRET_KEY=<strong-random-secret>
```

AI features additionally require the appropriate provider configuration.

Do not commit:

```text
.env
.venv/
.venv-linux/
.pytest_cache/
__pycache__/
app/instance/
generated reports
SQLite runtime databases
API credentials
```

## Deployment Notes

The project has been locally verified through:

```text
Windows Python environment
        ↓
239 tests passing
        ↓
Ubuntu / WSL2
        ↓
239 tests passing
        ↓
Gunicorn
        ↓
Flask application
        ↓
HTTP 200 responses
```

This provides a Linux/Gunicorn validation path before cloud deployment.

## Development Roadmap

### Completed

- V3.0 Resume Analysis Foundation
- ATS Analysis
- Resume Quality
- Job Matching
- Recommendation Engine
- Dashboard
- Analytics
- Analysis History
- PDF Reports
- V3.2 Resume Intelligence
- V3.3 AI Writing Assistant
- V3.4 AI Job Tailoring
- V4.0 Resume Builder
- Five Resume Templates
- Analyzer → Builder integration
- Browser PDF export
- Production-oriented configuration

### Future

Potential future versions may include:

- User accounts
- Authentication
- Cloud resume storage
- Saved resumes
- Personal resume dashboard
- Cross-version score analytics
- PostgreSQL-backed multi-user deployment
- Cloud file storage
- Expanded resume templates

## Development Workflow

Keep commits organized using conventional categories such as:

```text
feat:
fix:
refactor:
test:
docs:
style:
chore:
```

Examples:

```text
feat: add V4.0 resume builder
feat: connect resume analyzer to builder
fix: refine resume builder PDF print layout
test: expand resume builder validation coverage
docs: update project documentation
```

## License

See [`LICENSE`](LICENSE) for license information.
