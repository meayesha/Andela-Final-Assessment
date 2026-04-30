# Final Bootcamp Assessment: MCP-Powered Todo Management Chatbot

## Assessment Overview

This assessment is your opportunity to demonstrate both technical and soft skills acquired during the bootcamp. You will build, deploy, and document a complete MCP-powered solution for a real-world business scenario. Your work must be production-ready, hosted, and accompanied by clear video explanations.

---

## Problem Statement

### Business Scenario

A client needs a simple, reliable, and user-friendly Todo Management Chatbot. The chatbot should allow users to manage their personal todo lists (create, read, update, delete tasks) through natural language conversation. The backend must be built as a local MCP server, and the frontend must provide a modern, interactive chat UI with conversation history and streaming responses.

### Requirements

#### 1. MCP Server (Backend)

- Implement a local MCP server (Python) that exposes CRUD operations for todos.
- Use SQLite as the persistent data store for all todo items.
- Each todo should have: `id`, `title`, `description`, `completed` (bool), and `created_at`.
- The MCP server must expose tools for:
  - Creating a todo
  - Listing all todos
  - Updating a todo (by id)
  - Deleting a todo (by id)
  - Marking a todo as completed/incomplete
- Follow all best practices from the MCP knowledge base (async, Pydantic models, error handling, etc).

#### 2. Chatbot Agent (Middleware)

- Build an agent (using the OpenAI Agents SDK or similar) that connects to your MCP server and exposes its tools to the LLM.
- The agent should:
  - Interpret user requests (e.g., "Add 'Buy milk' to my todos", "Show all completed tasks", "Delete task 3")
  - Call the appropriate MCP tool(s) and return results in natural language.
  - Support streaming responses for a responsive UI.
  - Maintain conversation history for each user session.
- Follow all agent and MCP integration best practices from the knowledge base.

#### 3. Frontend (UI)

- Build a modern web UI (React, Next.js, or similar) that:
  - Allows users to chat with the agent to manage their todos.
  - Displays full conversation history for the session.
  - Streams agent responses in real time.
  - Clearly shows todo list state (e.g., current todos, completed/incomplete status).
- The UI must be visually clear, responsive, and user-friendly.

#### 4. Deployment

- Deploy both the backend (MCP server + agent) and frontend to a public host (e.g., Vercel, Render, AWS, etc).
- The deployed app must be accessible to reviewers via a public URL.

#### 5. Submission

- Submit your code via GitHub.
- Submit the deployed app URL and three required video links (see below) via the provided Google Form.

#### 6. Video Documentation

- Record and submit three short videos (2–3 minutes each):
  1. Scoping the business problem and identifying goals.
  2. Explaining your reasoning and walking through your codebase.
  3. Demonstrating the working, deployed app.
- Videos must show both your face and your screen (code + app). Reasoning and clarity are prioritized over polish.

#### 7. Additional Expectations

- Prioritize must-have functionality (CRUD, basic chat, deployment) before adding nice-to-haves (e.g., search, reminders, UI themes).
- Use AI tools as you would in a real job, but review and understand all code you submit.
- Follow all best practices from the MCP and agents knowledge bases.
- Document all challenges and solutions as you work (maintain clear records for review and iteration).

---

## Evaluation Criteria

- Functional, robust MCP server and agent integration
- Clean, user-friendly chat UI with streaming and history
- Successful deployment and accessibility
- Clear, thoughtful video explanations
- Adherence to best practices and knowledge base conventions
- Ownership and understanding of your code

---

Good luck! This is your chance to showcase your readiness for real-world client work.
