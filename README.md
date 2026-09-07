# AI Mail Web Application

A 5-day assignment implementation: a browser Gmail client controlled by natural-language AI.

## What this version demonstrates

- Gmail Inbox and Sent views
- Read/open a real Gmail message
- Compose and send a real email
- Search/filter through natural language
- AI tool/function calling
- AI receives current screen + selected email context
- Browser UI updates after an AI action

## Architecture

Browser UI -> FastAPI -> OpenAI Responses API -> tool call -> Gmail API -> real Gmail mailbox

## 1. Install

Use Python 3.10+.

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
```

## 2. Google Gmail API

Create a Google Cloud project, enable Gmail API, configure OAuth consent, and create an OAuth 2.0 Desktop App client.

Download the JSON file and save it in this folder as:

credentials.json

The first run opens Google's login/consent page. After approval, token.json is created locally.

For this demo, the app asks for:
- gmail.readonly
- gmail.send

## 3. OpenAI API key

Copy `.env.example` to `.env` and put your API key in it.

Example:

OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.6-luna

If that model is not enabled for your API account, set OPENAI_MODEL to a model available in your account.

## 4. Run

```bash
uvicorn app:app --reload
```

Then open:

http://127.0.0.1:8000

The visible output is the browser application.

## 5. Demo commands

Try:

- Show unread emails
- Find emails from Sarah
- Open the latest email
- Send an email to john@example.com with subject Meeting Tomorrow and tell him to meet at 3 PM

Use a real address that you control for the first send test.

## 6. What to show the evaluator

1. Inbox loaded from real Gmail
2. Type a natural-language search and show the AI finding matching mail
3. Open a message
4. Ask the AI to summarize/read the selected message
5. Ask AI to compose/send an email
6. Open Sent and show the sent message
7. Explain that the LLM does not directly send mail: it chooses a defined tool, and the backend executes the Gmail API call.

## Important

Do not upload credentials.json, token.json, or .env to GitHub.
