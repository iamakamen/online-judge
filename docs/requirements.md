# Online Judge V1 Requirements

## Product Goal

Build a small, fast, reliable Online Judge focused on the core loop:

Login/Register
→ Dashboard
→ Practice
→ Select Problem
→ Read Problem
→ Write Code
→ Run
→ Debug
→ Submit
→ Judge
→ Result
→ Problem Solved / Continue

## V1 Scope

### Authentication

- Login
- Registration
- Email OTP verification during registration
- Username
- Password
- Confirm password
- Mandatory registration fields
- Automatic login after successful registration
- Login validation and errors
- Forgot Password is V2. In V1 it shows a "Coming in V2" message.

Authentication edge cases include:

- Empty fields
- Invalid email
- Duplicate email
- Duplicate username
- Weak password
- Password mismatch
- Wrong OTP
- Expired OTP
- OTP attempt limits
- OTP request limits
- Email service failure
- Interrupted registration
- Browser refresh during registration
- Nonexistent account
- Wrong password
- Unverified account
- Expired access token
- Invalid/expired refresh token
- Logout
- Multiple login sessions

### Dashboard

- Welcome message
- Solved count
- Global Rank display placeholder
- Day Streak
- Practice
- Learn
- Contest
- Forum
- Profile

Learn, Contest, Forum, and Profile are V2 and show a "Coming in V2"
message.

The separate Submissions statistic is not included in the V1 dashboard.

Global Rank is display-only in V1.

### Practice

- DSA topics
- Problems grouped by topic
- Solved state
- Difficulty
- Tags
- Difficulty filtering
- Tag filtering
- Combined filtering
- Topic expand/collapse
- Vertical scrolling
- Topic progress
- Topic completion visual state
- Collapsible sidebar
- Logo navigation to Dashboard
- Context-sensitive topic counts when filters are active

Recommended practice API:

- GET /api/v1/practice/topics
- GET /api/v1/problems
- GET /api/v1/problems/{id}
- GET /api/v1/problems/{id}/progress

Problem lists should support:

- topic
- difficulty
- tags
- search
- page
- page_size

Official hidden test inputs must never be returned to the browser.

### Problem Page

- Problem name
- Problem description
- Programming-language selector
- Code editor
- Expandable editor
- Run
- Submit
- Custom Input
- Output
- Result
- User-triggered AI error help
- Appropriate scrolling

The submission-history UI is V2, but V1 Submit functionality is required.

### Code Editor

V1 supports:

- Python 3.12
- C++17

Required editor behavior:

- Language-specific code preservation
- Language-specific undo/redo history
- Starter/boilerplate code
- Remove boilerplate
- Clear user-written code while retaining boilerplate
- Undo
- Redo
- Language switching
- Preserve code when switching languages
- Restore language-specific editor state

The editor should use CodeMirror 6.

For V1, frontend state or optional localStorage is sufficient for editor
state persistence.

### Run

Run has two modes:

1. Predefined Run test cases
2. User-provided custom input

Run must never use the official hidden submission test cases.

Run results should provide appropriate input, expected output, actual
output, pass/fail status, runtime, and error information.

Custom input is transient and must not require a database table.

Run must enforce:

- Time limits
- Memory limits
- Output limits
- Sandbox destruction after execution

### Submit

Submit uses only official submission test cases.

Flow:

User Code
→ Queue
→ Judge Worker
→ Compile
→ Sandbox Execution
→ Judge
→ Result

Supported verdicts include:

- Accepted
- Wrong Answer
- Compile Error
- Runtime Error
- Time Limit Exceeded
- Memory Limit Exceeded
- System Error

Submission processing must persist enough state for reliable asynchronous
execution and reconnect/retrieval behavior.

An Accepted submission marks the problem as solved and updates topic
progress.

### AI Help

AI help is explicitly user-triggered.

It must:

- Explain the specific error
- Give targeted hints
- Focus on the current problem, code, and error
- Work for Run errors
- Work for Submit errors

It must not:

- Automatically call AI
- Become a general chatbot
- Implement RAG
- Implement an autonomous agent

The planned provider is Amazon Bedrock with Nova Lite.

AI failure must not break judging.

### Problem CRUD

Problem CRUD is required at the backend level.

Required endpoints:

- POST /api/v1/problems
- GET /api/v1/problems
- GET /api/v1/problems/{id}
- PATCH /api/v1/problems/{id}
- DELETE /api/v1/problems/{id}

Create requires:

- Topic
- Title
- Statement
- Difficulty
- Tags
- Starter code
- Time limit
- Memory limit
- Run test cases
- Submit test cases

There is no V1 admin UI.

Initial problem data may be inserted through a seed script.

### V1 Database Requirements

Core entities include:

- Users
- OTP codes
- Topics
- Problems
- Test cases
- Submissions
- Submission results

Submission history is V2, but submission records and results exist in V1
because asynchronous Submit requires persistence.

Solved state may be derived from accepted submissions for V1.

### Security Requirements

User code must never execute directly inside the FastAPI process.

User code executes inside a Docker sandbox.

Execution containers require:

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

Application secrets must never be passed into user-code containers.

Never expose:

- DATABASE_URL
- JWT secrets
- AWS credentials
- Redis credentials
- Other application secrets

### Important V1 Limitations

V1 is not:

- A large-scale production judge
- A contest platform
- A social platform
- A learning platform
- A multi-region system
- A Kubernetes cluster
- A fully hardened adversarial execution environment
- A full admin platform

V1 is a focused Online Judge with:

- Authentication
- Problem practice
- Code execution
- Judging
- Progress
- Targeted AI debugging

## V2 Boundary

Do not implement:

- Dedicated landing page
- Learn
- Contest
- Contest leaderboard
- Forum
- Profile
- Admin UI
- Forgot Password
- Light mode
- Submission-history UI
- Future collaboration/community functionality
