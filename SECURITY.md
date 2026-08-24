# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in AI Resume Analyzer, please
report it privately through GitHub's available security reporting tools
rather than opening a public issue.

Please include:

- A clear description of the vulnerability
- Steps to reproduce the issue
- The affected component or endpoint
- Relevant logs or screenshots when appropriate
- The potential impact

Please do not include API keys, passwords, personal information,
resume contents, or other sensitive data in a public issue or report.

## Supported Version

The `main` branch represents the current production release.

Development work may continue on feature and development branches.

## Security Practices

The project currently includes:

- PDF upload validation
- Upload size limits
- Input sanitization
- CSRF protection
- Secure production configuration
- Environment-based secrets
- Safe database handling
- Generic internal error responses

Never commit:

- API keys
- Passwords
- `.env` files
- Database files
- Generated reports
- Other private credentials