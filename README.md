# AI Mail Agent

> An AI-powered Gmail web application that turns natural-language instructions into real email operations through a simple web interface.

## Overview

AI Mail Agent is a lightweight Gmail client integrated with an AI assistant. Unlike a conventional chatbot, the assistant can interpret natural-language requests, select a controlled backend tool, execute the operation against Gmail, and present the result in the application.

The project focuses on real Gmail integration, LLM tool calling, UI control, clean separation of concerns, and safe credential handling.

## Features

### Mail Client
- Real Gmail Inbox
- Real Gmail Sent view
- Email detail retrieval
- Compose email UI
- Real email sending through Gmail API
- Gmail search/filter support

### AI Assistant
Example commands:
```text
Show unread emails
Show my sent emails
Find emails from Sarah
Find emails about internship
```

The assistant converts natural-language intent into structured Gmail operations.

### AI Tools

| Tool | Purpose |
|---|---|
| `list_emails` | Retrieve Inbox/Sent messages and apply Gmail search queries |
| `open_email` | Retrieve a specific email |
| `send_email` | Send a real email through Gmail |

## Architecture

```text
Browser UI
 HTML / CSS / JavaScript
          |
          | HTTP / JSON
          v
     FastAPI Backend
          |
     +----+----+
     |         |
     v         v
 OpenAI      Gmail API
 Responses   OAuth 2.0
 API + Tools
```

### AI request flow

For:

```text
Show unread emails
```

1. Browser sends the command to `/api/agent`.
2. FastAPI provides the command and current UI context to the model.
3. OpenAI selects the appropriate function/tool.
4. The backend executes the tool against Gmail.
5. Gmail returns real messages.
6. The tool result is returned to the model with the corresponding tool-call context.
7. The model generates the final response.
8. The frontend displays the result in the AI Assistant panel.

This keeps AI decision-making separate from actual application-side execution.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| AI | OpenAI Responses API |
| AI integration | Function / tool calling |
| Email provider | Google Gmail API |
| Authentication | Google OAuth 2.0 |
| Configuration | `.env` |
| Server | Uvicorn |
| Version control | Git / GitHub |

## Project Structure

```text
ai-mail-agent/
├── static/
│   └── index.html
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Local-only files are intentionally excluded:

```text
.env
credentials.json
token.json
.venv/
__pycache__/
```

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Serves the web application |
| `/api/inbox` | GET | Returns Gmail Inbox messages |
| `/api/sent` | GET | Returns Gmail Sent messages |
| `/api/email/{message_id}` | GET | Retrieves a specific email |
| `/api/send` | POST | Sends an email through Gmail |
| `/api/agent` | POST | Processes a natural-language AI command |

## Gmail Integration

The application uses the Gmail API for real mail operations.

Implemented operations include:
- Listing Inbox messages
- Listing Sent messages
- Searching messages with Gmail query syntax
- Retrieving full message details
- Sending MIME-formatted emails through Gmail

### OAuth scopes

```text
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.send
```

OAuth tokens are stored locally and excluded from Git.

## Context Awareness

The AI request includes application context such as:
- Current screen/view
- Currently selected email, when available

This allows the assistant to understand that its command is being issued within the mail application rather than as an isolated chat.

## Security

Secrets are deliberately excluded from the public repository.

`.gitignore` protects:

```text
.env
credentials.json
token.json
.venv/
__pycache__/
```

Create `.env` locally:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.6-luna
```

Never commit real API keys or OAuth credentials.

## Local Setup

### Prerequisites

- Python 3.10+
- Git
- Google account with Gmail access
- Google Cloud project with Gmail API enabled
- Google OAuth credentials
- OpenAI API key

### 1. Clone

```bash
git clone https://github.com/shapnamasha2302214-droid/ai-mail-agent.git
cd ai-mail-agent
```

### 2. Create virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure OpenAI

Create `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.6-luna
```

### 5. Configure Gmail OAuth

1. Create/select a Google Cloud project.
2. Enable the Gmail API.
3. Configure the OAuth consent screen.
4. Create an OAuth client.
5. Download the client JSON.
6. Rename it to `credentials.json`.
7. Place it in the project root.

Do not commit this file.

### 6. Run

```bash
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Complete Google OAuth on the first authenticated Gmail request.

## Engineering Decisions

### FastAPI

FastAPI provides a lightweight backend boundary between the browser, AI integration, and Gmail service.

### Gmail API

Using the real Gmail API demonstrates actual mail integration rather than relying on mock email data.

### Function/tool calling

The assistant is designed as an action-oriented agent:

```text
Natural language
       ↓
AI intent
       ↓
Tool selection
       ↓
Backend execution
       ↓
Real Gmail operation
```

This makes the AI an interface controller rather than only a text generator.

### Lightweight architecture

The implementation intentionally avoids unnecessary infrastructure for an assignment-sized MVP. The design can be extended without replacing the core layers.

## Assignment Evaluation Mapping

| Evaluation area | Implementation |
|---|---|
| Real mail integration | Google Gmail API |
| Inbox / Sent | Gmail API |
| Compose and send | Web UI + Gmail API |
| AI compose/control | OpenAI tool calling |
| Search/filter | Natural language → Gmail queries |
| UI context | Current screen + selected email context |
| Clean architecture | UI / FastAPI / AI / Gmail separation |
| Credential safety | `.gitignore` + environment variables |

## Current Limitations

The current implementation is intentionally focused on the core MVP.

Potential extensions:
- Gmail push notifications for true background real-time synchronization
- AI-powered reply and forward
- Human confirmation before sending
- Full conversation/thread view
- Rich email cards in the AI panel
- More advanced multi-step agent orchestration
- Production authentication and deployment

## Future Improvements

### Real-time synchronization
Use Gmail watch/history APIs and a backend notification channel so new messages can appear without manual refresh.

### Human-in-the-loop sending
Show recipient, subject, and body for confirmation before executing a real send.

### Reply and forward
Add dedicated tools for replying to and forwarding the currently selected message.

### Thread view
Group related Gmail messages into conversation threads.

### Rich AI UI
Render email previews, sender, subject, date, and action buttons directly in the assistant panel.

### Production deployment
Add HTTPS, secure secret management, production OAuth configuration, user authentication, background jobs, monitoring, and logging.

## Demo

Add screenshots to a `docs/` directory:

```text
docs/
├── inbox.png
├── ai-assistant.png
└── compose.png
```

Recommended demo flow:
1. Show Gmail Inbox.
2. Ask `Show unread emails`.
3. Ask `Show my sent emails`.
4. Perform an AI search.
5. Compose and send an email.
6. Show the sent message.

## Testing Checklist

- [ ] Gmail OAuth works
- [ ] Inbox displays real messages
- [ ] Sent displays real messages
- [ ] Email detail works
- [ ] Normal compose/send works
- [ ] AI unread search works
- [ ] AI sent-email query works
- [ ] AI search works
- [ ] Tool calls return successfully
- [ ] `.env` is not committed
- [ ] `credentials.json` is not committed
- [ ] `token.json` is not committed
- [ ] Repository is publicly accessible

## Repository

https://github.com/shapnamasha2302214-droid/ai-mail-agent

## Author

**Vivin M J**

AI Mail Agent — Engineering Hiring Assignment
