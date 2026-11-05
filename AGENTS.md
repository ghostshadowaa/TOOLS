# AGENTS.md — Shadow Tools

## Project scope
Shadow Tools has two distinct execution targets:
- Online dashboard: Flask on Render.
- Offline utilities: Python inside Kali NetHunter (and, where explicitly supported, Termux).

Keep online and local execution separate. Render is not a Kali host and must never be described as Android root or as having access to the user's phone.

## Change discipline
1. Read the existing implementation before editing.
2. Modify only files needed for the requested task.
3. Never overwrite, delete, rename, or reformat unrelated files.
4. Preserve existing behavior unless the user explicitly requests a change.
5. Do not add features, dependencies, services, or external data transfers without documenting their purpose.
6. Do not claim a feature works unless it has been tested; label unfinished features clearly.
7. Prefer small modules, clear interfaces, type hints where useful, and meaningful error messages.
8. Keep Python compatible with the version documented in README.md.
9. Never commit secrets, API keys, tokens, passwords, personal data, or local databases.

## Security and privacy
- Never add arbitrary shell execution, command injection, remote command execution, or a web endpoint that runs terminal commands.
- Never expose Render environment variables, filesystem contents, debug traces, or internal network services.
- Validate and normalize all user input. Protect outbound network requests against SSRF, redirects to private networks, and oversized responses.
- Use timeouts and bounded response sizes for network operations.
- Do not collect, locate, correlate, publish, or create dossiers about private people using CPF, RG, phone numbers, email addresses, names, home addresses, usernames, or similar personal identifiers.
- Do not add credential theft, password spraying, brute force, phishing, malware, stealth, persistence, or evasion functionality.
- OSINT modules must focus on public technical infrastructure and non-personal information. Make third-party data sharing explicit.
- Network and web security checks must be restricted to systems the operator owns or is explicitly authorized to assess.
- Do not automatically install or run offensive tools. Local package installation must be explicit, visible, and limited to a documented allowlist.
- Root is never assumed. Explain the difference between Android root and a Kali PRoot environment.

## Web application
- Keep Flask routes read-only and narrowly scoped.
- Do not accept arbitrary URLs where a hostname-only input is sufficient.
- Apply request-size limits, rate limits, output escaping, and safe error handling.
- Never put a Render web service's network access behind a public arbitrary scanner.
- Keep health checks lightweight and free of external dependencies.

## Tests and documentation
- Add or update tests for changed behavior.
- Run the test suite and syntax checks when possible.
- Update README.md when setup, dependencies, routes, or behavior changes.
- Keep the Render start command and health-check path in sync with the app.
