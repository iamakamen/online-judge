# Online Judge V1 Architecture

## 1. Architectural Goal

V1 is a focused Online Judge implemented as a modular monolith with a separate asynchronous judge worker.

The architecture is intentionally small:

- React/Vite frontend
- FastAPI backend
- PostgreSQL
- Redis
- Separate judge worker
- Docker-based execution sandbox
- Amazon Bedrock / Nova Lite for explicitly triggered AI error help
- Brevo for OTP email

The system should avoid unnecessary microservices and infrastructure.

---

## 2. High-Level Architecture

```text
Browser
  |
  | HTTPS
  v
React / Vite Frontend
  |
  | REST API
  v
FastAPI Application
  |
  +--------------------+
  |                    |
  v                    v
PostgreSQL           Redis
                       |
                       | submission queue
                       v
                 Judge Worker
                       |
                       v
                 Docker Sandbox
                  /                            /                     Python 3.12          C++17
```

The FastAPI application is the modular monolith. The judge worker is a
separate process/container because arbitrary user code must never execute
inside the API process.

---

## 3. Frontend

### Technology

- React
- Vite
- TypeScript
- CodeMirror 6

The frontend contains the V1 user flow:

```text
Login/Register
    |
Dashboard
    |
Practice
    |
Problem
    |
Run / Custom Input
    |
Submit
    |
Result
```

The code editor is loaded only on the Problem page.

V1 does not introduce a large frontend framework or unnecessary state
management library.

---

## 4. Backend

### Technology

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

The backend is a modular monolith.

A proposed internal organization is:

```text
backend/
└── app/
    ├── main.py
    ├── api/
    ├── core/
    ├── db/
    ├── models/
    ├── schemas/
    ├── services/
    ├── repositories/
    └── workers/
```

The exact internal module structure may evolve during implementation, but
the system remains a modular monolith rather than being split into
unnecessary microservices.

---

## 5. API Responsibilities

The API handles:

- Authentication
- Registration
- OTP verification
- Login
- Token handling
- Dashboard data
- Practice/topic data
- Problem retrieval
- Problem CRUD
- Run requests
- Custom-input execution requests
- Submit requests
- Submission persistence
- Submission status retrieval
- Result retrieval
- User progress
- Explicit AI-help requests

The API must not directly execute arbitrary user code.

---

## 6. Authentication Architecture

Registration uses email OTP verification.

The registration flow is:

```text
User enters registration data
        |
        v
Validate registration data
        |
        v
Generate OTP
        |
        v
Store OTP securely
        |
        v
Send OTP through Brevo
        |
        v
User enters OTP
        |
        v
Verify OTP
        |
        v
Create/activate account
        |
        v
Log user in
```

Authentication uses access and refresh token concepts.

The backend must handle:

- Expired access tokens
- Invalid/expired refresh tokens
- Logout
- Multiple sessions
- OTP expiry
- OTP attempt limits
- OTP request limits

Credentials and secrets must not be stored in source control.

---

## 7. Database Architecture

PostgreSQL is the primary relational datastore.

Core entities include:

```text
Users
OTP Codes
Topics
Problems
Test Cases
Submissions
Submission Results
```

The database is accessed by the FastAPI application and, where required
by the judge workflow, by trusted backend/worker components.

Official hidden test inputs must never be returned to the browser.

### Problem/Test Case Separation

A problem stores its metadata and statement separately from test cases.

Test cases distinguish between:

- Run test cases
- Official Submit test cases

Run test cases are allowed to be exposed as appropriate to the user
experience.

Official Submit test inputs remain server-side and are never returned to
the frontend.

---

## 8. Redis Architecture

Redis provides the V1 asynchronous submission queue.

The intended Submit flow is:

```text
Frontend
   |
   v
FastAPI
   |
   +--> Persist submission
   |
   +--> Enqueue job in Redis
              |
              v
         Judge Worker
```

Redis is not the system of record for submissions. PostgreSQL remains
the durable datastore.

Redis is used for queueing and asynchronous coordination.

---

## 9. Judge Worker

The judge worker is separate from the FastAPI application.

Its responsibilities are:

1. Read a submission job from Redis.
2. Load the required trusted problem/test-case information.
3. Prepare an isolated execution environment.
4. Compile the submission when required.
5. Execute the code against the appropriate test cases.
6. Enforce resource limits.
7. Determine the verdict.
8. Persist the result.
9. Update the submission state.
10. Allow the frontend to retrieve the result.

The worker must not expose arbitrary execution capabilities to the public
internet.

---

## 10. Run Architecture

Run is synchronous from the user's perspective, but execution still uses
the same secure sandboxing principles.

Run supports:

- Predefined Run test cases
- Custom input

Run must never execute the official hidden submission test cases.

Conceptually:

```text
Frontend
   |
   v
FastAPI
   |
   v
Execution Service / Worker
   |
   v
Docker Sandbox
   |
   v
Execution Result
   |
   v
Frontend
```

Custom input is transient and does not require a dedicated database table.

---

## 11. Submit Architecture

Submit is asynchronous.

```text
User Code
   |
   v
FastAPI
   |
   +--> Create submission record
   |
   +--> Queue submission in Redis
              |
              v
         Judge Worker
              |
              v
         Docker Sandbox
              |
              v
       Compile / Execute
              |
              v
       Judge Test Cases
              |
              v
      Persist final result
```

Supported verdicts include:

