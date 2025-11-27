TITAN-X CORE v1
Session-Level Behavioural Metrics Engine for Adaptive Products

Titan-X Core is a fast, lightweight, developer-friendly behavioural metrics engine designed for real-time, session-based analysis.
It helps you understand how users interact with your product — without intrusive tracking, PII, or heavy machine learning.

Built for developers building:

Adaptive UX

Onboarding flows

EdTech experiences

Productivity tools

Games and interaction-driven applications

Behaviour-aware dashboards

Real-time interaction scoring

Titan-X Core provides a clean API to ingest events, compute rolling metrics, and retrieve session summaries — all with simple JSON calls.

🚀 Key Features

Session lifecycle API (start → event → end)

Rolling behavioural metrics in real time

Lightweight, zero-ML, zero-database (v1 local state engine)

Deterministic, transparent metrics

Simple JSON payloads and responses

Fast to integrate with Postman, Bubble, Make, Zapier, JS, Python

Privacy-safe: no user tracking, no fingerprints, no PII required

Consistent response wrapper across all endpoints

📦 Installation

Clone the repository:

git clone https://github.com/<your-org>/titan-core
cd titan-core


Install dependencies:

pip install -r requirements.txt


Run the API locally:

uvicorn main_v1:app --reload


Access documentation:

http://127.0.0.1:8000/docs

🧠 How Titan Works (v1)

In v1, Titan-X Core focuses on session-level metrics, calculated from the events you send.

Each event may include:

friction

hesitation

pace

Titan automatically maintains:

number of events

average friction

average hesitation

average pace

These metrics are simple, transparent, and immediately useful for adaptive products.

Higher-resolution models and additional signals will be introduced in future versions.

📡 API Reference
1. GET /health

Quick liveness check.

Response
{
  "ok": true,
  "msg": "ok",
  "data": {}
}

2. GET /status

Returns service metadata.

Response
{
  "ok": true,
  "data": {
    "service": "titan-x-core",
    "version": "1.0.0",
    "mode": "dev"
  }
}

3. POST /v1/start

Start a behavioural session.

Request
{
  "session_id": "demo-session-1",
  "user_id": "user-123",
  "metadata": {}
}

Response
{
  "ok": true,
  "event": "session_started",
  "data": {
    "session_id": "demo-session-1",
    "user_id": "user-123"
  }
}

4. POST /v1/event

Record a behavioural event.

Request
{
  "session_id": "demo-session-1",
  "event_type": "click",
  "timestamp": 1764152000.0,
  "friction": 0.31,
  "hesitation": 0.45,
  "pace": 0.82,
  "context": {
    "page": "dashboard",
    "element": "button_play",
    "extra": {}
  }
}

Response
{
  "ok": true,
  "event": "event_recorded",
  "data": {
    "session_id": "demo-session-1",
    "event_type": "click",
    "rolling": {
      "events_count": 1,
      "average_friction": 0.31,
      "average_hesitation": 0.45,
      "average_pace": 0.82
    }
  }
}

5. POST /v1/end

Finalize a session and return summary metrics.

Request
{
  "session_id": "demo-session-1",
  "include_summary": true
}

Response
{
  "ok": true,
  "event": "session_ended",
  "data": {
    "session_id": "demo-session-1",
    "summary": {
      "events_count": 1,
      "average_friction": 0.31,
      "average_hesitation": 0.45,
      "average_pace": 0.82
    }
  }
}

🧩 Integrations

Titan-X Core works cleanly with:

Postman (collection included)

Bubble (via API Connector)

Make.com

Zapier

Any frontend (JS/React/Vue)

Any backend (Python/Node/Go/etc.)

Example integrations are included in /examples.

🛡 Privacy

Titan-X Core v1 operates entirely on non-PII interaction metrics and does not perform identity tracking or fingerprinting.

You control what metadata you send.

🔭 Roadmap

Additional behavioural signals

Weighted scoring

Developer dashboards

SDKs (JS/Python)

Titan Agent (adaptive recommendation layer)

Cross-session pattern analysis

📝 License

MIT.


## Helper Modules (v1)

### AI Support (v1)

Titan-Core includes a small deterministic support helper to make it easier to debug and adopt the API.

**Endpoint**

`POST /v1/support/ask`

**Request body**

```json
{
  "question": "How do I record events?",
  "endpoint": "/v1/event",
  "error_message": null,
  "include_examples": true
}


question (required): free-form question about using Titan-Core.

endpoint (optional): the endpoint you are working with (e.g. /v1/start, /v1/event, /v1/end).

error_message (optional): paste an error string to get a friendly explanation + hints.

include_examples (optional, default true): if true, the response may include example requests.

Typical response

{
  "ok": true,
  "event": "support_answer",
  "data": {
    "answer": "...",
    "topic_id": "record-event",
    "endpoint": "/v1/event",
    "example_request": { "...": "..." },
    "example_response_hint": "...",
    "error_explanation": null,
    "suggested_next_action": "..."
  },
  "meta": { "version": "1.0.0", "source": "titan-core-support-v1", "timestamp": 0 }
}

AI Marketing (v1)

Titan-Core also exposes a deterministic marketing helper for creating short pieces of copy
for docs, landing pages and developer outreach. There are no external AI calls – all
output is template-driven and safe to keep in a public repository.

Endpoint

POST /v1/marketing/generate

Request body

{
  "use_case": "landing_headline",
  "audience": "developer",
  "tone": "technical",
  "product_name": "Titan-Core",
  "include_variants": true
}


use_case: one of

"landing_headline"

"feature_blurb"

"dev_portal_intro"

"changelog_snippet"

"email_invite"

audience: one of "developer", "cto", "product".

tone: one of "neutral", "friendly", "technical".

product_name (optional): override the name (defaults to "Titan-Core").

include_variants (bool, default true): if false, variants will be an empty list.

Typical response

{
  "ok": true,
  "event": "marketing_copy",
  "data": {
    "primary": "Titan-Core: behavioural telemetry for real-time product decisions.",
    "variants": [
      "Add behavioural intelligence to your product with Titan-Core.",
      "Titan-Core helps you see where users slow down, hesitate and drop off."
    ],
    "use_case": "landing_headline",
    "audience": "developer",
    "tone": "technical",
    "product_name": "Titan-Core"
  },
  "meta": { "version": "1.0.0", "source": "titan-core-marketing-v1", "timestamp": 0 }
}


Paste → save.

---

## Step 2 — Commit & push

Back in VS Code:

1. Go to **Source Control** (left bar).  
2. You should see changed files (`README.md`, maybe the new routes already staged earlier).  
3. Commit message:

```text
feat: add support and marketing helpers