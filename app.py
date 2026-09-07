import os
import base64
from email.mime.text import MIMEText
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from openai import OpenAI

load_dotenv()

# Gmail permissions needed by this demo.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

app = FastAPI(title="AI Mail Web Application")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

gmail_service = None


def get_gmail():
    """Create/reuse an authenticated Gmail API client."""
    global gmail_service

    if gmail_service is not None:
        return gmail_service

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                raise RuntimeError(
                    "credentials.json is missing. Download an OAuth Desktop App "
                    "credential from Google Cloud and put it in the project root."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    gmail_service = build("gmail", "v1", credentials=creds)
    return gmail_service


def header(headers, name):
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def decode_body(payload):
    """Extract a readable text/plain or text/html body."""
    if not payload:
        return ""

    mime = payload.get("mimeType", "")
    body = payload.get("body", {})
    data = body.get("data")

    if data:
        raw = base64.urlsafe_b64decode(data + "===")
        return raw.decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        text = decode_body(part)
        if text:
            return text

    return ""


def message_to_dict(msg, full=False):
    payload = msg.get("payload", {})
    headers = payload.get("headers", [])

    result = {
        "id": msg.get("id"),
        "threadId": msg.get("threadId"),
        "from": header(headers, "From"),
        "to": header(headers, "To"),
        "subject": header(headers, "Subject"),
        "date": header(headers, "Date"),
        "snippet": msg.get("snippet", ""),
        "labelIds": msg.get("labelIds", []),
    }

    if full:
        result["body"] = decode_body(payload)

    return result


def list_messages(label_ids=None, q=None, max_results=20):
    service = get_gmail()
    req = service.users().messages().list(
        userId="me",
        labelIds=label_ids or [],
        q=q,
        maxResults=max_results,
    )
    response = req.execute()

    messages = []
    for item in response.get("messages", []):
        full = (
            service.users()
            .messages()
            .get(userId="me", id=item["id"], format="full")
            .execute()
        )
        messages.append(message_to_dict(full))

    return messages


def get_message(message_id):
    service = get_gmail()
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    return message_to_dict(msg, full=True)


def send_email(to, subject, body):
    service = get_gmail()

    message = MIMEText(body, "plain", "utf-8")
    message["To"] = to
    message["Subject"] = subject

    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent = (
        service.users()
        .messages()
        .send(userId="me", body={"raw": encoded})
        .execute()
    )
    return sent.get("id")


class SendRequest(BaseModel):
    to: str
    subject: str
    body: str


class ChatRequest(BaseModel):
    command: str
    screen: Optional[str] = "inbox"
    selected_email: Optional[dict] = None


TOOLS = [
    {
        "type": "function",
        "name": "list_emails",
        "description": "List emails from Gmail. Use label INBOX for inbox and SENT for sent mail. Use a Gmail search query for filters such as is:unread or from:someone@example.com.",
        "parameters": {
            "type": "object",
            "properties": {
                "label": {
                    "type": "string",
                    "enum": ["INBOX", "SENT"],
                    "description": "Mailbox to read."
                },
                "query": {
                    "type": "string",
                    "description": "Optional Gmail search query."
                }
            },
            "required": ["label"]
        }
    },
    {
        "type": "function",
        "name": "open_email",
        "description": "Open one specific email when the user asks to read/open an email.",
        "parameters": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "Gmail message ID."
                }
            },
            "required": ["message_id"]
        }
    },
    {
        "type": "function",
        "name": "send_email",
        "description": "Send a real email through Gmail. Only use this when the user explicitly asks to send an email.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"}
            },
            "required": ["to", "subject", "body"]
        }
    },
]


def run_tool(name, args):
    if name == "list_emails":
        return list_messages([args["label"]], args.get("query") or None)
    if name == "open_email":
        return get_message(args["message_id"])
    if name == "send_email":
        message_id = send_email(args["to"], args["subject"], args["body"])
        return {"success": True, "message_id": message_id}
    raise ValueError(f"Unknown tool: {name}")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/api/inbox")
def inbox():
    try:
        return list_messages(["INBOX"])
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/sent")
def sent():
    try:
        return list_messages(["SENT"])
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/email/{message_id}")
def email(message_id: str):
    try:
        return get_message(message_id)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/send")
def send(req: SendRequest):
    try:
        message_id = send_email(req.to, req.subject, req.body)
        return {"success": True, "message_id": message_id}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/agent")
def agent(req: ChatRequest):
    system = """You are an AI email assistant controlling a Gmail web application.

You can perform real actions using tools. The user wants natural-language control
of the email application.

Rules:
1. Use the current screen and selected email context when relevant.
2. For "show unread", use Gmail query is:unread.
3. For "find/search", convert the request into a Gmail search query.
4. For "open/read", use open_email when a message id is available.
5. For sending, call send_email only when the user explicitly requests sending.
6. Never invent an email address. If the recipient is ambiguous, ask for clarification.
7. After a tool action, return a concise human-readable result.
"""

    context = {
        "current_screen": req.screen,
        "selected_email": req.selected_email,
    }

    try:
        response = openai_client.responses.create(
            model=MODEL,
            instructions=system,
            input=[
                {
                    "role": "user",
                    "content": (
                        f"Application context: {context}\n"
                        f"User command: {req.command}"
                    ),
                }
            ],
            tools=TOOLS,
        )

        tool_results = []
        action_results = []

        for item in response.output:
            if item.type == "function_call":
                import json
                args = json.loads(item.arguments)
                result = run_tool(item.name, args)
                action_results.append(
                    {"tool": item.name, "arguments": args, "result": result}
                )
                tool_results.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result),
                    }
                )

        if tool_results:
            # IMPORTANT:
            # Send the original model tool-call items together with
            # the corresponding function_call_output items.
            follow_up_input = list(response.output) + tool_results

            final = openai_client.responses.create(
                model=MODEL,
                instructions=system,
                input=follow_up_input,
                tools=TOOLS,
            )

            answer = final.output_text
        else:
            answer = response.output_text
        return {
            "answer": answer,
            "actions": action_results,
        }

    except Exception as e:
        raise HTTPException(500, str(e))
