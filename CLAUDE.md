# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development
```bash
# Start development servers with hot reload (frontend + backend)
pnpm run dev

# Individual dev servers
npm run frontend:dev    # Frontend only (port 3000)
npm run backend:dev     # Backend only (port auto-assigned)

# CopilotKit Agent & Express Server
cd agent && python server.py              # Agent server (port 8000)
cd express && npx ts-node server.ts       # Express CopilotKit proxy (port 4000)

# Test agent locally
cd agent && python agent.py               # Run agent test

# Build production version
./build-npm-package.sh
```

### Testing & Validation
```bash
# Run all checks (frontend + backend)
npm run check

# Frontend specific
cd frontend && npm run lint          # Lint TypeScript/React code
cd frontend && npm run format:check  # Check formatting
cd frontend && npx tsc --noEmit     # TypeScript type checking

# Backend specific  
cargo test --workspace               # Run all Rust tests
cargo test -p <crate_name>          # Test specific crate
cargo test test_name                # Run specific test
cargo fmt --all -- --check          # Check Rust formatting
cargo clippy --all --all-targets --all-features -- -D warnings  # Linting

# Agent specific
cd agent && python agent.py         # Test agent functionality
cd express && npx ts-node server.ts # Test express server

# Type generation (after modifying Rust types)
npm run generate-types               # Regenerate TypeScript types from Rust
npm run generate-types:check        # Verify types are up to date
```

### Database Operations
```bash
# SQLx migrations
sqlx migrate run                     # Apply migrations
sqlx database create                 # Create database

# Database is auto-copied from dev_assets_seed/ on dev server start
```

## Architecture Overview

### Tech Stack
- **Backend**: Rust with Axum web framework, Tokio async runtime, SQLx for database
- **Frontend**: React 18 + TypeScript + Vite, Tailwind CSS, shadcn/ui components  
- **Database**: SQLite with SQLx migrations
- **Type Sharing**: ts-rs generates TypeScript types from Rust structs
- **MCP Server**: Built-in Model Context Protocol server for AI agent integration
- **CopilotKit Agent**: Python-based LangGraph agent with CopilotKit integration
- **Express Proxy**: TypeScript Express server for CopilotKit runtime proxy

### Project Structure
```
crates/
├── server/         # Axum HTTP server, API routes, MCP server
├── db/            # Database models, migrations, SQLx queries
├── executors/     # AI coding agent integrations (Claude, Gemini, etc.)
├── services/      # Business logic, GitHub, auth, git operations
├── local-deployment/  # Local deployment logic
└── utils/         # Shared utilities

frontend/          # React application
├── src/
│   ├── components/  # React components (TaskCard, ProjectCard, etc.)
│   ├── pages/      # Route pages
│   ├── hooks/      # Custom React hooks (useEventSourceManager, etc.)
│   └── lib/        # API client, utilities

agent/             # CopilotKit LangGraph Agent
├── agent.py       # Main agent logic with LangGraph workflow
├── server.py      # FastAPI server for CopilotKit integration
├── requirements.txt # Python dependencies
├── .env           # Environment variables (API keys, model config)
└── venv/          # Python virtual environment (ignored by git)

express/           # CopilotKit Runtime Proxy
├── server.ts      # Express server with CopilotKit runtime
├── tsconfig.json  # TypeScript configuration
└── package.json   # Node.js dependencies

shared/types.ts    # Auto-generated TypeScript types from Rust
```

### Key Architectural Patterns

1. **Event Streaming**: Server-Sent Events (SSE) for real-time updates
   - Process logs stream to frontend via `/api/events/processes/:id/logs`
   - Task diffs stream via `/api/events/task-attempts/:id/diff`

2. **Git Worktree Management**: Each task execution gets isolated git worktree
   - Managed by `WorktreeManager` service
   - Automatic cleanup of orphaned worktrees

3. **Executor Pattern**: Pluggable AI agent executors
   - Each executor (Claude, Gemini, etc.) implements common interface
   - Actions: `coding_agent_initial`, `coding_agent_follow_up`, `script`

4. **MCP Integration**: Vibe Kanban acts as MCP server
   - Tools: `list_projects`, `list_tasks`, `create_task`, `update_task`, etc.
   - AI agents can manage tasks via MCP protocol

5. **CopilotKit Integration**: Real-time AI chat interface
   - Frontend uses CopilotKit React components for chat UI
   - Express server proxies requests to Python agent via CopilotKit runtime
   - LangGraph agent handles complex multi-step conversations with tools

### API Patterns

- REST endpoints under `/api/*`
- Frontend dev server proxies to backend (configured in vite.config.ts)
- CopilotKit chat requests: Frontend -> Express (port 4000) -> Python Agent (port 8000)
- Authentication via GitHub OAuth (device flow)
- All database queries in `crates/db/src/models/`

### Development Workflow

1. **Backend changes first**: When modifying both frontend and backend, start with backend
2. **Type generation**: Run `npm run generate-types` after modifying Rust types
3. **Database migrations**: Create in `crates/db/migrations/`, apply with `sqlx migrate run`
4. **Component patterns**: Follow existing patterns in `frontend/src/components/`

### Testing Strategy

- **Unit tests**: Colocated with code in each crate
- **Integration tests**: In `tests/` directory of relevant crates  
- **Frontend tests**: TypeScript compilation and linting only
- **CI/CD**: GitHub Actions workflow in `.github/workflows/test.yml`

### Environment Variables

Build-time (set when building):
- `GITHUB_CLIENT_ID`: GitHub OAuth app ID (default: Bloop AI's app)
- `POSTHOG_API_KEY`: Analytics key (optional)

Runtime:
- `BACKEND_PORT`: Backend server port (default: auto-assign)
- `FRONTEND_PORT`: Frontend dev port (default: 3000)
- `HOST`: Backend host (default: 127.0.0.1)
- `DISABLE_WORKTREE_ORPHAN_CLEANUP`: Debug flag for worktrees

Agent-specific (in `agent/.env`):
- `ANTHROPIC_API_KEY`: API key for Claude models
- `MODEL_NAME`: Model name (default: "bedrock-haiku-3.5")
- `BASE_URL`: Model API base URL
- `PORT`: Agent server port (default: 8000)

### CopilotKit Integration Setup

The project includes a complete CopilotKit integration with the following architecture:

1. **Frontend (port 3000)**: React app with CopilotKit chat components
2. **Express Proxy (port 4000)**: CopilotKit runtime that forwards requests to the agent
3. **Python Agent (port 8000)**: LangGraph-based agent with tools and conversation handling

#### Starting the full stack:
```bash
# Terminal 1: Backend (Rust)
pnpm run dev

# Terminal 2: Agent server
cd agent && python server.py

# Terminal 3: Express proxy
cd express && npx ts-node server.ts

# Frontend should already be running from Terminal 1
```

#### Agent Development:
- Agent logic is in `agent/agent.py` using LangGraph workflow
- Tools can be added to the `tools` array in `agent.py`
- Environment variables are loaded from `agent/.env`
- Test locally with `cd agent && python agent.py`