- Accepted
- Wrong Answer
- Compile Error
- Runtime Error
- Time Limit Exceeded
- Memory Limit Exceeded
- System Error

An Accepted submission updates the user's solved state and topic
progress.

---

## 12. Docker Sandbox Architecture

Arbitrary user code executes inside Docker containers.

The sandbox is the security boundary for V1 execution.

Each execution must use a temporary isolated environment.

Required restrictions include:

- No network access
- CPU limits
- Memory limits
- Execution timeout
- Process/PID limits
- Temporary filesystem
- No host filesystem mounts
- No Docker socket
- No privileges
- Dropped Linux capabilities
- no-new-privileges

The execution container must not receive application secrets.

Never pass into an execution container:

```text
DATABASE_URL
JWT secrets
AWS credentials
Redis credentials
Other application secrets
```

The sandbox must be destroyed after execution.

---

## 13. Language Runner Architecture

V1 supports:

```text
Python 3.12
C++17
```

The runner interface should be extensible so future languages can be added
without rewriting the judge architecture.

A conceptual interface is:

```text
Language
   |
   +--> prepare
   +--> compile (if required)
   +--> execute
   +--> collect result
```

Python executes using the required Python 3.12 runtime.

C++17 is compiled before execution.

Compilation and execution occur inside the sandbox.

---

## 14. Resource Limits

Each execution must have explicit limits for:

- CPU
- Memory
- Wall-clock execution time
- Process/PID count
- Output size

The exact numeric values are implementation/configuration decisions and
must be centralized rather than scattered through application code.

---

## 15. AI Help Architecture

AI help is explicitly user-triggered.

The intended flow is:

```text
User clicks AI Help
       |
       v
Frontend sends problem/code/error context
       |
       v
FastAPI
       |
       v
Amazon Bedrock / Nova Lite
       |
       v
Targeted explanation / hint
       |
       v
Frontend
```

AI help is not part of the normal judge path.

A Bedrock failure must not cause judging to fail.

V1 does not implement:

- General chatbot behavior
- RAG
- Autonomous agents
- Automatic AI calls

AI help is scoped to the current problem, code, and error.

---

## 16. Email Architecture

Brevo is used for registration OTP email.

The email provider is an external integration and must be accessed only
from trusted backend code.

Email credentials must be stored as environment/secret configuration and
never committed to Git.

Email delivery failure is handled as an authentication failure case and
must not expose credentials or internal provider details to the user.

---

## 17. Deployment Architecture

The initial development/deployment environment is an AWS EC2 Linux host.

Docker runs on the EC2 instance.

The initial infrastructure is:

```text
AWS EC2
 |
 +-- Docker
      |
      +-- PostgreSQL
      +-- Redis
      +-- FastAPI application
      +-- Frontend
      +-- Judge worker
      +-- Execution containers created for judge jobs
```

The current development machine is Windows 10, but WSL is not a required
part of the project architecture because Docker and the application
environment are being hosted on the AWS EC2 Linux machine.

---

## 18. Docker Compose

Docker Compose is used for the initial multi-container development
environment.

Current infrastructure services include:

- PostgreSQL 16
- Redis 7

Application and judge services can be added to the Compose configuration
as implementation proceeds.

Database and Redis ports should remain bound to localhost on the EC2 host
unless there is a specific, justified requirement to expose them.

---

## 19. Frontend/Backend Communication

The frontend communicates with the backend through REST APIs.

The browser must not connect directly to:

- PostgreSQL
- Redis
- Docker
- Judge containers
- AWS credentials
- Other internal infrastructure

The API is the trusted boundary between the browser and backend services.

---

## 20. Data Flow Summary

### Registration

```text
Browser
  -> FastAPI
  -> PostgreSQL
  -> Brevo
```

### Login

```text
Browser
  -> FastAPI
  -> PostgreSQL
  -> Token response
```

### Practice

```text
Browser
  -> FastAPI
  -> PostgreSQL
```

### Run

```text
Browser
  -> FastAPI
  -> Secure execution
  -> Docker sandbox
  -> Result
  -> Browser
```

### Submit

```text
Browser
  -> FastAPI
  -> PostgreSQL
  -> Redis
  -> Judge Worker
  -> Docker sandbox
  -> PostgreSQL
  -> Browser
```

### AI Help

```text
Browser
  -> FastAPI
  -> Bedrock / Nova Lite
  -> Browser
```

---

## 21. V1 vs V2 Architectural Boundary

The following remain outside the V1 architecture:

- Dedicated landing page
- Learn system
- Contest system
- Contest leaderboard
- Forum
- Profile
- Admin UI
- Forgot Password
- Submission-history UI
- Light mode
- Large-scale distributed judge infrastructure
- Kubernetes
- Multi-region deployment
- General-purpose AI chatbot
- RAG
- Autonomous AI agent

V2 navigation may still display "Coming in V2" where required by the
product specification.

---

## 22. Architecture Principles

1. Keep V1 small.
2. Keep the API modular but monolithic.
3. Keep judging asynchronous.
4. Never execute user code in the API process.
5. Treat Docker as the execution isolation boundary.
6. Keep official hidden test data server-side.
7. Keep PostgreSQL as the durable source of truth.
8. Use Redis for queueing, not durable submission storage.
9. Keep AI explicitly user-triggered.
10. Do not introduce unnecessary infrastructure.
11. Keep secrets outside Git.
12. Prefer understandable implementations over premature abstraction.
