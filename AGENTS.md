# Online Judge V1 - AI Agent Rules

## Scope

Current scope: V1 only.

Do not implement V2 features.

## V1 Features

- Authentication
- Dashboard
- Practice
- Problem
- Run
- Custom Input
- Submit
- Judge
- Result
- AI error help
- Problem CRUD API

## V2 Features

Do not implement:

- Learn
- Contest
- Forum
- Profile
- Admin UI
- Light mode
- Dedicated landing page
- Submission history UI
- Forgot Password

V2 navigation items may display a "Coming in V2" message where required by the UI specification.

## Run

Run supports:

- predefined Run test cases
- custom input

Run must never execute the official hidden submission test cases.

## Submit

Submit executes against the official submission test cases.

A successful Accepted submission updates the user's solved state and topic progress.

## Judge Security

Never execute user code directly inside the FastAPI process.

User code must execute inside a Docker sandbox.

Execution containers must have:

- no network access
- CPU limits
- memory limits
- execution timeout
- process/PID limits
- temporary filesystem
- no host filesystem mounts
- no Docker socket
- no privileges
- dropped Linux capabilities
- no-new-privileges

Never expose application secrets to user-code containers.

Never pass:

- DATABASE_URL
- JWT secrets
- AWS credentials
- Redis credentials
- other application secrets

to execution containers.

## Dependencies

Do not add unnecessary dependencies.

Do not introduce a framework unless there is a concrete requirement.

V1 stack:

- React
- Vite
- TypeScript
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Docker
- Python 3.12
- C++17
- Amazon Bedrock / Nova Lite
- Boto3
- Brevo for OTP email

## Architecture

Use a modular monolith with a separate judge worker process/container.

Do not introduce unnecessary microservices.

The API handles application logic.

Redis provides the V1 submission queue.

The judge worker handles code execution.

Docker provides the sandbox boundary.

## Frontend

Use React/Vite/TypeScript.

Do not add:

- Next.js
- Redux
- Material UI
- Ant Design
- Framer Motion
- large component frameworks
- unnecessary state-management libraries

Load the code editor only on the Problem page.

## Supported Languages

V1 supports:

- Python 3.12
- C++17

The language runner interface should remain extensible for future languages.

## Code Quality

Do not refactor unrelated modules.

Do not change the architecture without explicit instruction.

Keep implementations small and understandable.

Prefer correctness and security over UI polish.

Run relevant tests after changes.

## AI

AI help is explicitly user-triggered.

Do not automatically call AI.

Do not build a general chatbot.

Do not build RAG or an autonomous agent in V1.

AI help should focus on the current problem, code, and error.

## Git

Every completed checkpoint should have a Git commit.

Keep commits focused.

Do not commit secrets.

Never commit `.env` files containing real credentials.

