# AI Engineer Assessment — Customer Support Chatbot (Meridian Electronics)

## Situation

You are an AI engineer at **Meridian Electronics**, a mid-size company that sells computer products — monitors, keyboards, printers, networking gear, and accessories. Support currently runs on phone and email. Leadership wants a prototype AI chatbot for common requests: **product availability**, **placing orders**, **order history**, and **authenticating returning customers**.

The backend team exposes internal services as an **MCP server** (Streamable HTTP):

- **`MCP_SERVER_URL`** — default in this repo: `https://order-mcp-74afyau24q-uc.a.run.app/mcp`  
- **Transport:** Streamable HTTP  

## Assignment

Build a **deployable, production-oriented prototype**: clean architecture, error handling, tests where appropriate, and decisions you can defend in a security review.

### Constraints

| Area | Requirement |
|------|----------------|
| **LLM** | Cost-effective tier (e.g. **GPT-4o-mini**, **Gemini Flash**, **Claude Haiku**) via **OpenRouter**. |
| **UI** | Functional chat with **streaming** and **session history**; this repo uses **Next.js**. |
| **Deployment** | **Hugging Face Spaces** (Docker). Bonus: **Vercel** for the Clerk-enabled frontend. |
| **Scope** | Connect to the MCP server, let the agent **discover tools**, and handle workflows implied by those tools. |

The implementation in this repo follows **this** assignment.
