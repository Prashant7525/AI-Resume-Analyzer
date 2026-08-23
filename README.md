# AI Resume Analyzer

A Flask-based resume analysis and career toolkit with ATS analysis, resume quality checks, job matching, AI-assisted writing/tailoring, analysis history, PDF reports, and a structured V4.0 Resume Builder.

## Highlights

- Resume PDF text extraction and analysis
- ATS structure and completeness checks
- Resume quality and improvement recommendations
- Job-description matching and keyword coverage
- AI-assisted summary, bullet, experience, and project writing
- AI job tailoring with deterministic development fallback
- Analysis history and saved analysis views
- PDF report generation
- Responsive dashboard UI
- Privacy and terms pages
- Secure upload limits, input sanitization, CSRF protection, and production configuration
- **V4.0 Resume Builder**
  - Structured personal information
  - Skills
  - Multiple experience entries with bullet points
  - Multiple projects with technologies, descriptions, links, and bullet points
  - Multiple education entries
  - Certifications and achievements
  - Live resume preview
  - Five visual templates
  - Local draft autosave
  - JSON export/import
  - Browser print / Save as PDF
  - Responsive layout and dark-mode support

## Project structure

```text
AI-Resume-Analyzer/
├── app/
│   ├── ai/
│   ├── builder/
│   ├── templates/
│   ├── static/
│   ├── main.py
│   ├── database.py
│   ├── ats_analyzer.py
│   ├── job_matcher.py
│   └── ...
├── tests/
├── Procfile
├── requirements.txt
└── .python-version
```

## Local setup

Create and activate a virtual environment, then install the pinned dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the application:

```powershell
python -m app.main
```

The development server uses:

```text
http://127.0.0.1:5000
```

## AI configuration

AI features are optional. Configure the provider through environment variables:

```text
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-5.6
OPENAI_TIMEOUT=30
```

Never commit `.env` files, API keys, or other secrets.

## Resume Builder

Open:

```text
/builder
```

The builder is intentionally usable without an AI key.

### Draft storage

Builder drafts are saved in the browser's local storage on the current device/browser. They are not uploaded to the server automatically.

Use **Export JSON** when you want a portable backup. **Import JSON** can restore that backup on another browser/device.

### PDF output

Use **Print / Save PDF** and choose the browser's PDF printer. The print stylesheet removes the application UI and formats the resume for A4 output.

## Testing

Run the complete test suite:

```powershell
pytest -q
```

Run only Resume Builder tests:

```powershell
pytest -q tests/test_resume_builder.py
```

The builder's Python model/service/validator layer is dependency-free and can be tested independently.

## Production notes

Set at least:

```text
APP_ENV=production
SECRET_KEY=<strong-random-secret>
OPENAI_API_KEY=<optional-ai-key>
```

Use a production WSGI server such as Gunicorn as configured by the `Procfile`.

Do not commit:

- `.env`
- `.venv/`
- `.pytest_cache/`
- `__pycache__/`
- `app/instance/`
- generated reports
- SQLite runtime databases
- API credentials

## License

See `LICENSE`.
