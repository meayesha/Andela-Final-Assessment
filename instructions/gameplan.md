# IDE Coding Agent Gameplan for MCP Assessment

## 🚦 Stage 0: Environment & Deployment Preparation (MANDATORY)

**Before any implementation, the agent MUST:**

1. **Analyze the Problem Statement**

   - Extract requirements for environment, dependencies, and deployment preferences.

2. **Prepare the Python Environment**

   - Ensure [uv](https://github.com/astral-sh/uv) is installed and used for all Python package management.
   - Ensure [npm](https://www.npmjs.com/) is installed for the Next.js frontend.
   - **This repository:** Python lives under `backend/` with `backend/pyproject.toml` and `backend/uv.lock`. From the repo root:
     - `cd backend && uv sync` — installs the locked environment into `backend/.venv`.
     - The FastAPI app is `backend/api/main.py` (import path `api.main:app`). The stdio MCP server is `backend/todo_mcp` (`python -m todo_mcp` with `cwd`/`PYTHONPATH` set to `backend/`).
   - A root `requirements.txt` may exist for Docker/Hugging Face convenience; treat **`backend/pyproject.toml` as the source of truth** for agent/MCP dependencies unless the Dockerfile says otherwise.
   - If any package is missing, the agent must halt and prompt for resolution.

3. **Prepare the Folder Structure**

    - **Check the current app structure:**
       - Before making changes, analyze the existing project structure to determine if it should be:
          - Built fresh from the gold standard
          - Cleaned up (spring cleaning)
          - Updated incrementally
       - **Prompt the user** to choose which action to take before proceeding.
    - Based on the deployment preference (ask the user if not specified), create the recommended folder structure:
       - If the deployment strategy is in the knowledge base, follow it exactly (see `instructions/deployment_knowledge_base/`).
       - If not, use a generic, best-practice structure (e.g., `backend/`, `frontend/`).
       - **This assessment repo** already uses `backend/` (FastAPI + MCP + SQLite), `frontend/` (Next.js App Router), and a **single root `.env`** loaded by the API and referenced by Next via `frontend/next.config.ts`. Prefer incremental changes over flattening everything to the repository root.
    - Ensure all folders and files required for the chosen deployment are present before coding begins.

4. **Maintain Environment & Structure**
   - Any time new requirements or deployment changes arise, update **`backend/pyproject.toml`** (and run `uv lock` / `uv sync` in `backend/`), root **`.env.example`**, and **`README.md`** when behavior or env vars change. Regenerate or adjust root `requirements.txt` only if Docker/HF builds depend on it.
   - Always keep the environment and structure in sync with project needs.

5. **Initiate Git Version Control**
    - After finalizing the project structure and environment setup, initialize a git repository in the project root (if not already initialized).
    - Make an initial commit with the finalized structure and environment files.

**The agent must strictly enforce this stage before any code or implementation work. If these steps are not completed, the agent must not proceed.**

This gameplan is designed to help a software engineer and their IDE coding agent complete a high-pressure MCP assessment, from problem analysis to deployment, with video documentation. It leverages the existing MCP knowledge base, prioritizes simplicity, modularity, and best practices, and ensures all steps are granular and well-documented.

**All functions must have clear type annotations and docstrings.**

---

## Agent Knowledge Base Integration

For any agent-related implementation (tool registration, tool dispatch, push notifications, user data tracking, PDF parsing, Gradio UI, agent chaining/manager pattern, external API enrichment, etc.), the IDE agent must consult the relevant guides in `instructions/agents_knowledge_base/`. These guides are atomic and contain all code patterns and best practices for agent development. This ensures that agent logic is robust, maintainable, and consistent with project conventions.

---

---

## Strategy: OpenAI Agents SDK Agent with MCP Integration

When building a chat solution that utilizes an MCP server, follow this strategy to create an OpenAI Agents SDK agent that is equipped with the MCP server and can be used as a tool by the OpenAI library chat completions API:

1. **Create an Agent Class/Function for the Role**

   - Define an agent (using the OpenAI Agents SDK) whose role is to interact with the MCP server for a specific task (e.g., retrieval, orchestration, moderation, etc.).
   - Equip the agent with the MCP server connection and tools, following the conventions in the knowledge base.

2. **Wrap the Agent Execution**

   - Implement a function (e.g., `run_agent_with_mcp`) that wraps `Runner.run` (for standard calls) or `Runner.run_streamed` (for streaming), depending on user preference.
   - This function should:
     - Accept user input and context.
     - Call the agent with the MCP server and tools.
     - Return the result (or stream chunks if streaming).
     - Be fully typed and documented.

   ```python
   async def run_agent_with_mcp(user_input: str, stream: bool = False) -> Any:
       """Run the OpenAI Agents SDK agent with MCP integration, optionally streaming."""
       if stream:
           async for chunk in Runner.run_streamed(agent, user_input):
               yield chunk
       else:
           result = await Runner.run(agent, user_input)
           return result.final_output
   ```

3. **Expose as a Tool for OpenAI Chat**

   - Register this function as a tool (using JSON schema or the conventions in the knowledge base) so it can be called by the OpenAI library chat completions API.
   - Ensure the tool is discoverable and its schema is well-documented.

4. **Follow All Knowledge Base Conventions**
   - Use only patterns, practices, and code structures established in the agents and MCP knowledge bases.
   - Ensure atomicity, modularity, and clear separation of concerns.

This approach enables seamless integration of advanced agent logic with MCP-powered tools, and allows OpenAI chat completions to leverage these agents as callable tools in a chat workflow.

## Preferred Strategy: OpenAI Agents SDK Agent with MCP Integration

When building a chat solution that utilizes an MCP server, the recommended approach is to create an OpenAI Agents SDK agent equipped with the MCP server and expose it as a tool for the OpenAI library chat completions API. **However, always ask the user if they prefer to use a different approach or have specific requirements before proceeding.**

If the user agrees to this strategy, follow these steps:

1. **Create an Agent Class/Function for the Role**

   - Define an agent (using the OpenAI Agents SDK) whose role is to interact with the MCP server for a specific task (e.g., retrieval, orchestration, moderation, etc.).
   - Equip the agent with the MCP server connection and tools, following the conventions in the knowledge base.

2. **Wrap the Agent Execution**

   - Implement a function (e.g., `run_agent_with_mcp`) that wraps `Runner.run` (for standard calls) or `Runner.run_streamed` (for streaming), depending on user preference.
   - This function should:
     - Accept user input and context.
     - Call the agent with the MCP server and tools.
     - Return the result (or stream chunks if streaming).
     - Be fully typed and documented.

   ```python
   async def run_agent_with_mcp(user_input: str, stream: bool = False) -> Any:
         """Run the OpenAI Agents SDK agent with MCP integration, optionally streaming."""
         if stream:
               async for chunk in Runner.run_streamed(agent, user_input):
                     yield chunk
         else:
               result = await Runner.run(agent, user_input)
               return result.final_output
   ```

3. **Expose as a Tool for OpenAI Chat**

   - Register this function as a tool (using JSON schema or the conventions in the knowledge base) so it can be called by the OpenAI library chat completions API.
   - Ensure the tool is discoverable and its schema is well-documented.

4. **Follow All Knowledge Base Conventions**
   - Use only patterns, practices, and code structures established in the agents and MCP knowledge bases.
   - Ensure atomicity, modularity, and clear separation of concerns.

This approach enables seamless integration of advanced agent logic with MCP-powered tools, and allows OpenAI chat completions to leverage these agents as callable tools in a chat workflow.

---

## Crucial MCP Integration Steps (before implementation)

1. **Compiling MCP Params**

   - Use and reference: `how_to_compile_mcp_server_params.md`, `how_to_connect_to_mcp_servers_using_params.md`.
   - Or use the problem statement, and if needed, search online for MCPServerStdio compatibility with Smithery or other remote MCPs.
   - Ensure params are typed and documented.

2. **Connecting and Listing Tools**

   - Use and reference: `how_to_debug_or_list_tools_on_mcp_server.md`, `how_to_connect_to_mcp_servers_using_params.md`.
   - Write code to connect to the MCP server with params and print/list available tools.
   - If needed, search online for additional examples or troubleshooting.

3. **Minimal Agent Test**

   - Write minimal code to use the agent with the tool for a basic test.
   - Reference: `how_to_equip_agents_with_tools.md`, `how_to_prompt_agents_with_tools_for_best_results.md`.

4. **Full Agent Usage**
   - Once minimal test works, expand agent logic as required by the problem statement (e.g., chatbot powered by agent with MCP tools).
   - Reference: problem statement and all relevant knowledge base files.

---

---

## Step 1: Problem Analysis & Solution Proposal

1. **Receive the Problem Statement**

   - The user provides the assessment problem to be solved using an MCP server (local or remote, from boilerplate or documentation).

2. **Knowledge Base-Driven Solution Proposal**

   - The agent consults all relevant MCP knowledge base files (code patterns, best practices, deployment guides, etc.).
   - It proposes a solution in clear, modular steps, referencing knowledge base files and including pseudocode if helpful.
   - The proposal should match this repo’s layout: **FastAPI** in `backend/api/`, **stdio MCP** in `backend/todo_mcp/`, **Next.js** in `frontend/`. Avoid introducing a second, conflicting entry layout (e.g. a root-level `api/index.py`) unless the user explicitly wants to migrate.
   - The agent prioritizes:
     - Simplicity (minimal files, clear structure)
     - Granularity (step-by-step, atomic changes)
     - Modularity (functions, clear separation of concerns)
     - Best practices (logging, error handling, config management, typing, and docstrings)

3. **User Review & Iteration**
   - The agent presents the proposal to the user for review.
   - If the user requests changes, the agent updates the proposal, explains tradeoffs/impacts, and ensures consistency with the knowledge base.
   - The agreed proposal is saved as `instructions/proposal.md`.

---

## Step 2: Iterative Implementation & Local Validation

1. **Boilerplate & Logging**

   - The agent verifies or extends the existing FastAPI app (`backend/api/main.py`): health route, logging, and env loading from the **repo root `.env`** (already wired for OpenRouter, SQLite paths, CORS, optional Clerk).
   - The user is asked to confirm basic setup (e.g., `uv run uvicorn api.main:app` from `backend/`, or **`python run_local.py`** from the repo root).
   - Any issues are documented in `instructions/challenges.md` (create that file if missing).

2. **Function-by-Function Implementation (Iterative Minimalism & Prioritization)**

   - **Prioritize must-have functionality:** Focus first on implementing the core features required for the solution to work (the "must haves").
   - **Add nice-to-haves after core is working:** Once all must-haves are functional and tested, begin adding "nice to have" features or enhancements, guided by the problem statement and user feedback.
   - **Always start with something minimal:** Write the smallest possible version of the function, endpoint, or feature that can be tested.
   - **Test immediately:** Run and verify the minimal implementation before adding complexity.
   - **Incrementally add and test:** Add one small piece of logic or a new feature, then test again. Repeat this cycle for every change.
   - The user is prompted to confirm each step works locally (or report issues).
   - All challenges, errors, and fixes are documented in `instructions/challenges.md`.

3. **Frontend Integration (if required)**

   - If a frontend is needed, the agent creates minimal UI components/pages, connects to the backend, and repeats the iterative test/confirm/log process.
   - The goal is a locally functional app (FE + BE) with all challenges documented.

4. **Local Success Confirmation**
   - Once the user confirms local functionality, the agent summarizes challenges and solutions, preparing for deployment.

### This repository — local dev quick reference

- **One command (repo root):** `python run_local.py` — starts `uv run uvicorn …` in `backend/` and `npm run dev` in `frontend/`, merges shell env with root `.env` (shell wins on conflicts). See also `./scripts/dev.sh` and `./scripts/run-backend.sh`.
- **Env:** Copy `.env.example` → `.env` at repo root. Set at least **`OPENROUTER_API_KEY`**, **`NEXT_PUBLIC_API_URL`** (e.g. `http://127.0.0.1:8000` when Next runs separately), and optional **`CORS_ORIGINS`** / Clerk vars per `README.md`.
- **LLM:** The agent uses **OpenRouter** (Chat Completions), not a hard-coded OpenAI-only path — see `backend/api/openrouter.py` and `instructions/agents_knowledge_base/how_to_connect_to_openai_agents_sdk_using_openrouter.md`.
- **Data:** Todos and agent session memory use **SQLite** under configurable paths (`DATA_DIR`, `TODO_DB_PATH`, `AGENT_DB_PATH`); empty values in `.env` are treated as unset — see `backend/api/main.py`.

---

## Step 3: Deployment

1. **Deployment Target Selection**

   - The agent asks the user for their preferred deployment environment (e.g., Vercel, AWS, local server).
   - If the environment is covered in the knowledge base, the agent provides a checklist and requests any needed info (API keys, config, etc.).
   - If not, the agent informs the user and proceeds with a best-effort/freestyle approach.

2. **Deployment Execution & Troubleshooting**

   - The agent assists with all deployment steps, referencing knowledge base guides where available.
   - The user confirms if deployment is successful.
   - Any deployment issues are logged in `instructions/challenges.md` (under a deployment section), with user/agent actions and solutions.

3. **Deployment Success Confirmation**
   - On success, the agent summarizes the deployment process and outcomes.

---

## Step 4: Final Documentation & Video Guidance

1. **Experience Summary**

   - The agent generates a final summary in `instructions/summary.md` (proposal, challenges, deployment, outcomes).
   - It also creates `instructions/experience.md` with:
     - A summary of the proposal and solution
     - Key challenges and how they were solved
     - Deployment process and results
     - Guidance for the user to record short (5 min) videos for:
       - Solution proposal
       - Challenges and solutions
       - Final deployed app demo

2. **Continuous Documentation**
   - All steps, decisions, and issues are documented in the relevant markdown files for transparency and reproducibility.

---

## References

- All solution steps must reference the relevant MCP knowledge base files, code patterns, and deployment guides used.
- For MCP integration, reference:
  - `how_to_compile_mcp_server_params.md`: How to structure MCP params
  - `how_to_connect_to_mcp_servers_using_params.md`: How to connect to MCP servers using params
  - `how_to_debug_or_list_tools_on_mcp_server.md`: How to list/debug tools on MCP servers
  - `how_to_equip_agents_with_tools.md`: How to equip agents with tools
  - `how_to_prompt_agents_with_tools_for_best_results.md`: How to prompt agents for best results
- For deployment, reference:
  - `deployment_knowledge_base/how_to_deploy_mcp_servers_to_vercel.md` — **read the “This repository” section first** (split: Next on Vercel, Python API elsewhere); the rest is a generic legacy monorepo pattern.
  - Root **`README.md`** — Vercel root directory `frontend/`, Hugging Face Docker, env vars, CORS, SQLite caveats.
  - (Other `deployment_knowledge_base/` files as available)
- Pseudocode and code snippets should be included where helpful.

---

**This gameplan ensures a seamless, transparent, and well-documented workflow for MCP assessments, maximizing the effectiveness of the IDE coding agent and supporting the engineer throughout the process.**
